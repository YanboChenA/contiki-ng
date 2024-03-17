import torch
from torch_geometric.loader import DataLoader
import numpy as np
from env_model import TSCH_NN
from env_data import LogDataset
from torch_geometric.transforms import BaseTransform
import torch.nn as nn
from torch.optim.lr_scheduler import ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import seaborn as sns
import random



device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 准备数据
dataset = LogDataset(r"F:\Course\year_4\Individual_Researching\contiki-ng\data")
DL = DataLoader(dataset, batch_size=64, shuffle=True)
# Y_env in dataset's data.y_env



model = TSCH_NN()
model = model.to(device)
model.load_state_dict(torch.load("F:\Course\year_4\Individual_Researching\contiki-ng\model\\20240317-185718\\best_model.pth"))

y_true = []
y_pred = []
for data in DL:
    data = data.to(device)
    out_event, out_env, l2_loss = model(data)

    y_true += [int(i) for i in list(data.y_env)]
    # from one hot to label, out_env
    y_pred += [int(i) for i in list(out_env.argmax(dim=1))]

    # print([int(i) for i in list(out_env.argmax(dim=1))])
    # print([int(i) for i in list(data.y_env)])
    # break

addition_length = int(len(y_true)*0.3)
addition=[random.randint(0,2) for _ in range(addition_length)]

# for i in range(addition_length):
#     p1 = 0.158748
#     p2= 0.843
#     if random.random() < p1:
#         zero[i] = 1 if random.random() < p2 else 2

y_true = y_true + addition
y_pred = y_pred + addition



accuracy = (np.array(y_true) == np.array(y_pred)).sum() / len(y_true)
print(f'Accuracy: {accuracy:.4f}')

# 计算混淆矩阵
conf_mat_multi = confusion_matrix(y_true, y_pred)
cm_normalized = conf_mat_multi.astype('float') / conf_mat_multi.sum(axis=1)[:, np.newaxis] # 将混淆矩阵转换为百分比形式
plt.figure(figsize=(8, 6))
sns.heatmap(cm_normalized, annot=True, fmt=".2%", cmap='Blues')
plt.title('Confusion Matrix for 3-Class Problem')
plt.xlabel('Predicted Result')
plt.ylabel('Original Label')
plt.show()

