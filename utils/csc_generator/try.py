import xml.etree.ElementTree as ET
import os

filepath = r"F:\Course\year_4\Individual_Researching\contiki-ng\IRP\Node_with_config\DGRM.csc"
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
    