import gc
import os
import sys
sys.path.append("..")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from colorama import Fore
import benchlist
import sieve_benchmark


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


def bandwidth_sensitivity(path, suite, bench, ch):
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet = benchlist.chiplet_num
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


            path = benchlist.bench_path
            if not os.path.exists(path + suite + "/result/"):
                os.mkdir(path + suite + "/result/")
            if not os.path.exists(path + suite + "/result/" + ch):
                os.mkdir(path + suite + "/result/" + ch)
            path = path + suite + "/result/" + ch
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
                plt.savefig(path + "/bandwidth_ipc_total" + str(ch) + ".jpg")
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
                plt.savefig(path + "/bandwidth_throughput_total" + str(ch) + ".jpg")
                plt.close()


def kernel_sensitivity_test(ch):
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    benchmarks = benchlist.nominated_benchmarks
    path = benchlist.bench_path

    for suite in benchmarks.keys():
        for benchmark in benchmarks[suite]:
            data = {}
            if not os.path.exists(path + suite + "/" + benchmark + "/result/"):
                os.mkdir(path + suite + "/" + benchmark + "/result/")
            if not os.path.exists(path + suite + "/" + benchmark + "/result/" + ch):
                os.mkdir(path + suite + "/" + benchmark + "/result/" + ch + "/")
            if not os.path.exists(path + suite + "/" + benchmark + "/result/" + ch + "/per_kernel_sensitivity"):
                os.mkdir(path + suite + "/" + benchmark + "/result/" + ch + "/per_kernel_sensitivity/")
            for topo in topology:
                data.setdefault(topo, {})
                for nv in NVLink:
                    data[topo].setdefault(nv, {})
                    topol, NV, chip = determine_architecture(topo, nv, ch)
                    file_path = path + suite + "/" + benchmark + "/" + topo + "/" + nv + "/" + ch + "/"
                    file_name = suite + "-" + benchmark + "_NV" + str(NV) + "_1vc_" + str(chip) + "ch_" + topol + ".txt"
                    content = ""
                    with open(file_path + file_name, "r") as file:
                        content = file.readlines()
                    kernel_num = 0
                    ipc = 0
                    flag = 0
                    for line in content:
                        if "kernel_launch_uid" in line:
                            kernel_num = int(line.split(" = ")[1])
                            flag = 1
                        if "gpu_ipc" in line and flag == 1:
                            if "nan" not in line.split(" = ")[1]:
                                ipc = float(line.split(" = ")[1])
                        if "gpu_throughput" in line and flag == 1:
                            if "nan" not in line.split(" = ")[1]:
                                thrughtput = float(line.split(" = ")[1])
                                if kernel_num not in data[topo][nv].keys():
                                    data[topo][nv].setdefault(kernel_num, {})
                                data[topo][nv][kernel_num]["ipc"] = ipc
                                data[topo][nv][kernel_num]["throughput"] = thrughtput
                                flag = 0
            data = dict(sorted(data.items(), key=lambda x: x[0]))
            for topo in data.keys():
                data[topo] = dict(sorted(data[topo].items(), key=lambda x: x[0]))
                for nv in data[topo].keys():
                    data[topo][nv] = dict(sorted(data[topo][nv].items(), key=lambda x: x[0]))
            throghput = {}
            ipc = {}
            for topo in data.keys():
                for nv in data[topo].keys():
                    for kernel_num in data[topo][nv].keys():
                        if kernel_num not in throghput.keys():
                            throghput.setdefault(kernel_num, {}).setdefault(topo, {})
                            ipc.setdefault(kernel_num, {}).setdefault(topo, {})
                        else:
                            if topo not in throghput[kernel_num].keys():
                                throghput[kernel_num].setdefault(topo, {})
                            if topo not in ipc[kernel_num].keys():
                                ipc[kernel_num].setdefault(topo, {})
                        for key, value in data[topo][nv][kernel_num].items():
                            if key == "ipc":
                                ipc[kernel_num][topo][nv] = value
                            elif key == "throughput":
                                throghput[kernel_num][topo][nv] = value
            for kernel_num in ipc.keys():
                plt.figure(figsize=(10, 8))
                for topo in ipc[kernel_num].keys():
                    ipc[kernel_num] = dict(sorted(ipc[kernel_num].items(), key=lambda x: x[0]))
                    plt.plot(ipc[kernel_num][topo].keys(), ipc[kernel_num][topo].values(), marker="o", label=topo)
                plt.title("kernel " + str(kernel_num))
                plt.xlabel("Bandwidth")
                plt.ylabel("ipc")
                plt.legend()
                plt.tight_layout()
                plt.savefig(path + suite + "/" + benchmark + "/result/" + ch + "/per_kernel_sensitivity/bandwidth_ipc_kernel_" + str(kernel_num) + ".jpg")
                plt.close()

            for kernel_num in throghput.keys():
                plt.figure(figsize=(10, 8))
                for topo in throghput[kernel_num].keys():
                    throghput[kernel_num] = dict(sorted(throghput[kernel_num].items(), key=lambda x: x[0]))
                    plt.plot(throghput[kernel_num][topo].keys(), throghput[kernel_num][topo].values(), marker="o", label=topo)
                plt.title("kernel " + str(kernel_num))
                plt.xlabel("Bandwidth")
                plt.ylabel("throughput (byte/cycle)")
                plt.legend()
                plt.tight_layout()
                plt.savefig(path + suite + "/" + benchmark + "/result/" + ch + "/per_kernel_sensitivity/bandwidth_throughput_kernel_" + str(kernel_num) + ".jpg")
                plt.close()


def iat_sensitivity_test(ch):
    datasets = []
    for nv in benchlist.NVLink:
        sub_path = benchlist.bench_path + "burst_stats_" + nv + ".csv"
        datasets.append(pd.read_csv(sub_path))
    iat = {}
    for suite in benchlist.suits:
        for bench in benchlist.benchmarks[suite]:
            for topo in benchlist.topology:
                info = 0
                for nv in benchlist.NVLink:
                    if nv == "NVLink4":
                        info = datasets[0]
                    elif nv == "NVLink3":
                        info = datasets[1]
                    elif nv == "NVLink2":
                        info = datasets[2]
                    elif nv == "NVLink1":
                        info = datasets[3]
                    for i in info.index:
                        if info["suite"][i] == suite:
                            if info["benchmark"][i] == bench:
                                if sieve_benchmark.is_sensitivie(suite, bench, info["kernel"][i]):
                                    if suite not in iat.keys():
                                        iat.setdefault(suite, {}).setdefault(bench, {}).setdefault(info["kernel"][i],
                                                                                                   {}).setdefault(
                                            info["topology"][i], {})[nv] = info["IAT_mean"][i]
                                    else:
                                        if bench not in iat[suite].keys():
                                            iat[suite].setdefault(bench, {}).setdefault(
                                                info["kernel"][i], {}).setdefault(info["topology"][i], {})[nv] = \
                                                info["IAT_mean"][i]
                                        else:
                                            if info["kernel"][i] not in iat[suite][bench].keys():
                                                iat[suite][bench].setdefault(
                                                    info["kernel"][i], {}).setdefault(info["topology"][i], {})[nv] = \
                                                    info["IAT_mean"][i]
                                            else:
                                                if info["topology"][i] not in iat[suite][bench][
                                                    info["kernel"][i]].keys():
                                                    iat[suite][bench][info["kernel"][i]].setdefault(info["topology"][i],
                                                                                                    {})[nv] = \
                                                        info["IAT_mean"][i]
                                                else:
                                                    iat[suite][bench][info["kernel"][i]][info["topology"][i]][nv] = \
                                                    info["IAT_mean"][i]
        for suite in iat.keys():
            benchmark = []
            kernels = []
            topology = []
            nv4 = []
            nv3 = []
            nv2 = []
            nv1 = []
            for bench in iat[suite].keys():
                for kernel in iat[suite][bench].keys():
                    for topo in iat[suite][bench][kernel].keys():
                        benchmark.append(bench)
                        kernels.append(kernel)
                        topology.append(topo)
                        for nv, value in iat[suite][bench][kernel][topo].items():
                            if nv == "NVLink4":
                                nv4.append(value)
                            elif nv == "NVLink3":
                                nv3.append(value)
                            elif nv == "NVLink2":
                                nv2.append(value)
                            elif nv == "NVLink1":
                                nv1.append(value)
                benchmark.append(" ")
                kernels.append(" ")
                topology.append(" ")
                nv4.append(" ")
                nv3.append(" ")
                nv2.append(" ")
                nv1.append(" ")
            table = {"benchmark": benchmark, "kernels": kernels, "topology": topology, "NVLink4": nv4, "NVLink3": nv3,
                     "NVLink2": nv2, "NVLink1": nv1}
            df = pd.DataFrame(table,
                              columns=["benchmark", "kernels", "topology", "NVLink4", "NVLink3", "NVLink2", "NVLink1"])
            df.set_index(["benchmark", "kernels", "topology", "NVLink4"], inplace=True)
            df.to_csv(benchlist.bench_path + suite + "/result/" + ch + "/iat_sensitivity.csv", index=True)


def burst_volume_sensitivity_test(ch):
    datasets = []
    for nv in benchlist.NVLink:
        sub_path = benchlist.bench_path + "burst_stats_" + nv + ".csv"
        datasets.append(pd.read_csv(sub_path))
    iat = {}
    for suite in benchlist.suits:
        for bench in benchlist.benchmarks[suite]:
            for topo in benchlist.topology:
                info = 0
                for nv in benchlist.NVLink:
                    if nv == "NVLink4":
                        info = datasets[0]
                    elif nv == "NVLink3":
                        info = datasets[1]
                    elif nv == "NVLink2":
                        info = datasets[2]
                    elif nv == "NVLink1":
                        info = datasets[3]
                    for i in info.index:
                        if info["suite"][i] == suite:
                            if info["benchmark"][i] == bench:
                                if sieve_benchmark.is_sensitivie(suite, bench, info["kernel"][i]):
                                    if suite not in iat.keys():
                                        iat.setdefault(suite, {}).setdefault(bench, {}).setdefault(info["kernel"][i],
                                                                                                   {}).setdefault(
                                            info["topology"][i], {})[nv] = info["vol_mean"][i]
                                    else:
                                        if bench not in iat[suite].keys():
                                            iat[suite].setdefault(bench, {}).setdefault(
                                                info["kernel"][i], {}).setdefault(info["topology"][i], {})[nv] = \
                                                info["vol_mean"][i]
                                        else:
                                            if info["kernel"][i] not in iat[suite][bench].keys():
                                                iat[suite][bench].setdefault(
                                                    info["kernel"][i], {}).setdefault(info["topology"][i], {})[nv] = \
                                                    info["vol_mean"][i]
                                            else:
                                                if info["topology"][i] not in iat[suite][bench][
                                                    info["kernel"][i]].keys():
                                                    iat[suite][bench][info["kernel"][i]].setdefault(info["topology"][i],
                                                                                                    {})[nv] = \
                                                        info["vol_mean"][i]
                                                else:
                                                    iat[suite][bench][info["kernel"][i]][info["topology"][i]][nv] = \
                                                    info["vol_mean"][i]
        for suite in iat.keys():
            benchmark = []
            kernels = []
            topology = []
            nv4 = []
            nv3 = []
            nv2 = []
            nv1 = []
            for bench in iat[suite].keys():
                for kernel in iat[suite][bench].keys():
                    for topo in iat[suite][bench][kernel].keys():
                        benchmark.append(bench)
                        kernels.append(kernel)
                        topology.append(topo)
                        for nv, value in iat[suite][bench][kernel][topo].items():
                            if nv == "NVLink4":
                                nv4.append(value)
                            elif nv == "NVLink3":
                                nv3.append(value)
                            elif nv == "NVLink2":
                                nv2.append(value)
                            elif nv == "NVLink1":
                                nv1.append(value)
                benchmark.append(" ")
                kernels.append(" ")
                topology.append(" ")
                nv4.append(" ")
                nv3.append(" ")
                nv2.append(" ")
                nv1.append(" ")
            table = {"benchmark": benchmark, "kernels": kernels, "topology": topology, "NVLink4": nv4, "NVLink3": nv3,
                     "NVLink2": nv2, "NVLink1": nv1}
            df = pd.DataFrame(table,
                              columns=["benchmark", "kernels", "topology", "NVLink4", "NVLink3", "NVLink2", "NVLink1"])
            df.set_index(["benchmark", "kernels", "topology", "NVLink4"], inplace=True)
            df.to_csv(benchlist.bench_path + suite + "/result/" + ch + "/burst_volume_sensitivity.csv", index=True)


def burst_length_sensitivity_test(ch):
    datasets = []
    for nv in benchlist.NVLink:
        sub_path = benchlist.bench_path + "burst_stats_" + nv + ".csv"
        datasets.append(pd.read_csv(sub_path))
    iat = {}
    for suite in benchlist.suits:
        for bench in benchlist.benchmarks[suite]:
            for topo in benchlist.topology:
                info = 0
                for nv in benchlist.NVLink:
                    if nv == "NVLink4":
                        info = datasets[0]
                    elif nv == "NVLink3":
                        info = datasets[1]
                    elif nv == "NVLink2":
                        info = datasets[2]
                    elif nv == "NVLink1":
                        info = datasets[3]
                    for i in info.index:
                        if info["suite"][i] == suite:
                            if info["benchmark"][i] == bench:
                                if sieve_benchmark.is_sensitivie(suite, bench, info["kernel"][i]):
                                    if suite not in iat.keys():
                                        iat.setdefault(suite, {}).setdefault(bench, {}).setdefault(info["kernel"][i],
                                                                                                   {}).setdefault(
                                            info["topology"][i], {})[nv] = info["dur_mean"][i]
                                    else:
                                        if bench not in iat[suite].keys():
                                            iat[suite].setdefault(bench, {}).setdefault(
                                                info["kernel"][i], {}).setdefault(info["topology"][i], {})[nv] = \
                                                info["dur_mean"][i]
                                        else:
                                            if info["kernel"][i] not in iat[suite][bench].keys():
                                                iat[suite][bench].setdefault(
                                                    info["kernel"][i], {}).setdefault(info["topology"][i], {})[nv] = \
                                                    info["dur_mean"][i]
                                            else:
                                                if info["topology"][i] not in iat[suite][bench][
                                                    info["kernel"][i]].keys():
                                                    iat[suite][bench][info["kernel"][i]].setdefault(info["topology"][i],
                                                                                                    {})[nv] = \
                                                        info["dur_mean"][i]
                                                else:
                                                    iat[suite][bench][info["kernel"][i]][info["topology"][i]][nv] = \
                                                    info["dur_mean"][i]
        for suite in iat.keys():
            benchmark = []
            kernels = []
            topology = []
            nv4 = []
            nv3 = []
            nv2 = []
            nv1 = []
            for bench in iat[suite].keys():
                for kernel in iat[suite][bench].keys():
                    for topo in iat[suite][bench][kernel].keys():
                        benchmark.append(bench)
                        kernels.append(kernel)
                        topology.append(topo)
                        for nv, value in iat[suite][bench][kernel][topo].items():
                            if nv == "NVLink4":
                                nv4.append(value)
                            elif nv == "NVLink3":
                                nv3.append(value)
                            elif nv == "NVLink2":
                                nv2.append(value)
                            elif nv == "NVLink1":
                                nv1.append(value)
                benchmark.append(" ")
                kernels.append(" ")
                topology.append(" ")
                nv4.append(" ")
                nv3.append(" ")
                nv2.append(" ")
                nv1.append(" ")
            table = {"benchmark": benchmark, "kernels": kernels, "topology": topology, "NVLink4": nv4, "NVLink3": nv3,
                     "NVLink2": nv2, "NVLink1": nv1}
            df = pd.DataFrame(table,
                              columns=["benchmark", "kernels", "topology", "NVLink4", "NVLink3", "NVLink2", "NVLink1"])
            df.set_index(["benchmark", "kernels", "topology", "NVLink4"], inplace=True)
            df.to_csv(benchlist.bench_path + suite + "/result/" + ch + "/burst_length_sensitivity.csv", index=True)


if __name__ == "__main__":
    kernel_sensitivity_test()
