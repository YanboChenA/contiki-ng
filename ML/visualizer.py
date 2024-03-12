'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-11 10:09:30
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-11 16:35:06
FilePath: \contiki-ng\ML\visualizer.py
Description: 
'''
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from parse import *


class Visualizer():
    def __init__(self, node_map, features: Features):
        self.pos={int(key): value for key, value in node_map.items()}
        self.node_features = features.node_features
        self.edge_features_IPv6 = features.edge_features_IPv6
        self.edge_features_TSCH = features.edge_features_tsch
        self.edge_index_IPv6 = features.edge_index_IPv6
        self.edge_index_TSCH = features.edge_index_tsch

    def show_node_map(self, index = None, weight = None):
        # Show the node map, the node in self.pos is the node map
        G = nx.Graph()
        G.add_nodes_from(self.pos)
        # if weight is None and index is None:
        nx.draw(G, self.pos, with_labels=True, font_weight='bold')
        plt.show()

    
    def show_graph_tsch(self, index = 10):
        G = nx.Graph()
        G.add_nodes_from(self.pos)
        # # In self.edge_index_TSCH is a three layer list, the outer layer is edge_index, the middle layer is the period index, the inner layer is the node index map
        edge_index = self.edge_index_TSCH[index]
        for i in edge_index:
            G.add_edge(i[0], i[1])

        nx.draw(G, self.pos, with_labels=True, font_weight='bold')
        plt.show()
        


if __name__ == '__main__':
    import pickle
    import json
    with open(r"F:\Course\year_4\Individual_Researching\contiki-ng\ML\feature.pkl", 'rb') as file:
        features = pickle.load(file)

    with open(r"F:\Course\year_4\Individual_Researching\contiki-ng\data\label\2024-03-10_21-23-45.json", 'r') as file:
        data = json.load(file)

    print(features.node_features.shape)
    print(len(features.edge_features_IPv6[1][0]))
    print(features.edge_features_tsch[1])

    # node_map = data['node_map']
    # visualizer = Visualizer(node_map, features)
    # visualizer.show_node_map()
    # visualizer.show_graph_tsch()

    