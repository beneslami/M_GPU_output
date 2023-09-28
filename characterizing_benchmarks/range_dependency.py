import gc
import os
import sys
import pandas as pd
sys.path.append("../")
import benchlist
from pathlib import Path
import numpy as np
from colorama import Fore
from hurst import compute_Hc
import matplotlib.pyplot as plt
from tabulate import tabulate


def measure_hurst(path, traffic, suite, bench, kernel_num):
    series = pd.Series(list(traffic.values()), index=list(traffic.keys()))
    try:
        H, c, data = compute_Hc(series, simplified=True)
        f, ax = plt.subplots()
        ax.plot(data[0], c*data[0]**H, color="deepskyblue", label="H={:.3f}".format(H))
        ax.scatter(data[0], data[1], color="purple")
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Time interval')
        ax.set_ylabel('R/S ratio')
        ax.set_title(str(suite) + " " + str(bench) + " hurst exponent")
        plt.legend()
        if not os.path.exists(path + "/plots"):
            os.mkdir(path + "/plots/")
        path += "/plots/"
        if not os.path.exists(path + str(kernel_num)):
            os.mkdir(path + str(kernel_num))
        path += str(kernel_num)
        plt.tight_layout()
        plt.savefig(path + "/hurst_" + str(kernel_num) + ".jpg")
        plt.close()
    except:
        H = -1
    return H


def calculate_hurst(file_name, suite, bench, kernel_num):
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
    value = -1
    path = os.path.dirname(os.path.dirname(file_name))
    value = measure_hurst(path, traffic, suite, bench, kernel_num)
    return "{:.2f}".format(value)


if __name__ == "__main__":
    suits = benchlist.suits
    benchmarks = benchlist.nominated_benchmarks
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet_num = benchlist.chiplet_num
    path = benchlist.bench_path

    hurst_list = [["", "", "NVLink4", "NVLink3", "NVLink2", "NVLink1"]]
    for suite in suits:
        if os.path.exists(path + suite) and (suite == "deepbench"):
            for bench in benchmarks[suite]:
                bench_item = []
                if os.path.exists(path + suite + "/" + bench) and (bench == "rnn"):
                    bench_item.append(bench)
                    for topo in topology:
                        topo_item = []
                        if os.path.exists(path + suite + "/" + bench + "/" + topo): #and topo == "torus":
                            topo_item.append(topo)
                            for nv in NVLink:
                                if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv): #and nv == "NVLink1":
                                    nv_item = []
                                    for ch in chiplet_num:
                                        if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch):
                                            sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                                            if len(os.listdir(os.path.dirname(os.path.dirname(sub_path)))) != 0:
                                                h_list = []
                                                for trace_file in os.listdir(sub_path):
                                                    if Path(trace_file).suffix == '.txt':
                                                        if os.path.getsize(sub_path + trace_file) > 100000:
                                                            value = calculate_hurst(sub_path + trace_file, suite, bench)
                                                            """if suite not in hurst_list.keys():
                                                                hurst_list.setdefault(suite, {}).setdefault(bench, []).append(value)
                                                            else:
                                                                if bench not in hurst_list[suite].keys():
                                                                    hurst_list[suite].setdefault(bench, []).append(value)
                                                                else:
                                                                    hurst_list[suite][bench].append(value)"""
                                                            if value != -1:
                                                                h_list.append(value)
                                            if len(h_list) != 0:
                                                nv_item.append("{:.2f}".format(np.mean(h_list)))
                                                h_list.clear()
                                topo_item.append(nv_item)
                        bench_item.append(topo_item)
                hurst_list.append(bench_item)
    print(tabulate(hurst_list))
