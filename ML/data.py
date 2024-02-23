'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-02-22 10:05:02
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-02-22 13:59:08
FilePath: \contiki-ng\ML\data.py
Description: 
'''
from torch_geometric.data import InMemoryDataset
import torch
import numpy as np


class LogDataset(InMemoryDataset):
    def __init__(self, root, transform=None, pre_transform=None):
        super(LogDataset, self).__init__(root, transform, pre_transform)
        self.data, self.slices = torch.load(self.processed_paths[0])
        # with open(filepath, 'r') as file:
        #     self.lines = file.readlines()
        # # self.process()
            
    @property
    def raw_file_names(self):
        # 返回原始文件名列表
        return ['loglistener1.txt']

    @property
    def processed_file_names(self):
        # 返回处理后的文件名列表
        return ['data.pt']

    def download(self):
        # 如果需要，可以在这里实现数据的下载逻辑
        pass

    def parse_line(self, line):
        # input a line in log, parse it and return a list of values and type
        

    def process(self):

        linenumber = 518
        data = self.lines[linenumber].split()
        print(data)

if __name__ == "__main__":

    root = "F:/Course/year_4/Individual_Researching/contiki-ng/data"
    dataset = LogDataset(root)
    dataset.process()
