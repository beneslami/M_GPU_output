import csv
import pandas as pd
import matplotlib.pyplot as plt
from hurst import compute_Hc


chiplet = []
chiplet_0 = dict(
    SM_ID=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
           28, 29, 30, 31],
    LLC_ID=[128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143], port=192)

chiplet_1 = dict(
    SM_ID=[32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
           59, 60, 61, 62, 63],
    LLC_ID=[144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159], port=193)

chiplet_2 = dict(
    SM_ID=[64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
           91, 92, 93, 94, 95],
    LLC_ID=[160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175], port=194)

chiplet_3 = dict(
    SM_ID=[96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117,
           118, 119, 120, 121, 122, 123, 124, 125, 126, 127],
    LLC_ID=[176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191], port=195)

chiplet.append(chiplet_0)
chiplet.append(chiplet_1)
chiplet.append(chiplet_2)
chiplet.append(chiplet_3)

per_core = {0: {}, 1: {}, 2: {}, 3: {}}
per_core_update = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
traffic_flow = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
injection_rate = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}


def chip_select(num):
    out = -1
    for i in range(len(chiplet)):
        if num in chiplet[i]["SM_ID"]:
            out = i
            break
        if num in chiplet[i]["LLC_ID"]:
            out = i
            break
        if num == chiplet[i]["port"]:
            out = i
            break
    return out


def check_local_or_remote(x):  # 0 for local, 1 for remote
    """for i in range(len(chiplet)):
        if (int(x[1].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[1].split(": ")[1]) in chiplet[i]["LLC_ID"]):
            if (int(x[2].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[2].split(": ")[1]) in chiplet[i]["LLC_ID"]):
                return 0
        return 1"""
    if int(x[1].split(": ")[1]) >= 192 or int(x[1].split(": ")[1]) <= 195:
        if int(x[2].split(": ")[1]) >= 192 or int(x[2].split(": ")[1]) <= 195:
            return 1
    return 0


def hurst():
    out = {0: {}, 1: {}, 2: {}, 3: {}}
    for core in per_core_update.keys():
        for dest in per_core_update[core].keys():
            for cycle, byte in per_core_update[core][dest].items():
                s = sum(byte)
                if cycle not in out[core].keys():
                    out[core][cycle] = s
                else:
                    out[core][cycle] += s

    H_192, c_192, data_192 = compute_Hc(list(out[0].values()))
    H_193, c_193, data_193 = compute_Hc(list(out[1].values()))
    H_194, c_194, data_194 = compute_Hc(list(out[2].values()))
    H_195, c_195, data_195 = compute_Hc(list(out[3].values()))

    f, ax = plt.subplots(2, 2, figsize=(12, 12))
    ax[0, 0].plot(data_192[0], c_192 * data_192[0] ** H_192, color="deepskyblue")
    ax[0, 0].scatter(data_192[0], data_192[1], color="purple")
    ax[0, 0].set_xscale('log')
    ax[0, 0].set_yscale('log')
    ax[0, 0].text(100, 2, "slope = " + str("{:.3f}".format(H_192)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax[0, 0].set_title("core 0")

    ax[0, 1].plot(data_193[0], c_193 * data_193[0] ** H_193, color="deepskyblue")
    ax[0, 1].scatter(data_193[0], data_193[1], color="purple")
    ax[0, 1].set_xscale('log')
    ax[0, 1].set_yscale('log')
    ax[0, 1].text(200, 2, "slope = " + str("{:.3f}".format(H_193)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax[0, 1].set_title("core 1")

    ax[1, 0].plot(data_194[0], c_194 * data_194[0] ** H_194, color="deepskyblue")
    ax[1, 0].scatter(data_194[0], data_194[1], color="purple")
    ax[1, 0].set_xscale('log')
    ax[1, 0].set_yscale('log')
    ax[1, 0].text(100, 2, "slope = " + str("{:.3f}".format(H_194)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax[1, 0].set_title("core 2")

    ax[1, 1].plot(data_195[0], c_195 * data_195[0] ** H_195, color="deepskyblue")
    ax[1, 1].scatter(data_195[0], data_195[1], color="purple")
    ax[1, 1].set_xscale('log')
    ax[1, 1].set_yscale('log')
    ax[1, 1].text(100, 2, "slope = " + str("{:.3f}".format(H_195)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax[1, 1].set_title("core 3")
    plt.show()


def plot_core_traffic(dir):
    global per_core
    global per_core_update
    global traffic_flow
    flag = 0
    prev = 0
    cycle = 0
    for core in range(0, 4):
        for dest in range(0, 4):
            if core != dest:
                file2 = open(dir + "pre_" + str(core) + "_" + str(dest) + ".txt", "r")
                raw_content = ""
                if file2.mode == "r":
                    raw_content = file2.readlines()
                for line in raw_content:
                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                    if flag == 0:
                        prev = int(item[0])
                        cycle = 1
                        flag = 1
                    elif flag == 1:
                        cycle += int(item[0]) - prev
                        prev = int(item[0])
                    byte_list = item[1][1:][:-2].split(", ")
                    temp = []
                    for byte in byte_list:
                        temp.append(int(byte))
                    if cycle not in per_core[core].keys():
                        per_core[core][cycle] = sum(temp)
                        per_core_update[core][dest][cycle] = sum(temp)
                    else:
                        per_core[core][cycle] += sum(temp)
                    if cycle not in per_core_update[core][dest].keys():
                        per_core_update[core][dest][cycle] = sum(temp)
                    else:
                        per_core_update[core][dest][cycle] += sum(temp)
                    traffic_flow[core][dest] += sum(temp)
    del(per_core)
    del(traffic_flow)
    """fig, ax = plt.subplots(4, 1, figsize=(20, 8))
    ax[0].bar(list(per_core[0].keys()), list(per_core[0].values()), width=4, label="core0")
    ax[1].bar(list(per_core[1].keys()), list(per_core[1].values()), width=4, label="core1")
    ax[2].bar(list(per_core[2].keys()), list(per_core[2].values()), width=4, label="core2")
    ax[3].bar(list(per_core[3].keys()), list(per_core[3].values()), width=4, label="core3")
    plt.xlabel("Cycle")
    plt.ylabel("byte")
    plt.show()"""


def calculate_injection_rate(dir):
    off = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    total_off = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    pair_core_update = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    temp = {0: {}, 1: {}, 2: {}, 3: {}}
    off_2 = {0: 0, 1: 0, 2: 0, 3: 0}
    total_2 = {0: 0, 1: 0, 2: 0, 3: 0}
    injection_rate_2 = {0: 0, 1: 0, 2: 0, 3: 0}
    flag = prev = 0
    for source in per_core_update.keys():
        for dest in per_core_update[source].keys():
            for cyc in per_core_update[source][dest].keys():
                if flag == 0:
                    pair_core_update[source][dest][cyc] = per_core_update[source][dest][cyc]
                    temp[source].setdefault(cyc, []).append(per_core_update[source][dest][cyc])
                    prev = cyc
                    flag = 1
                elif flag == 1:
                    if cyc - prev > 1:
                        for k in range(prev + 1, cyc):
                            pair_core_update[source][dest].setdefault(k, []).append(0)
                            temp[source].setdefault(k, []).append(0)
                    temp[source].setdefault(cyc, []).append(per_core_update[source][dest][cyc])
                    prev = cyc

    """for core in pair_core_update.keys():
        for dest in pair_core_update[core].keys():
            for cyc in pair_core_update[core][dest].keys():
                if not(isinstance(pair_core_update[core][dest][cyc], int)) and pair_core_update[core][dest][cyc][0] == 0:
                    off[core][dest] += 1
                total_off[core][dest] += 1"""

    for core in temp.keys():
        for cyc in temp[core].keys():
            if not (isinstance(temp[core][cyc], int)) and temp[core][cyc][0] == 0 and len(temp[core][cyc]) == 1:
                off_2[core] += 1
            total_2[core] += 1

    for core in temp.keys():
        try:
            injection_rate_2[core] = 1 - (off_2[core] / total_2[core])
        except ZeroDivisionError:
            continue

    print(injection_rate_2)
    """for core in pair_core_update.keys():
        for dest in pair_core_update[core].keys():
            try:
                injection_rate[core][dest] = 1 - (off[core][dest] / total_off[core][dest])
            except ZeroDivisionError:
                continue

    with open(dir + "injection_rate.txt", "w") as file:
        for core in injection_rate.keys():
            file.write("core: " + str(core) + "\n")
            for dest in injection_rate[core].keys():
                file.write(str(dest) + ": " + str(injection_rate[core][dest]) + "\n")
            file.write("\n")"""


def calculate_link_usage(dir):
    link_usage = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    for i in range(0, 4):
        for j in range(0, 4):
            if i != j:
                with open(dir + "link_usage" + str(i) + "_" + str(j) + "_per_cycle.txt", "r") as file:
                    raw_content = ""
                    if file.mode == "r":
                        raw_content = file.readlines()
                for line in raw_content:
                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                    cycle = int(item[0])
                    byte_list = item[1][1:][:-2].split(", ")
                    temp = []
                    for byte in byte_list:
                        temp.append(int(byte))
                    if cycle not in link_usage[i][j].keys():
                        link_usage[i][j][cycle] = sum(temp)
                    else:
                        link_usage[i][j][cycle] += sum(temp)
    l = []
    l.append(list(link_usage[0].values()))
    l.append(list(link_usage[1].values()))
    l.append(list(link_usage[2].values()))
    l.append(list(link_usage[3].values()))
    for src in link_usage.keys():
        for dest in link_usage[src].keys():
            with open(dir + "link_usage" + str(src) + str(dest) + ".txt", "w") as file:
                for cyc, byte in link_usage[src][dest].items():
                    file.write((str(byte)) + "\n")


def calculate_traffic_flow(dir):
    with open(dir + "traffic_flow.txt", "w") as file:
        for src in traffic_flow.keys():
            file.write("source: " + str(src) + "\n")
            for dest in traffic_flow[src].keys():
                file.write(str(dest) + " -> " + str(traffic_flow[src][dest]) + "\n")


def calculate_network_latency_distribution(dir):
    network_latency = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    for i in range(0, 4):
        for j in range(0, 4):
            if i != j:
                with open(dir + "network_latency_" + str(i) + "_" + str(j) + ".txt", "r") as file:
                    raw_content = ""
                    if file.mode == "r":
                        raw_content = file.readlines()
                for line in raw_content:
                    if int(line) not in network_latency[i][j].keys():
                        network_latency[i][j][int(line)] = 1
                    else:
                        network_latency[i][j][int(line)] += 1

    with open(dir + "network_latency.csv", "w") as file:
        writer = csv.writer(file)
        for src in network_latency.keys():
            writer.writerow([src])
            for dest in network_latency[src].keys():
                writer.writerow([dest])
                writer.writerow(['latency', 'freq'])
                for lat, freq in network_latency[src][dest].items():
                    writer.writerow([lat, freq])


def calculate_packet_latency_distribution(dir):
    packet_latency = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
                       3: {0: {}, 1: {}, 2: {}}}
    for i in range(0, 4):
        for j in range(0, 4):
            if i != j:
                with open(dir + "packet_latency_" + str(i) + "_" + str(j) + ".txt", "r") as file:
                    raw_content = ""
                    if file.mode == "r":
                        raw_content = file.readlines()
                for line in raw_content:
                    if int(line) not in packet_latency[i][j].keys():
                        packet_latency[i][j][int(line)] = 1
                    else:
                        packet_latency[i][j][int(line)] += 1
    with open(dir + "packet_latency.csv", "w") as file:
        writer = csv.writer(file)
        for src in packet_latency.keys():
            writer.writerow([src])
            for dest in packet_latency[src].keys():
                writer.writerow([dest])
                writer.writerow(['latency', 'freq'])
                for lat, freq in packet_latency[src][dest].items():
                    writer.writerow([lat, freq])


def calculate_throughput(dir):
    pass


if __name__ == '__main__':
    dir = "benchmarks/PolyBench/syrk/pre/out/"
    plot_core_traffic(dir)
    calculate_injection_rate(dir)
    """calculate_link_usage(dir)
    calculate_network_latency_distribution(dir)
    calculate_packet_latency_distribution(dir)
    calculate_traffic_flow(dir)
    calculate_throughput(dir)"""