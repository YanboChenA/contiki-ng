'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-17 09:57:51
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-17 10:23:22
FilePath: \contiki-ng\ML\check.py
Description: 
'''
import torch
from data import LogDataset , LogTransform

def check_dataset(dataset):
    for i in range(len(dataset)):
        data = dataset[i]
        print(f"Checking data {i}:")
        # print("x attribute dimensions:", data.x.size())
        # print("edge_index_IPv6 attribute dimensions:", data.edge_index_IPv6.size())
        # print("edge_attr_IPv6 attribute dimensions:", data.edge_attr_IPv6.size())
        # print("edge_index_TSCH attribute dimensions:", data.edge_index_TSCH.size())
        # print("edge_attr_TSCH attribute dimensions:", data.edge_attr_TSCH.size())
        # print("y_event attribute dimensions:", data.y_event.size())
        # print("y_env attribute dimensions:", data.y_env.size())

        # 检查维度是否匹配
        if data.edge_index_IPv6.size(1) != data.edge_attr_IPv6.size(0):
            print("Error: edge_index_IPv6 and edge_attr_IPv6 dimensions do not match!")
        
        if data.edge_index_TSCH.size(1) != data.edge_attr_TSCH.size(0):
            print("Error: edge_index_TSCH and edge_attr_TSCH dimensions do not match!")

        # 添加其他需要检查的匹配逻辑

if __name__ == "__main__":
    root = "F:/Course/year_4/Individual_Researching/contiki-ng/data"
    dataset = LogDataset(root, pre_transform=LogTransform())
    check_dataset(dataset)
