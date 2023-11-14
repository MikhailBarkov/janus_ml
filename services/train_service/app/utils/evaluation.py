import torch
import torch.nn.functional as F
import torchmetrics.functional as MF
import dgl


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def predict(graph, model, batch_size, device):
    graph.ndata["h"] = graph.ndata["feat"]
    sampler = dgl.dataloading.NeighborSampler(
        [25]*model.n_classes, prefetch_node_feats=["feat"], prefetch_labels=["label"]
    )
    data_loader = dgl.dataloading.DataLoader(
        graph,
        torch.arange(graph.number_of_nodes()).to(device),
        sampler,
        device=device,
        batch_size=batch_size,
        num_workers=2
    )

    for i, layer in enumerate(model.layers):
        y = torch.zeros(
            graph.num_nodes(),
            model.n_hidden if i != len(model.layers) - 1 else model.n_classes,
            device='cpu'
        )
        for input_nodes, output_nodes, blocks in data_loader:
            block = blocks[0]
            x = block.srcdata['h']
            h = layer(block, x)
            if i != len(model.layers) - 1:
                h = F.relu(h)
                h = model.dropout(h)

            y[output_nodes] = h.to('cpu')

        graph.ndata["h"] = y

    del graph.ndata['h']
    return y


def evaluate(dataset, test_mask, model):
    predict_batch_size = 4069
    graph = dataset[0]

    with torch.no_grad():
        pred = predict(graph, model.to(device), predict_batch_size, device)
        pred = pred[test_mask]
        label = graph.ndata["label"][test_mask]
        accuracy = MF.accuracy(
            pred, label, 'multiclass', num_classes=model.n_classes
        )
        precision = MF.average_precision(
            pred, label, 'multiclass', average='macro', num_classes=model.n_classes
        )

    return round(accuracy.item(), 3), round(precision.item(), 3)
