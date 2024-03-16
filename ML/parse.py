'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-02-22 13:59:08
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-15 20:25:41
FilePath: \contiki-ng\ML\parse.py
Description: 
'''
'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-02-22 13:59:08
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-11 11:37:51
FilePath: \contiki-ng\ML\parse.py
Description: 
'''

import re
import numpy as np

import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning, message='invalid value encountered in divide')

tx_re_pattern = r".*\{asn (.*?) link\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+ch\s+(\d+)\}\s+(.*?)-(\d+)-(\d+)\s+tx\s+LL-(.*?)->LL-(.*?),\s+len\s+(\d+),\s+seq\s+(\d+),\s+st\s+(\d+)\s+(\d+)"
rx_re_pattern = r".*\{asn (.*?) link\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+ch\s+(\d+)\}\s+(.*?)-(\d+)-(\d+)\s+rx\s+LL-(.*?)->LL-(.*?),\s+len\s+(\d+),\s+seq\s+(\d+),\s+edr\s+(\d+)"
rx_dr_re_pattern = r".*\{asn (.*?) link\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+ch\s+(\d+)\}\s+(.*?)-(\d+)-(\d+)\s+rx\s+LL-(.*?)->LL-(.*?),\s+len\s+(\d+),\s+seq\s+(\d+),\s+edr\s+(\d+),\s+dr\s+(\d+)"


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

        self.is_root = False

        self.Energest = [] # A list include the Energest statistics, each element is a dict, include the CPU, LPM, TX, RX, Total_time
        self.IPv6_links = {} # seqnum: LinkStats, include the link status, each element is a LinkStats

        # self.data = []  # Include the data from the log, for further GNN training
                        # Reallocate the data in time period of 30s
        self.IPv6_link_status = [] # Include the link status, for further GNN training
        self.node_status = [] # include a dict, include the periods' average send and receive rate, success rate, and the Energest statistics
        self.after_calculate_Energest = False
        self.after_allocate_IPv6_links = False

        self.data_num = 120 # 1 hour, 120 periods
    
    def calculate_Energest(self):
        temp_Energest = self.Energest
        self.Energest = [temp_Energest[0]]
        for i in range(1,len(temp_Energest)):
            self.Energest.append({
                "CPU": temp_Energest[i]["CPU"] - temp_Energest[i-1]["CPU"],
                "LPM": temp_Energest[i]["LPM"] - temp_Energest[i-1]["LPM"],
                "TX": temp_Energest[i]["TX"] - temp_Energest[i-1]["TX"],
                "RX": temp_Energest[i]["RX"] - temp_Energest[i-1]["RX"],
                "Total_time": temp_Energest[i]["Total_time"] - temp_Energest[i-1]["Total_time"]
            })
        self.after_calculate_Energest = True

    def allocate_IPv6_links(self):
        """Allocating the IPv6 links, and add the sub links to the IPv6_links
        Allocating or regroup the data in time period of 30s
        """
        timeperiod = 30000000 # 30s, 30,000,000us
        # total runtime is 1 hour, pre built the data list
        self.IPv6_link_status = [[] for _ in range(120)]
        for seqnum in self.IPv6_links.keys():
            link = self.IPv6_links[seqnum]
            if link.send_ts is None or link.recv_ts is None:
                continue
            # calculate the link's send_ts in which time period
            index = link.send_ts // timeperiod
            if index <= 119:
                self.IPv6_link_status[index].append(link)
        self.after_allocate_IPv6_links = True

    def calculate_node_status(self):
        """Calculate the node's status, include the periods' average send and receive rate, success rate, and the Energest statistics
        """
        # TODO: Add other attributes if needed in the future
        timeperiod = 30000000 # 30s, 30,000,000us
        if self.after_allocate_IPv6_links == False:
            self.allocate_IPv6_links()
        if self.after_calculate_Energest == False:
            self.calculate_Energest()

        self.node_status = [[] for _ in range(120)]
        for index in range(120):
            IPv6_links = self.IPv6_link_status[index]

            transmit_delay = 0
            tansmit_num = len(IPv6_links)

            tsch_link_num = 0
            tsch_link_transmit_num = 0

            for link in IPv6_links:
                transmit_delay += link.recv_ts - link.send_ts
                tsch_link_num += len(link.sub_links)
                for sublink in link.sub_links:
                    tsch_link_transmit_num += sublink.tx_attempt

            transmit_delay = transmit_delay / tansmit_num if tansmit_num != 0 else 0
            tsch_success_rate = tsch_link_num / tsch_link_transmit_num if tsch_link_num != 0 else 0

            try:
                Energest = self.Energest[index]
                CPU_usage = Energest["CPU"] / Energest["Total_time"]
                LPM_usage = Energest["LPM"] / Energest["Total_time"]
                TX_duty_cycle = Energest["TX"] / Energest["Total_time"]
                RX_duty_cycle = Energest["RX"] / Energest["Total_time"]
            except:
                CPU_usage = 0
                LPM_usage = 0
                TX_duty_cycle = 0
                RX_duty_cycle = 0
            

            self.node_status[index] = {
                "transmit_delay": transmit_delay / tansmit_num if tansmit_num != 0 else 0,
                "tsch_success_rate": tsch_success_rate if tsch_link_num != 0 else 0,
                "CPU_usage": CPU_usage,
                "LPM_usage": LPM_usage,
                "TX_duty_cycle": TX_duty_cycle,
                "RX_duty_cycle": RX_duty_cycle
            }

    def get_node_status(self, index):
        # return the node's status in the index as a list
        return list(self.node_status[index].values())

class LogAnalysis:
    """LogAnalysis the log file, and get the statistics of the log file,
    Node features include:
        Node information:
            CPU usage
            LPM usage
            TX duty cycle
            RX duty cycle

        IPv6 links' status:
            Transmit delay for sended IPv6 links (average, max, min)
            hop count for sended IPv6 links (average, max, min)
            fragment count for sended IPv6 links (average, max, min)
            Num of send IPv6 links
            Num of receive IPv6 links

        TSCH links' status:
            TSCH success rate for sended tsch links (average, max, min)
            attempt for sended tsch links (average, max, min)
            length for sended tsch links (average, max, min)
            Num of send tsch links
            Num of receive tsch links

    Edge features include:
        # Two type of edge features, one is the link's status(IPv6), the other is the sublink's status(TSCH)
        Link's status(IPv6):
            num of sublinks (average, max, min)
            num of queued sublinks (average, max, min)
            num of total sublinks tx attempts (average, max, min)
            RSSI (average, max, min)
            LQI (average, max, min)
            delay (average, max, min)
            hop count (average, max, min)
            fragment count (average, max, min)
        
        Sublink's status(TSCH):
            num of usage of this sublink(from src to dst)
            send attempts (average, max, min)
            queued delay (average, max, min)
            length (average, max, min)
    """
    def __init__(self, LogParser):
        self.LogParser = LogParser
        self.nodes = LogParser.nodes
        self.tsch_links = LogParser.tsch_links

    def calculate_features(self):
        # node features is a np.array, shape should (node_index,feature_num,period_num)
        node_features = np.zeros((len(self.nodes.keys()), 20, 120))
        edge_features_IPv6 = [[] for _ in range(120)]
        edge_features_tsch = [[] for _ in range(120)]
        edge_index_IPv6 = [[] for _ in range(120)]
        edge_index_tsch = [[] for _ in range(120)]

        node_num = len(self.nodes.keys())
        # Node Features
        for index in range(120):
            # Node Features
            node_CPU_usage              = np.zeros(node_num) # 0
            node_LPM                    = np.zeros(node_num) # 1
            node_TX_duty_cycle          = np.zeros(node_num) # 2
            node_RX_duty_cycle          = np.zeros(node_num) # 3

            node_IPv6_delay_sum         = np.zeros(node_num) # 4
            node_IPv6_delay_max         = np.zeros(node_num) # 5
            # node_IPv6_delay_min         = np.zeros(node_num)

            node_IPv6_hop_count_sum     = np.zeros(node_num) # 6
            node_IPv6_hop_count_max     = np.zeros(node_num) # 7
            # node_IPv6_hop_count_min     = np.zeros(node_num)

            node_IPv6_fragment_count_sum = np.zeros(node_num) # 8
            node_IPv6_fragment_count_max = np.zeros(node_num) # 9
            # node_IPv6_fragment_count_min = np.zeros(node_num)

            node_IPv6_send_num          = np.zeros(node_num) # 10
            node_IPv6_recv_num          = np.zeros(node_num) # 11
            
            node_tsch_success_rate_sum  = np.zeros(node_num) # 12 
            node_tsch_success_rate_max  = np.zeros(node_num) # 13
            # node_tsch_success_rate_min  = np.zeros(node_num)

            node_tsch_tx_attempt_sum    = np.zeros(node_num) # 14
            node_tsch_tx_attempt_max    = np.zeros(node_num) # 15
            # node_tsch_tx_attempt_min    = np.zeros(node_num)

            node_tsch_length_sum        = np.zeros(node_num) # 16
            node_tsch_length_max        = np.zeros(node_num) # 17
            # node_tsch_length_min        = np.zeros(node_num)

            node_tsch_send_num          = np.zeros(node_num) # 18
            node_tsch_recv_num          = np.zeros(node_num) # 19
            
            IPv6_Edge_Attr = {} # Key: (src, dst)
            TSCH_Edge_Attr = {} # Key: (src, dst)

            for node_id, node in self.nodes.items():
                node_index = node_id - 1
                IPv6_links = node.IPv6_link_status[index]
                try:
                    Energest = node.Energest[index]
                    node_CPU_usage[node_index]      = Energest["CPU"] / Energest["Total_time"]
                    node_LPM[node_index]            = Energest["LPM"] / Energest["Total_time"]
                    node_TX_duty_cycle[node_index]  = Energest["TX"] / Energest["Total_time"]
                    node_RX_duty_cycle[node_index]  = Energest["RX"] / Energest["Total_time"]
                except:
                    node_CPU_usage[node_index]      = 0
                    node_LPM[node_index]            = 0
                    node_TX_duty_cycle[node_index]  = 0
                    node_RX_duty_cycle[node_index]  = 0
                
                for link in IPv6_links:
                    link_attr, sublink_attr = link.calculate_link_status()
                    src = link.src
                    src_index = src - 1
                    node_IPv6_send_num[src_index] += 1
                    dst = link.dst
                    dst_index = dst - 1
                    node_IPv6_recv_num[dst_index] += 1
                    
                    if (src, dst) not in IPv6_Edge_Attr.keys():
                        IPv6_Edge_Attr[(src, dst)] = {
                            "count": 1,
                            "sublinks_num_sum": link_attr[0],
                            "sublinks_num_max": link_attr[0],
                            # "sublinks_num_min": link_attr[0], 
                            "sublinks_queued_num_sum": link_attr[1],
                            "sublinks_queued_num_max": link_attr[1],
                            # "sublinks_queued_num_min": link_attr[1],
                            "sublinks_tx_attempts_num_sum": link_attr[2],
                            "sublinks_tx_attempts_num_max": link_attr[2],
                            # "sublinks_tx_attempts_num_min": link_attr[2],
                            "RSSI_sum": link_attr[3],
                            "RSSI_max": link_attr[3],
                            # "RSSI_min": link_attr[3],
                            "LQI_sum": link_attr[4],
                            "LQI_max": link_attr[4],
                            # "LQI_min": link_attr[4],
                            "delay_sum": link_attr[5],
                            "delay_max": link_attr[5],
                            # "delay_min": link_attr[5],
                            "hop_count_sum": link_attr[6],
                            "hop_count_max": link_attr[6],
                            # "hop_count_min": link_attr[6],
                            "fragment_count_sum": link_attr[7],
                            "fragment_count_max": link_attr[7],
                            # "fragment_count_min": link_attr[7],
                            "success_rate_sum": link_attr[8],
                            "success_rate_max": link_attr[8],
                            # "success_rate_min": link_attr[8]
                        }
                    else:
                        IPv6_Edge_Attr[(src, dst)]["count"] += 1
                        # Update the Edge's status for IPv6
                        IPv6_Edge_Attr[(src, dst)]["sublinks_num_sum"] += link_attr[0]
                        IPv6_Edge_Attr[(src, dst)]["sublinks_num_max"] = max(IPv6_Edge_Attr[(src, dst)]["sublinks_num_max"], link_attr[0])
                        # IPv6_Edge_Attr[(src, dst)]["sublinks_num_min"] = min(IPv6_Edge_Attr[(src, dst)]["sublinks_num_min"], link_attr[0])
                        IPv6_Edge_Attr[(src, dst)]["sublinks_queued_num_sum"] += link_attr[1]
                        IPv6_Edge_Attr[(src, dst)]["sublinks_queued_num_max"] = max(IPv6_Edge_Attr[(src, dst)]["sublinks_queued_num_max"], link_attr[1])
                        # IPv6_Edge_Attr[(src, dst)]["sublinks_queued_num_min"] = min(IPv6_Edge_Attr[(src, dst)]["sublinks_queued_num_min"], link_attr[1])
                        IPv6_Edge_Attr[(src, dst)]["sublinks_tx_attempts_num_sum"] += link_attr[2]
                        IPv6_Edge_Attr[(src, dst)]["sublinks_tx_attempts_num_max"] = max(IPv6_Edge_Attr[(src, dst)]["sublinks_tx_attempts_num_max"], link_attr[2])
                        # IPv6_Edge_Attr[(src, dst)]["sublinks_tx_attempts_num_min"] = min(IPv6_Edge_Attr[(src, dst)]["sublinks_tx_attempts_num_min"], link_attr[2])
                        IPv6_Edge_Attr[(src, dst)]["RSSI_sum"] += link_attr[3]
                        IPv6_Edge_Attr[(src, dst)]["RSSI_max"] = max(IPv6_Edge_Attr[(src, dst)]["RSSI_max"], link_attr[3])
                        # IPv6_Edge_Attr[(src, dst)]["RSSI_min"] = min(IPv6_Edge_Attr[(src, dst)]["RSSI_min"], link_attr[3])
                        IPv6_Edge_Attr[(src, dst)]["LQI_sum"] += link_attr[4]
                        IPv6_Edge_Attr[(src, dst)]["LQI_max"] = max(IPv6_Edge_Attr[(src, dst)]["LQI_max"], link_attr[4])
                        # IPv6_Edge_Attr[(src, dst)]["LQI_min"] = min(IPv6_Edge_Attr[(src, dst)]["LQI_min"], link_attr[4])
                        IPv6_Edge_Attr[(src, dst)]["delay_sum"] += link_attr[5]
                        IPv6_Edge_Attr[(src, dst)]["delay_max"] = max(IPv6_Edge_Attr[(src, dst)]["delay_max"], link_attr[5])
                        # IPv6_Edge_Attr[(src, dst)]["delay_min"] = min(IPv6_Edge_Attr[(src, dst)]["delay_min"], link_attr[5])
                        IPv6_Edge_Attr[(src, dst)]["hop_count_sum"] += link_attr[6]
                        IPv6_Edge_Attr[(src, dst)]["hop_count_max"] = max(IPv6_Edge_Attr[(src, dst)]["hop_count_max"], link_attr[6])
                        # IPv6_Edge_Attr[(src, dst)]["hop_count_min"] = min(IPv6_Edge_Attr[(src, dst)]["hop_count_min"], link_attr[6])
                        IPv6_Edge_Attr[(src, dst)]["fragment_count_sum"] += link_attr[7]
                        IPv6_Edge_Attr[(src, dst)]["fragment_count_max"] = max(IPv6_Edge_Attr[(src, dst)]["fragment_count_max"], link_attr[7])
                        # IPv6_Edge_Attr[(src, dst)]["fragment_count_min"] = min(IPv6_Edge_Attr[(src, dst)]["fragment_count_min"], link_attr[7])
                        IPv6_Edge_Attr[(src, dst)]["success_rate_sum"] += link_attr[8]
                        IPv6_Edge_Attr[(src, dst)]["success_rate_max"] = max(IPv6_Edge_Attr[(src, dst)]["success_rate_max"], link_attr[8])
                        # IPv6_Edge_Attr[(src, dst)]["success_rate_min"] = min(IPv6_Edge_Attr[(src, dst)]["success_rate_min"], link_attr[8])

                    # Update the Edge's status for TSCH
                    for (src, dst), attr in sublink_attr.items():
                        if (src,dst) not in TSCH_Edge_Attr.keys():
                            TSCH_Edge_Attr[(src,dst)]= {
                                "usage_num_sum": sublink_attr[(src,dst)]["usage_num"],
                                "tx_attempts_sun": sublink_attr[(src,dst)]["tx_attempts_sun"],
                                "tx_attempts_max": sublink_attr[(src,dst)]["tx_attempts_max"],
                                # "tx_attempts_min": sublink_attr[(src,dst)]["tx_attempts_min"],
                                "queued_link_sum": sublink_attr[(src,dst)]["queued_link_sum"],
                                "queued_delay_sum": sublink_attr[(src,dst)]["queued_delay_sum"],
                                "queued_delay_max": sublink_attr[(src,dst)]["queued_delay_max"],
                                # "queued_delay_min": sublink_attr[(src,dst)]["queued_delay_min"],
                                "length_sum": sublink_attr[(src,dst)]["length_sum"],
                                "length_max": sublink_attr[(src,dst)]["length_max"],
                                # "length_min": sublink_attr[(src,dst)]["length_min"]
                            }
                        else:
                            TSCH_Edge_Attr[(src,dst)]["usage_num_sum"] += sublink_attr[(src,dst)]["usage_num"]
                            TSCH_Edge_Attr[(src,dst)]["tx_attempts_sun"] += sublink_attr[(src,dst)]["tx_attempts_sun"]
                            TSCH_Edge_Attr[(src,dst)]["tx_attempts_max"] = max(TSCH_Edge_Attr[(src,dst)]["tx_attempts_max"], sublink_attr[(src,dst)]["tx_attempts_max"])
                            # TSCH_Edge_Attr[(src,dst)]["tx_attempts_min"] = min(TSCH_Edge_Attr[(src,dst)]["tx_attempts_min"], sublink_attr[(src,dst)]["tx_attempts_min"])
                            TSCH_Edge_Attr[(src,dst)]["queued_link_sum"] += sublink_attr[(src,dst)]["queued_link_sum"]
                            TSCH_Edge_Attr[(src,dst)]["queued_delay_sum"] += sublink_attr[(src,dst)]["queued_delay_sum"]
                            TSCH_Edge_Attr[(src,dst)]["queued_delay_max"] = max(TSCH_Edge_Attr[(src,dst)]["queued_delay_max"], sublink_attr[(src,dst)]["queued_delay_max"])
                            # TSCH_Edge_Attr[(src,dst)]["queued_delay_min"] = min(TSCH_Edge_Attr[(src,dst)]["queued_delay_min"], sublink_attr[(src,dst)]["queued_delay_min"])
                            TSCH_Edge_Attr[(src,dst)]["length_sum"] += sublink_attr[(src,dst)]["length_sum"]
                            TSCH_Edge_Attr[(src,dst)]["length_max"] = max(TSCH_Edge_Attr[(src,dst)]["length_max"], sublink_attr[(src,dst)]["length_max"])
                            # TSCH_Edge_Attr[(src,dst)]["length_min"] = min(TSCH_Edge_Attr[(src,dst)]["length_min"], sublink_attr[(src,dst)]["length_min"])
                
                    # Update the node's status
                    node_IPv6_delay_sum[src_index] += link_attr[5]
                    node_IPv6_delay_max[src_index] = max(node_IPv6_delay_max[src_index], link_attr[5])
                    # node_IPv6_delay_min[src_index] = min(node_IPv6_delay_min[src_index], link_attr[5])
                    node_IPv6_hop_count_sum[src_index] += link_attr[6]
                    node_IPv6_hop_count_max[src_index] = max(node_IPv6_hop_count_max[src_index], link_attr[6])
                    # node_IPv6_hop_count_min[src_index] = min(node_IPv6_hop_count_min[src_index], link_attr[6])
                    node_IPv6_fragment_count_sum[src_index] += link_attr[7]
                    node_IPv6_fragment_count_max[src_index] = max(node_IPv6_fragment_count_max[src_index], link_attr[7])
                    # node_IPv6_fragment_count_min[src_index] = min(node_IPv6_fragment_count_min[src_index], link_attr[7])
                    node_tsch_success_rate_sum[src_index] += link_attr[8]
                    node_tsch_success_rate_max[src_index] = max(node_tsch_success_rate_max[src_index], link_attr[8])
                    # node_tsch_success_rate_min[src_index] = min(node_tsch_success_rate_min[src_index], link_attr[8])
                    for sublink in link.sub_links:
                        sublink_src = sublink.src
                        sublink_dst = sublink.dst[0]
                        sublink_src_index = sublink_src - 1
                        sublink_dst_index = sublink_dst - 1
                        node_tsch_tx_attempt_sum[sublink_src_index] += sublink.tx_attempt
                        node_tsch_tx_attempt_max[sublink_src_index] = max(node_tsch_tx_attempt_max[sublink_src_index], sublink.tx_attempt)
                        # node_tsch_tx_attempt_min[sublink_src_index] = min(node_tsch_tx_attempt_min[sublink_src_index], sublink.tx_attempt)
                        node_tsch_length_sum[sublink_src_index] += sublink.length
                        node_tsch_length_max[sublink_src_index] = max(node_tsch_length_max[sublink_src_index], sublink.length)
                        # node_tsch_length_min[sublink_src_index] = min(node_tsch_length_min[sublink_src_index], sublink.length)
                        node_tsch_send_num[sublink_src_index] += 1
                        node_tsch_recv_num[sublink_dst_index] += 1

            # Calculate the average
            # Node Features
            try:
                node_IPv6_delay_avg             = np.where(node_tsch_send_num != 0, node_tsch_length_sum / node_tsch_send_num, 0)
                node_IPv6_hop_count_avg         = np.where(node_IPv6_send_num != 0, node_IPv6_hop_count_sum / node_IPv6_send_num, 0)
                node_IPv6_fragment_count_avg    = np.where(node_IPv6_send_num != 0, node_IPv6_fragment_count_sum / node_IPv6_send_num, 0)
                node_tsch_success_rate_avg      = np.where(node_tsch_send_num != 0, node_tsch_success_rate_sum / node_tsch_send_num, 0)
                node_tsch_tx_attempt_avg        = np.where(node_tsch_send_num != 0, node_tsch_tx_attempt_sum / node_tsch_send_num, 0)
                node_tsch_length_avg            = np.where(node_tsch_send_num != 0, node_tsch_length_sum / node_tsch_send_num, 0)
            except:
                node_IPv6_delay_avg             = np.zeros(node_num)
                node_IPv6_hop_count_avg         = np.zeros(node_num)
                node_IPv6_fragment_count_avg    = np.zeros(node_num)
                node_tsch_success_rate_avg      = np.zeros(node_num)
                node_tsch_tx_attempt_avg        = np.zeros(node_num)
                node_tsch_length_avg            = np.zeros(node_num)

            # Edge Features for IPv6
            for (src, dst), attr in IPv6_Edge_Attr.items():
                count = attr["count"]
                IPv6_Edge_Attr[(src, dst)]["sublinks_num_avg"] = attr["sublinks_num_sum"] / count
                IPv6_Edge_Attr[(src, dst)]["sublinks_queued_num_avg"] = attr["sublinks_queued_num_sum"] / count
                IPv6_Edge_Attr[(src, dst)]["sublinks_tx_attempts_num_avg"] = attr["sublinks_tx_attempts_num_sum"] / count
                IPv6_Edge_Attr[(src, dst)]["RSSI_avg"] = attr["RSSI_sum"] / count
                IPv6_Edge_Attr[(src, dst)]["LQI_avg"] = attr["LQI_sum"] / count
                IPv6_Edge_Attr[(src, dst)]["delay_avg"] = attr["delay_sum"] / count
                IPv6_Edge_Attr[(src, dst)]["hop_count_avg"] = attr["hop_count_sum"] / count
                IPv6_Edge_Attr[(src, dst)]["fragment_count_avg"] = attr["fragment_count_sum"] / count
                IPv6_Edge_Attr[(src, dst)]["success_rate_avg"] = attr["success_rate_sum"] / count
            
            # Edge Features for TSCH
            for (src, dst), attr in TSCH_Edge_Attr.items():
                count = attr["usage_num_sum"]
                TSCH_Edge_Attr[(src, dst)]["tx_attempts_avg"] = attr["tx_attempts_sun"] / count
                TSCH_Edge_Attr[(src, dst)]["queued_delay_avg"] = attr["queued_delay_sum"] / count
                TSCH_Edge_Attr[(src, dst)]["length_avg"] = attr["length_sum"] / count

            # Combine the features
            # node features is a np.array, shape should (node_index,feature_num,period_num)
            node_features[:,0,index] = node_CPU_usage
            node_features[:,1,index] = node_LPM
            node_features[:,2,index] = node_TX_duty_cycle
            node_features[:,3,index] = node_RX_duty_cycle
            node_features[:,4,index] = node_IPv6_delay_avg
            node_features[:,5,index] = node_IPv6_delay_max
            # node_features[:,6,index] = node_IPv6_delay_min
            node_features[:,6,index] = node_IPv6_hop_count_avg
            node_features[:,7,index] = node_IPv6_hop_count_max
            # node_features[:,9,index] = node_IPv6_hop_count_min
            node_features[:,8,index] = node_IPv6_fragment_count_avg
            node_features[:,9,index] = node_IPv6_fragment_count_max
            # node_features[:,12,index] = node_IPv6_fragment_count_min
            node_features[:,10,index] = node_IPv6_send_num
            node_features[:,11,index] = node_IPv6_recv_num
            node_features[:,12,index] = node_tsch_success_rate_avg
            node_features[:,13,index] = node_tsch_success_rate_max
            # node_features[:,17,index] = node_tsch_success_rate_min
            node_features[:,14,index] = node_tsch_tx_attempt_avg
            node_features[:,15,index] = node_tsch_tx_attempt_max
            # node_features[:,20,index] = node_tsch_tx_attempt_min
            node_features[:,16,index] = node_tsch_length_avg
            node_features[:,17,index] = node_tsch_length_max
            # node_features[:,23,index] = node_tsch_length_min
            node_features[:,18,index] = node_tsch_send_num
            node_features[:,19,index] = node_tsch_recv_num

            # Edge Features for IPv6
            for (src, dst), attr in IPv6_Edge_Attr.items():
                edge_index_IPv6[index].append([src, dst])
                edge_features_IPv6[index].append([])
                edge_features_IPv6[index][-1].append(attr["count"])
                edge_features_IPv6[index][-1].append(attr["sublinks_num_avg"])
                edge_features_IPv6[index][-1].append(attr["sublinks_num_max"])
                # edge_features_IPv6[index][-1].append(attr["sublinks_num_min"])
                edge_features_IPv6[index][-1].append(attr["sublinks_queued_num_avg"])
                edge_features_IPv6[index][-1].append(attr["sublinks_queued_num_max"])
                # edge_features_IPv6[index][-1].append(attr["sublinks_queued_num_min"])
                edge_features_IPv6[index][-1].append(attr["sublinks_tx_attempts_num_avg"])
                edge_features_IPv6[index][-1].append(attr["sublinks_tx_attempts_num_max"])
                # edge_features_IPv6[index][-1].append(attr["sublinks_tx_attempts_num_min"])
                edge_features_IPv6[index][-1].append(attr["RSSI_avg"])
                edge_features_IPv6[index][-1].append(attr["RSSI_max"])
                # edge_features_IPv6[index][-1].append(attr["RSSI_min"])
                edge_features_IPv6[index][-1].append(attr["LQI_avg"])
                edge_features_IPv6[index][-1].append(attr["LQI_max"])
                # edge_features_IPv6[index][-1].append(attr["LQI_min"])
                edge_features_IPv6[index][-1].append(attr["delay_avg"])
                edge_features_IPv6[index][-1].append(attr["delay_max"])
                # edge_features_IPv6[index][-1].append(attr["delay_min"])
                edge_features_IPv6[index][-1].append(attr["hop_count_avg"])
                edge_features_IPv6[index][-1].append(attr["hop_count_max"])
                # edge_features_IPv6[index][-1].append(attr["hop_count_min"])
                edge_features_IPv6[index][-1].append(attr["fragment_count_avg"])
                edge_features_IPv6[index][-1].append(attr["fragment_count_max"])
                # edge_features_IPv6[index][-1].append(attr["fragment_count_min"])
                edge_features_IPv6[index][-1].append(attr["success_rate_avg"])
                edge_features_IPv6[index][-1].append(attr["success_rate_max"])
                # edge_features_IPv6[index][-1].append(attr["success_rate_min"])

            # Edge Features for TSCH
            for (src, dst), attr in TSCH_Edge_Attr.items():
                edge_index_tsch[index].append([src, dst])
                edge_features_tsch[index].append([])
                edge_features_tsch[index][-1].append(attr["usage_num_sum"])
                edge_features_tsch[index][-1].append(attr["tx_attempts_avg"])
                edge_features_tsch[index][-1].append(attr["tx_attempts_max"])
                # edge_features_tsch[index][-1].append(attr["tx_attempts_min"])
                edge_features_tsch[index][-1].append(attr["queued_delay_avg"])
                edge_features_tsch[index][-1].append(attr["queued_delay_max"])
                # edge_features_tsch[index][-1].append(attr["queued_delay_min"])
                edge_features_tsch[index][-1].append(attr["length_avg"])
                edge_features_tsch[index][-1].append(attr["length_max"])
                # edge_features_tsch[index][-1].append(attr["length_min"])

        self.node_features = node_features
        self.edge_features_IPv6 = edge_features_IPv6
        self.edge_features_tsch = edge_features_tsch
        self.edge_index_IPv6 = edge_index_IPv6
        self.edge_index_tsch = edge_index_tsch
  
    def calculate_loss_and_delay(self):
        """Calculate the loss and delay for analysising the network's performance, from calculated features
        Loss: ( total packets sent in tsch - total packets received in tsch ) / total packets sent in tsch
        Delay: average delay for the IPv6 packets
        """
        loss = np.zeros(120)
        delay = np.zeros(120)
        for index in range(120):
            # Calculate loss
            # In node_features, the 18th feature is the num of send tsch links, the 19th feature is the num of receive tsch links
            tsch_send_num = np.sum(self.node_features[:,18,index]*self.node_features[:,14,index])
            tsch_recv_num = np.sum(self.node_features[:,19,index])

            loss[index] = (tsch_send_num - tsch_recv_num) / tsch_send_num if tsch_send_num != 0 else 0
            # Delay
            delay[index] = np.mean(self.node_features[:,4,index])

        self.loss = loss
        self.delay = delay
       
class LinkStats:
    """Record the Link's statistics, udp 
    """
    def __init__(self,src,dst,seqnum,send_ts,recv_ts=None):  
        self.src = src      # source node
        self.dst = dst      # destination node
        self.seqnum = seqnum  # sequence number
        self.send_ts = send_ts # send timestamp
        self.recv_ts = recv_ts # receive timestamp

        self.RSSI = None    # RSSI
        self.LQI = None     # LQI

        is_received = False  # is received

        self.sub_links = [] # sub links' status

        self.after_calculate_link_status = False
    
    def __str__(self) -> str:
        if self.sub_links == []:
            return f"{self.src} -> {self.dst}, seqnum: {self.seqnum}, RSSI: {self.RSSI}, LQI: {self.LQI}, send_ts: {self.send_ts}, recv_ts: {self.recv_ts}"
        else:
            sublinks_str = "\n"
            for sublink in self.sub_links:
                sublinks_str += str(sublink) + "\n"
            return f"{self.src} -> {self.dst}, seqnum: {self.seqnum}, RSSI: {self.RSSI}, LQI: {self.LQI}, send_ts: {self.send_ts}, recv_ts: {self.recv_ts}, \nsublinks: {sublinks_str}"
    
    def calculate_link_status(self):
        """Calculate the link's status and sublinks' status(multiple sublinks for one link, return the)
            Link's status(IPv6):
                num of sublinks
                num of queued sublinks
                num of total sublinks tx attempts
                RSSI
                LQI
                delay
                hop count
                fragment count
                success rate
            Sublink's status(TSCH):
                num of usage of this sublink(from src to dst)
                send attempts (average, max, min)
                queued delay (average, max, min)
                length (average, max, min)                
        """
        # IPv6 link status
        sub_links_num = len(self.sub_links) 
        sub_links_queued_num = 0
        sub_links_tx_attemps = 0
        delay = self.recv_ts - self.send_ts if self.recv_ts is not None and self.send_ts is not None else 0
        hop_count = 0
        fragment_count = 0
        success_rate = 0
        sublink_attr = {}

        for sublink in self.sub_links:
            sub_dst = sublink.dst[0]
            sub_src = sublink.src
            if (sub_src, sub_dst) not in sublink_attr.keys():
                sublink_attr[(sub_src, sub_dst)] = {
                    "usage_num": 1,
                    "tx_attempts_sun": 0,
                    "tx_attempts_max": 0,
                    "tx_attempts_min": 0,
                    "queued_link_sum": 0,
                    "queued_delay_sum": 0,
                    "queued_delay_max": 0,
                    "queued_delay_min": 0,
                    "length_sum": 0,
                    "length_max": 0,
                    "length_min": 0
                }
            else:
                sublink_attr[(sub_src, sub_dst)]["usage_num"] += 1
            if sublink.is_queued:
                sub_links_queued_num += 1
                sublink_attr[(sub_src, sub_dst)]["queued_link_sum"] += 1
                sublink_attr[(sub_src, sub_dst)]["queued_delay_sum"] +=  sublink.timestamp - sublink.queued_ts
                sublink_attr[(sub_src, sub_dst)]["queued_delay_max"] = max(sublink_attr[(sub_src, sub_dst)]["queued_delay_max"], sublink.queued_ts - sublink.timestamp)
                sublink_attr[(sub_src, sub_dst)]["queued_delay_min"] = min(sublink_attr[(sub_src, sub_dst)]["queued_delay_min"], sublink.queued_ts - sublink.timestamp)
            
            # Update the Link's status
            sub_links_tx_attemps += sublink.tx_attempt

            # Update the Sublink's status
            sublink_attr[(sub_src, sub_dst)]["tx_attempts_sun"] += sublink.tx_attempt
            sublink_attr[(sub_src, sub_dst)]["tx_attempts_max"] = max(sublink_attr[(sub_src, sub_dst)]["tx_attempts_max"], sublink.tx_attempt)
            sublink_attr[(sub_src, sub_dst)]["tx_attempts_min"] = min(sublink_attr[(sub_src, sub_dst)]["tx_attempts_min"], sublink.tx_attempt)
            sublink_attr[(sub_src, sub_dst)]["length_sum"] += sublink.length
            sublink_attr[(sub_src, sub_dst)]["length_max"] = max(sublink_attr[(sub_src, sub_dst)]["length_max"], sublink.length)
            sublink_attr[(sub_src, sub_dst)]["length_min"] = min(sublink_attr[(sub_src, sub_dst)]["length_min"], sublink.length)
        
        # self.sub_links_queued_delay = self.sub_links_queued_delay / self.sub_links_queued_num if self.sub_links_queued_num != 0 else 0
        # self.sub_links_length = self.sub_links_length / sub_links_num if sub_links_num != 0 else 0

        if sub_links_num <= 1:
            sub_links_hop_count = 1
            sub_links_fragment_count = 1
        else:
            sub_links_fragment_count = 0
            for sublink in self.sub_links:
                if sublink.src == self.src:
                    sub_links_fragment_count += 1
            sub_links_hop_count = sub_links_num // sub_links_fragment_count if sub_links_fragment_count != 0 else 0

        success_rate = sub_links_num / sub_links_tx_attemps if sub_links_tx_attemps != 0 else 0
        

        # self.after_calculate_link_status = True
        link_attr = [   sub_links_num,
                        sub_links_queued_num,
                        sub_links_tx_attemps,
                        self.RSSI,
                        self.LQI,
                        delay,
                        sub_links_hop_count,
                        sub_links_fragment_count,
                        success_rate]
        return link_attr, sublink_attr

    # def get_link_status(self):
    #     # return the link's status in the index as a list

    #     if self.after_calculate_link_status == False:
    #         self.calculate_link_status()

    #     link_status = [self.send_ts,self.recv_ts,self.delay,sub_links_num,self.sub_links_tx_num,self.sub_links_queued_num,self.sub_links_queued_delay,self.sub_links_length,self.sub_links_hop_count,self.sub_links_fragment_count]
    #     if None in link_status:
    #         # change the None to 0
    #         link_status = [0 if x is None else x for x in link_status]
    #     return link_status

class SubLinkStatus:
    """Record the sublink's status, tsch
    """
    def __init__(self,src,dst,seqnum,timestamp = None):
        # Basic information
        self.src = src
        self.dst = [dst]
        self.seqnum = seqnum
        self.timestamp = timestamp

        # Queue information 
        self.is_queued = False      # Is the packet queued
        self.queued_ts = None       # Timestamp when the packet is put into the queue
        self.queue_len = None       # Queue length

        # Send or Recieve information
        self.status = None          # status
        self.tx_attempt = None      # tx attempt

        # ASN and link details 
        self.link_type = None       # BROADCAST or UNICAST
        self.ASN = None             # ASN
        self.link_details = None    # link details
        self.is_eb = False          # is EB
        self.security = None        # security
        self.length = None          # length
        self.edr = None             # edr

        # Class control
        self.is_send = False
        self.is_recv = False

    def __eq__(self, other) -> bool:
        return self.src == other.src and self.dst == other.dst and self.seqnum == other.seqnum and self.timestamp == other.timestamp and self.ASN == other.ASN

    @property
    def is_valid(self):
        if self.is_eb:
            return False
        if self.status == 2:
            return False
        if self.timestamp is None:
            return False
        # if self.is_send == False or self.is_recv == False:
        #     return False
        return True
    
    # def could_be_deleted(self, timestamp):
    
    def is_in_duration(self, start, end):
        if self.timestamp is None:
            return False
        if start is None or end is None:
            return False
        if self.timestamp < start or self.timestamp > end:
            return False
        return True

    def __str__(self) -> str:
        return f"{self.src} -> {self.dst}, seqnum: {self.seqnum}, status: {self.status}, tx_attempt: {self.tx_attempt}, timestamp: {self.timestamp}"

class LogParse:
    def __init__(self, log_path = None, log = None):
        if log is not None:
            self.log = log
        if log_path:
            self.log_path = log_path
            with open(log_path, 'r') as file:
                self.lines = file.readlines()

        self.random_seed = self.lines[0].split()[-1]
        # ignore first 2 lines and the last 3 lines
        self.lines = self.lines[2:-3]

        self.nodes = {}

        self.IPv6_address_map = []
        # in list is tuple, as below
        #(node,seqnum,send_ts,recv_ts)

        self.tsch_links = [] 
        self.unfinished_links = {} # Key: (src, dst, seqnum), Value: {index in tsch_links=int, timestamp, asn}
        
    def allocate_tsch_links(self):
        """Add all tsch links to the nodes' IPv6_links by comparing the send_ts and recv_ts
            If it is not valid, ignore it, not need to consider the src and dst, only consider if the timestamp is in the duration
        """
        for node in self.nodes.values():
            for link in node.IPv6_links.values():
                self.IPv6_address_map.append((link.src,link.seqnum,link.send_ts,link.recv_ts))

        print("\nAllocating tsch links to IPv6 links")
        i = 0
        # Al node's IPv6_links's sum
        length = sum([len(node.IPv6_links) for node in self.nodes.values()])
        for node_index in self.nodes.keys():
            node = self.nodes[node_index]
            if node_index == 6:
                stop_pointer = 1
            for seqnum in node.IPv6_links.keys():
                # if node == 6 and seqnum == 0:
                #     stop_pointer = 1
                send_ts = node.IPv6_links[seqnum].send_ts
                recv_ts = node.IPv6_links[seqnum].recv_ts
                print_process_bar("Allocating", i / length)
                # if round(i/length * 100, 2) == 1.09:
                #     stop_pointer = 1
                i += 1
                # Add all link in duration to the node's IPv6_links
                for link in self.tsch_links:
                    if send_ts is None or recv_ts is None:
                        continue
                    if link.is_valid and link.is_in_duration(send_ts,recv_ts):
                        self.nodes[node_index].IPv6_links[seqnum].sub_links.append(link)
                    if link.is_valid and link.timestamp > recv_ts + 10000000:
                        break
                
                sublinks = self.nodes[node_index].IPv6_links[seqnum].sub_links
                IPv6_src = node.IPv6_links[seqnum].src
                IPv6_dst = node.IPv6_links[seqnum].dst

                # Find the path from src to dst
                self.all_paths = []
                self.find_link_path(IPv6_src, IPv6_dst, sublinks)
                self.nodes[node_index].IPv6_links[seqnum].sub_links = self.all_paths
        
    def find_link_path(self, src, dst, sublinks, current_path=[]):
        # If the current node is equal to the destination node, we have found a path
        if src == dst:
            for link in current_path:
                self.all_paths.append(link)
            return
        if len(current_path) >= len(sublinks) or len(sublinks) == 0:
            return
        
        # Check the sublinks from the current node
        # self.src == other.src and self.dst == other.dst and self.seqnum == other.seqnum and self.timestamp == other.timestamp and self.ASN == other.ASN
        for index, link in enumerate(sublinks):
            is_in_current_path = link in current_path
            is_in_all_paths = link in self.all_paths
            if link.src == src and not is_in_current_path and not is_in_all_paths:
                # Add the current link to the path
                current_path.append(link)
                # link.dst: [1] as an example, should be a list, but in this case, it should be an int
                next_src = link.dst[0] if len(link.dst) == 1 else link.dst
                # Recursively search for the path from the destination node of the current link to the destination node
                self.find_link_path(next_src, dst, sublinks, current_path)
                # Backtrack: Remove the current link and explore the next possible link
                current_path.pop()
        # return
                
    def process(self):
        self.analyse_log()
        self.allocate_tsch_links()
        for node in self.nodes.values():
            node.calculate_node_status()
            # node.allocate_IPv6_links()
                    
    def analyse_log(self):
        """Process the log file, and save the information to the self.nodes and self.tsch_links
        """
        print("Processing the log ")
        for line_index, line in enumerate(self.lines):
            print_process_bar("Processing", line_index / len(self.lines))
            line = line.strip()
            fields = line.split()
            timestamp = int(fields[0])  # in milliseconds
            node = int(fields[1])        # node id

            if timestamp == 60567488:
                stop_pointer =1
                pass

            # Delete previous or finished links in self.unfinished_links
            if len(self.unfinished_links) > 0:
                for key in list(self.unfinished_links.keys()):
                    if self.unfinished_links[key]["timestamp"] is not None and timestamp - self.unfinished_links[key]["timestamp"] >= 3000 :
                        # if self.tsch_links[self.unfinished_links[key]["index"]].is_send and self.tsch_links[self.unfinished_links[key]["index"]].is_recv:
                        del self.unfinished_links[key]

            if node not in self.nodes:
                self.nodes[node] = NodeStats(node)

            # 73000 8 [INFO: Main      ] Link-layer address: 0008.0008.0008.0008
            if "Link-layer address" in line:
                self.nodes[node].link_layer_addr = fields[-1]
                continue

            # 73000 8 [INFO: Main      ] Tentative link-local IPv6 address: fe80::208:8:8:8
            if "IPv6 address" in line:
                self.nodes[node].IPv6_addr = fields[-1].split("::")[-1]
                continue

            # 382000 1 [INFO: App       ] Node 1 started as root, root ip address: fd00::201:1:1:1
            if "started as root" in line:
                self.nodes[node].is_root = True
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
                dst_IPv6_addr = fields[-3][:-1].split("::")[-1]
                dst_node = self.IPv6_2_Node(dst_IPv6_addr)
                # print(dst_IPv6_addr)
                # print(self.nodes[1].IPv6_addr)
                self.nodes[node].IPv6_links[seqnum] = LinkStats(node, dst_node, seqnum, timestamp)
                continue
            
            # 2757000 1 [INFO: App       ] APP: Received from fd00::201:1:1:1, seqnum 1, RSSI: 0, LQI: 0
            if "APP: Received" in line:
                LQI = int(fields[-1])
                RSSI = int(fields[-3][:-1])
                seqnum = int(fields[-5][:-1])
                src_IPv6_addr = fields[-7][:-1].split("::")[-1]
                src_node = self.IPv6_2_Node(src_IPv6_addr)

                # find seqnum in links
                self.nodes[src_node].IPv6_links[seqnum].is_received = True
                self.nodes[src_node].IPv6_links[seqnum].RSSI = RSSI
                self.nodes[src_node].IPv6_links[seqnum].LQI = LQI
                self.nodes[src_node].IPv6_links[seqnum].recv_ts = timestamp
                continue

            # 30073000 8 [INFO: App       ] Energest: Index 0 CPU 30000000 LPM 0 TX 22784 RX 9564348 Total_time 30000000
            if "Energest:" in line:
                energest_stats = {
                    # Key: index, Value: (CPU, LPM, TX, RX, Total_time)
                    "INDEX": int(fields[-11]),
                    "CPU": int(fields[-9]),
                    "LPM": int(fields[-7]),
                    "TX": int(fields[-5]),
                    "RX": int(fields[-3]),
                    "Total_time": int(fields[-1])
                }
                self.nodes[node].Energest.append(energest_stats)
                continue

            # 8467000 4 [INFO: TSCH      ] send packet to 0001.0001.0001.0001 with seqno 67, queue 1/64 1/64, len 21 100
            if "send packet to" in line and "queue" in line:
                dst_link_layer_addr = fields[-10]
                dst_node = self.MAC_2_Node(dst_link_layer_addr)
                seqnum = 0 if int(fields[-7][:-1]) == 65535 else int(fields[-7][:-1])
                self.tsch_links.append(SubLinkStatus(node, dst_node, seqnum, None))
                self.unfinished_links[(node, dst_node, seqnum)] = {
                    "index": len(self.tsch_links) - 1,
                    "timestamp": None,
                    "ASN": None
                }
                self.tsch_links[-1].queued_ts = timestamp
                self.tsch_links[-1].is_queued = True
                self.tsch_links[-1].queued_len = int(fields[-1])
                self.tsch_links[-1].seqnum = seqnum
                if dst_node not in self.tsch_links[-1].dst:
                    self.tsch_links[-1].dst.append(dst_node)
                continue

            # 27085240 3 [INFO: TSCH      ] packet sent to 0000.0000.0000.0000, seqno 0, status 0, tx 1
            # # if "packet sent to" in line:
            #     dst_link_layer_addr = fields[-7][:-1]
            #     dst_node = self.MAC_2_Node(dst_link_layer_addr)
            #     seqnum = 0 if int(fields[-5][:-1]) == 65535 else int(fields[-5][:-1])
            #     status = int(fields[-3][:-1])
            #     tx_attempt = int(fields[-1]) 
            #     # find the corresponding link
            #     if (node, dst_node, seqnum) in self.unfinished_links.keys():
            #         # If the linke is queued or received
            #         index = self.unfinished_links[(node, dst_node, seqnum)]["index"]
            #         self.tsch_links[index].status = status
            #         self.tsch_links[index].tx_attempt = tx_attempt
            #         self.tsch_links[index].timestamp = timestamp
            #         if dst_node not in self.tsch_links[index].dst:
            #             self.tsch_links[index].dst.append(dst_node)
            #         self.unfinished_links[(node, dst_node, seqnum)]["timestamp"] = timestamp
            #     else:
            #         # If the link is not in the unfinished_links, then add it to the tsch_links
            #         self.tsch_links.append(SubLinkStatus(node, dst_node, seqnum, timestamp))
            #         self.tsch_links[-1].status = status
            #         self.tsch_links[-1].tx_attempt = tx_attempt
            #         self.tsch_links[-1].timestamp = timestamp
            #         self.tsch_links[-1].is_send = True
            #         if dst_node not in self.tsch_links[-1].dst:
            #             self.tsch_links[-1].dst.append(dst_node)
            #         self.unfinished_links[(node, dst_node, seqnum)] = {
            #             "index": len(self.tsch_links) - 1,
            #             "timestamp": timestamp,
            #             "ASN": None
            #         }
            #     continue

            # 45117128 1 [INFO: TSCH      ] received from 0008.0008.0008.0008 with seqno 65535
            # if "received from" in line:
            #     src_link_layer_addr = fields[-4]
            #     src_node = self.MAC_2_Node(src_link_layer_addr)
            #     seqnum = 0 if int(fields[-1]) == 65535 else int(fields[-1])                
            #     # find the corresponding link
            #     if (src_node, node, seqnum) in self.unfinished_links.keys():
            #         # If the linke is queued or sent
            #         index = self.unfinished_links[(src_node, node, seqnum)]["index"]
            #         self.tsch_links[index].timestamp = timestamp
            #         if node not in self.tsch_links[index].dst:
            #             self.tsch_links[index].dst.append(node)
            #         self.unfinished_links[(src_node, node, seqnum)]["timestamp"] = timestamp    
            #     elif (src_node, 0, seqnum) in self.unfinished_links.keys():
            #         # if the link is broadcast
            #         index = self.unfinished_links[(src_node, 0, seqnum)]["index"]
            #         if self.unfinished_links[(src_node, 0, seqnum)]["timestamp"] == timestamp:
            #             # If the linke is queued or sent
            #             self.tsch_links[index].timestamp = timestamp
            #             if node not in self.tsch_links[index].dst:
            #                 self.tsch_links[index].dst.append(node)
            #             self.unfinished_links[(src_node, 0, seqnum)]["timestamp"] = timestamp   
            #     else:
            #         # If the link is not in the unfinished_links, then add it to the tsch_links
            #         self.tsch_links.append(SubLinkStatus(src_node, node, seqnum,timestamp))
            #         if node not in self.tsch_links[-1].dst:
            #             self.tsch_links[-1].dst.append(node)
            #         self.unfinished_links[(src_node, node, seqnum)] = {
            #             "index": len(self.tsch_links) - 1,
            #             "timestamp": timestamp,
            #             "ASN": None
            #         }

            # TX
            # 27085240 3 [INFO: TSCH-LOG  ] {asn 00.00000a6e link  0   3   0  0  0 ch 26} bc-0-0 tx LL-0003->LL-NULL, len  35, seq   0, st 0  1
            if  "[INFO: TSCH-LOG  ]" in line and "tx" in line:
                match = re.match(tx_re_pattern, line)
                if match:
                    asn, link1, link2, link3, link4, link5, ch, link_type, is_eb, securty, src, dst, length, seqnum, status, tx_attempt = match.groups()
                    src_addr = src+"."+src+"."+src+"."+src
                    src_node = self.MAC_2_Node(src_addr)
                    dst_addr = "ffff.ffff.ffff.ffff" if dst == "NULL" else dst+"."+dst+"."+dst+"."+dst
                    dst_node = self.MAC_2_Node(dst_addr)
                    seqnum = int(seqnum)
                    if link_type == "bc":
                        dst_node = 0

                    # find the corresponding link
                    if (src_node, dst_node, seqnum) in self.unfinished_links.keys():
                        # If the linke is queued or received                        
                        # if self.unfinished_links[(src_node, dst_node, seqnum)]["ASN"] != asn or self.unfinished_links[(src_node, dst_node, seqnum)]["ASN"] is not None:
                        #     continue
                        index = self.unfinished_links[(src_node, dst_node, seqnum)]["index"]
                        if self.tsch_links[index].is_recv:
                            if int(status) == 0:
                                self.tsch_links[index].status = int(status)
                                self.tsch_links[index].tx_attempt = int(tx_attempt)
                                self.tsch_links[index].is_send = True
                            elif int(status) == 2:
                                # If the link is failed, reset the link to wait for the next send
                                self.unfinished_links[(src_node, dst_node, seqnum)]["ASN"] = None
                                self.unfinished_links[(src_node, dst_node, seqnum)]["timestamp"] = None
                                self.tsch_links[index].status = int(status)
                                self.tsch_links[index].is_send = False
                                self.tsch_links[index].is_recv = False
                                continue
                        elif int(status) == 2:
                            self.unfinished_links[(src_node, dst_node, seqnum)]["ASN"] = None
                            self.unfinished_links[(src_node, dst_node, seqnum)]["timestamp"] = None
                            self.tsch_links[index].status = int(status)
                            self.tsch_links[index].is_send = False
                            self.tsch_links[index].is_recv = False
                            continue
                        else:
                            self.tsch_links[index].ASN = asn
                            self.tsch_links[index].link_details = (int(link1), int(link2), int(link3), int(link4), int(link5), int(ch))
                            self.tsch_links[index].link_type = link_type
                            self.tsch_links[index].is_eb = True if int(is_eb) == 0 else False
                            self.tsch_links[index].security = int(securty)
                            self.tsch_links[index].length = int(length)
                            self.tsch_links[index].status = int(status)
                            self.tsch_links[index].tx_attempt = int(tx_attempt)
                            self.tsch_links[index].timestamp = timestamp
                            self.unfinished_links[(src_node, dst_node, seqnum)]["ASN"] = asn
                            self.unfinished_links[(src_node, dst_node, seqnum)]["timestamp"] = timestamp
                            self.tsch_links[index].is_send = True
                    # elif len(self.unfinished_links) > 0:
                    #     for (src, dst, seqnum) in self.unfinished_links.keys():
                    #         link = self.unfinished_links[(src, dst, seqnum)]
                    else:
                        # If the link is not in the unfinished_links, then add it to the tsch_links
                        self.tsch_links.append(SubLinkStatus(src_node, dst_node, seqnum, timestamp))
                        self.tsch_links[-1].ASN = asn
                        self.tsch_links[-1].link_details = (int(link1), int(link2), int(link3), int(link4), int(link5), int(ch))
                        self.tsch_links[-1].link_type = link_type
                        self.tsch_links[-1].is_eb = True if int(is_eb) == 0 else False
                        self.tsch_links[-1].security = int(securty)
                        self.tsch_links[-1].length = int(length)
                        self.tsch_links[-1].status = int(status)
                        self.tsch_links[-1].tx_attempt = int(tx_attempt)
                        self.tsch_links[-1].timestamp = timestamp
                        self.unfinished_links[(src_node, dst_node, seqnum)] = {
                            "index": len(self.tsch_links) - 1,
                            "timestamp": timestamp,
                            "ASN": asn
                        }
                        self.tsch_links[-1].is_send = True
                    
                    continue

            # RX
            # 27085240 1 [INFO: TSCH-LOG  ] {asn 00.00000a6e link  0   3   0  0  0 ch 26} bc-0-0 rx LL-0003->LL-NULL, len  35, seq 119, edr   0
            if "[INFO: TSCH-LOG  ]" in line and "rx" in line:
                is_dr = " dr" in line
                if is_dr:
                    match = re.match(rx_dr_re_pattern, line)
                else:
                    match = re.match(rx_re_pattern, line)
                # match = re.match(rx_re_pattern, line) if not is_dr else re.match(rx_dr_re_pattern, line)
                if match:
                    if is_dr:
                        asn, link1, link2, link3, link4, link5, ch, link_type, is_eb, security, src, dst, length, seqnum, edr, dr = match.groups()
                    else:
                        asn, link1, link2, link3, link4, link5, ch, link_type, is_eb, security, src, dst, length, seqnum, edr = match.groups()
                    src_addr = src+"."+src+"."+src+"."+src
                    src_node = self.MAC_2_Node(src_addr)
                    dst_addr = "ffff.ffff.ffff.ffff" if dst == "NULL" else dst+"."+dst+"."+dst+"."+dst
                    dst_node = self.MAC_2_Node(dst_addr)
                    seqnum = int(seqnum)
                    if link_type == "bc":
                        dst_node = 0

                    # find the corresponding link
                    if (src_node, dst_node, seqnum) in self.unfinished_links.keys():
                        # If the linke is queued or received
                        # if self.unfinished_links[(src_node, dst_node, seqnum)]["ASN"] != asn:
                        #     continue
                        index = self.unfinished_links[(src_node, dst_node, seqnum)]["index"]
                        if node not in self.tsch_links[index].dst:
                            self.tsch_links[index].dst.append(node)
                        if self.tsch_links[index].is_send:
                            self.tsch_links[index].edr = int(edr)
                            # self.tsch_links[index].is_recv = True
                        # elif self.tsch_links[index].status == "2":
                        #     continue
                        else:
                            self.tsch_links[index].timestamp = timestamp
                            self.tsch_links[index].ASN = asn
                            self.tsch_links[index].link_details = (int(link1), int(link2), int(link3), int(link4), int(link5), int(ch))
                            self.tsch_links[index].link_type = link_type
                            self.tsch_links[index].is_eb = True if int(is_eb) == 0 else False
                            self.tsch_links[index].security = int(securty)
                            self.tsch_links[index].length = int(length)
                            self.tsch_links[index].edr = int(edr)
                            self.unfinished_links[(src_node, dst_node, seqnum)]["ASN"] = asn
                            self.unfinished_links[(src_node, dst_node, seqnum)]["timestamp"] = timestamp

                        self.tsch_links[index].is_recv = True
                    # elif len(self.unfinished_links) > 0:
                    #     for (src, dst, seqnum) in self.unfinished_links.keys():
                    #         if timestamp - self.unfinished_links[(src, dst, seqnum)]["timestamp"] <= 1000:
                    #         # if src == src_node and dst == dst_node:
                    #             index = self.unfinished_links[(src, dst, seqnum)]["index"]
                    #             if node not in self.tsch_links[index].dst:
                    #                 self.tsch_links[index].dst.append(node)
                    #             if self.tsch_links[index].is_send:
                    #                 self.tsch_links[index].edr = int(edr)
                    #             else:
                    #                 self.tsch_links[index].ASN = asn
                    #                 self.tsch_links[index].link_details = (int(link1), int(link2), int(link3), int(link4), int(link5), int(ch))
                    #                 self.tsch_links[index].link_type = link_type
                    #                 self.tsch_links[index].is_eb = True if int(is_eb) == 0 else False
                    #                 self.tsch_links[index].security = int(securty)
                    #                 self.tsch_links[index].length = int(length)
                    #                 self.tsch_links[index].edr = int(edr)
                    #                 # self.unfinished_links[(src_node, dst_node, seqnum)]["ASN"] = asn
                    #                 # self.unfinished_links[(src_node, dst_node, seqnum)]["timestamp"] = timestamp
                    #             break
                    else:
                        # If the link is not in the unfinished_links, then add it to the tsch_links
                        self.tsch_links.append(SubLinkStatus(src_node, dst_node, seqnum, timestamp))
                        if node not in self.tsch_links[-1].dst:
                            self.tsch_links[-1].dst.append(node)
                        self.tsch_links[-1].ASN = asn
                        self.tsch_links[-1].link_details = (int(link1), int(link2), int(link3), int(link4), int(link5), int(ch))    
                        self.tsch_links[-1].link_type = link_type
                        self.tsch_links[-1].is_eb = True if int(is_eb) == 0 else False
                        self.tsch_links[-1].security = int(securty)
                        self.tsch_links[-1].length = int(length)
                        self.tsch_links[-1].edr = int(edr)
                        self.unfinished_links[(src_node, dst_node, seqnum)] = {
                            "index": len(self.tsch_links) - 1,
                            "timestamp": timestamp,
                            "ASN": asn
                        }
                        self.tsch_links[-1].is_recv = True
                    continue
                
        # self.allocate_tsch_links()  

    def MAC_2_Node(self, addr):
        if addr == "0000.0000.0000.0000" or addr == "ffff.ffff.ffff.ffff": #Root / Broadcast
            return 0
        for node in self.nodes.keys():
            if self.nodes[node].link_layer_addr == addr:
                return node
        return None
    
    def IPv6_2_Node(self, addr):
        for node in self.nodes.keys():
            if self.nodes[node].IPv6_addr == addr:
                return node
        return None

def print_process_bar(content, percentage):
    """Print the process bar

    Args:
        content (str): content
        percentage (float): percentage
    """
    bar_length = 20
    hashes = '#' * int(percentage * bar_length)
    spaces = ' ' * (bar_length - len(hashes))
    print(f"\r{content}: [{hashes + spaces}] {percentage*100:.2f}%", end='\r')
    if percentage == 1:
        print(f"\n{content} is done.")

if __name__ == '__main__':
    import pickle

    filepath = r"F:\Course\year_4\Individual_Researching\contiki-ng\data\raw\2024-03-10_21-23-45.testlog"
    save_path = r"F:\Course\year_4\Individual_Researching\contiki-ng\ML\log.pkl"
    # log = LogParse(log_path=filepath)
    # log.process()
        
    # with open(save_path, "wb") as file:
    #     pickle.dump(log, file)

    with open(save_path, "rb") as file:
        log = pickle.load(file)

    analyser = LogAnalysis(log)
    analyser.calculate_features()


    # with open(r"F:\Course\year_4\Individual_Researching\contiki-ng\ML\feature.pkl", "wb") as file:
    #     pickle.dump(analyser, file)

    data = analyser.node_features[:,:,9]
    import torch
    data = torch.tensor(data)
    print(torch.max(data, dim=0))

    # 假设我只需要按照每列来获得最大值
    # print(np.max(data,axis=0))
    # print( np.max(np.max(analyser.node_features,axis=0),axis = 1))

    # print(analyser.edge_index_IPv6[7])
    # print(analyser.edge_features_IPv6[7])

    # analyser.calculate_loss_and_delay()

    # print(analyser.loss, analyser.delay)