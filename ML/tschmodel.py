'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-11 14:37:16
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-16 00:23:04
FilePath: \contiki-ng\ML\tschmodel.py
Description: 
'''
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv, global_mean_pool, global_max_pool
import numpy as np

class TSCH_NN(nn.Module):
    def __init__(self, node_feature_dim = 20, edge_feature_dim_ipv6 = 19, edge_feature_dim_tsch = 7, out_dim = 16, num_classes = 3):
        super(TSCH_NN, self).__init__()

        N_Heads = 16
        hidden_dim1 = 64  # 新增的第一个隐藏层维度
        hidden_dim2 = 32  # 新增的第二个隐藏层维度
        hidden_dim3 = 16  # 新增的第三个隐藏层维度
        
        # GAT层处理IPv6链接
        self.GAT_ipv6 = GATConv(in_channels=node_feature_dim, 
                                out_channels=out_dim, 
                                heads=N_Heads, 
                                dropout=0.8,
                                concat=True)
                                # edge_dim=edge_feature_dim_ipv6)
        
        # GAT层处理TSCH链接
        self.GAT_tsch = GATConv(in_channels=node_feature_dim, 
                                out_channels=out_dim, 
                                heads=N_Heads,
                                dropout=0.8,
                                concat=True)
                                # edge_dim=edge_feature_dim_tsch)
        
        # 特征融合层
        self.feature_fusion = nn.Linear(N_Heads * out_dim * 2, hidden_dim1)

        # 新增的隐藏层
        self.hidden1 = nn.Linear(hidden_dim1, hidden_dim2)
        self.hidden2 = nn.Linear(hidden_dim2, hidden_dim3)
        self.hidden3 = nn.Linear(hidden_dim3, out_dim)

        # 新增的全连接层
        self.fc = nn.Linear(hidden_dim3, out_dim)        
        
        # 预测图级别标签的层
        self.classifier_event = nn.Linear(out_dim, num_classes)
        self.classifier_env = nn.Linear(out_dim, num_classes)
        
    def forward(self,data, batch):
        x = data.x
        edge_index_ipv6 = data.edge_index_IPv6
        edge_attr_ipv6 = data.edge_attr_IPv6
        edge_index_tsch = data.edge_index_TSCH
        edge_attr_tsch = data.edge_attr_TSCH
        
        
        # 通过两个GAT层处理节点特征
        nodes_ipv6 = self.GAT_ipv6(x, edge_index_ipv6, edge_attr_ipv6)
        nodes_tsch = self.GAT_tsch(x, edge_index_tsch, edge_attr_tsch)
        
        # 特征融合
        nodes_fused = torch.cat([nodes_ipv6, nodes_tsch], dim=-1)
        nodes_fused = F.relu(self.feature_fusion(nodes_fused))


        # 通过额外的隐藏层
        nodes_fused = F.relu(self.hidden1(nodes_fused))
        nodes_fused = F.relu(self.hidden2(nodes_fused))
        nodes_fused = F.relu(self.hidden3(nodes_fused))
        
        # 应用平均池化层得到图级特征
        graph_features = global_mean_pool(nodes_fused, batch)
        # graph_features = global_mean_pool(nodes_fused, batch)
        
        # 预测图级标签
        out_event = self.classifier_event(graph_features)
        out_env = self.classifier_env(graph_features)
        
        return out_event, out_env

class TSCH_NN_Node(nn.Module):
    def __init__(self, node_feature_dim=20, out_dim=16, num_classes=3):
        super(TSCH_NN_Node, self).__init__()

        N_Heads = 4
        hidden_dim1 = 64  # 第一个隐藏层的维度
        hidden_dim2 = 32  # 第二个隐藏层的维度
        hidden_dim3 = 16  # 第三个隐藏层的维度
        
        # GAT层处理IPv6链接，注意移除了edge_dim参数
        self.GAT_ipv6 = GATConv(in_channels=node_feature_dim, 
                                out_channels=out_dim, 
                                heads=N_Heads, 
                                dropout=0.8,
                                concat=True, 
                                add_self_loops=True)
        
        # 特征融合层
        self.feature_fusion = nn.Linear(N_Heads * out_dim, hidden_dim1)  # 更新输入维度

        # 隐藏层
        self.hidden1 = nn.Linear(hidden_dim1, hidden_dim2)
        self.hidden2 = nn.Linear(hidden_dim2, hidden_dim3)
        self.hidden3 = nn.Linear(hidden_dim3, out_dim)
        
        # 预测图级别标签的层/ use a soft max
        self.classifier_event = nn.Linear(out_dim, num_classes)
        self.classifier_env = nn.Linear(out_dim, num_classes)

    def forward(self, data, batch):
        x = data.x
        edge_index_ipv6 = data.edge_index_IPv6

        # 通过GAT层处理节点特征，移除对TSCH的引用
        nodes_ipv6 = self.GAT_ipv6(x, edge_index_ipv6)
        
        # 特征融合（在这个场景下实际上就是直接处理nodes_ipv6的输出）
        nodes_fused = F.relu(self.feature_fusion(nodes_ipv6))

        # 通过额外的隐藏层
        nodes_fused = F.relu(self.hidden1(nodes_fused))
        nodes_fused = F.relu(self.hidden2(nodes_fused))
        nodes_fused = F.relu(self.hidden3(nodes_fused))
        
        # 应用平均池化层得到图级特征
        graph_features = global_mean_pool(nodes_fused, batch)
        
        # 预测图级标签
        out_event = self.classifier_event(graph_features)
        out_env = self.classifier_env(graph_features)
        
        return out_event, out_env
    
class TSCH_NN_NG(nn.Module):
    def __init__(self, input_dim =18, output_dim=8, class_num=3):
        super(TSCH_NN_NG, self).__init__()

        self.fc1 = nn.Linear(input_dim, 32)

        self.fc2 = nn.Linear(32, 16)
        self.fc3 = nn.Linear(16, output_dim)

        self.foutput_layer_1 = nn.Linear(output_dim, class_num)
        # self.foutput_layer_2 = nn.Linear(output_dim, class_num)

    def forward(self, x):


        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))

        output_event = self.foutput_layer_1(x)
        # output_env = self.foutput_layer_2(x)

        return output_event

