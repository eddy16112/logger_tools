#!/usr/bin/env python3

import re

class GPUDMA(object):
    def __init__(self, key, xd, read, write, size):
        self.key = key
        self.xd = xd
        self.read = read
        self.write = write
        self.size = size
        self.bw = 0
        self.timeline = [None, None]

    def add_start(self, start):
        self.timeline[0] = start

    def add_complete(self, complete):
        self.timeline[1] = complete

    def compute_bw(self):
        self.bw = self.size/1024/1024 / (self.timeline[1] - self.timeline[0])

def parse_gpudma(line, gpudma_dict):
    items = [x.strip() for x in line.split()]
    # start
    if items[7] == "create:":
        xd = items[8].split("=")[1]
        read = items[9].split("=")[1]
        write = items[10].split("=")[1]
        size = int(items[11].split("=")[1])
        key = xd + "|" + read + "|" + write
        assert key not in gpudma_dict.keys()
        gpudma = GPUDMA(key, xd, read, write, size)
        gpudma_dict[key] = gpudma
        start_time = float(items[3])
        gpudma.add_start(start_time)
    elif items[7] == "complete:":
        xd = items[8].split("=")[1]
        read = items[9].split("=")[1]
        write = items[10].split("=")[1]
        size = int(items[11].split("=")[1])
        key = xd + "|" + read + "|" + write
        if key not in gpudma_dict.keys():
            print(key, items)
            assert 0
        assert gpudma_dict[key].key == key
        complete_time = float(items[3])
        gpudma_dict[key].add_complete(complete_time)
        gpudma_dict[key].compute_bw()

def parse_log(log_file):
    gpudma_dict = dict()

    line = log_file.readline()
    while line:
        line = line.rstrip("\n")

        gpudma_regex = re.search(r"\{gpudma\}", line)
        if (gpudma_regex):
            parse_gpudma(line, gpudma_dict)
        
        line = log_file.readline()

    bw_list = []
    for key in gpudma_dict.keys():
        bw_list.append(gpudma_dict[key].bw)

    print(sum(bw_list)/len(bw_list), max(bw_list), min(bw_list), len(bw_list), gpudma_cost)

if __name__ == '__main__':
    log_file = open("gpudma.txt", "r")
    parse_log(log_file)
    log_file.close()

    