import random

import numpy as np
import torch
from torch.utils.data import DataLoader
from torch.utils.data.dataset import Dataset
from torch import nn
from torchinfo import summary

import consts
import metrics


# Helpful guides:
#   - https://www.learnpytorch.io/04_pytorch_custom_datasets/
#   - https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html
#   - Early stopping: https://clay-atlas.com/us/blog/2021/08/25/pytorch-en-early-stopping/


class DRALdataset(Dataset):
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    def __getitem__(self, index: int):
        x_df = self.X.iloc[index]
        y_df = self.Y.iloc[index]
        x_arr = x_df.to_numpy()
        y_arr = y_df.to_numpy()
        return x_arr, y_arr

    def __len__(self):
        return self.X.shape[0]


class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.linear_sigmoid_stack = nn.Sequential(
            nn.Linear(100, 66),
            nn.Sigmoid(),
            nn.Linear(66, 66),
            nn.Sigmoid(),
            nn.Linear(66, 100),
        )

    def forward(self, x):
        x = x.to(torch.float32)
        x_out = self.linear_sigmoid_stack(x)
        return x_out


def train(dataloader, model, loss_fn, optimizer, device):
    model.train()
    for batch, (X, Y) in enumerate(dataloader):
        X, Y = X.to(device), Y.to(device)
        Y_pred = model(X)
        loss = loss_fn(Y_pred, Y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()


def test(dataloader, model, loss_fn, device):

    num_batches = len(dataloader)
    model.eval()
    test_loss = 0

    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            test_loss += loss_fn(pred, y).item()

    test_loss /= num_batches
    print(f"\tAverage loss: {test_loss:>8f}")
    return test_loss


def test_neural_network(X_train_df, X_test_df, Y_train_df, Y_test_df):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using {device} device")

    # Set seed for reproducibility. TODO Some of this code may be unnecessary. See:
    # https://pytorch.org/docs/stable/notes/randomness.html
    torch.manual_seed(consts.RANDOM_STATE_VAL)
    random.seed(consts.RANDOM_STATE_VAL)
    np.random.seed(consts.RANDOM_STATE_VAL)
    g = torch.Generator()
    g.manual_seed(consts.RANDOM_STATE_VAL)

    def seed_worker(worker_id):
        worker_seed = torch.initial_seed() % 2**32
        np.random.seed(worker_seed)
        random.seed(worker_seed)

    model = NeuralNetwork().to(device)
    batch_size = 32

    summary(model)
    print(f"{batch_size = }")

    train_data = DRALdataset(X_train_df, Y_train_df)
    test_data = DRALdataset(X_test_df, Y_test_df)

    train_dataloader = DataLoader(
        train_data, batch_size=batch_size, worker_init_fn=seed_worker, generator=g
    )
    test_dataloader = DataLoader(
        test_data, batch_size=batch_size, worker_init_fn=seed_worker, generator=g
    )

    loss_fn = metrics.mean_euclidean_distance_tensor
    learning_rate = 1e-3
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)

    # TODO Add early stopping.

    epochs = 50
    test_loss = 0
    for epoch_num in range(epochs):
        print(f"Epoch {epoch_num+1}, ", end="")
        train(train_dataloader, model, loss_fn, optimizer, device)
        test_loss = test(test_dataloader, model, loss_fn, device)

    return test_loss
