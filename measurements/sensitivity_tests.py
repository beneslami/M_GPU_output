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
    data = {}
    for length in queue_length:
        q_path = path + "/" + str(length) + "/" + bench_name
        latency = {}
        for vc in vc_num:
            vc_file = q_path + "_" + str(vc) + "vc_" + str(length) + ".txt"
            content = ""
            temp_latency = {}
            with open(vc_file, "r") as file:
                content = file.readlines()
            flag = 0
            flag2 = 0
            kernel_num = -1
            for line in content:
                if "-kernel id" in line:
                    kernel_num = int(line.split(" = ")[1])
                    flag = 1
                if "chLet-DETAILS" in line and flag == 1:
                    flag2 = 1
                if flag2 == 1:
                    if "Packet latency average" in line and flag == 1:
                        temp_latency[kernel_num] = float(line.split(" = ")[1])
                        flag = 0
                        flag2 = 0

            if vc not in latency.keys():
                latency[vc] = temp_latency
            else:
                for ker in temp_latency.keys():
                    latency[vc][ker] = temp_latency[ker]
        data[length] = latency
    data = dict(sorted(data.items(), key=lambda x: x[0]))
    for l in data.keys():
        data[l] = dict(sorted(data[l].items(), key=lambda x: x[0]))

    kernels_list = list(data[32][1].keys())
    kernels_list.sort()
    vc_list = list(data[32].keys())
    vc_list.sort()
    q_list = list(data.keys())
    q_list.sort()
    if not os.path.exists(path + "/figures/"):
        os.mkdir(path + "/figures/")
    plt.figure(figsize=(10, 10))
    for k in kernels_list:
        for vc in vc_list:
            temp = []
            for length in q_list:
                temp.append(data[length][vc][k])
            plt.plot(q_list, temp, marker="o", label=str(vc) + " vc")
        plt.title("kernel " + str(k))
        plt.xticks(q_list)
        plt.ylabel("packet latency")
        plt.xlabel("queue length")
        plt.tight_layout()
        plt.savefig(path + "/figures/latency_kernel_" + str(k) + ".jpg")
        plt.close()
    gc.enable()
    gc.collect()


def ipc_sensitivity_test(path):
    bench_name = path.split("/")[-1]
    vc_num = vc_lengths(path)
    queue_length = queue_lengths(path)
    data = {}
    for length in queue_length:
        q_path = path + "/" + str(length) + "/" + bench_name
        vc_ipc = {}
        for vc in vc_num:
            vc_file = q_path + "_" + str(vc) + "vc_" + str(length) + ".txt"
            content = ""
            temp_ipc = {}
            with open(vc_file, "r") as file:
                content = file.readlines()
            kernel_num = -1
            flag = 0
            for line in content:
                if "kernel_launch_uid" in line:
                    try:
                        int(line.split(" = ")[1])
                    except:
                        continue
                    else:
                        kernel_num = int(line.split(" = ")[1])
                        flag = 1
                if "gpu_sim_cycle" in line and flag == 1:
                    if "nan" not in line:
                        temp_ipc[kernel_num] = int(line.split(" = ")[1])
                        flag = 0
                    else:
                        continue
            if vc not in vc_ipc.keys():
                vc_ipc[vc] = temp_ipc
            else:
                for k, num in temp_ipc.items():
                    vc_ipc[vc][k] = num
        data[length] = vc_ipc
    data = dict(sorted(data.items(), key=lambda x: x[0]))
    for length in data.keys():
        data[length] = dict(sorted(data[length].items(), key=lambda x: x[0]))
    kernels_list = list(data[32][1].keys())
    kernels_list.sort()
    vc_list = list(data[32].keys())
    vc_list.sort()
    q_list = list(data.keys())
    q_list.sort()
    if not os.path.exists(path + "/figures/"):
        os.mkdir(path + "/figures/")
    for k in kernels_list:
        plt.figure(figsize=(10, 10))
        for vc in vc_list:
            temp = []
            for length in q_list:
                temp.append(data[length][vc][k])
            plt.plot(q_list, temp, marker="o", label=str(vc) + " vc")
        plt.title("kernel " + str(k))
        plt.xticks(q_list)
        plt.ylabel("IPC")
        plt.xlabel("queue length")
        plt.legend()
        plt.tight_layout()
        plt.savefig(path + "/figures/ipc_kernel_" + str(k) + ".jpg")
        plt.close()

    for k in kernels_list:
        fig, ax = plt.subplots(layout='constrained')
        width = 0.25
        multiplier = 0
        x_tick = list(data.keys())
        x = np.arange(len(x_tick))
        for vc in vc_list:
            temp = []
            for length in q_list:
                temp.append(data[length][vc][k])
            offset = width * multiplier
            col = ""
            if vc == 1:
                col = "black"
            elif vc == 4:
                col = "yellow"
            elif vc == 8:
                col = "red"
            ax.bar(x + offset, temp, width, color=col, label=str(vc) + " vc")
            multiplier += 1
        ax.set_xlabel("queue length")
        ax.set_ylabel('ipc')
        ax.set_title("kernel " + str(k))
        ax.set_xticks(x + width, x_tick)
        ax.legend()
        plt.tight_layout()
        plt.savefig(path + "/figures/ipc2_kernel_" + str(k) + ".jpg")
        plt.close()

    gc.enable()
    gc.collect()


def throughput_sensitivity(path):
    bench_name = path.split("/")[-1]
    vc_num = vc_lengths(path)
    queue_length = queue_lengths(path)
    data = {}
    for length in queue_length:
        q_path = path + "/" + str(length) + "/" + bench_name
        throughput = {}
        for vc in vc_num:
            vc_file = q_path + "_" + str(vc) + "vc_" + str(length) + ".txt"
            content = ""
            with open(vc_file, "r") as file:
                content = file.readlines()
            temp_throughput = {}
            kernel_num = -1
            for line in content:
                if "kernel_launch_uid" in line:
                    try:
                        int(line.split(" = ")[1])
                    except:
                        continue
                    else:
                        kernel_num = int(line.split(" = ")[1])
                if "gpu_throughput" in line:
                    temp_throughput[kernel_num] = float(line.split(" = ")[1])

            if vc not in throughput.keys():
                throughput[vc] = temp_throughput
            else:
                for k, th in temp_throughput.keys():
                    throughput[vc][k] = th
        data[length] = throughput

    data = dict(sorted(data.items(), key=lambda x: x[0]))
    for length in data.keys():
        data[length] = dict(sorted(data[length].items(), key=lambda x: x[0]))
    kernels_list = list(data[32][1].keys())
    kernels_list.sort()
    vc_list = list(data[32].keys())
    vc_list.sort()
    q_list = list(data.keys())
    q_list.sort()
    if not os.path.exists(path + "/figures/"):
        os.mkdir(path + "/figures/")
    for k in kernels_list:
        plt.figure(figsize=(10, 10))
        for vc in vc_list:
            temp = []
            for length in q_list:
                temp.append(data[length][vc][k])
            plt.plot(q_list, temp, marker="o", label=str(vc) + " vc")
        plt.title("kernel " + str(k))
        plt.xticks(q_list)
        plt.ylabel("throughput(byte/cycle)")
        plt.xlabel("queue length")
        plt.legend()
        plt.tight_layout()
        plt.savefig(path + "/figures/throughput_kernel_" + str(k) + ".jpg")
        plt.close()

    gc.enable()
    gc.collect()


def bandwidth_sensitivity(path, suite, bench):
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet = benchlist.chiplet_num
    for ch in chiplet:
        if ch == "4chiplet":
            bandwidth_ipc = {}
            bandwidth_throughput = {}
            for topo in topology:
                for nv in NVLink:
                    topol, NV, chipNum = determine_architecture(topo, nv, ch)
                    sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/"
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

            path += suite + "/" + bench

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