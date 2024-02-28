'''
Author: Yanbo Chen xt20786@bristol.ac.uk
Date: 2024-02-23 11:48:26
LastEditors: YanboChenA xt20786@bristol.ac.uk
LastEditTime: 2024-02-28 15:16:54
FilePath: \contiki-ng\ML\try.py
Description: 
'''
import re

line  = "22707072 3 [INFO: TSCH-LOG  ] {asn 00.000008b8 link  0   3   0  0  0 ch 15} uc-1-0 rx LL-0001->LL-0003, len  41, seq  11, edr   0, dr   0"
line =  "3687128 4 [INFO: TSCH-LOG  ] {asn 00.0000014a link  0   3   0  0  0 ch 26} bc-1-0 rx LL-0001->LL-NULL, len  94, seq   0, edr   0, dr   0"
pattern = r".*\{asn (.*?) link\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+ch\s+(\d+)\}\s+(.*?)-(\d+)-(\d+)\s+rx\s+LL-(.*?)->LL-(.*?),\s+len\s+(\d+),\s+seq\s+(\d+),\s+edr\s+(\d+),\s+dr\s+(\d+)"
match = re.match(pattern, line)
print(match.groups())
asn, link1, link2, link3, link4, link5, ch, link_type, is_eb, security, src, dst, length, seqnum, edr, dr = match.groups()

# print("fe80::208:8:8:8".split("::")[-1])