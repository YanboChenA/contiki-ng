'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-02-22 10:05:02
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-04 11:58:47
FilePath: \contiki-ng\ML\data.py
Description: 
'''

import torch
from torch_geometric.data import InMemoryDataset, Data
import os
import numpy as np
from parse import *

class LogDataset(InMemoryDataset):
    def __init__(self, root, transform=None, pre_transform=None):
        super(LogDataset, self).__init__(root, transform, pre_transform)
        self.data, self.slices = torch.load(self.processed_paths[0])
        # with open(filepath, 'r') as file:
        #     self.lines = file.readlines()
        # # self.process()
            
    @property
    def raw_file_names(self):
        # return ['some_file_1.testlog', 'some_file_2.testlog', ...]
        raw_names = []
        for file in os.listdir(self.raw_dir):
            if file.endswith(".testlog"):
                raw_names.append(file)

        return raw_names

    @property
    def processed_file_names(self):
        # return ['data_1.pt', 'data_2.pt', ...]
        processed_names = []
        for raw_file_name in self.raw_file_names:
            processed_name = f"processed_{raw_file_name.replace('.testlog', '.pt')}"
            processed_names.append(processed_name)
        return processed_names

    def download(self):
        # Not needed
        pass

    def process(self):
        for raw_file_name in self.raw_file_names:
            # Initialize an empty list to store the data objects
            data_list = []
            
            # Read the raw data
            filepath = os.path.join(self.raw_dir, raw_file_name)  # assume only use the first file
            
            # Parse the log file
            log_parser = LogParse(log_path=filepath)
            log_parser.process()

            # From the log_parser get the nodes, including the node status, and the some links
            nodes = log_parser.nodes

            # 1 hour = 120 periods (30s/period)
            for period_index in range(120):
                # Node Features
                node_num = len(log_parser.nodes.keys()) # 8
                node_num = len(nodes.keys()) # 8
                node_features = [[] for _ in range(node_num)]
                period_index = 5
                for node_id in range(1,node_num+1):
                    node = nodes[node_id]
                    node_status = node.get_node_status(period_index)
                    node_features[node_id-1] = node_status

                node_features = torch.tensor(node_features, dtype=torch.float)

                # Edge Index and Edge Features
                edge_index = []
                edge_features = []
                







                # 创建Data对象
                data = Data(x=node_features, edge_index=edge_index)
                if self.pre_transform is not None:
                    data = self.pre_transform(data)
                
                data_list.append(data)

            # Use the collate function to create a batch of data objects
            data, slices = self.collate(data_list)

            # Save the processed data to the processed_dir
            processed_file_name = f"processed_{raw_file_name.replace('.txt', '.pt')}"
            torch.save((data, slices), os.path.join(self.processed_dir, processed_file_name))

        
if __name__ == "__main__":
    root = "F:/Course/year_4/Individual_Researching/contiki-ng/data"
    dataset = LogDataset(root)
    print(dataset.raw_file_names)
    # print(dataset.processed_file_names)
    # dataset.process()
