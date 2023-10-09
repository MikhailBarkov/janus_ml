import torch
import torch.nn.functional as F
import torchmetrics.functional as MF
import dgl


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def predict(graph, model, batch_size, device):
    graph.ndata["h"] = graph.ndata["feat"]
    sampler = dgl.dataloading.MultiLayerFullNeighborSampler(1)
    data_loader = dgl.dataloading.DataLoader(
        graph,
        torch.arange(graph.number_of_nodes()).to(device),
        sampler,
        device=device,
        batch_size=batch_size,
        num_workers=2
    )

    for l, layer in enumerate(model.layers):
        y = torch.zeros(
            graph.num_nodes(),
            model.n_hidden if l != len(model.layers) - 1 else model.n_classes,
            device='cpu'
        )
        for input_nodes, output_nodes, blocks in data_loader:
            block = blocks[0]
            x = block.srcdata['h']
            h = layer(block, x)
            if l != len(model.layers) - 1:
                h = F.relu(h)
                h = model.dropout(h)

            y[output_nodes] = h.to('cpu')

        graph.ndata["h"] = y

    del graph.ndata['h']
    return y


def evaluate(dataset, model):
    predict_batch_size = 4096
    graph = dataset[0]
    test_idx = graph.ndata['test_mask'].type(torch.int64)

    with torch.no_grad():
        pred = predict(graph, model.to(device), predict_batch_size, device)
        pred = pred[test_idx]
        label = graph.ndata["label"][test_idx]
        accuracy = MF.accuracy(pred, label, 'multiclass', num_classes=model.n_classes)
        accuracy = round(accuracy.item(), 3)

    return accuracy