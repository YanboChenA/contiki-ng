'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-05 15:37:39
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-05 15:41:48
FilePath: \contiki-ng\ML\csv_generator.py
Description: 
'''
import xml.etree.ElementTree as ET
import argparse
import os

# get the path of this example
SELF_PATH = os.path.dirname(os.path.abspath(__file__))
print("Self path:", SELF_PATH)

# move two levels up
CONTIKI_PATH = os.path.dirname(SELF_PATH)
print("CONTIKI_PATH:", CONTIKI_PATH)

COOJA_PATH = os.path.normpath(os.path.join(CONTIKI_PATH, "tools", "cooja"))
print("COOJA_PATH:", COOJA_PATH)

# contiki-ng/data/raw as the save path
SAVE_PATH = os.path.join(CONTIKI_PATH, "data", "raw")
print("SAVE_PATH:", SAVE_PATH)


# class CSC_Generator:
#     def __init__(self):
#         nodes = []

if __name__ == "__main__":
    pass