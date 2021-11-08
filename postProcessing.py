import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from hurst import compute_Hc
from scipy import stats
import numpy as np


chiplet = []
chiplet_0 = dict(
    SM_ID=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
           28, 29, 30, 31],
    LLC_ID=[128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143], port=192)

link_01 = 0
chiplet_1 = dict(
    SM_ID=[32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
           59, 60, 61, 62, 63],
    LLC_ID=[144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159], port=193)

chiplet_2 = dict(
    SM_ID=[64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
           91, 92, 93, 94, 95],
    LLC_ID=[160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175], port=194)

link_12 = 0
chiplet_2 = dict(
    SM_ID=[64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
           91, 92, 93, 94],
    LLC_ID=[160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174], port=194)
link_23 = 0

chiplet_3 = dict(
    SM_ID=[96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117,
           118, 119, 120, 121, 122, 123, 124, 125, 126, 127],
    LLC_ID=[176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191], port=195)
link_30 = 0
chiplet.append(chiplet_0)
chiplet.append(chiplet_1)
chiplet.append(chiplet_2)
chiplet.append(chiplet_3)
injection = {0: {}, 1: {}, 2: {}, 3: {}}
throughput_flit_update = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
                  3: {0: {}, 1: {}, 2: {}}}
throughput_flit = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
              3: {0: {}, 1: {}, 2: {}}}
throughput_byte_update = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
                  3: {0: {}, 1: {}, 2: {}}}
throughput_byte = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
              3: {0: {}, 1: {}, 2: {}}}
packet_type_ratio = {0: {0: 0, 1: 0, 2: 0, 3: 0}, 1: {0: 0, 1: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 2: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0, 3: 0}}
per_chiplet_heat_map = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
                  3: {0: {}, 1: {}, 2: {}}}


def check_local_or_remote(x):  # 0 for local, 1 for remote
    for i in range(len(chiplet)):
        if (int(x[1].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[1].split(": ")[1]) in chiplet[i]["LLC_ID"]):
            if (int(x[2].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[2].split(": ")[1]) in chiplet[i]["LLC_ID"]):
                return 0
        return 1


def chip_select(x):
    if x == 192:
        return 0
    elif x == 193:
        return 1
    elif x == 194:
        return 2
    elif x == 195:
        return 3


def hurst(packet):
    out = {0: {}, 1: {}, 2: {}, 3: {}}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if len(packet[i][j]) > 7:
                continue
            else:
                if int(packet[i][j][5].split(": ")[1]) == 0 or int(packet[i][j][5].split(": ")[1]) == 2:
                    source = int(packet[i][j][0].split(": ")[1])
                    time = int(packet[i][j][6].split(": ")[1])
                    byte = int(packet[i][j][4].split(": ")[1])
                    if time not in out[source].keys():
                        out[source][time] = byte
                    else:
                        out[source][time] += byte

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


def flit_per_cycle(packet):
    out = {0: {}, 1: {}, 2: {}, 3: {}}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if len(packet[i][j]) > 7:
                continue
            else:
                if int(packet[i][j][3].split(": ")[1]) == -1:
                    if int(packet[i][j][5].split(": ")[1]) == 0 or int(packet[i][j][5].split(": ")[1]) == 2:
                        source = int(packet[i][j][0].split(": ")[1])
                        dest = int(packet[i][j][1].split(": ")[1])
                        time = int(packet[i][j][6].split(": ")[1])
                        byte = int(packet[i][j][4].split(": ")[1])
                        flit = 0
                        if byte == 8:
                            flit = 1
                        elif byte == 136:
                            flit = 5
                        elif byte == 72:
                            flit = 3
                        if time not in out[source].keys():
                            out[source][time] = flit
                        else:
                            out[source][time] += flit
                        if time not in throughput_flit[source][dest].keys():
                            throughput_flit[source][dest].setdefault(time, []).append(byte)
                        else:
                            throughput_flit[source][dest].setdefault(time, []).append(byte)
    zero = {0: 0, 1: 0, 2: 0, 3: 0}
    flag = prev = 0
    for source in throughput_flit.keys():
        for dest in throughput_flit[source].keys():
            for cyc in throughput_flit[source][dest].keys():
                if flag == 0:
                    throughput_flit_update[source][dest][cyc] = throughput_flit[source][dest][cyc]
                    prev = cyc
                    flag = 1
                elif flag == 1:
                    if cyc - prev > 1:
                        for k in range(prev + 1, cyc):
                            zero[source] += 1
                            throughput_flit_update[source][dest].setdefault(k, []).append(0)
                    throughput_flit_update[source][dest][cyc] = throughput_flit[source][dest][cyc]
                    prev = cyc

    fig, ax = plt.subplots(4, 1, figsize=(18, 5), dpi=200)
    ax[0].bar(list(out[0].keys()), list(out[0].values()), width=3)
    ax[0].set_ylim(0, 50)
    ax[1].bar(list(out[1].keys()), list(out[1].values()), width=3)
    ax[1].set_ylim(0, 50)
    ax[2].bar(list(out[2].keys()), list(out[2].values()), width=3)
    ax[2].set_ylim(0, 50)
    ax[3].bar(list(out[3].keys()), list(out[3].values()), width=3)
    ax[3].set_ylim(0, 50)
    plt.show()


def byte_per_cycle(packet):
    out1 = {0: {}, 1: {}, 2: {}, 3: {}}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if len(packet[i][j]) > 7:
                continue
            else:
                if int(packet[i][j][5].split(": ")[1]) == 0 or int(packet[i][j][5].split(": ")[1]) == 2:
                    source = int(packet[i][j][0].split(": ")[1])
                    dest = int(packet[i][j][1].split(": ")[1])
                    time = int(packet[i][j][6].split(": ")[1])
                    byte = int(packet[i][j][4].split(": ")[1])
                    if time not in out1[source].keys():
                        out1[source][time] = byte
                    else:
                        out1[source][time] += byte
                    if time not in throughput_byte[source][dest].keys():
                        throughput_byte[source][dest][time] = byte
                    else:
                        throughput_byte[source][dest][time] += byte
    zero = {0: 0, 1: 0, 2: 0, 3: 0}
    flag = prev = 0
    for source in throughput_byte.keys():
        for dest in throughput_byte[source].keys():
            for cyc in throughput_byte[source][dest].keys():
                if flag == 0:
                    throughput_byte_update[source][dest][cyc] = throughput_byte[source][dest][cyc]
                    prev = cyc
                    flag = 1
                elif flag == 1:
                    if cyc - prev > 1:
                        for k in range(prev + 1, cyc):
                            zero[source] += 1
                            throughput_byte_update[source][dest].setdefault(k, []).append(0)
                    throughput_byte_update[source][dest][cyc] = throughput_byte[source][dest][cyc]
                    prev = cyc

    fig, ax = plt.subplots(4, 1, figsize=(18, 5), dpi=200)
    ax[0].bar(list(out1[0].keys()), list(out1[0].values()), width=3)
    ax[1].bar(list(out1[1].keys()), list(out1[1].values()), width=3)
    ax[2].bar(list(out1[2].keys()), list(out1[2].values()), width=3)
    ax[3].bar(list(out1[3].keys()), list(out1[3].values()), width=3)
    plt.show()


def byte_per_cycle_dist(dir):
    dist = {0: {}, 1: {}, 2: {}, 3: {}}
    dist_sns = {0: [], 1: [], 2: [], 3: []}
    for source in throughput_byte.keys():
        for dest in throughput_byte[source].keys():
            for cycle, byte in throughput_byte[source][dest].items():
                dist_sns[source].append(byte)
                if byte not in dist[source].keys():
                    dist[source][byte] = 1
                else:
                    dist[source][byte] += 1

    fields = ['byte', 'dist']
    dist[0] = dict(sorted(dist[0].items(), key=lambda x: x[0]))
    with open(dir + "post/out/byte_0.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[0].items():
            writer.writerow([cyc, byte])
    dist[1] = dict(sorted(dist[1].items(), key=lambda x: x[0]))
    with open(dir + "post/out/byte_1.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[1].items():
            writer.writerow([cyc, byte])
    dist[2] = dict(sorted(dist[2].items(), key=lambda x: x[0]))
    with open(dir + "post/out/byte_2.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[2].items():
            writer.writerow([cyc, byte])
    dist[3] = dict(sorted(dist[3].items(), key=lambda x: x[0]))
    with open(dir + "post/out/byte_3.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[3].items():
            writer.writerow([cyc, byte])

    sns.set(style="dark", palette="muted", color_codes=True)
    fig, ax = plt.subplots(2, 2, figsize=(15, 15), sharex=True)
    sns.distplot(list(dist_sns[0]), hist=True, ax=ax[0, 0])
    ax[0, 0].set_title("core 0")
    ax[0, 0].set_xlim(-50, 1000)
    sns.distplot(list(dist_sns[1]), hist=True, ax=ax[0, 1])
    ax[0, 1].set_title("core 1")
    ax[0, 1].set_xlim(-50, 1000)
    sns.distplot(list(dist_sns[2]), hist=True, ax=ax[1, 0])
    ax[1, 0].set_title("core 2")
    ax[1, 0].set_xlim(-50, 1000)
    sns.distplot(list(dist_sns[3]), hist=True, ax=ax[1, 1])
    ax[1, 1].set_title("core 3")
    ax[1, 1].set_xlim(-50, 1000)
    plt.setp(ax, yticks=[])
    plt.tight_layout()
    plt.show()


def inter_departure_dist(dir):
    dist = {0: {}, 1: {}, 2: {}, 3: {}}
    dist_sns = {0: [], 1: [], 2: [], 3: []}
    flag = 0
    start = end = 0
    global throughput_byte_update
    global throughput_byte
    for source in throughput_byte.keys():
        for dest in throughput_byte[source].keys():
            for cyc in throughput_byte[source][dest].keys():
                if flag == 0:
                    throughput_byte_update[source][dest][cyc] = throughput_byte[source][dest][cyc]
                    prev = cyc
                    flag = 1
                elif flag == 1:
                    if cyc - prev > 1:
                        for k in range(prev + 1, cyc):
                            throughput_byte_update[source][dest].setdefault(k, []).append(0)
                    throughput_byte_update[source][dest][cyc] = throughput_byte[source][dest][cyc]
                    prev = cyc

    for core in throughput_byte_update.keys():
        for dest in throughput_byte_update[core].keys():
            throughput_byte_update[core][dest] = dict(sorted(throughput_byte_update[core][dest].items(), key=lambda x:x[0]))

    for core in throughput_byte_update.keys():
        for dest in throughput_byte_update[core].keys():
            for cyc, byte in throughput_byte_update[core][dest].items():
                if not(isinstance(byte, int)) and byte[0] == 0:
                    if flag == 0:
                        start = cyc
                        flag = 1
                    else:
                        continue
                else:
                    if flag == 1:
                        end = cyc
                        dist_sns[core].append(end - start)
                        if (end - start) not in dist[core].keys():
                            dist[core][end - start] = 1
                        else:
                            dist[core][end - start] += 1
                        flag = 0
                    else:
                        continue
            flag = end = start = 0
    fields = ['IAT', 'dist']
    dist[0] = dict(sorted(dist[0].items(), key=lambda x: x[0]))
    with open(dir + "post/out/iat_0.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[0].items():
            writer.writerow([cyc, byte])
    dist[1] = dict(sorted(dist[1].items(), key=lambda x: x[0]))
    with open(dir + "post/out/iat_1.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[1].items():
            writer.writerow([cyc, byte])
    dist[2] = dict(sorted(dist[2].items(), key=lambda x: x[0]))
    with open(dir + "post/out/iat_2.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[2].items():
            writer.writerow([cyc, byte])
    dist[3] = dict(sorted(dist[3].items(), key=lambda x: x[0]))
    with open(dir + "post/out/iat_3.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[3].items():
            writer.writerow([cyc, byte])

    sns.set(style="dark", palette="muted", color_codes=True)
    fig, ax = plt.subplots(2, 2, figsize=(15, 15), sharex=True)
    sns.distplot(list(dist_sns[0]), kde=True, hist=True, ax=ax[0, 0])
    ax[0, 0].set_title("core 0")
    ax[0, 0].set_xlim(-20, 300)
    sns.distplot(list(dist_sns[1]), kde=True, hist=True, ax=ax[0, 1])
    ax[0, 1].set_title("core 1")
    ax[0, 1].set_xlim(-20, 300)
    sns.distplot(list(dist_sns[2]), kde=True, hist=True, ax=ax[1, 0])
    ax[1, 0].set_title("core 2")
    ax[1, 0].set_xlim(-20, 300)
    sns.distplot(list(dist_sns[3]), kde=True, hist=True, ax=ax[1, 1])
    ax[1, 1].set_title("core 3")
    ax[1, 1].set_xlim(-20, 300)
    plt.setp(ax, yticks=[])
    plt.tight_layout()
    plt.show()


def outser(dir):
    for core in throughput_byte.keys():
        for dest in throughput_byte[core].keys():
            path = dir + "post/out/post_" + str(core) + "_" + str(dest) + ".txt"
            with open(path, "w") as file:
                for cycle, byte in throughput_byte[core][dest].items():
                    file.write(str(cycle) + "\t" + str(byte) + "\n")


def generate_packet_type_ratio(packet, dir):
    for i in packet.keys():
        for j in range(len(packet[i])):
            if len(packet[i][j]) > 7:
                continue
            else:
                if int(packet[i][j][3].split(": ")[1]) == -1:
                    packet_type_ratio[int(packet[i][j][0].split(": ")[1])][int(packet[i][j][5].split(": ")[1])] += 1
    fields = ['packet_type', 'frequency']
    with open(dir + "post/out/packet_ratio.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for core in packet_type_ratio.keys():
            writer.writerow([str(core)])
            for type, freq in packet_type_ratio[core].items():
                writer.writerow([type, freq])


def per_core_comparison(path):
    real_core = synthetic_core = 1
    real_dest = synthetic_dest = 3
    real_path = path + "/pre/out/pre_" + str(real_core) + "_" + str(real_dest) + ".txt"
    synthetic_path = path + "/post/out/post_" + str(synthetic_core) + "_" + str(synthetic_dest) + ".txt"
    real_list = {}
    syn_list = {}
    with open(real_path, "r") as file:
        reader = file.readlines()
    lined_list = {}
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        y = len(item[1].split("\n")[0][1:][:-1].split(","))
        for index in range(y):
            if int(item[0]) not in lined_list.keys():
                lined_list.setdefault(int(item[0]), []).append(int(item[1].split("\n")[0][1:][:-1].split(",")[index]))
            else:
                lined_list[int(item[0])].append(int(item[1].split("\n")[0][1:][:-1].split(",")[index]))

    for cycle, byte in lined_list.items():
        if sum(byte) not in real_list.keys():
            real_list[sum(byte)] = 1
        else:
            real_list[sum(byte)] += 1

    with open(synthetic_path, "r") as file:
        reader = file.readlines()
    lined_list = {}
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        y = len(item[1].split("\n")[0][1:][:-1].split(","))
        for index in range(y):
            if int(item[0]) not in lined_list.keys():
                lined_list.setdefault(int(item[0]), []).append(int(item[1].split("\n")[0][1:][:-1].split(",")[index]))
            else:
                lined_list[int(item[0])].append(int(item[1].split("\n")[0][1:][:-1].split(",")[index]))

    for cycle, byte in lined_list.items():
        if sum(byte) not in syn_list.keys():
            syn_list[sum(byte)] = 1
        else:
            syn_list[sum(byte)] += 1
    real_list = dict(sorted(real_list.items(), key=lambda x:x[0]))
    syn_list = dict(sorted(syn_list.items(), key=lambda x:x[0]))

    # Generating CDF
    _sum = 0
    for byte in real_list.keys():
        _sum += real_list[byte]
    for byte in real_list.keys():
        real_list[byte] = real_list[byte]/_sum
    real_cum = {}
    prev = 0
    for byte in real_list.keys():
        real_cum[byte] = real_list[byte] + prev
        prev = real_cum[byte]

    _sum = 0
    for byte in syn_list.keys():
        _sum += syn_list[byte]
    for byte in syn_list.keys():
        syn_list[byte] = syn_list[byte] / _sum
    syn_cum = {}
    prev = 0
    for byte in syn_list.keys():
        syn_cum[byte] = syn_list[byte] + prev
        prev = syn_cum[byte]

    print(real_cum)
    print(syn_cum)
    plt.plot(list(real_cum.keys()), list(real_cum.values()), label="Real")
    plt.plot(list(syn_cum.keys()), list(syn_cum.values()), label="Synthetic")
    plt.legend(loc="best")
    plt.title("CDF of bytes from core " + str(real_core) + " to core " + str(real_dest))
    plt.show()


def generate_packet_latency(packet, dir):
    dist = {}
    start = 0
    for i in packet.keys():
        for line in packet[i]:
            if int(line[3].split(": ")[1]) == -1:
                start = int(line[6].split(": ")[1])
            elif int(line[4].split(": ")[1]) == 4:
                if (int(line[7].split(": ")[1]) - start) not in dist.keys():
                    dist[int(line[7].split(": ")[1]) - start] = 1
                else:
                    dist[int(line[7].split(": ")[1]) - start] += 1
                break
    with open(dir + "post/out/packet_latency.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['latency', 'density'])
        for lat, freq in dist.items():
            writer.writerow([lat, freq])


if __name__ == "__main__":
    path = "benchmarks/PolyBench/syrk/"
    with open(path + 'post/out.txt', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    packet_ = {}
    packet = {}
    for i in range(len(lined_list)):
        if int(lined_list[i][2].split(": ")[1]) in packet_.keys():
            packet_.setdefault(int(lined_list[i][2].split(": ")[1]), []).append(lined_list[i])
        else:
            packet_.setdefault(int(lined_list[i][2].split(": ")[1]), []).append(lined_list[i])
    packet = dict(sorted(packet_.items(), key=lambda x: x[0]))
    #flit_per_cycle(packet)
    #byte_per_cycle(packet)
    #byte_per_cycle_dist(path)
    #inter_departure_dist(path)
    #outser(path)
    #generate_packet_type_ratio(packet, path)
    #per_core_comparison(path)
    generate_packet_latency(packet, path)