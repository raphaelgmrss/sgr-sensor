#!/usr/bin/env python
# coding: utf-8

# ## SGR Stem

# ### Prerequisites

# In[2]:


import time
import random
import itertools

import numpy as np
import scipy as sp
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import sklearn.metrics as metrics
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader


# In[3]:


device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using {} device".format(device))


# ### Definitions

# In[4]:


class Repeater(nn.Module):
    def __init__(
        self,
        input_size=1,
        output_size=1,
        hidden_size=2**7,
        num_layers=2**2,
        learning_rate=1e-2,
        dropout=0,
        lag=2**8,
        epochs=2**7,
    ):
        super().__init__()

        self.input_size = input_size
        self.output_size = output_size
        self.learning_rate = learning_rate
        self.lag = lag
        self.epochs = epochs
        self.train_loss = []
        self.val_loss = []
        self.period = []

        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            batch_first=True,
            dropout=dropout,
        )
        self.linear = nn.Linear(self.hidden_size, self.output_size)

        self.loss_fn = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.parameters(), lr=self.learning_rate)

    def forward(self, x, y):
        h_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        c_0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(device)
        output, (h_n, c_n) = self.lstm(torch.cat((x, y), dim=2), (h_0, c_0))

        z = self.linear(output)

        return z

    def train_loop(self, dataloader):
        train_loss = []
        period = []

        for batch, (x, y) in enumerate(dataloader):
            start = time.time()

            x = torch.FloatTensor(x.float()).to(device)
            y = torch.FloatTensor(y.float()).to(device)

            z = self.forward(x, y[:, : self.lag, :])
            loss = self.loss_fn(z[:, -1, :], y[:, -1, :])
            train_loss.append(loss.item())

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            end = time.time()
            period.append(end - start)

            progress = int(np.round((batch + 1) / len(dataloader) * 100))
            print(
                "\r{}/{} [{}] {}".format(
                    batch + 1,
                    len(dataloader),
                    "=" * progress + " " * (100 - progress),
                    str(progress) + "%",
                ),
                end="",
            )

        self.train_loss.append(np.mean(train_loss))
        self.period.append(np.mean(period))
        print("\n", end="")

    def val_loop(self, dataloader):
        val_loss = []

        with torch.no_grad():
            for x, y in dataloader:
                x = torch.FloatTensor(x.float()).to(device)
                y = torch.FloatTensor(y.float()).to(device)

                z = self.forward(x, y[:, : self.lag, :])
                loss = self.loss_fn(z[:, -1, :], y[:, -1, :])
                val_loss.append(loss.item())

            self.val_loss.append(np.mean(val_loss))

    def fit(self, train_dataloader, val_dataloader):
        self.train_loss = []
        self.val_loss = []
        self.period = []

        for epoch in range(self.epochs):
            print("\rEpoch {}/{}".format(epoch + 1, self.epochs))

            self.train_loop(train_dataloader)
            self.val_loop(val_dataloader)

            print(
                "{0:.4f}s {1:.4f}s/step - train_loss: {2:.8f} - val_loss: {3:.8f} \n".format(
                    np.sum(self.period),
                    np.mean(self.period),
                    np.mean(self.train_loss),
                    np.mean(self.val_loss),
                )
            )

    def test(self, x, initial_value=None):
        k = self.lag

        if initial_value != None:
            x_0 = initial_value[0]
            y_0 = initial_value[1]

            x = np.concatenate((x_0[-k:, :], x), axis=0)
            y = y_0[-k:, :]
        else:
            y = np.zeros((self.lag, self.output_size))

        x = torch.FloatTensor(np.expand_dims(x, axis=0)).to(device)
        y = torch.FloatTensor(np.expand_dims(y, axis=0)).to(device)

        self.test_period = []
        with torch.no_grad():
            for i in range(x.shape[1]):
                start = time.time()

                z = self.forward(x[:, i : i + k, :], y[:, i : i + k, :])
                y = torch.cat((y, torch.unsqueeze(z[:, -1, :], dim=0)), dim=1)

                end = time.time()
                self.test_period.append(end - start)

                if (i + k + 1) >= x.shape[1]:
                    break

        if initial_value != None:
            y = np.squeeze(y[:, k:, :].cpu().numpy(), axis=0)
        else:
            y = np.squeeze(y.cpu().numpy(), axis=0)

        return y


class Regressor(nn.Module):
    def __init__(self, input_size=1, output_size=1, learning_rate=1e-2, epochs=2**7):
        super().__init__()

        self.input_size = input_size
        self.output_size = output_size
        self.learning_rate = learning_rate
        self.epochs = epochs

        self.train_loss = []
        self.val_loss = []
        self.period = []

        self.linear_relu_stack = nn.Sequential(
            nn.Linear(self.input_size, 256),
            nn.LeakyReLU(),
            nn.Linear(256, 512),
            nn.LeakyReLU(),
            nn.Linear(512, 256),
            nn.LeakyReLU(),
            nn.Linear(256, self.output_size),
        )

        self.loss_fn = nn.MSELoss()
        self.optimizer = torch.optim.SGD(self.parameters(), lr=self.learning_rate)

    def forward(self, x):
        z = self.linear_relu_stack(x)

        return z

    def train_loop(self, dataloader):
        train_loss = []
        period = []

        for batch, (x, y) in enumerate(dataloader):
            start = time.time()

            x = torch.FloatTensor(x.float()).to(device)
            y = torch.FloatTensor(y.float()).to(device)

            z = self.forward(x)
            loss = self.loss_fn(z, y)
            train_loss.append(loss.item())

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            end = time.time()
            period.append(end - start)

            progress = int(np.round((batch + 1) / len(dataloader) * 100))
            print(
                "\r{}/{} [{}] {}".format(
                    batch + 1,
                    len(dataloader),
                    "=" * progress + " " * (100 - progress),
                    str(progress) + "%",
                ),
                end="",
            )

        self.train_loss.append(np.mean(train_loss))
        self.period.append(np.mean(period))
        print("\n", end="")

    def val_loop(self, dataloader):
        val_loss = []

        with torch.no_grad():
            for x, y in dataloader:
                x = torch.FloatTensor(x.float()).to(device)
                y = torch.FloatTensor(y.float()).to(device)

                z = self.forward(x)
                loss = self.loss_fn(z, y)
                val_loss.append(loss.item())

        self.val_loss.append(np.mean(val_loss))

    def fit(self, train_dataloader, val_dataloader):
        self.train_loss = []
        self.val_loss = []
        self.period = []

        for epoch in range(self.epochs):
            print("\rEpoch {}/{}".format(epoch + 1, self.epochs))

            self.train_loop(train_dataloader)
            self.val_loop(val_dataloader)

            print(
                "{0:.4f}s {1:.4f}s/step - train_loss: {2:.8f} - val_loss: {3:.8f} \n".format(
                    np.sum(self.period),
                    np.mean(self.period),
                    np.mean(self.train_loss),
                    np.mean(self.val_loss),
                )
            )


# In[5]:


class RepeaterDataset(Dataset):
    def __init__(self, x, y, lag):
        self.x = x
        self.y = y
        self.lag = lag

    def __len__(self):
        return len(self.x) - self.lag

    def __getitem__(self, idx):
        x = self.x[idx : idx + self.lag]
        y = self.y[idx : idx + self.lag + 1]
        return x, y


class RegressorDataset(Dataset):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __getitem__(self, index):
        return self.x[index], self.y[index]

    def __len__(self):
        return len(self.x)


# In[6]:


class Generator:
    def __init__(self):
        pass

    def preprocess(self, date_time, value, sampling_period):
        data = {
            "date_time": date_time,
            "value": value,
        }
        signal_df = pd.DataFrame(data=data).set_index("date_time")
        signal_df.index = pd.to_datetime(signal_df.index)
        signal_df = signal_df.resample(sampling_period).interpolate(
            method="linear", limit_direction="both", axis=0
        )
        return signal_df

    def generate_date_time(self, start_date, end_date, sampling_period):
        date_time = (
            pd.date_range(
                start=start_date,
                end=end_date,
                freq=sampling_period,
            )
            .strftime("%Y-%m-%d %H:%M:%S")
            .tolist()
        )
        return date_time

    def generate_step(
        self,
        period,
        offset_time,
        rise_time,
        initial_value,
        setpoint,
    ):
        step_period = int(np.around((period - offset_time)))
        rise_patch = (
            (setpoint - initial_value) / rise_time * np.arange(rise_time)
            + initial_value
        ).tolist()
        step = (
            [initial_value] * (period - step_period)
            + rise_patch
            + [setpoint] * (step_period - rise_time)
        )

        return step

    def generate_prbs(
        self,
        period,
        initial_value,
        setpoint_min,
        setpoint_max,
        setpoint_step,
        duration_min,
        duration_max,
    ):
        setpoints = np.arange(setpoint_min, setpoint_max, setpoint_step)
        pad_range = np.asarray([duration_min, duration_max])
        prbs = [initial_value]
        while len(prbs) < period:
            pad = int(np.random.uniform(pad_range[0], pad_range[1]))
            if len(prbs) + pad > period:
                pad = period - len(prbs)
            setpoint = np.random.choice(setpoints)
            prbs += [setpoint] * pad

        return prbs

    def generate_key(self, length=8, seed=None):
        if seed is None:
            seed = int(time.time_ns())

        random.seed(seed)
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"

        key = ""
        for i in range(length):
            key += random.choice(chars)

        return key

    def generate_combinations(self, lists):
        combinations = list(itertools.product(*lists))

        return combinations

    def generate_dataloaders(self, x, y, lag=2**5, batch_size=2**5):
        self.x = x
        self.y = y

        feature_range = (-1, 1)
        self.x_scaler = MinMaxScaler(feature_range=feature_range)
        self.y_scaler = MinMaxScaler(feature_range=feature_range)
        self.x_scaled = self.x_scaler.fit_transform(x)
        self.y_scaled = self.y_scaler.fit_transform(y)

        x_train, x_val, y_train, y_val = train_test_split(
            self.x_scaled, self.y_scaled, test_size=0.5, random_state=42, shuffle=False
        )
        x_val, x_test, y_val, y_test = train_test_split(
            x_val, y_val, test_size=0.5, random_state=42, shuffle=False
        )

        self.x_train = x_train
        self.y_train = y_train
        self.x_val = x_val
        self.y_val = y_val
        self.x_test = x_test
        self.y_test = y_test

        self.train_dataloader = DataLoader(
            RepeaterDataset(self.x_train, self.y_train, lag),
            batch_size=batch_size,
            shuffle=True,
        )
        self.val_dataloader = DataLoader(
            RepeaterDataset(self.x_val, self.y_val, lag),
            batch_size=batch_size,
            shuffle=True,
        )

        return self.train_dataloader, self.val_dataloader


# In[7]:


class Evaluator:
    def __init__(self):
        self.metrics_dict = {}
        self.corr_df = None

    def measure(self, y_true, y_pred):
        self.metrics_dict[
            "explained_variance_score"
        ] = metrics.explained_variance_score(y_true, y_pred)
        self.metrics_dict["mean_absolute_error"] = metrics.mean_absolute_error(
            y_true, y_pred
        )
        self.metrics_dict["mean_squared_error"] = metrics.mean_squared_error(
            y_true, y_pred
        )
        self.metrics_dict["root_mean_squared_error"] = np.sqrt(
            self.metrics_dict["mean_squared_error"]
        )
        self.metrics_dict["median_absolute_error"] = metrics.median_absolute_error(
            y_true, y_pred
        )
        self.metrics_dict[
            "mean_absolute_percentage_error"
        ] = metrics.mean_absolute_percentage_error(y_true, y_pred)
        self.metrics_dict["d2_absolute_error_score"] = metrics.d2_absolute_error_score(
            y_true, y_pred
        )
        self.metrics_dict["d2_pinball_score"] = metrics.d2_pinball_score(y_true, y_pred)
        self.metrics_dict["r2_score"] = metrics.r2_score(y_true, y_pred)

        return self.metrics_dict

    def correlate(self, data, columns, method="pearson"):
        df = pd.DataFrame(data=data)
        df.columns = columns
        self.corr_df = df.corr(method=method)

        return self.corr_df
