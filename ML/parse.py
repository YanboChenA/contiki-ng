'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-02-22 13:59:08
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-02-23 22:11:50
FilePath: \contiki-ng\ML\parse.py
Description: 
'''
import re

# Define the link type
Link_APP    =   1
Link_TSCH   =   2

class NodeStats:
    """Record the Node's statistics, and should record for each 30s
    Args:
        id (int): Node's id 

    """
    def __init__(self,id):
        self.id = id

        self.link_layer_addr = None
        self.IPv6_addr = None

        self.tsch_join_time_sec = None
        self.is_tsch_joined = False

        self.Energist_CPU = []
        self.Energist_LPM = []
        self.Energist_TX = []
        self.Energist_RX = []
        self.Energist_RX = []
class LinkStats:
    """Record the Link's statistics
    """
    def __init__(self,type,src,dst,seqnum,send_ts,recv_ts=None):
        self.type = type
        self.src = src
        self.dst = dst
        self.seqnum = None
        self.send_ts = None
        self.recv_ts = None
        

class LogParse:
    def __init__(self, log_path = None, log = None):
        if log is not None:
            self.log = log
        if log_path:
            self.log_path = log_path
            with open(log_path, 'r') as file:
                self.log = file.readlines()
        self.nodes = {}
        self.applinks = {}         
        pass
    
    def process(self):
        for line in self.log:
            line = line.strip()
            fields = line.split()

            try:
                timestamp = int(fields[0]) // 1000 # in milliseconds
                node = int(fields[1])        # node id
            except:
                continue

            if node not in self.nodes:
                self.nodes[node] = NodeStats(node)

            # 73000 8 [INFO: Main      ] Link-layer address: 0008.0008.0008.0008
            if "Link-layer address" in line:
                self.nodes[node].link_layer_addr = fields[-1]
                continue

            # 73000 8 [INFO: Main      ] Tentative link-local IPv6 address: fe80::208:8:8:8
            if "IPv6 address" in line:
                self.nodes[node].IPv6_addr = fields[-1]
                continue

            # 508000 4 [INFO: TSCH      ] association done (1), sec 0, PAN ID 81a5, asn-0.c, jp 1, timeslot id 0, hopping id 0, slotframe len 0 with 0 links, from 0001.0001.0001.0001
            if "association done" in line:
                # print("association done")
                if self.nodes[node].tsch_join_time_sec is None:
                    self.nodes[node].tsch_join_time_sec = timestamp
                self.nodes[node].is_tsch_joined = True
                continue

            # 536000 2 [INFO: TSCH Queue] update time source: (NULL LL addr) -> 0001.0001.0001.0001
            if "update time source" in line:
                self.nodes[node].tsch_time_source = line.split(" -> ")[1]
                continue


            if "leaving the network" in line:
                self.nodes[node].is_tsch_joined = False
                continue

            # 2757000 1 [INFO: App       ] APP: Sending to fd00::201:1:1:1, seqnum 1
            if "APP: Sending" in line:
                seqnum = int(fields[-1])
                dst_IPv6_addr = fields[-3][:-1]    
                print(dst_IPv6_addr)
                for node in self.nodes.keys():
                    if self.nodes[node].IPv6_addr == dst_IPv6_addr:
                        dst_node = node
                # print(line)
                print(self.nodes[1].IPv6_addr)
                # print(self.nodes.keys())
                self.applinks[seqnum] = LinkStats(Link_APP, node, dst_node, seqnum, timestamp)
                continue
            
            # 2757000 1 [INFO: App       ] APP: Received from fd00::201:1:1:1, seqnum 1, RSSI: 0, LQI: 0
            if "APP: Received" in line:
                LQI = int(fields[-1])
                RSSI = int(fields[-3][:-1])
                seqnum = int(fields[-5][:-1])
                src_IPv6_addr = fields[-7][:-1]
                # find seqnum in applinks
                self.applinks[seqnum].RSSI = RSSI
                self.applinks[seqnum].LQI = LQI
                self.applinks[seqnum].recv_ts = timestamp
                continue

            # 2757000 1 [INFO: App       ] Energest: CPU 2375000 LPM 0 TX 1120 RX 234000
            if "Energest:" in line:
                # CPU = int(fields[-7])
                # LPM = int(fields[-5])
                # TX = int(fields[-3])
                # RX = int(fields[-1])
                self.nodes[node].Energist_CPU.append(int(fields[-7]))
                self.nodes[node].Energist_LPM.append(int(fields[-5]))
                self.nodes[node].Energist_TX.append(int(fields[-3]))
                self.nodes[node].Energist_RX.append(int(fields[-1]))
                continue



if __name__ == '__main__':
    filepath = "F:\Course\year_4\Individual_Researching\contiki-ng\data\\raw\COOJA.testlog"
    log = LogParse(log_path=filepath)
    log.process()
    # log = log_parse(log_path=filepath)
    # log._try()