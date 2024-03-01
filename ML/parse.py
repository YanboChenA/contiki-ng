'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-02-22 13:59:08
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-03-01 22:35:10
FilePath: \contiki-ng\ML\parse.py
Description: 
'''

import re
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

        self.Energest = []
        self.IPv6_links = {}

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

    def __str__(self) -> str:
        if self.sub_links == []:
            return f"{self.src} -> {self.dst}, seqnum: {self.seqnum}, RSSI: {self.RSSI}, LQI: {self.LQI}, send_ts: {self.send_ts}, recv_ts: {self.recv_ts}"
        else:
            sublinks_str = "\n"
            for sublink in self.sub_links:
                sublinks_str += str(sublink) + "\n"
            return f"{self.src} -> {self.dst}, seqnum: {self.seqnum}, RSSI: {self.RSSI}, LQI: {self.LQI}, send_ts: {self.send_ts}, recv_ts: {self.recv_ts}, \nsublinks: {sublinks_str}"
    # def get_
        
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
            for seqnum in node.IPv6_links.keys():
                # if node == 6 and seqnum == 0:
                #     stop_pointer = 1
                send_ts = node.IPv6_links[seqnum].send_ts
                recv_ts = node.IPv6_links[seqnum].recv_ts
                print_process_bar("Allocating", i / length)
                i += 1
                # Add all link in duration to the node's IPv6_links
                for link in self.tsch_links:
                    if send_ts is None or recv_ts is None:
                        continue
                    if link.is_valid and link.is_in_duration(send_ts,recv_ts):
                        self.nodes[node_index].IPv6_links[seqnum].sub_links.append(link)
                    # if link.is_valid and link.timestamp > recv_ts:
                    #     break

                # Find link that match the IPv6_links, pind the matched path, means
                # there will be multiple links in the sub_links to form a IPv6_links or a path
                # and the below code should delete the link that is not right
                # link_with_right_src = []
                # link_with_right_dst = []
                # for link in self.nodes[node_index].IPv6_links[seqnum].sub_links:
                    
                    
    def process(self):
        """Process the log file, and save the information to the self.nodes and self.tsch_links
        """
        print("Processing the log ")
        for line_index, line in enumerate(self.lines):
            print_process_bar("Processing", line_index / len(self.lines))
            line = line.strip()
            fields = line.split()
            timestamp = int(fields[0])  # in milliseconds
            node = int(fields[1])        # node id

            if timestamp == 60837488:
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
                
        self.allocate_tsch_links()  

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

def delete_lines(input_file, output_file):
    """Delete lines from the files, and save as another file

    Args:
        filename (str): file path
    """
    
    with open(input_file, 'r') as file:
        lines = file.readlines()
        line_number = len(lines)
        # add first 2 lines and the last 3 lines to cancel_lines
        save_lines = []
        lines = lines[2:-3]
        for index, line in enumerate(lines):
            line = line.strip()
            # 73000 8 [INFO: Main      ] Link-layer address: 0008.0008.0008.0008
            if "Link-layer address" in line:
                save_lines.append(line)
                continue

            # 73000 8 [INFO: Main      ] Tentative link-local IPv6 address: fe80::208:8:8:8
            if "IPv6 address" in line:
                save_lines.append(line)
                continue

            # 382000 1 [INFO: App       ] Node 1 started as root, root ip address: fd00::201:1:1:1
            if "started as root" in line:
                save_lines.append(line)
                continue

            # 508000 4 [INFO: TSCH      ] association done (1), sec 0, PAN ID 81a5, asn-0.c, jp 1, timeslot id 0, hopping id 0, slotframe len 0 with 0 links, from 0001.0001.0001.0001
            if "association done" in line:
                save_lines.append(line)
                continue

            # 536000 2 [INFO: TSCH Queue] update time source: (NULL LL addr) -> 0001.0001.0001.0001
            if "update time source" in line:
                save_lines.append(line)
                continue

            if "leaving the network" in line:
                save_lines.append(line)
                continue

            # 2757000 1 [INFO: App       ] APP: Sending to fd00::201:1:1:1, seqnum 1
            if "APP: Sending" in line:
                save_lines.append(line)
                continue
            
            # 2757000 1 [INFO: App       ] APP: Received from fd00::201:1:1:1, seqnum 1, RSSI: 0, LQI: 0
            if "APP: Received" in line:
                save_lines.append(line)
                continue

            # 30073000 8 [INFO: App       ] Energest: Index 0 CPU 30000000 LPM 0 TX 22784 RX 9564348 Total_time 30000000
            if "Energest:" in line:
                save_lines.append(line)
                continue

            # 8467000 4 [INFO: TSCH      ] send packet to 0001.0001.0001.0001 with seqno 67, queue 1/64 1/64, len 21 100
            if "send packet to" in line and "queue" in line:
                save_lines.append(line)
                continue

            # 27085240 3 [INFO: TSCH      ] packet sent to 0000.0000.0000.0000, seqno 0, status 0, tx 1
            if "packet sent to" in line:
                save_lines.append(line)
                continue

            # 27085240 3 [INFO: TSCH-LOG  ] {asn 00.00000a6e link  0   3   0  0  0 ch 26} bc-0-0 tx LL-0003->LL-NULL, len  35, seq   0, st 0  1
            if "INFO: TSCH-LOG" in line:
                save_lines.append(line)
                continue

            if "received from" in line:
                save_lines.append(line)
                continue

        # save as another file
        with open(output_file, 'w') as file:
            for line in save_lines:
                file.write(line + "\n")

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
    filepath = "F:\Course\year_4\Individual_Researching\contiki-ng\data\\raw\\2024-02-27_14-35-05.testlog"
    log = LogParse(log_path=filepath)
    log.process()
    

    for i in range(10):

        print(log.nodes[6].IPv6_links[i])   

    # eb_count = 0
    # failed_count = 0
    # useless_links = []
    # for index,link in enumerate(log.tsch_links):
    #     if link.is_eb:
    #         eb_count += 1
    #         useless_links.append(index)
    #     if link.status == 2:
    #         failed_count += 1
    #         useless_links.append(index)

    # print(f"There are {eb_count} EBs in the log file.")
    # print(f"There are {failed_count} failed links in the log file.")
    

    # print(log.MAC_2_Node("0001.0001.0001.0001"))
    # print(len(log.nodes[1].Energest))
    # print(len(log.nodes[3].IPv6_links))
    # for link in list(log.nodes[3].IPv6_links.values())[:10]:
    #     print(link)
    # print(len(log.nodes[3].tsch_links))
    # for link in list(log.nodes[3].tsch_links.values())[:50]:
    #     print(link)


