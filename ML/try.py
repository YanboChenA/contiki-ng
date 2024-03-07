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

SELF_PATH = os.path.dirname(os.path.abspath(__file__))
print("Self path:", SELF_PATH)
save_file = os.path.join(SELF_PATH, "try.csc")

filepath = r"F:\Course\year_4\Individual_Researching\contiki-ng\IRP\Node_with_config\cooja.csc"
tree = ET.parse(filepath)
root = tree.getroot()

print(root.tag, root.attrib)
for child in root:
    print(child.text,child.tag, child.attrib)
    # if child.tag == "simulation":
    #     for c in child:
    #         print(c.tag, c.attrib)
    # if child.tag=="plugin":
    #     for c in child:
    #         print(c.tag, c.attrib)
    
tree = ET.ElementTree(root)
ET.indent(tree, space="\t", level=0)
tree.write(save_file, encoding="utf-8", xml_declaration=True)