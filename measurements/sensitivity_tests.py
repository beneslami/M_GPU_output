import gc
import os
import matplotlib.pyplot as plt
import numpy as np
from colorama import Fore
import benchlist


def determine_architecture(topo, nv, ch):
    topol = ""
    chipNum = -1
    NV = -1
    if topo == "torus":
        topol = "2Dtorus"
    elif topo == "ring":
        topol = "ring"
    elif topo == "mesh":
        topol = "2Dmesh"
    elif topo == "fly":
        if ch == "4chiplet" or ch == "8chiplet":
            topol = "1fly"
        else:
            topol = "2fly"
    if ch == "4chiplet":
        chipNum = 4
    elif ch == "8chiplet":
        chipNum = 8
    elif ch == "16chiplet":
        chipNum = 16
    if nv == "NVLink4":
        NV = 4
    elif nv == "NVLink3":
        NV = 3
    elif nv == "NVLink2":
        NV = 2
    elif nv == "NVLink1":
        NV = 1
    return topol, NV, chipNum


def queue_lengths(path):
    queue = []
    for file in os.listdir(path):
        if file.title().isdecimal():
            queue.append(int(file.title()))
    return queue


def vc_lengths(path):
    vc = []
    for dirs in os.listdir(path):
        for file in os.listdir(path + "/" + dirs):
            items = file.split("_")
            for item in items:
                if "vc" in item:
                    num = int(item[0])
                    if num not in vc:
                        vc.append(num)
    vc.sort()
    return vc


def latency_sensitivity_test(path):
    bench_name = path.split("/")[-1]
    vc_num = vc_lengths(path)
    queue_length = queue_lengths(path)
    latency = {}
    for length in queue_length:
        q_path = path + "/" + str(length) + "/" + bench_name
        for vc in vc_num:
            vc_file = q_path + "_" + str(vc) + "vc_" + str(length) + ".txt"
            content = ""
            temp_latency = []
            ipc = []
            with open(vc_file, "r") as file:
                content = file.readlines()
            for line in content:
                if "Packet latency average" in line and "samples)" in line:
                    temp_latency.append(float(line.split(" = ")[1].split(" (")[0]))
            if vc not in latency.keys():
                latency.setdefault(vc, {})[length] = temp_latency[-1]
            else:
                if length not in latency[vc].keys():
                    latency[vc][length] = temp_latency[-1]

    for vc in latency.keys():
        plt.plot(list(latency[vc].keys()), list(latency[vc].values()), marker="o", label=str(vc) + " vc")
    plt.xticks(list(latency[list(latency)[0]].keys()))
    plt.xlabel("Queue length")
    plt.ylabel("latency")
    plt.title(bench_name + " latency sensitivity")
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()

    gc.enable()
    gc.collect()


def ipc_sensitivity_test(path):
    bench_name = path.split("/")[-1]
    vc_num = vc_lengths(path)
    queue_length = queue_lengths(path)
    ipc = {}
    for length in queue_length:
        q_path = path + "/" + str(length) + "/" + bench_name
        for vc in vc_num:
            vc_file = q_path + "_" + str(vc) + "vc_" + str(length) + ".txt"
            content = ""
            temp_ipc = []
            with open(vc_file, "r") as file:
                content = file.readlines()
            for line in content:
                if "gpu_ipc" in line:
                    temp_ipc.append(float(line.split(" = ")[1]))
            if vc not in ipc.keys():
                ipc.setdefault(vc, {})[length] = np.mean(temp_ipc)
            else:
                if length not in ipc[vc].keys():
                    ipc[vc][length] = np.mean(temp_ipc)

    for vc in ipc.keys():
        plt.plot(list(ipc[vc].keys()), list(ipc[vc].values()), marker="o", label=str(vc) + " vc")
    plt.xticks(list(ipc[list(ipc)[0]].keys()))
    plt.xlabel("Queue length")
    plt.ylabel("ipc")
    plt.title(bench_name + " ipc sensitivity")
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()

    x_tick = ipc[list(ipc.keys())[0]].keys()
    data = {}
    for vc in ipc.keys():
        for queue, value in ipc[vc].items():
            if vc not in data.keys():
                data.setdefault(vc, []).append(value)
            else:
                data[vc].append(value)
    x = np.arange(len(x_tick))
    width = 0.25
    multiplier = 0
    fig, ax = plt.subplots(layout='constrained')
    for attribute, measurement in data.items():
        offset = width * multiplier
        col = ""
        if attribute == 1:
            col = "black"
        elif attribute == 4:
            col = "yellow"
        elif attribute == 8:
            col = "red"
        ax.bar(x + offset, measurement, width, color=col, label=str(attribute) + " vc")
        multiplier += 1

    ax.set_xlabel("queue length")
    ax.set_ylabel('ipc')
    ax.set_title('parboil-spmv relative IPC')
    ax.set_xticks(x + width, x_tick)
    ax.legend()
    plt.show()

    gc.enable()
    gc.collect()


def throughput_sensitivity(path):
    bench_name = path.split("/")[-1]
    vc_num = vc_lengths(path)
    queue_length = queue_lengths(path)
    throughput = {}
    for length in queue_length:
        q_path = path + "/" + str(length) + "/" + bench_name
        for vc in vc_num:
            vc_file = q_path + "_" + str(vc) + "vc_" + str(length) + ".txt"
            content = ""
            temp_thr = []
            with open(vc_file, "r") as file:
                content = file.readlines()
            duration = -1
            tot_cycle = 0
            partial_sum = 0
            for line in content:
                if "gpu_sim_cycle" in line:
                    duration = int(line.split(" = ")[1])
                    tot_cycle += duration
                if "gpu_throughput" in line:
                    partial_sum += float(line.split(" = ")[1])*duration
                    temp_thr.append(float(line.split(" = ")[1]))
            if vc not in throughput.keys():
                throughput.setdefault(vc, {})[length] = partial_sum/tot_cycle
            else:
                if length not in throughput[vc].keys():
                    throughput[vc][length] = partial_sum/tot_cycle
    for vc in throughput.keys():
        plt.plot(list(throughput[vc].keys()), list(throughput[vc].values()), marker="o", label=str(vc) + " vc")
    plt.xticks(list(throughput[list(throughput)[0]].keys()))
    plt.xlabel("Queue length")
    plt.ylabel("throughput (byte/cycle)")
    plt.title(bench_name + " throughput sensitivity")
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.close()

    gc.enable()
    gc.collect()


def bandwidth_sensitivity(path, suite, bench):
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet = benchlist.chiplet_num
    for ch in chiplet:
        bandwidth_ipc = {}
        bandwidth_throughput = {}
        for topo in topology:
            for nv in NVLink:
                topol, NV, chipNum = determine_architecture(topo, nv, ch)
                sub_path = path + topo + "/" + nv + "/" + ch + "/"
                file_name = suite + "-" + bench + "_NV" + str(NV) + "_1vc_" + str(chipNum) + "ch_" + topol + ".txt"
                if len(os.listdir(os.path.dirname(sub_path))) != 0:
                    content = ""
                    with open(sub_path + file_name, "r") as file:
                        content = file.readlines()
                    duration = -1
                    tot_cycle = 0
                    partial_sum = 0
                    ipc = []
                    for line in content:
                        if "gpu_ipc" in line:
                            if "nan" not in line.split(" = ")[1]:
                                ipc.append(float(line.split(" = ")[1]))
                        elif "gpu_sim_cycle" in line:
                            duration = int(line.split(" = ")[1])
                            tot_cycle += duration
                        elif "gpu_throughput" in line:
                            if "nan" not in line.split(" = ")[1]:
                                partial_sum += float(line.split(" = ")[1]) * duration
                    if topo not in bandwidth_ipc.keys():
                        bandwidth_ipc.setdefault(topo, {})[nv] = np.mean(ipc)
                    else:
                        bandwidth_ipc[topo][nv] = np.mean(ipc)
                    if topo not in bandwidth_throughput.keys():
                        bandwidth_throughput.setdefault(topo, {})[nv] = partial_sum/tot_cycle
                    else:
                        bandwidth_throughput[topo][nv] = partial_sum/tot_cycle
                else:
                    print(Fore.YELLOW + "directory " + sub_path + " is empty" + Fore.WHITE)

        for topo in bandwidth_ipc.keys():
            bandwidth_ipc[topo] = dict(sorted(bandwidth_ipc[topo].items(), key=lambda x: x[0]))
        if len(bandwidth_ipc) != 0:
            plt.figure(figsize=(10, 7))
            for topo in bandwidth_ipc.keys():
                plt.plot(list(bandwidth_ipc[topo].keys()), list(bandwidth_ipc[topo].values()), marker="o", label=topo)
            plt.xlabel("Bandwidth")
            plt.ylabel("ipc")
            plt.title(suite + "-" + bench + " bandwidth/ipc sensitivity")
            plt.tight_layout()
            plt.legend()
            plt.savefig(path + "/bandwidth_ipc_" + str(ch) + ".jpg")
            plt.close()

        for topo in bandwidth_throughput.keys():
            bandwidth_throughput[topo] = dict(sorted(bandwidth_throughput[topo].items(), key=lambda x: x[0]))
        if len(bandwidth_throughput) != 0:
            plt.figure(figsize=(10, 7))
            for topo in bandwidth_throughput.keys():
                plt.plot(list(bandwidth_throughput[topo].keys()), list(bandwidth_throughput[topo].values()), marker="o", label=topo)
            plt.xlabel("Bandwidth")
            plt.ylabel("throughput(byte/cycle/chiplet)")
            plt.title(suite + "-" + bench + " bandwidth/throughput sensitivity")
            plt.legend()
            plt.tight_layout()
            plt.savefig(path + "/bandwidth_throughput_" + str(ch) + ".jpg")
            plt.close()


def kernel_sensitivity_test(): # number of remote request per kilo instruction
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet = benchlist.chiplet_num
    benchmarks = benchlist.nominated_benchmarks
    path = benchlist.bench_path
    benchmark_data = {}
    for suite in benchmarks.keys():
        if suite == "pannotia":
            for benchmark in benchmarks[suite]:
                if benchmark == "pagerank":
                    for topo in topology:
                        if topo == "torus":
                            for nv in NVLink:
                                if nv == "NVLink4":
                                    kernel_num = 0
                                    for ch in chiplet:
                                        if ch == "4chiplet":
                                            topol, NV, chip = determine_architecture(topo, nv, ch)
                                            file_path = path + suite + "/" + benchmark + "/" + topo + "/" + nv + "/" + ch + "/"
                                            file_name = suite + "-" + benchmark + "_NV" + str(NV) + "_1vc_" + str(chip) + "ch_" + topol + ".txt"
                                            content = ""
                                            with open(file_path + file_name, "r") as file:
                                                content = file.readlines()
                                            remote_req = -1
                                            instructions = -1
                                            for line in content:
                                                if "Hossein: Number of Remote Requests" in line:
                                                    remote_req = int(line.split(": ")[2])
                                                if "gpu_tot_sim_insn" in line:
                                                    if "nan" not in line.split(" = ")[1]:
                                                        instructions = int(line.split(" = ")[1])
                                            if remote_req != -1 and instructions != -1 and instructions != 0:
                                                ratio = (remote_req / instructions)*100
                                                if suite not in benchmark_data.keys():
                                                    benchmark_data.setdefault(suite, {})[benchmark] = ratio
                                                else:
                                                    if benchmark not in benchmark_data[suite].keys():
                                                        benchmark_data[suite][benchmark] = ratio

    for suite in benchmark_data.keys():
        print(suite)
        for bench, ratio in benchmark_data[suite].items():
            print("\t" + bench + " -> " + str(ratio))


if __name__ == "__main__":
    kernel_sensitivity_test()