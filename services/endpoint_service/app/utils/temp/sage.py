import dgl
import torch
import dgl.data
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchmetrics import Accuracy
from pytorch_lightning import LightningModule
import pickle


class SAGE(LightningModule):

    def __init__(
        self,
        in_feats: int,
        n_layers: int,
        n_hidden: int,
        n_classes: int,
        aggregator_type: str,
        dropout: float,
        learning_rate: float
    ):
        super().__init__()

        self.NAME = 'SAGE'

        self.layers = nn.ModuleList()
        self.layers.append(
            dgl.nn.SAGEConv(in_feats, n_hidden, aggregator_type)
        )
        for i in range(1, n_layers - 1):
            self.layers.append(
                dgl.nn.SAGEConv(n_hidden, n_hidden, aggregator_type)
            )
        self.layers.append(
            dgl.nn.SAGEConv(n_hidden, n_classes, aggregator_type)
        )

        self.dropout = nn.Dropout()
        self.n_hidden = n_hidden
        self.n_classes = n_classes
        self.learning_rate = learning_rate
        self.train_acc = Accuracy('multiclass', num_classes=n_classes)
        self.val_acc = Accuracy('multiclass', num_classes=n_classes)

    def forward(self, graph, x):
        h = x
        for l in self.layers:
            h = l(graph, h)
            if l != len(self.layers) - 1:
                h = F.relu(h)
                h = self.dropout(h)
        return h

    def training_step(self, batch, batch_idx):
        input_nodes, output_nodes, blocks = batch
        x = blocks[0].srcdata["feat"]
        y = blocks[-1].dstdata["label"]
        y_hat = self(blocks, x)
        loss = F.cross_entropy(y_hat, y)
        self.train_acc(torch.argmax(y_hat, 1), y)
        self.log(
            "train_acc",
            self.train_acc,
            prog_bar=True,
            on_step=True,
            on_epoch=False
        )
        return loss

    def validation_step(self, batch, batch_idx):
        input_nodes, output_nodes, blocks = batch
        x = blocks[0].srcdata["feat"]
        y = blocks[-1].dstdata["label"]
        y_hat = self(blocks, x)
        self.val_acc(torch.argmax(y_hat, 1), y)
        self.log(
            "val_acc",
            self.val_acc,
            prog_bar=True,
            on_step=True,
            on_epoch=True,
            sync_dist=True
        )

    def configure_optimizers(self):
        optimizer = torch.optim.Adam(
            self.parameters(),
            lr=self.learning_rate,
            weight_decay=5e-4
        )
        return optimizer
