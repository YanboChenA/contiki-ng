'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-02-23 11:48:26
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-07 10:57:58
FilePath: \contiki-ng\ML\try.py
Description: 
'''
import xml.etree.ElementTree as ET
import os
from copy import deepcopy

SELF_PATH = os.path.dirname(os.path.abspath(__file__))

# get the path of this example
SELF_PATH = os.path.dirname(os.path.abspath(__file__))
print("Self path:", SELF_PATH)

# move two levels up
CONTIKI_PATH = os.path.dirname(SELF_PATH)
print("CONTIKI_PATH:", CONTIKI_PATH)

# Contiki-ng/IRP/Node_with_config
CSC_PATH = os.path.normpath(os.path.join(CONTIKI_PATH, "IRP", "Node_with_config"))

csc_file = os.path.join(CSC_PATH, 'cooja.csc')


print("Self path:", SELF_PATH)
save_file = os.path.join(SELF_PATH, "try.csc")


tree = ET.parse(csc_file)
root = tree.getroot()

# MT = root.find("motetype")

raw_mote = root.find(".//mote")
print(raw_mote.tag, raw_mote.attrib)
new_mote = deepcopy(raw_mote)
pos = new_mote.find(".//pos")
pos.set("x", "100.0")
pos.set("y", "100.0")
id = new_mote.find(".//id")
id.text = "10"

# print(pos.tag, pos.attrib)
root.find(".//motetype").append(new_mote)




# print(root.tag, root.attrib)

RM = root.find(".//radiomedium")
bg_noise_mean = RM.find("bg_noise_mean")
bg_noise_mean.set("value", "-90.5")
# for param in RM:
#     if param.tag == "bg_noise_mean":
#         param.attrib['value'] = "0.1"
        
# print(RM.tag,RM.attrib)


# for L1 in root:
#     # print(L1.text,L1.tag, L1.attrib)
#     if L1.tag == "simulation":
#         for L2 in L1:
#             # print(L2.tag, L2.attrib)
#             if L2.tag == "radiomedium":
#                 print(L2.tag,L2.attrib)
#                 for L3 in L2:
#                     print(L3.tag, L3.attrib)


# RM = root.find("simulation").find("radiomedium")
# print(RM.tag,RM.attrib)
                    


    
    #     for c in child:
    #         print(c.tag, c.attrib)
    
tree = ET.ElementTree(root)
# ET.indent(tree, space="\t", level=0)
tree.write(save_file, encoding="utf-8", xml_declaration=True)