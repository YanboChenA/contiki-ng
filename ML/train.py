'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-11 13:57:38
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-11 21:21:57
FilePath: \contiki-ng\ML\train.py
Description: 
'''
import torch
from torch_geometric.loader import DataLoader
import numpy as np
# from datetime import datetime
from tschmodel import TSCH_NN
from data import LogDataset

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# device = torch.device("cpu")

dataset = LogDataset(r"F:\Course\year_4\Individual_Researching\contiki-ng\data")
train_loader = DataLoader(dataset, batch_size=1, shuffle=True)

# train_dataset, val_dataset = torch.utils.data.random_split(dataset, [int(len(dataset)*0.8), len(dataset) - int(len(dataset)*0.8)])

# train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
# val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

model = TSCH_NN()
model = model.to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = torch.nn.CrossEntropyLoss()


def train():
    model.train()
    total_loss = 0
    for data in train_loader:
        data = data.to(device)
        optimizer.zero_grad()
        out1, out2 = model(data.x, data.edge_index_IPv6, data.edge_attr_IPv6, data.edge_index_TSCH, data.edge_attr_TSCH, data.batch)
        loss = criterion(out1, data.y_event) + criterion(out2, data.y_env)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(train_loader)

# 训练循环
for epoch in range(1, 101):
    loss = train()
    print(f'Epoch: {epoch}, Loss: {loss}')