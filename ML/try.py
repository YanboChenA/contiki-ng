'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-02-23 11:48:26
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-02-23 12:30:01
FilePath: \contiki-ng\ML\try.py
Description: 
'''
# 2757000 1 [INFO: App       ] APP: Received from fd00::201:1:1:1, seqnum 1, RSSI: 0, LQI: 0
line = "2757000 1 [INFO: App       ] APP: Received from fd00::201:1:1:1, seqnum 1, RSSI: 0, LQI: 0"
line = line.strip()
fields = line.split()

LQI = int(fields[-1])
RSSI = int(fields[-3][:-1])
seqnum = int(fields[-5][:-1])
src_IPv6_addr = fields[-7][:-1]
print(f"src_IPv6_addr: {src_IPv6_addr}, seqnum: {seqnum}, RSSI: {RSSI}, LQI: {LQI}")