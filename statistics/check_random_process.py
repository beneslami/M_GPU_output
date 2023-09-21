import gc
import os
import sys
sys.path.append("../")
import benchlist
from pathlib import Path
import matplotlib.pyplot as plt


def read_file(file_name):
    raw_content = ""
    request_packet = {}
    with open(file_name, "r") as file:
        raw_content = file.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    del (raw_content)
    for i in range(len(lined_list)):
        if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
            if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        else:
            request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
    del (lined_list)
    gc.enable()
    gc.collect()
    return request_packet


def measrure_off_state_cdf(request_packet):
    traffic = {}
    dist = {}
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "request injected":
                src = int(request_packet[id][j][1].split(": ")[1])
                dst = int(request_packet[id][j][2].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if cycle not in traffic.keys():
                    traffic[cycle] = byte
                else:
                    traffic[cycle] += byte
            if request_packet[id][j][0] == "reply injected":
                src = int(request_packet[id][j][2].split(": ")[1])
                dst = int(request_packet[id][j][1].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if cycle not in traffic.keys():
                    traffic[cycle] = byte
                else:
                    traffic[cycle] += byte
            if request_packet[id][j][0] == "FW buffer":
                src = int(request_packet[id][j][2].split(": ")[1])
                dst = int(request_packet[id][j][1].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if cycle not in traffic.keys():
                    traffic[cycle] = byte
                else:
                    traffic[cycle] += byte
    prev_cycle = 0
    flag = 0
    for cyc, byte in traffic.items():
        if flag == 0:
            prev_cycle = cyc
            flag = 1
        else:
            if cyc - prev_cycle > 1:
                if cyc - prev_cycle not in dist.keys():
                    dist[cyc - prev_cycle] = 1
                else:
                    dist[cyc - prev_cycle] += 1
            prev_cycle = cyc
    dist = dict(sorted(dist.items(), key=lambda x: x[0]))
    total = sum(dist.values())
    for duration, freq in dist.items():
        dist[duration] = freq / total
    total = 0
    for duration, freq in dist.items():
        dist[duration] = freq + total
        total += freq
    return dist


if __name__ == "__main__":
    suits = benchlist.suits
    benchmarks = benchlist.benchmarks
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet_num = benchlist.chiplet_num
    path = benchlist.bench_path

    for suite in suits:
        if os.path.exists(path + suite) and suite == "rodinia":
            for bench in benchmarks[suite]:
                if os.path.exists(path + suite + "/" + bench) and (bench == "b+tree"):
                    for topo in topology:
                        if os.path.exists(path + suite + "/" + bench + "/" + topo):  # and topo != "torus":
                            for nv in NVLink:
                                if os.path.exists(
                                        path + suite + "/" + bench + "/" + topo + "/" + nv):  # and nv == "NVLink4":
                                    for ch in chiplet_num:
                                        if os.path.exists(
                                                path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch):
                                            sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                                            if len(os.listdir(os.path.dirname(os.path.dirname(sub_path)))) != 0:
                                                chip_num = int(ch[0])
                                                for trace_file in os.listdir(sub_path):
                                                    if Path(trace_file).suffix == '.txt':
                                                        if os.path.getsize(sub_path + trace_file) > 10000:
                                                            request_packet = read_file(sub_path + trace_file)
                                                            cdf = measrure_off_state_cdf(request_packet)
                                                            plt.plot(list(cdf.keys()), list(cdf.values()), marker="o", label=nv)
                                                            cdf = {}
                                                            request_packet = {}
                            plt.legend()
                            plt.title(topo)
                            plt.show()
                            plt.close()