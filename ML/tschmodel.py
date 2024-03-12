'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-11 14:37:16
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-11 21:06:28
FilePath: \contiki-ng\ML\tschmodel.py
Description: 
'''
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATConv, global_mean_pool

# class TSCH_NN(torch.nn.Module):
#     def __init__(self, num_node_features = 20, num_edge_features_ipv6 = 19, num_edge_features_tsch = 7, num_classes =3):
class TSCH_NN(nn.Module):
    def __init__(self, node_feature_dim = 20, edge_feature_dim_ipv6 = 19, edge_feature_dim_tsch = 7, out_dim = 16, num_classes = 3):
        super(TSCH_NN, self).__init__()
        
        # GAT层处理IPv6链接
        self.gat_ipv6 = GATConv(in_channels=node_feature_dim, 
                                out_channels=out_dim, 
                                heads=1, 
                                concat=True, 
                                edge_dim=edge_feature_dim_ipv6)
        
        # GAT层处理TSCH链接
        self.gat_tsch = GATConv(in_channels=node_feature_dim, 
                                out_channels=out_dim, 
                                heads=1, 
                                concat=True, 
                                edge_dim=edge_feature_dim_tsch)
        
        # 特征融合层
        self.feature_fusion = nn.Linear(out_dim * 2, out_dim)
        
        # 预测图级别标签的层
        self.classifier_event = nn.Linear(out_dim, num_classes)
        self.classifier_env = nn.Linear(out_dim, num_classes)
        
    def forward(self, x, edge_index_ipv6, edge_attr_ipv6, edge_index_tsch, edge_attr_tsch, batch):
        # 通过两个GAT层处理节点特征
        nodes_ipv6 = self.gat_ipv6(x, edge_index_ipv6, edge_attr_ipv6)
        nodes_tsch = self.gat_tsch(x, edge_index_tsch, edge_attr_tsch)
        
        # 特征融合
        nodes_fused = torch.cat([nodes_ipv6, nodes_tsch], dim=-1)
        nodes_fused = F.relu(self.feature_fusion(nodes_fused))
        
        # 应用平均池化层得到图级特征
        graph_features = global_mean_pool(nodes_fused, batch)
        
        # 预测图级标签
        out_event = self.classifier_event(graph_features)
        out_env = self.classifier_env(graph_features)
        
        return out_event, out_env