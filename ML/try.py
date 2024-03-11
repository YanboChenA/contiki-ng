'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-03-09 16:29:58
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-11 10:38:42
FilePath: \contiki-ng\ML\try.py
Description: 
'''
import json
with open(r"F:\Course\year_4\Individual_Researching\contiki-ng\data\label\2024-03-10_21-23-45.json", 'r') as file:
    data = json.load(file)

print(data["label_list"])

