import xml.etree.ElementTree as ET
from copy import deepcopy
import sys
import os
import random

class CSC_generator:
    def __init__(self, csc_file = "MRM.csc"):
        """

        Args:   
            csc_file (str): the path of the csc file
        """
        SELF_PATH = os.path.dirname(os.path.abspath(__file__))# Contiki-ng/IRP/Node_with_config
        CONTIKI_PATH = os.path.dirname(SELF_PATH)
        # CSC_PATH = os.path.normpath(os.path.join(CONTIKI_PATH, "IRP", "Node_with_config"))
        CSC_FILES = os.path.normpath(os.path.join(CONTIKI_PATH, "IRP", "CSC_files"))

        csc_file = os.path.join(CSC_FILES, csc_file)
        self.tree = ET.parse(csc_file)
        self.reset()

    def reset(self):
        self.new_tree = deepcopy(self.tree)
        self.root = self.new_tree.getroot()
        self.motetype = self.root.find(".//motetype")       
        self.radiomedium = self.root.find(".//radiomedium")
        
      
    def save(self, save_file):
        # ET.indent(self.tree, space="\t", level=0)
        self.new_tree.write(save_file, encoding="utf-8", xml_declaration=True)

    def add_mote(self, id, x, y):
        """Add mote in the root file

        Args:
            id (int): the mote id
            x (float): the x coordinate of the mote
            y (float): the y coordinate of the mote
        """
        raw_mote = self.root.find(".//mote")
        new_mote = deepcopy(raw_mote)

        pos = new_mote.find(".//pos")
        pos.set("x", str(x))
        pos.set("y", str(y))
        
        mote_id = new_mote.find(".//id")
        mote_id.text = str(id)
        
        self.motetype.append(new_mote)

    def set_bg_noise_mean(self, value):
        """Set the value of the bg_noise_mean

        Args:
            value (float): the value of the bg_noise_mean
        """
        bg_noise_mean = self.radiomedium.find(".//bg_noise_mean")
        bg_noise_mean.set("value", str(value))
        # for param in self.radiomedium:
        #     if param.tag == "bg_noise_mean":
        #         param.attrib['value'] = str(value)

def generate_csc_file(node_num = 8, env_label = 0, save_file = None):
    """
    
    Args:
        node_num (int): the number of nodes in the simulation
        env_label (int): the label of the environment 
                        0 : For normal backgtound noise, default -87
                        1 : For medium background noise, -85
                        2 : For High background noise, -83
    """
    csv_generator = CSC_generator()
    csv_generator.reset()
    csv_generator.set_bg_noise_mean(-87 + env_label * 2)
    node_map = generate_node_map(node_num)
    for i,(x,y) in node_map.items():
        if i == 1:
            pass
        else:
            csv_generator.add_mote(i, x, y)
    csv_generator.save(save_file)
    return node_map

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
            node_map[i] = (0, 0)
            continue
        else:

            #  x and y coordinate: float in range (0, 100)
            x_coordinate = random.uniform(-50, 50)
            y_coordinate = random.uniform(-50, 50)

            node_map[i] = (x_coordinate, y_coordinate)
    return node_map



if __name__ == '__main__':
        SELF_PATH = os.path.dirname(os.path.abspath(__file__))# Contiki-ng/IRP/Node_with_config
        CONTIKI_PATH = os.path.dirname(SELF_PATH)
        SAVE_PATH = os.path.normpath(os.path.join(CONTIKI_PATH, "IRP", "Node_with_config"))
        # CSC_FILES = os.path.normpath(os.path.join(CONTIKI_PATH, "IRP", "CSC_files"))
        # SAVE_PATH/try.csc
        save_file = os.path.join(SAVE_PATH, "try.csc")
        generate_csc_file(8, 0, save_file)
