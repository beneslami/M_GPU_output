import gc
import os
import sys
import pandas as pd
sys.path.append("../")
import benchlist
from pathlib import Path
import numpy as np
from hurst import compute_Hc
import matplotlib.pyplot as plt


def measure_hurst(path, traffic, suite, bench):
    series = pd.Series(traffic.values())
    H, c, data = compute_Hc(series, simplified=True)
    f, ax = plt.subplots()
    ax.plot(data[0], c*data[0]**H, color="deepskyblue", label="H={:.4f}".format(H))
    ax.scatter(data[0], data[1], color="purple")
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Time interval')
    ax.set_ylabel('R/S ratio')
    ax.set_title(str(suite) + " " + str(bench) + " hurst exponent")
    plt.legend()
    if not os.path.exists(path + "/plots"):
        os.mkdir(path + "/plots/")
    plt.savefig(path + "/plots/hurst.png")
    plt.close()
    return H


def calculate_hurst(file_name, suite, bench):
    file2 = open(file_name, "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    file2.close()
    del(file2)
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    del (raw_content)
    request_packet = {}
    for i in range(len(lined_list)):
        if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
            if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        else:
            request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
    del (lined_list)
    gc.enable()
    gc.collect()
    traffic = {}
    for id in request_packet.keys():
        for i in range(len(request_packet[id])):
            if request_packet[id][i][0] == "request injected":
                byte = int(request_packet[id][i][7].split(": ")[1])
                cycle = int(request_packet[id][i][5].split(": ")[1])
                if cycle not in traffic.keys():
                    traffic[cycle] = byte
                else:
                    traffic[cycle] += byte
                break
    path = os.path.dirname(os.path.dirname(file_name))
    value = measure_hurst(path, traffic, suite, bench)
    return value


if __name__ == "__main__":
    suits = benchlist.suits
    benchmarks = benchlist.single_kernels
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet_num = benchlist.chiplet_num
    path = benchlist.bench_path

    hurst_list = {}
    for suite in suits:
        if os.path.exists(path + suite) and (suite == "SDK"):
            for bench in benchmarks[suite]:
                if os.path.exists(path + suite + "/" + bench):
                    for topo in topology:
                        if os.path.exists(path + suite + "/" + bench + "/" + topo) and topo == "torus":
                            for nv in NVLink:
                                if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv) and nv == "NVLink4":
                                    for ch in chiplet_num:
                                        if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch):
                                            sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                                            if len(os.listdir(os.path.dirname(os.path.dirname(sub_path)))) != 0:
                                                for trace_file in os.listdir(sub_path):
                                                    if Path(trace_file).suffix == '.txt':
                                                        if os.path.getsize(sub_path + trace_file) > 10000:
                                                            value = calculate_hurst(sub_path + trace_file, suite, bench)
                                                            if suite not in hurst_list.keys():
                                                                hurst_list.setdefault(suite, {}).setdefault(bench, []).append(value)
                                                            else:
                                                                if bench not in hurst_list[suite].keys():
                                                                    hurst_list[suite].setdefault(bench, []).append(value)
                                                                else:
                                                                    hurst_list[suite][bench].append(value)

    for suite in hurst_list.keys():
        print(suite)
        for bench, h_list in hurst_list[suite].items():
            print("\t" + str(bench) + "\t" + str(h_list))
