'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-05 15:37:39
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-07 10:32:25
FilePath: \contiki-ng\ML\csv_generator.py
Description: 
'''

import os
import random
import math

import matplotlib.pyplot as plt
import networkx as nx

# get the path of this example
SELF_PATH = os.path.dirname(os.path.abspath(__file__))
print("Self path:", SELF_PATH)

# move two levels up
CONTIKI_PATH = os.path.dirname(SELF_PATH)
print("CONTIKI_PATH:", CONTIKI_PATH)

# Contiki-ng/IRP/Node_with_config
CSC_PATH = os.path.normpath(os.path.join(CONTIKI_PATH, "IRP", "Node_with_config"))

csc_file = os.path.join(CSC_PATH, 'cooja.csc')

def get_distance(point1,point2):
    """Calculate the distance between two points.

    Args:
        point1 (tuple): (x1, y1)
        point2 (tuple): (x2, y2)
    """
    (x1, y1) = point1
    (x2, y2) = point2
    return math.sqrt((x1-x2)**2 + (y1-y2)**2)

def generate_node_map(num):
    """Generate a map of nodes with random x and y coordinates, and the node should not far away the neighbor more than 20.

    Args:
        num (int): number of nodes

    Returns:
        dict: node_map: {node_id: (x, y)}
    """
    # set random seed
    # random.seed(1)
    node_map = {}
    for i in range(1,num+1):
        if i == 1:
            # sink node
            node_map[i] = (50, 50)
            continue
        else:

            #  x and y coordinate: float in range (0, 100)
            x_coordinate = random.uniform(0, 100)
            y_coordinate = random.uniform(0, 100)

            node_map[i] = (x_coordinate, y_coordinate)
    return node_map

def generate_link_map(node_map, label = 0):
    """Generate a map of links status between nodes, including the ratio, signal, LQI and delay.
    Using FSPL (Free Space Path Loss) model to calculate the signal strength.
    Increase in the distance, the signal strength will decrease, the LQI will decrease, and the delay will increase.
    And add some random noise to the status.
    

    Args:
        node_map (dict): node_map: {node_id: (x, y)}
        label (int): label for the training data, describe the status of the network
                                                    : 0: normal
                                                    : 1: high latency
                                                    : 2: high packet loss
                                                    : 3: high latency and packet loss

    Returns:
        dict: link_map: {(src, dst): (ratio, signal, LQI, delay)}
    """
    standard_ratio = 1.0    # 1.0 means 100%
    standard_signal = -10   # dBm, the signal strength, the smaller the better
    standard_LQI = 105      # Link Quality Indicator, the larger the better
    standard_delay = 0      # ms, the smaller the better, change in discrete steps and environment dependent
    link_map = {}
    for src in range(1, len(node_map) + 1):
        for dst in range(src + 1, len(node_map) + 1):
            distance = get_distance(node_map[src], node_map[dst])
            signal = calculate_signal(distance)
            LQI = calculate_LQI(signal)
            delay = calculate_delay(distance)
            ratio = calculate_ratio(signal, label)
            link_map[(src, dst)] = (ratio, signal, LQI, delay)
    return link_map

            
def calculate_ratio(signal, SNR_threshold= 6, noise_mean = -50, label=0):
    """Calculate the ratio of the signal strength, LQI and delay based on the label.

    Args:
        signal (float): signal strength in dBm
        SNR_threshold (float): signal-to-noise ratio threshold
        noise_mean (float): mean of the noise
        label (int): label for the training data, describe the status of the network
                                                    : 0: normal
                                                    : 1: high latency
                                                    : 2: high packet loss
                                                    : 3: high latency and packet loss

    Returns:
        float: ratio of the signal strength, LQI and delay
    """
    if label == 0:
        pass
    elif label == 2:
        noise_mean = -50

    SINR = signal - noise_mean
    if SINR >= SNR_threshold:
        return 1.0
    else:
        difference = SNR_threshold - SINR
        return math.exp(-difference / 10)



def calculate_FSPL(d, f=2400):
    """Calculate the Free Space Path Loss (FSPL) model to calculate the signal strength.
    FSPL(dB) = 20 * log10(d) + 20 * log10(f) + 20 * log10(4 * pi / c)

    Args:
        d (float): distance in meters between the source and the destination
        f (int, optional): frequency in MHz. Defaults to 2400.

    Returns:
        float: signal strength in dBm
    """
    FSPL = 20 * math.log10(d)  + 20 * math.log10(f) + 20 * math.log10(4 * math.pi / 299792458)
    return FSPL

def calculate_signal(distance, output_power=1.5):
    """Calculate the signal strength based on the Free Space Path Loss (FSPL) model.

    Args:
        FSPL (float): Free Space Path Loss (FSPL) in dB
        output_power (float, optional): output power in dBm. Defaults to 1.5.

    Returns:
        float: signal strength in dBm
    """
    FSPL = calculate_FSPL(distance)
    signal = output_power + FSPL
    return signal

def calculate_LQI(signal, sensitivity=-100, LQI_max=105):
    """Calculate the LQI (Link Quality Indicator) based on the signal strength.

    Args:
        signal (float): signal strength in dBm
        sensitivity (int, optional): sensitivity in dBm. Defaults to -100.
        LQI_max (int, optional): maximum value of LQI. Defaults to 105.

    Returns:
        int: Link Quality Indicator (LQI)
    """
    if signal < sensitivity:
        return 0
    else:
        LQI = (signal - sensitivity) / (0 - sensitivity) * LQI_max
        return round(min(LQI, LQI_max))

def calculate_delay(d, c=299792458):
    """Calculate the delay based on the distance between the source and the destination.

    Args:
        d (float): distance in meters between the source and the destination
        c (int, optional): speed of light in m/s. Defaults to 299792458.

    Returns:
        float: delay in ms
    """
    delay = d / c
    return delay


def print_distance(node_map):
    for i in range(1, len(node_map) + 1):
        for j in range(i + 1, len(node_map) + 1):
            print(f"Distance between node {i} and node {j} is {get_distance(node_map[i], node_map[j])}")

def draw_network_graph(node_map):
    # 创建一个图
    G = nx.Graph()

    # 添加节点
    for i, (x, y) in node_map.items():
        G.add_node(i, pos=(x, y))

    # for i in range(1, len(positions) + 1):
    #     for j in range(i + 1, len(positions) + 1):
    #         G.add_edge(i, j)

    pos = nx.get_node_attributes(G, 'pos')

    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=700, edge_color='k', linewidths=1, font_size=15)

    plt.show()

class NetworkGraph:
    def __init__(self):
        self.G = nx.Graph()

    def add_node(self, node_id, pos):
        self.G.add_node(node_id, pos=pos)

    def add_edge(self, source, target, weight=1, color='black'):
        self.G.add_edge(source, target, weight=weight, color=color)

    def draw_graph(self):
        pos = nx.get_node_attributes(self.G, 'pos')
        colors = [self.G[u][v]['color'] for u, v in self.G.edges()]
        weights = [self.G[u][v]['weight'] for u, v in self.G.edges()]

        nx.draw(self.G, pos, with_labels=True, edges=self.G.edges(), edge_color=colors, width=weights,
                node_color='skyblue', node_size=700, linewidths=1, font_size=15)
        plt.show()

if __name__ == "__main__":
    node_map = generate_node_map(10)
    for node, (x,y) in node_map.items():
        print(node, x,y)
    for (node1, node2), (ratio, signal, LQI, delay) in generate_link_map(node_map).items():
        print(f"{node1} -> {node2}: ratio {ratio}, signal {signal}, LQI {LQI}, delay {delay}")
        
    # print_distance(node_map)
    draw_network_graph(node_map)
