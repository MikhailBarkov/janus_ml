import torch
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint
from sklearn.model_selection import train_test_split

from utils.split import train_val_test_split
from utils.train_setup import device
from utils.data_module import DataModule
from settings import config


class NodeClassificationTrainer(Trainer):

    def __init__(self, hyperparameters_config, Model, split=[0.8, 0.1, 0.1]):
        self.batch_size = config.batch_size

        self.Model = Model

        self.n_layers = hyperparameters_config['n_layers']
        self.n_hidden_multiplier = hyperparameters_config['n_hidden_multiplier']
        self.dropout = hyperparameters_config['dropout']
        self.learning_rate = hyperparameters_config['learning_rate']
        self.split = split

        checkpoint_callback = ModelCheckpoint(monitor="val_acc", save_top_k=1)

        super().__init__(
            max_epochs=hyperparameters_config['max_epochs'],
            enable_progress_bar=False,
            log_every_n_steps=100,
            callbacks=[checkpoint_callback]
        )

    def fit(self, dataset):
        g = dataset[0]

        train_idx, val_idx, g.ndata["test_mask"] = train_val_test_split(g, self.split)

        fanouts = [20]*self.n_layers
        data_module = DataModule(
            g,
            train_idx,
            val_idx,
            fanouts,
            self.batch_size,
        )

        a, b = self.n_hidden_multiplier
        n_hidden = int(a * data_module.in_feats + b * data_module.n_classes)
        params = {
            "in_feats": data_module.in_feats,
            "n_layers": self.n_layers,
            "n_hidden": n_hidden,
            "n_classes": data_module.n_classes,
            "aggregator_type": "mean",
            "dropout": self.dropout,
            "learning_rate": self.learning_rate
        }
        model = self.Model(
            **params
        )
        super().fit(model, datamodule=data_module)
        return model, params
