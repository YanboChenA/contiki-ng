import torch
from torch.utils.data import DataLoader, Dataset
from data import LogDataset
import torch.nn as nn
import torch.optim as optim
from tschmodel import TSCH_NN_NG

class GraphDataset(Dataset):
    def __init__(self, pyg_dataset):
        self.pyg_dataset = pyg_dataset
        
    def __len__(self):
        return len(self.pyg_dataset)
    
    def __getitem__(self, idx):
        data = self.pyg_dataset[idx]
        
        # 提取全局图特征，例如通过取所有节点特征的平均值
        x = torch.max(data.x, dim=0)[0]

        # 提取某几个列，
        indices = [4,5,10,11,12,13,14,15,16,17,18,19]
        
        new_x =[x[i] for i in indices]
        new_x = new_x+ [int(data.y_event) for _ in range(6)]

        x = torch.tensor(new_x)
        

        # 假设data.y是图的标签 to 1D tensor
        y = data.y_event
        # y = torch.tensor(y,dtype=torch.long)
        
        return x, y
    
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# 假设pyg_dataset是您从PyG加载的图数据集
pyg_dataset = LogDataset(r"F:\Course\year_4\Individual_Researching\contiki-ng\data")

dataset = GraphDataset(pyg_dataset)

# 使用DataLoader来批量加载数据
data_loader = DataLoader(dataset, batch_size=32, shuffle=True)

model = TSCH_NN_NG()
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

def accuracy(output, labels):
    _, pred = output.max(dim=1)
    correct = pred.eq(labels).sum().item()
    return correct / labels.size(0)

def train():
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    for x, y in data_loader: 
        x, y = x.to(device), y.to(device)
        y = torch.squeeze(y)
        optimizer.zero_grad()
        out = model(x)
        # print(out,y)
        loss = criterion(out, y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        correct += accuracy(out, y) * y.size(0)
        total += y.size(0)
    avg_loss = total_loss / len(data_loader)
    avg_acc = correct / total
    return avg_loss, avg_acc

if __name__ == "__main__":
    for x,y in data_loader:
        print(x)
        print(y)
        break
    # print('Training...')
    # for epoch in range(100):
    #     train_loss, train_acc = train()
    #     print(f'Epoch: {epoch:03d}, Loss: {train_loss:.4f}, Acc: {train_acc:.4f}')