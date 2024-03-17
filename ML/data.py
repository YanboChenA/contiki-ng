'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-02-22 10:05:02
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-17 15:33:54
FilePath: \contiki-ng\ML\data.py
Description: 
'''

import torch
from torch_geometric.data import InMemoryDataset, Data
import os
import numpy as np
from parse import *
import json
from torch_geometric.transforms import BaseTransform
import pickle

class LogTransform(BaseTransform):
    def __call__(self, data):
        # for index of edge_index, minus 1 to fit the 0-based index
        data = self.index_minus_one(data)
        # for the node features, limit the value of each feature
        # data = self.custom_node_feature_lim(data)
        return data
    
    def index_minus_one(self, data):
        data.edge_index_IPv6 -= 1
        data.edge_index_TSCH -= 1
        return data
    
    def custom_node_feature_lim(self, data):
        # two list, one is the upper limit, the other is the lower limit
        # recalculate the node features, 使得节点特征被归一化，使得每个特征的值在0-1之间
        node_features = data.x                                                                                                                                         
        upper_limit = [1,       1,      1,      1,
                       1e3,     1e7,    1e2,    1e2,
                       1e1,     1e1,    1e3,    1e3,
                       1e1,     1e1,    1e1,    1e1,
                       1e3,     1e3,    1e3,    1e3]
        lower_limit = [0 for _ in range(20)]
        for i in range(20):
            node_features[:,i] = (node_features[:,i] - lower_limit[i]) / (upper_limit[i] - lower_limit[i])
        data.x = node_features
        return data

class LogDataset(InMemoryDataset):
    def __init__(self, root, transform=None, pre_transform=None):
        self._root = root
        super(LogDataset, self).__init__(root, transform, pre_transform)
        # self.data, self.slices, data_list = torch.load(self.processed_paths[0])
        self.load_processed_data()

    def load_processed_data(self):
        self.data_list = []
        for processed_file in self.processed_file_names:
            path = os.path.join(self.processed_dir, processed_file)
            data, slices, data_list = torch.load(path)
            # Merge the data_list
            # new_data_list = []
            # for data in data_list:
            #     if data.y_event!= 0:
            #         new_data_list.append(data)
            for _data in data_list:
                _data.y_event = torch.tensor([0], dtype=torch.long) if _data.y_event == 0 else torch.tensor([1], dtype=torch.long)
                if _data.y_env == 0:
                    self.data_list.append(_data)
        self.data, self.slices = self.collate(self.data_list)

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
    
    @property
    def label_file_names(self):
        # return ["label_1.json", "label_2.json", ...]
        label_names = []
        label_path = os.path.join(self.root, "label")
        for file in os.listdir(label_path):
            if file.endswith(".json"):
                label_names.append(file)

    def download(self):
        # Not needed
        pass

    def process(self):
        self.label_dir = os.path.join(self.root, "label")
        self.quick_raw_dir = os.path.join(self.root, "quick_raw")
        for raw_file_name in self.raw_file_names:
            # check if the processed file already exists
            processed_file_name = f"processed_{raw_file_name.replace('.testlog', '.pt')}"
            processed_file_path = os.path.join(self.processed_dir, processed_file_name)
            if os.path.exists(processed_file_path):
                print(f"File {processed_file_name} already exists, skipping...")
                continue
            else:
                print(f"Processing file {raw_file_name}...")
            

            # Initialize an empty list to store the data objects
            data_list = []
            
            # Read the raw data
            filepath = os.path.join(self.raw_dir, raw_file_name)  # assume only use the first file
            quick_path = os.path.join(self.quick_raw_dir, raw_file_name.replace('.testlog', '.pkl'))

            if os.path.exists(quick_path):
                with open(quick_path, 'rb') as file:
                    analyser = pickle.load(file)
            else:
                # Parse the log file
                log_parser = LogParse(log_path=filepath)
                log_parser.process()

                # Read Features
                analyser = LogAnalysis(log_parser)
                analyser.calculate_features()
                with open(quick_path, 'wb') as file:
                    pickle.dump(analyser, file)

            # Read Labels
            label_path = os.path.join(self.root, "label", raw_file_name.replace('.testlog', '.json'))
            with open(label_path, 'r') as file:
                labels = json.load(file)
            event_labels = labels["label_list"]
            env_label = labels["env_label"]

            

            # # From the log_parser get the nodes, including the node status, and the some    links
            # nodes = log_parser.nodes

            # 1 hour = 120 periods (30s/period)
            for period_index in range(1,120):
                # Node Features
                node_features = analyser.node_features[:,:,period_index]

                # Edge Index and Edge Features for IPv6
                edge_index_IPv6 = analyser.edge_index_IPv6[period_index]
                edge_features_IPv6 = analyser.edge_features_IPv6[period_index]

                # Edge Index and Edge Features for TSCH    
                edge_index_TSCH = analyser.edge_index_tsch[period_index]  
                edge_features_TSCH = analyser.edge_features_tsch[period_index]          

                # Convert the data to PyTorch tensors
                node_features = torch.tensor(node_features, dtype=torch.float)
                edge_index_IPv6 = torch.tensor(edge_index_IPv6, dtype=torch.long).t().contiguous()
                edge_index_TSCH = torch.tensor(edge_index_TSCH, dtype=torch.long).t().contiguous()
                edge_features_IPv6 = torch.tensor(edge_features_IPv6, dtype=torch.float)
                edge_features_TSCH = torch.tensor(edge_features_TSCH, dtype=torch.float)

                # Label
                event_label = event_labels[period_index]

                # # add the event label to the node features, add a new column to the last
                # event_label_list = np.array([event_label for _ in range(node_features.shape[0])])
                # event_label_list = torch.tensor(event_label_list, dtype=torch.long).unsqueeze(-1)
                # node_features = torch.cat([node_features, event_label_list], dim=-1)
                

                # Create Data object
                data = Data(x=node_features,
                            edge_index_IPv6=edge_index_IPv6,
                            edge_index_TSCH=edge_index_TSCH,
                            edge_attr_IPv6=edge_features_IPv6,
                            edge_attr_TSCH=edge_features_TSCH,
                            y_event = torch.tensor([event_label], dtype=torch.long),
                            y_env = torch.tensor([env_label], dtype=torch.long))
                
                if self.pre_transform is not None:
                    data = self.pre_transform(data)
                data_list.append(data)

            # Use the collate function to create a batch of data objects
            data, slices = self.collate(data_list)

            # Save the processed data to the processed_dir
            # processed_file_name = f"processed_{raw_file_name.replace('.testlog', '.pt')}"
            # torch.save((data, slices), os.path.join(self.processed_dir, processed_file_name))
            torch.save((data, slices, data_list), processed_file_path)

if __name__ == "__main__":
    root = "F:/Course/year_4/Individual_Researching/contiki-ng/data"

    # print(len(dataset))
    # print(dataset.raw_file_names)
    # print(dataset.processed_file_names)
    
    # print(dataset.processed_file_names)
    # dataset.process()

    # transform = LogTransform()
    dataset = LogDataset(root,pre_transform=LogTransform())
    from torch_geometric.loader import DataLoader
    loader = DataLoader(dataset, batch_size=1, shuffle=True)

    for data in loader:
        x = torch.mean(data.x, dim=0)
        print(x,data.y_event)
        





