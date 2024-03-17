'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-11 13:57:38
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-17 18:57:07
FilePath: \contiki-ng\ML\train.py
Description: 
'''
import torch
from torch_geometric.loader import DataLoader
import numpy as np
from tschmodel import TSCH_NN
from data import LogDataset
from torch_geometric.transforms import BaseTransform
import torch.nn as nn
from torch.optim.lr_scheduler import ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import datetime
import os

SELF_PATH = os.path.dirname(os.path.abspath(__file__))
CONTIKI_PATH = os.path.dirname(SELF_PATH)
MODEL_PATH = os.path.join(CONTIKI_PATH, "model")
if not os.path.exists(MODEL_PATH):
    os.makedirs(MODEL_PATH)
current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
SAVE_PATH = os.path.join(MODEL_PATH, current_time)
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)

# 设置超参数
num_epochs = 2000  # 总共训练200轮
learning_rate = 0.001
batch_size = 64
plot_interval = 20  # 每20轮绘制一次图像
enable_plot = False

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 准备数据
dataset = LogDataset(r"F:\Course\year_4\Individual_Researching\contiki-ng\data")

# 划分训练集和验证集
train_dataset, val_dataset = train_test_split(dataset, test_size=0.2, random_state=42)

# 创建数据加载器
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

# 初始化模型
model = TSCH_NN().to(device)

# Load the pre-trained model
file = "F:\Course\year_4\Individual_Researching\contiki-ng\model\\20240317-183025\\best_model.pth"
model.load_state_dict(torch.load(file))

# 初始化优化器和学习率调度程序
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, betas=(0.9, 0.999), eps=1e-8)
scheduler = ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5, verbose=True)

# 定义损失函数
criterion_event = nn.CrossEntropyLoss()
criterion_env = nn.CrossEntropyLoss()

best_acc_env = 0.65
# 训练模型
for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    correct_event = 0
    total_event = 0
    correct_env = 0
    total_env = 0
    features = []  # 用于存储特征向量
    train_labels = []  # 存储训练数据的标签

    # 在训练集上迭代
    for data in train_loader:
        data = data.to(device)
        optimizer.zero_grad()

        out_event, out_env, l2_loss = model(data)
        # graph_features, l2_loss = model(data, data.batch)


        loss_event = criterion_event(out_event, data.y_event)
        loss_env = criterion_env(out_env, data.y_env)
        loss = loss_event + loss_env + l2_loss

        loss.backward()
        optimizer.step()

        total_loss += loss.item()

        _, predicted_event = torch.max(out_event.data, 1)
        total_event += data.y_event.size(0)
        correct_event += (predicted_event == data.y_event).sum().item()

        _, predicted_env = torch.max(out_env.data, 1)
        total_env += data.y_env.size(0)
        correct_env += (predicted_env == data.y_env).sum().item()

        # 提取特征并存储
        features.append(model(data)[0].cpu().detach().numpy())
        train_labels.append(data.y_event.cpu().numpy())  # 假设是事件分类的标签

    train_loss = total_loss / len(train_loader)
    train_acc_event = correct_event / total_event
    train_acc_env = correct_env / total_env

    if (epoch + 1) % plot_interval == 0 and enable_plot is True:  # 每20轮绘制一次图像
        # Concatenate features
        features = np.concatenate(features, axis=0)
        train_labels = np.concatenate(train_labels)

        # Apply t-SNE
        tsne = TSNE(n_components=2, perplexity=30, learning_rate=200)
        tsne_features = tsne.fit_transform(features)

        # Plot t-SNE embeddings
        plt.figure(figsize=(10, 8))
        plt.scatter(tsne_features[:, 0], tsne_features[:, 1], c=train_labels, cmap=plt.cm.get_cmap("jet", 10))
        plt.colorbar()
        plt.title("t-SNE Visualization of Feature Space")
        plt.xlabel("t-SNE Dimension 1")
        plt.ylabel("t-SNE Dimension 2")
        plt.show()

    # 打印训练过程中的指标
    print(f"Epoch: {epoch+1}/{num_epochs}, "
          f"train_loss: {train_loss:.4f}, "
          f"train_acc_event: {train_acc_event:.4f}, "
          f"train_acc_env: {train_acc_env:.4f}")

    # 保存模型  
    if train_acc_env > best_acc_env:
        best_acc_env = train_acc_env
        torch.save(model.state_dict(), f"{SAVE_PATH}/best_model.pth")
        print("Model saved when train_acc_env is", best_acc_env)

torch.save(model.state_dict(), f"{SAVE_PATH}/final_model.pth")
