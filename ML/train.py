'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-11 13:57:38
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-16 00:16:01
FilePath: \contiki-ng\ML\train.py
Description: 
'''
import torch
from torch_geometric.loader import DataLoader
import numpy as np
# from datetime import datetime
from tschmodel import TSCH_NN, TSCH_NN_Node, TSCH_NN_NG
from data import LogDataset
import time
import datetime
import os
import csv
from torch_geometric.transforms import BaseTransform

import warnings

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# device = torch.device("cpu")

# dataset = LogDataset(r"F:\Course\year_4\Individual_Researching\contiki-ng\data", transform=_transform)
dataset = LogDataset(r"F:\Course\year_4\Individual_Researching\contiki-ng\data")

# 分割数据集为训练集和验证集
train_size = int(len(dataset) * 0.8)
val_size = len(dataset) - train_size
train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

model = TSCH_NN()
# model = TSCH_NN_Node()
# model = TSCH_NN_NG()
model = model.to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
# optimizer = torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.1)
# optimizer = torch.optim.AdamW(model.parameters(), lr=0.0001, betas=(0.9, 0.999), eps=1e-8, weight_decay=1e-2)
# optimizer = torch.optim.RMSprop(model.parameters(), lr=0.001, alpha=0.99, eps=1e-8)

criterion = torch.nn.CrossEntropyLoss()

def accuracy(output, labels):
    _, pred = output.max(dim=1)
    correct = pred.eq(labels).sum().item()
    return correct / labels.size(0)

# def train():
    model.train()
    total_loss = 0
    correct_event = 0
    correct_env = 0
    total = 0
    for data in train_loader:
        data = data.to(device)
        optimizer.zero_grad()
        out_event, out_env = model(data.x, data.edge_index_IPv6, data.edge_attr_IPv6, data.edge_index_TSCH, data.edge_attr_TSCH, data.batch)
        loss_event = criterion(out_event, data.y_event)
        loss_env = criterion(out_env, data.y_env)
        loss = loss_event + loss_env
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        correct_event += accuracy(out_event, data.y_event) * data.y_event.size(0)
        correct_env += accuracy(out_env, data.y_env) * data.y_env.size(0)
        total += data.y_event.size(0)
    avg_loss = total_loss / len(train_loader)
    avg_acc_event = correct_event / total
    avg_acc_env = correct_env / total
    return avg_loss, avg_acc_event, avg_acc_env

def train():
    model.train()  # 设置模型为训练模式
    total_loss = 0
    correct_event = 0
    total = 0
    for data in train_loader:
        data = data.to(device)
        optimizer.zero_grad()  
        out_event, _ = model(data, data.batch)
        loss_event = criterion(out_event, data.y_event)
        loss_event.backward()  
        optimizer.step()  
        total_loss += loss_event.item()
        correct_event += accuracy(out_event, data.y_event) * data.y_event.size(0)
        total += data.y_event.size(0)
    avg_loss = total_loss / len(train_loader)
    avg_acc_event = correct_event / total
    return avg_loss, avg_acc_event, 0

# 验证函数
def validate():
    model.eval()
    val_loss = 0
    correct_event = 0
    correct_env = 0
    total = 0
    with torch.no_grad():
        for data in val_loader:
            data = data.to(device)
            out_event, out_env = model(data.x, data.edge_index_IPv6, data.edge_attr_IPv6, data.edge_index_TSCH, data.edge_attr_TSCH, data.batch)
            val_loss += criterion(out_event, data.y_event).item() + criterion(out_env, data.y_env).item()
            correct_event += accuracy(out_event, data.y_event) * data.y_event.size(0)
            correct_env += accuracy(out_env, data.y_env) * data.y_env.size(0)
            total += data.y_event.size(0)
    avg_loss = val_loss / len(val_loader)
    avg_acc_event = correct_event / total
    avg_acc_env = correct_env / total
    return avg_loss, avg_acc_event, avg_acc_env

if __name__ == "__main__":
    # for data in train_loader:
    #     print(data.x)
        
    loss = []
    print('Start Training:')
    for epoch in range(15):
        train_loss, train_acc_event, train_acc_env = train()
        # val_loss, val_acc_event, val_acc_env = validate()
        val_loss = 0
        val_acc_event = 0
        val_acc_env = 0
        print('Epoch: {:03d}'.format(epoch+1),
              'train_loss: {:.4f}'.format(train_loss),
              'train_acc_event: {:.4f}'.format(train_acc_event),
              'train_acc_env: {:.4f}'.format(train_acc_env),
              'val_loss: {:.4f}'.format(val_loss),
              'val_acc_event: {:.4f}'.format(val_acc_event),
              'val_acc_env: {:.4f}'.format(val_acc_env))
        
        # Add early stopping
        # loss.append(train_loss)
        # if len(loss) > 5:
    
    # show the first 15 input lable and output lable
    i =0
    for data in val_loader:
        data = data.to(device)
        out_event, out_env = model(data, data.batch)
        if i <= 10:
            print("Input label: ", data.y_event)
            print("Output label: ", out_event.argmax(dim=1))
        i += 1
        if i == 10:
            break

    # # Save the model
    # save_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    # save_path = os.path.join(dataset._root, "model", save_time)
    # if not os.path.exists(save_path):
    #     os.makedirs(save_path)
    # save_file = os.path.join(save_path, "model.pth")
    # torch.save(model.state_dict(), save_file)
    # print('Model saved at:', save_file)