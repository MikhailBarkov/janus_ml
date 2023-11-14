from sklearn.model_selection import train_test_split


def train_val_test_split(graph, split=(0.8, 0.1, 0.1)):

    train_size, val_size, test_size = split
    train, test = train_test_split(graph.nodes(), test_size=test_size)
    train_size = train_size * 1 / (train_size + val_size)
    train, val = train_test_split(train, train_size=train_size)

    return train, val, test
