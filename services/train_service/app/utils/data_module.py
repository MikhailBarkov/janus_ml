import dgl
import torch
from pytorch_lightning import LightningDataModule


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class DataModule(LightningDataModule):

    def __init__(
        self, graph, train_idx, val_idx, fanouts, batch_size
    ):
        super().__init__()

        sampler = dgl.dataloading.NeighborSampler(
            fanouts, prefetch_node_feats=["feat"], prefetch_labels=["label"]
        )

        self.graph = graph
        self.train_idx = train_idx
        self.val_idx = val_idx
        self.sampler = sampler
        self.batch_size = batch_size
        self.in_feats = graph.ndata["feat"].shape[1]
        self.n_classes = len(torch.unique(graph.ndata['label']))

    def train_dataloader(self):
        loader = dgl.dataloading.DataLoader(
            self.graph,
            self.val_idx,
            self.sampler,
            device=device,
            batch_size=self.batch_size,
            num_workers=1
        )

        with loader.enable_cpu_affinity():
            return loader

    def val_dataloader(self):
        loader = dgl.dataloading.DataLoader(
            self.graph,
            self.val_idx,
            self.sampler,
            device=device,
            batch_size=self.batch_size,
            num_workers=1
        )

        with loader.enable_cpu_affinity():
            return loader
