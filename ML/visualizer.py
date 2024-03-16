'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-11 10:09:30
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-13 16:46:04
FilePath: \contiki-ng\ML\visualizer.py
Description: 
'''
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from parse import *

def distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

class Visualize():
    def __init__(self, node_map, features):
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
        node_color = "Black"


        # # In self.edge_index_TSCH is a three layer list, the outer layer is edge_index, the middle layer is the period index, the inner layer is the node index map
        edge_index = self.edge_index_TSCH[index]
        edge_features = self.edge_features_TSCH[index]
        Usage_list = np.array([i[0] for i in edge_features])
        Attempt_list = np.array([i[1] for i in edge_features])
        Delay_list = np.array([i[3] for i in edge_features])
        Length_list = np.array([i[5] for i in edge_features])
        # print(Usage_list)
        # print(Attempt_list)
        # print(Delay_list)
        # print(Length_list)
        # print(Attempt_list * Delay_list * Length_list)

        # Width corresponds to the usage of the link then normalize to 0-5, the max width is 5, if usage == 0, width == 0
        Weights = 5 + (Usage_list / np.max(Usage_list)) * 5
        # Color corresponds to product of (attempt, delay, length) then normalize to 0-20, and colormap is plt.cm.Blues
        Colors = (Attempt_list * Delay_list * Length_list) / np.max(Attempt_list * Delay_list * Length_list) * 500
        # Change colors to int:
        Colors = Colors.astype(int)
        print(Colors)
        # # Set the color map
        cmap = plt.cm.Blues

        # Add edges to the graph
        for i in range(len(edge_index)):
            src = edge_index[i][0]
            dst = edge_index[i][1]
            G.add_edge(src, dst, weight=Weights[i])
            # Set the color of the edge
            G[src][dst]['color'] = cmap(Colors[i])

        # Add some control info edge in the graph
        # Loop the node, find the the other node in range of 70, and if the edge is not in the graph, add it to the graph
        for node in self.pos:
            for other_node in self.pos:
                if node != other_node:
                    if distance(self.pos[node][0], self.pos[node][1], self.pos[other_node][0], self.pos[other_node][1]) <= 70:
                        if not G.has_edge(node, other_node):
                            G.add_edge(node, other_node, weight=4)
                            G[node][other_node]['color'] = cmap(70)

            
        
        
        # Don't need to shown the label/ font of node, and add node color as black
        # nx.draw(G, self.pos, with_labels=False, font_weight='bold', edge_color=[G[u][v]['color'] for u,v in G.edges()], width=[G[u][v]['weight'] for u,v in G.edges()])
        nx.draw(G, self.pos, with_labels=False, font_weight='bold', edge_color=[G[u][v]['color'] for u,v in G.edges()], width=[G[u][v]['weight'] for u,v in G.edges()], node_color="#1C304A")
        # Add color bar

        # nx.draw(G, self.pos, with_labels=True, font_weight='bold')
        plt.show()
        


if __name__ == '__main__':
    import pickle
    import json
    import os

    DATA_PATH = r"F:\Course\year_4\Individual_Researching\contiki-ng\data"
    file_name = "2024-03-13_14-10-32"
    # data/label/2024-03-13_14-10-32.json
    log_file = os.path.join(DATA_PATH, "raw", file_name + ".testlog")
    label_file = os.path.join(DATA_PATH, "label", file_name + ".json")
    
    # log_parser = LogParse(log_file)
    # log_parser.process()

    # analyser = LogAnalysis(log_parser)
    # analyser.calculate_features
    
    SELF_DIR = os.path.dirname(os.path.abspath(__file__))
    save_analyser = os.path.join(SELF_DIR, "analyser.pkl")
    # with open(save_analyser, 'wb') as file:
    #     pickle.dump(analyser, file)

    with open(save_analyser, 'rb') as file:
        analyser = pickle.load(file)

    analyser.calculate_features()

    with open(label_file, "r") as f:
        label = json.load(f)
    
    node_map = label["node_map"]
    
    visulaizer = Visualize(node_map, analyser)
    # visulaizer.show_node_map()
    visulaizer.show_graph_tsch()
    