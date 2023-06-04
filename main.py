import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from spatialLocality import *
from contention import *
from calculate_link_usage import *
from throughput import *
from backpressure import *
from check_random_process import *
from pre_traffic_trace_categorizing import *
from phaseClustering import *
from temporalLocality import *
from bufferStats import *
from pre_traffic_trace_categorizing import *
from generate_model import *

def ipc(intput_):
    path_name = os.path.dirname(intput_)
    file_name = path_name + "/ipc.csv"
    df = pd.read_csv(file_name)
    x = df['interval']
    y = df['ipc']
    plt.plot(x, y)
    plt.show()


def throughtput(packet):
    chiplet = {}
    minimum = (list(packet))[0]
    minimum = int(packet[minimum][0][5].split(": ")[1])
    maximum = (list(packet))[len(packet)-1]
    maximum = int(packet[maximum][0][5].split(": ")[1])
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "request received" or packet[id][j][0] == "reply received":
                dest = int(packet[id][j][6].split(": ")[1])
                cycle = int(packet[id][j][5].split(": ")[1])
                byte = int(packet[id][j][7].split(": ")[1])
                if dest not in chiplet.keys():
                    chiplet[dest] = byte
                else:
                    chiplet[dest] += byte
    for src in chiplet.keys():
        chiplet[src] = (chiplet[src]/(maximum - minimum))*1.132
    chiplet = dict(sorted(chiplet.items(), key=lambda x: x[0]))
    print(sum(chiplet.values())/4)
    print(chiplet)


def off_time(packet):
    traffic = {}
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "request injected":
                cycle = int(packet[id][j][5].split(": ")[1])
                byte = int(packet[id][j][7].split(": ")[1])
                if cycle not in traffic.keys():
                    traffic[cycle] = byte
                else:
                    traffic[cycle] += byte
    plt.figure(figsize=(20, 6))
    plt.plot(traffic.keys(), traffic.values(), marker="*")
    plt.show()
    """prev = 0
    flag = 0
    off_dist = {}
    for cycle, byte in traffic.items():
        if 164100 <= cycle <= 165400:
            if flag == 0:
                prev = cycle
                flag = 1
            if cycle - prev >= 2:
                if cycle - prev not in off_dist.keys():
                    off_dist[cycle - prev] = 1
                else:
                    off_dist[cycle - prev] += 1
            prev = cycle

    off_dist = dict(sorted(off_dist.items(), key=lambda x: x[0]))
    total = sum(off_dist.values())
    for length, freq in off_dist.items():
        off_dist[length] = freq / total
    with open("offtime.csv", "w") as file:
        file.write("duration,pdf\n")
        for length, pdf in off_dist.items():
            file.write(str(length) + "," + str(pdf) + "\n")"""
    """prev = 0
    flag = 0
    on_dist = {}
    for cycle, byte in traffic.items():
        if 164100 <= cycle <= 165400:
            if flag == 0:
                prev = cycle
                flag = 1
            elif cycle - prev >= 2:
                if (cycle - prev - 1) not in on_dist.keys():
                    on_dist[cycle - prev - 1] = 1
                else:
                    on_dist[cycle - prev - 1] += 1
                prev = cycle

    on_dist = dict(sorted(on_dist.items(), key=lambda x: x[0]))
    total = sum(on_dist.values())
    for length, freq in on_dist.items():
        on_dist[length] = freq / total
    with open("ontime.csv", "w") as file:
        file.write("duration,pdf\n")
        for length, pdf in on_dist.items():
            file.write(str(length) + "," + str(pdf) + "\n")"""
    """byte_dist = {}
    for cycle, byte in traffic.items():
        if byte not in byte_dist.keys():
            byte_dist[byte] = 1
        else:
            byte_dist[byte] += 1
    byte_dist = dict(sorted(byte_dist.items(), key=lambda x: x[0]))
    total = sum(byte_dist.values())
    for byte, freq in byte_dist.items():
        byte_dist[byte] = freq / total
    with open("byte.csv", "w") as file:
        file.write("duration,pdf\n")
        for byte, pdf in byte_dist.items():
            file.write(str(byte) + "," + str(pdf) + "\n")"""


if __name__ == "__main__":
    request_packet = {}
    input_ = "../benchmarks/b+tree/torus/NVLink4/4chiplet/b+tree-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    #input_ = "../accelsim-chiplet/test/output.txt"
    chiplet_num = 4
    topology = ""
    nvlink = 0
    sub_str = os.path.basename(input_).split("_")
    for sub_s in sub_str:
        if sub_str.index(sub_s) != 0:
            if sub_s.__contains__("ch"):
                chiplet_num = int(re.split(r'(\d+)', sub_s)[1])
                break
    for sub_s in sub_str:
        if sub_s.__contains__("ring") or sub_s.__contains__("torus") or sub_s.__contains__(
                "mesh") or sub_s.__contains__("fly"):
            topology = sub_s
    for sub_s in sub_str:
        if sub_s.__contains__("NV"):
            nvlink = int(re.split(r'(\d+)', sub_s)[1])
            break

    file2 = open(input_, "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    file2.close()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    for i in range(len(lined_list)):
        if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
            if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        else:
            request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
    del (raw_content)
    del (lined_list)
    #calculate_link_usage_(input_, request_packet, chiplet_num)
    #spatial_locality(input_, request_packet, chiplet_num)
    #measure_throughput(input_, topology, chiplet_num, nvlink)
    #measure_contention(input_)
    #measure_backpressure(input_)
    #check_stationary(input_, request_packet, chiplet_num)
    #overall_plot(input_, request_packet)
    #phase_clustering(input_, request_packet)
    #ipc(input_)
    #temporal_locality(request_packet)
    #buffer_stats(request_packet)
    #off_time(request_packet)
    #overall_plot(input_, request_packet)
    generate_model(input_)