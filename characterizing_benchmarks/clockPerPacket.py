import gc
import os
import sys
sys.path.append("../")
import benchlist
from pathlib import Path
import numpy as np
from re_arrange_benchmark import *
import matplotlib.pyplot as plt


def per_packet_analysis(trace):
    request_latency = {}
    reply_latency = {}
    for id in trace.keys():
        ptype = -1
        cycle = -1
        chip = -1
        prev_step = ""
        for i in range(len(trace[id])):
            if trace[id][i][0] == "request injected":
                ptype = int(trace[id][i][4].split(": ")[1])
                cycle = int(trace[id][i][5].split(": ")[1])
                chip = int(trace[id][i][1].split(": ")[1])
                prev_step = trace[id][i][0]
            elif trace[id][i][0] == "reply injected":
                ptype = int(trace[id][i][4].split(": ")[1])
                cycle = int(trace[id][i][5].split(": ")[1])
                chip = int(trace[id][i][6].split(": ")[1])
                prev_step = trace[id][i][0]
            elif trace[id][i][0] == "inj rtr":
                if prev_step == "request injected":
                    assert(chip == int(trace[id][i][6].split(": ")[1]))
                    if "injection" not in request_latency.keys():
                        request_latency.setdefault("injection", []).append(int(trace[id][i][5].split(": ")[1]) - cycle)
                    else:
                        request_latency["injection"].append(int(trace[id][i][5].split(": ")[1]) - cycle)
                elif prev_step == "reply injected":
                    assert (chip == int(trace[id][i][1].split(": ")[1]))
                    if "injection" not in reply_latency.keys():
                        reply_latency.setdefault("injection", []).append(int(trace[id][i][5].split(": ")[1]) - cycle)
                    else:
                        reply_latency["injection"].append(int(trace[id][i][5].split(": ")[1]) - cycle)
                elif prev_step == "ejc rtr":
                    assert (ptype == int(trace[id][i][4].split(": ")[1]))
                    if int(trace[id][i][4].split(": ")[1]) == 0 or int(trace[id][i][4].split(": ")[1]) == 2:
                        if "link" not in request_latency.keys():
                            request_latency.setdefault("link", []).append(int(trace[id][i][5].split(": ")[1]) - cycle)
                        else:
                            request_latency["link"].append(int(trace[id][i][5].split(": ")[1]) - cycle)
                    elif int(trace[id][i][4].split(": ")[1]) == 1 or int(trace[id][i][4].split(": ")[1]) == 3:
                        if "link" not in reply_latency.keys():
                            reply_latency.setdefault("link", []).append(int(trace[id][i][5].split(": ")[1]) - cycle)
                        else:
                            reply_latency["link"].append(int(trace[id][i][5].split(": ")[1]) - cycle)
                prev_step = "inj rtr"
                cycle = int(trace[id][i][5].split(": ")[1])
                ptype = int(trace[id][i][4].split(": ")[1])
                chip = int(trace[id][i][6].split(": ")[1])
            elif trace[id][i][0] == "ejc rtr":
                if ptype == int(trace[id][i][4].split(": ")[1]):
                    assert(prev_step == "inj rtr")
                    if int(trace[id][i][4].split(": ")[1]) == 0 or int(trace[id][i][4].split(": ")[1]) == 2:
                        if "crossbar" not in request_latency.keys():
                            request_latency.setdefault("crossbar", []).append(int(trace[id][i][5].split(": ")[1]) - cycle)
                        else:
                            request_latency["crossbar"].append(int(trace[id][i][5].split(": ")[1]) - cycle)
                    elif int(trace[id][i][4].split(": ")[1]) == 1 or int(trace[id][i][4].split(": ")[1]) == 3:
                        if "crossbar" not in reply_latency.keys():
                            reply_latency.setdefault("crossbar", []).append(int(trace[id][i][5].split(": ")[1]) - cycle)
                        else:
                            reply_latency["crossbar"].append(int(trace[id][i][5].split(": ")[1]) - cycle)
                prev_step = trace[id][i][0]
                cycle = int(trace[id][i][5].split(": ")[1])
                ptype = int(trace[id][i][4].split(": ")[1])
                chip = int(trace[id][i][6].split(": ")[1])
            elif trace[id][i][0] == "request received":
                if prev_step == "ejc rtr":
                    if int(trace[id][i][4].split(": ")[1]) == 0 or int(trace[id][i][4].split(": ")[1]) == 1:
                        if "ejection" not in request_latency.keys():
                            request_latency.setdefault("ejection", []).append(int(trace[id][i][5].split(": ")[1]) - cycle)
                        else:
                            request_latency["ejection"].append(int(trace[id][i][5].split(": ")[1]) - cycle)
            elif trace[id][i][0] == "reply received":
                if prev_step == "ejc rtr":
                    if int(trace[id][i][4].split(": ")[1]) == 2 or int(trace[id][i][4].split(": ")[1]) == 3:
                        if "ejection" not in reply_latency.keys():
                            reply_latency.setdefault("ejection", []).append(int(trace[id][i][5].split(": ")[1]) - cycle)
                        else:
                            reply_latency["ejection"].append(int(trace[id][i][5].split(": ")[1]) - cycle)
    req_cpp = {}
    rep_cpp = {}
    for step, values in request_latency.items():
        req_cpp[step] = np.mean(values)
    for step, values in reply_latency.items():
        rep_cpp[step] = np.mean(values)
    return req_cpp, rep_cpp


def mk_groups(data):
    try:
        newdata = data.items()
    except:
        return
    thisgroup = []
    groups = []
    for key, value in newdata:
        newgroups = mk_groups(value)
        if newgroups is None:
            thisgroup.append((key, value))
        else:
            thisgroup.append((key, len(newgroups[-1])))
            if groups:
                groups = [g + n for n, g in zip(newgroups, groups)]
            else:
                groups = newgroups
    return [thisgroup] + groups


def add_line(ax, xpos, ypos):
    line = plt.Line2D([xpos, xpos], [ypos + .1, ypos], transform=ax.transAxes, color='black')
    line.set_clip_on(False)
    ax.add_line(line)


def label_group_bar(ax, data):
    bench = []
    kernels = []
    injection = []
    link = []
    crossbar = []
    ejection = []
    for benchmark in data.keys():
        bench.append(benchmark)
        for kernel_num in data[benchmark].keys():
            kernels.append(kernel_num)
            for ptype in data[benchmark][kernel_num].keys():
                if ptype == "request":
                    for step, latency in data[benchmark][kernel_num][ptype].items():
                        if step == "injection":
                            injection.append(latency)
                        elif step == "link":
                            link.append(latency)
                        elif step == "crossbar":
                            crossbar.append(latency)
                        elif step == "ejection":
                            ejection.append(latency)
    xticks = range(1, len(kernels)+1)
    ax.bar(xticks, injection, align='center', color="blue", label="injection")
    ax.bar(xticks, link, bottom=injection, align='center', color="red", label="link")
    ax.bar(xticks, crossbar, bottom=link, align='center', color="yellow", label="crossbar")
    ax.bar(xticks, ejection, bottom=crossbar, align='center', color="black", label="ejection")
    ax.set_xticks(xticks)
    ax.set_xticklabels(kernels)
    ax.set_xlim(.2, len(kernels) + .2)
    ax.yaxis.grid(True)

    scale = 1. / len(kernels)
    ypos = -0.1
    pos = 0
    line_points = []
    for i in kernels:
        if i == 1:
            add_line(ax, pos * scale, ypos)
            line_points.append(pos)
        pos += 1
    line_points.append(pos)
    ypos = -12
    for i in range(len(line_points) - 1):
        first = line_points[i]
        second = line_points[i + 1]
        ax.text(((first + second) / 2) + 0.5, ypos, bench[i], ha='center')


if __name__ == "__main__":
    suits = benchlist.suits
    benchmarks = benchlist.benchmarks
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet_num = benchlist.chiplet_num
    path = benchlist.bench_path

    for suite in suits:
        if os.path.exists(path + suite) and suite == "parboil":
            data = {}
            for bench in benchmarks[suite]:
                if os.path.exists(path + suite + "/" + bench) and bench != "spmv":
                    for topo in topology:
                        for nv in ["NVLink4"]:
                            for ch in ["4chiplet"]:
                                file_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                                if os.path.exists(file_path):
                                    for file in os.listdir(file_path):
                                        if Path(file).suffix == ".txt":
                                            kernel_num = int(file.split(".")[0][-1])
                                            request_packet = {}
                                            file2 = open(file_path + file, "r")
                                            raw_content = ""
                                            if file2.mode == "r":
                                                raw_content = file2.readlines()
                                            file2.close()
                                            lined_list = []
                                            for line in raw_content:
                                                item = [x for x in line.split("\t") if x not in ['', '\t']]
                                                lined_list.append(item)
                                            del (raw_content)
                                            for i in range(len(lined_list)):
                                                if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
                                                    if lined_list[i] not in request_packet[
                                                        int(lined_list[i][3].split(": ")[1])]:
                                                        request_packet.setdefault(int(lined_list[i][3].split(": ")[1]),
                                                                                  []).append(lined_list[i])
                                                else:
                                                    request_packet.setdefault(int(lined_list[i][3].split(": ")[1]),
                                                                              []).append(lined_list[i])
                                            del (lined_list)
                                            gc.enable()
                                            gc.collect()
                                            req_CPP_stack, rep_CPP_stack = per_packet_analysis(request_packet)
                                            data.setdefault(bench, {}).setdefault(kernel_num, {})
                                            data[bench][kernel_num]["request"] = req_CPP_stack
                                            data[bench][kernel_num]["response"] = rep_CPP_stack
                                else:
                                    print(Fore.YELLOW + file_path + " is empty" + Fore.RESET)
            if len(data) != 0:
                for bench in data.keys():
                    data[bench] = dict(sorted(data[bench].items(), key=lambda x: x[0]))
            if len(data) != 0:
                fig = plt.figure(figsize=(20, 8))
                ax = fig.add_subplot(1, 1, 1)
                label_group_bar(ax, data)
                plt.title("CPP stack - " + suite + " benchmark suite")
                #plt.tight_layout()
                plt.legend()
                plt.savefig(benchlist.bench_path + suite + "/ClockPerPacket.jpg")