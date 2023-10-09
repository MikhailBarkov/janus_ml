import torch
import numpy as np
from sklearn.model_selection import train_test_split


def train_val_test_split(graph, split=(0.8, 0.1, 0.1)):
    # idx = graph.nodes()
    train_size, val_size, test_size = split
    train, test = train_test_split(graph.nodes(), test_size=test_size)
    train_size = train_size * 1 / (train_size + val_size)
    train, val = train_test_split(train, train_size=train_size)

    train_mask = torch.tensor([1 if x in train else 0 for x in graph.nodes()])
    val_mask = torch.tensor([1 if x in val else 0 for x in graph.nodes()])
    test_mask = torch.tensor([1 if x in test else 0 for x in graph.nodes()])

    return train_mask, val_mask, test_mask
