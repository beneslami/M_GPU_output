import csv
import matplotlib.pyplot as plt
from hurst import compute_Hc
import warnings
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
injection_rate = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
throughput_byte_update = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
                  3: {0: {}, 1: {}, 2: {}}}
throughput_byte = {0: {}, 1: {}, 2: {}, 3: {}}
packet_type_ratio = {0: {0: 0, 1: 0, 2: 0, 3: 0}, 1: {0: 0, 1: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 2: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0, 3: 0}}
packet_type_ratio_ = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
per_chiplet_heat_map = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
                  3: {0: {}, 1: {}, 2: {}}}
src_window = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
inter_injection_rate = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
offered_throughput = {}
total_throughput = {}
offered_throughput_flit = {}
total_throughput_flit = {}


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

    """fig, ax = plt.subplots(4, 1, figsize=(18, 5), dpi=200)
    ax[0].bar(list(out[0].keys()), list(out[0].values()), width=3)
    ax[0].set_ylim(0, 50)
    ax[1].bar(list(out[1].keys()), list(out[1].values()), width=3)
    ax[1].set_ylim(0, 50)
    ax[2].bar(list(out[2].keys()), list(out[2].values()), width=3)
    ax[2].set_ylim(0, 50)
    ax[3].bar(list(out[3].keys()), list(out[3].values()), width=3)
    ax[3].set_ylim(0, 50)
    plt.show()"""


def byte_per_cycle(packet):
    global throughput_byte
    for i in packet.keys():
        for j in range(len(packet[i])):
            if len(packet[i][j]) == 6:
                if int(packet[i][j][4].split(": ")[1]) == 0 or int(packet[i][j][4].split(": ")[1]) == 2:
                    source = int(packet[i][j][0].split(": ")[1])
                    dest = int(packet[i][j][1].split(": ")[1])
                    time = int(packet[i][j][5].split(": ")[1])
                    byte = int(packet[i][j][3].split(": ")[1])
                    if time not in throughput_byte[source].keys():
                        throughput_byte[source].setdefault(time, {})
                        if dest not in throughput_byte[source][time].keys():
                            throughput_byte[source][time].setdefault(dest, []).append(byte)
                        else:
                            throughput_byte[source][time].setdefault(dest, []).append(byte)
                    else:
                        if dest not in throughput_byte[source][time].keys():
                            throughput_byte[source][time].setdefault(dest, []).append(byte)
                        else:
                            throughput_byte[source][time].setdefault(dest, []).append(byte)

    """zero = {0: 0, 1: 0, 2: 0, 3: 0}
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
                            throughput_byte_update[source][dest][k] = 0
                    throughput_byte_update[source][dest][cyc] = throughput_byte[source][dest][cyc]
                    prev = cyc"""


def byte_per_cycle_update():
    for src in throughput_byte.keys():
        for cyc in throughput_byte[src].keys():
            list_ = [0, 1, 2, 3]
            list_.remove(src)
            for dest in throughput_byte[src][cyc].keys():
                list_.remove(dest)
            if len(list_) != 0:
                for i in list_:
                    throughput_byte[src][cyc].setdefault(i, [])


def byte_per_cycle_dist(dir):
    global throughput_byte
    byte_dist = {0: {}, 1: {}, 2: {}, 3: {}}
    dist_ = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    for source in throughput_byte.keys():
        for cycle in throughput_byte[source].keys():
            temp = 0
            for dest in throughput_byte[source][cycle].keys():
                temp += sum(throughput_byte[source][cycle][dest])
                if len(throughput_byte[source][cycle][dest]) == 0:
                    if 0 not in dist_[source][dest].keys():
                        dist_[source][dest][0] = 1
                    else:
                        dist_[source][dest][0] += 1
                else:
                    if sum(throughput_byte[source][cycle][dest]) not in dist_[source][dest].keys():
                        dist_[source][dest][sum(throughput_byte[source][cycle][dest])] = 1
                    else:
                        dist_[source][dest][sum(throughput_byte[source][cycle][dest])] += 1
            if source == 0 and temp == 8:
                print(str(source) + "\t" + str(cycle))
            if temp not in byte_dist[source].keys():
                byte_dist[source][temp] = 1
            else:
                byte_dist[source][temp] += 1

    for src in dist_.keys():
        for dest in dist_[src].keys():
            dist_[src][dest] = dict(sorted(dist_[src][dest].items(), key=lambda x: x[0]))
    for src in dist_.keys():
        for dest in dist_[src].keys():
            with open(dir +"post/byte_" + str(src) + "_" + str(dest) + ".csv", "w") as file:
                for byte, dist in dist_[src][dest].items():
                    file.write(str(byte) + "," + str(dist) + "\n")

    fields = ['byte', 'dist']
    byte_dist[0] = dict(sorted(byte_dist[0].items(), key=lambda x: x[0]))
    with open(dir + "post/out/byte_0.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in byte_dist[0].items():
            writer.writerow([cyc, byte])
    byte_dist[1] = dict(sorted(byte_dist[1].items(), key=lambda x: x[0]))
    with open(dir + "post/out/byte_1.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in byte_dist[1].items():
            writer.writerow([cyc, byte])
    byte_dist[2] = dict(sorted(byte_dist[2].items(), key=lambda x: x[0]))
    with open(dir + "post/out/byte_2.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in byte_dist[2].items():
            writer.writerow([cyc, byte])
    byte_dist[3] = dict(sorted(byte_dist[3].items(), key=lambda x: x[0]))
    with open(dir + "post/out/byte_3.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in byte_dist[3].items():
            writer.writerow([cyc, byte])


def inter_departure_dist(dir):
    dist = {0: {}, 1: {}, 2: {}, 3: {}}
    flag = 0
    start = -1
    global throughput_byte
    for source in throughput_byte.keys():
        for cycle in throughput_byte[source].keys():
            if flag == 0:
                start = cycle
                flag = 1
            elif flag == 1:
                if (cycle - start) not in dist[source].keys():
                    dist[source][cycle - start] = 1
                else:
                    dist[source][cycle - start] += 1
                start = cycle
        flag = 0
        start = -1

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


def outser(dir):
    for src in throughput_byte.keys():
        for cyc in throughput_byte[src].keys():
            for dest in throughput_byte[src][cyc].keys():
                with open(dir + "post/out/post_" + str(src) + "_" + str(dest) + ".txt", "a") as file:
                    file.write(str(cyc) + "\t" + str(throughput_byte[src][cyc][dest]) + "\n")


def generate_packet_type_ratio(dir):
    dist = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    for src in throughput_byte.keys():
        for cyc in throughput_byte[src].keys():
            for dest, byte in throughput_byte[src][cyc].items():
                if len(byte) == 0:
                    if 0 not in dist[src][dest].keys():
                        dist[src][dest][0] = 1
                    else:
                        dist[src][dest][0] += 1
                else:
                    for b in byte:
                        if b not in dist[src][dest].keys():
                            dist[src][dest][b] = 1
                        else:
                            dist[src][dest][b] += 1
    with open(dir + "post/out/packet_ratio.csv", "w") as file:
        for src in dist.keys():
            file.write(str(src) + "\n")
            for dest in dist[src].keys():
                file.write(str(dest) + "\n")
                for packet, freq in dist[src][dest].items():
                    file.write(str(packet) + "," + str(freq) + "\n")

    """for i in packet.keys():
        for j in range(len(packet[i])):
            if len(packet[i][j]) == 6:
                if int(packet[i][j][4].split(": ")[1]) == 0 or int(packet[i][j][4].split(": ")[1]) == 2:
                    source = int(packet[i][j][0].split(": ")[1])
                    dest = int(packet[i][j][1].split(": ")[1])
                    time = int(packet[i][j][5].split(": ")[1])
                    type = int(packet[i][j][4].split(": ")[1])
                    if type not in packet_type_ratio[source].keys():
                        packet_type_ratio[source][type] = 1
                    else:
                        packet_type_ratio[source][type] += 1
                    if type not in packet_type_ratio_[source][dest].keys():
                        packet_type_ratio_[source][dest][type] = 1
                    else:
                        packet_type_ratio_[source][dest][type] += 1
    fields = ['packet_type', 'frequency']
    with open(dir + "post/out/packet_ratio.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for core in packet_type_ratio.keys():
            writer.writerow([str(core)])
            for type, freq in packet_type_ratio[core].items():
                writer.writerow([type, freq])"""
    """fields = ['packet_type', 'frequency']
    with open(dir + "post/out/packet_ratio_.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for core in packet_type_ratio_.keys():
            writer.writerow([str(core)])
            for dest in packet_type_ratio_[core].keys():
                writer.writerow([str(dest)])
                for type, freq in packet_type_ratio_[core][dest].items():
                    writer.writerow([type, freq])"""


def check_injection_rate(dir):
    global throughput_byte
    global injection_rate
    on = {}
    total = 0
    for source in throughput_byte.keys():
        for cyc in throughput_byte[source].keys():
            for dest in throughput_byte[source][cyc].keys():
                if dest not in on.keys():
                    on[dest] = 1
                else:
                    on[dest] += 1
            total += 1
        for dst in on.keys():
            injection_rate[source][dst] = on[dst] / total
        total = 0
        on.clear()
    with open(dir + "post/out/injection_rate.csv", "w") as file:
        for src in injection_rate.keys():
            file.write(str(src) + "\n")
            for dest, rate in injection_rate[src].items():
                file.write(str(dest)+ "," + str(rate) + "\n")


def generate_packet_latency(packet, dir):
    dist = {}
    start = 0
    flag_0 = -1
    flag_1 = -1
    for i in packet.keys():
        for j in range(len(packet[i])):
            if (int(packet[i][j][0].split(": ")[1]) == int(packet[i][j][3].split(": ")[1])) and int(packet[i][j][6].split(": ")[1]) == 0:
                start = int(packet[i][j][6].split(": ")[1])
                for k in range(j+1, len(packet[i])):
                    if (int(packet[i][k][1].split(": ")[1]) == int(packet[i][k][3].split(": ")[1])) and int(packet[i][k][6].split(": ")[1]) == 0:
                        if (int(packet[i][k][7].split(": ")[1]) - start) not in dist.keys():
                            dist[int(packet[i][k][7].split(": ")[1]) - start] = 1
                        else:
                            dist[int(packet[i][k][7].split(": ")[1]) - start] += 1
                        break
            elif (int(packet[i][j][0].split(": ")[1]) == int(packet[i][j][3].split(": ")[1])) and int(packet[i][j][6].split(": ")[1]) == 1:
                start = int(packet[i][j][6].split(": ")[1])
                for k in range(j+1, len(packet[i])):
                    if (int(packet[i][k][1].split(": ")[1]) == int(packet[i][k][3].split(": ")[1])) and int(packet[i][k][6].split(": ")[1]) == 1:
                        if (int(packet[i][k][7].split(": ")[1]) - start) not in dist.keys():
                            dist[int(packet[i][k][7].split(": ")[1]) - start] = 1
                        else:
                            dist[int(packet[i][k][7].split(": ")[1]) - start] += 1
                        break
            elif (int(packet[i][j][0].split(": ")[1]) == int(packet[i][j][3].split(": ")[1])) and int(packet[i][j][6].split(": ")[1]) == 2:
                start = int(packet[i][j][6].split(": ")[1])
                for k in range(j+1, len(packet[i])):
                    if (int(packet[i][k][1].split(": ")[1]) == int(packet[i][k][3].split(": ")[1])) and int(packet[i][k][6].split(": ")[1]) == 2:
                        if (int(packet[i][k][7].split(": ")[1]) - start) not in dist.keys():
                            dist[int(packet[i][k][7].split(": ")[1]) - start] = 1
                        else:
                            dist[int(packet[i][k][7].split(": ")[1]) - start] += 1
                        break
            elif (int(packet[i][j][0].split(": ")[1]) == int(packet[i][j][3].split(": ")[1])) and int(packet[i][j][6].split(": ")[1]) == 3:
                start = int(packet[i][j][6].split(": ")[1])
                for k in range(j+1, len(packet[i])):
                    if (int(packet[i][k][1].split(": ")[1]) == int(packet[i][k][3].split(": ")[1])) and int(packet[i][k][6].split(": ")[1]) == 3:
                        if (int(packet[i][k][7].split(": ")[1]) - start) not in dist.keys():
                            dist[int(packet[i][k][7].split(": ")[1]) - start] = 1
                        else:
                            dist[int(packet[i][k][7].split(": ")[1]) - start] += 1
                        break
    dist = dict(sorted(list(dist.items()), key=lambda x: x[0]))
    with open(dir + "post/out/packet_latency.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['latency', 'density'])
        for lat, freq in dist.items():
            writer.writerow([lat, freq])


def generate_traffic_flow(dir):
    traffic_flow = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    """for src in throughput_byte.keys():
        temp = 0
        for dest in throughput_byte[src].keys():
            for cyc, byte in throughput_byte[src][dest].items():
                temp += byte
            traffic_flow[src][dest] += temp"""
    for i in range(0, 4):
        for j in range(0, 4):
            if i != j:
                with open(dir + "post/out/post_" + str(i) + "_" + str(j) + ".txt") as file:
                    raw = file.readlines()
                    temp = 0
                    for line in raw:
                        item = [x for x in line.split("\t") if x not in ['', '\t']]
                        temp += int(item[1])
                traffic_flow[i][j] += temp

    fields = ['dest', 'byte']
    with open(dir + "post/out/traffic_flow.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for src in traffic_flow.keys():
            writer.writerow([str(src)])
            for dest, byte in traffic_flow[src].items():
                writer.writerow([dest, byte])


def generate_link_utilization(packet, dir):
    link = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    for i in packet.keys():
        for j in range(len(packet[i])):
            source = int(packet[i][j][0].split(": ")[1])
            dest = int(packet[i][j][1].split(": ")[1])
            router_id = int(packet[i][j][3].split(": ")[1])
            byte = int(packet[i][j][5].split(": ")[1])
            time = int(packet[i][j][7].split(": ")[1])
            if source == 0:
                if source == router_id:
                    if dest == 1:
                        if time not in link[router_id][dest].keys():
                            link[router_id][dest][time] = byte
                        else:
                            link[router_id][dest][time] += byte
                    elif dest == 3:
                        if time not in link[router_id][dest].keys():
                            link[router_id][dest][time] = byte
                        else:
                            link[router_id][dest][time] += byte
                else:
                    if router_id == 1:
                        if dest == 2:
                            if time not in link[router_id][dest].keys():
                                link[router_id][dest][time] = byte
                            else:
                                link[router_id][dest][time] += byte
                    elif router_id == 3:
                        if dest == 2:
                            if time not in link[router_id][dest].keys():
                                link[router_id][dest][time] = byte
                            else:
                                link[router_id][dest][time] += byte
            if source == 1:
                if source == router_id:
                    if dest == 0:
                        if time not in link[router_id][dest].keys():
                            link[router_id][dest][time] = byte
                        else:
                            link[router_id][dest][time] += byte
                    elif dest == 2:
                        if time not in link[router_id][dest].keys():
                            link[router_id][dest][time] = byte
                        else:
                            link[router_id][dest][time] += byte
                else:
                    if router_id == 0:
                        if dest == 3:
                            if time not in link[router_id][dest].keys():
                                link[router_id][dest][time] = byte
                            else:
                                link[router_id][dest][time] += byte
                    elif router_id == 2:
                        if dest == 3:
                            if time not in link[router_id][dest].keys():
                                link[router_id][dest][time] = byte
                            else:
                                link[router_id][dest][time] += byte
            if source == 2:
                if source == router_id:
                    if dest == 1:
                        if time not in link[router_id][dest].keys():
                            link[router_id][dest][time] = byte
                        else:
                            link[router_id][dest][time] += byte
                    elif dest == 3:
                        if time not in link[2][dest].keys():
                            link[router_id][dest][time] = byte
                        else:
                            link[router_id][dest][time] += byte
                else:
                    if router_id == 3:
                        if dest == 0:
                            if time not in link[router_id][dest].keys():
                                link[router_id][dest][time] = byte
                            else:
                                link[router_id][dest][time] += byte
                    elif router_id == 1:
                        if dest == 0:
                            if time not in link[router_id][dest].keys():
                                link[router_id][dest][time] = byte
                            else:
                                link[router_id][dest][time] += byte
            if source == 3:
                if source == router_id:
                    if dest == 0:
                        if time not in link[router_id][1].keys():
                            link[router_id][dest][time] = byte
                        else:
                            link[router_id][dest][time] += byte
                    elif dest == 2:
                        if time not in link[router_id][2].keys():
                            link[router_id][dest][time] = byte
                        else:
                            link[router_id][dest][time] += byte
                else:
                    if router_id == 2:
                        if dest == 1:
                            if time not in link[router_id][dest].keys():
                                link[router_id][dest][time] = byte
                            else:
                                link[router_id][dest][time] += byte
                    elif router_id == 0:
                        if dest == 1:
                            if time not in link[router_id][dest].keys():
                                link[router_id][dest][time] = byte
                            else:
                                link[router_id][dest][time] += byte

    with open(dir + "post/out/link_usage.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(['link', 'mean'])
        for i in link.keys():
            writer.writerow([i])
            for j in link[i].keys():
                with warnings.catch_warnings():
                    m = np.nanmean(list(link[i][j].values()))
                    writer.writerow([j, m])


def byte_to_flit(num):
    res = 0
    if num % 32 == 0:
        res = 0
    else:
        res = 1
    return int(num/32) + res


def calculate_throughput(packet, dir):
    global offered_throughput_flit
    global total_throughput_flit
    global offered_throughput
    global total_throughput
    for i in packet.keys():
        for j in range(len(packet[i])):
            if int(packet[i][j][0].split(": ")[1]) == int(packet[i][j][3].split(": ")[1]):
                time = int(packet[i][j][7].split(": ")[1])
                byte = int(packet[i][j][5].split(": ")[1])
                if time not in offered_throughput_flit.keys():
                    offered_throughput_flit[time] = byte_to_flit(byte)
                else:
                    offered_throughput_flit[time] += byte_to_flit(byte)
                if time not in total_throughput.keys():
                    total_throughput[time] = byte
                else:
                    total_throughput[time] += byte
                if time not in offered_throughput.keys():
                    offered_throughput[time] = byte
                else:
                    offered_throughput[time] += byte
            else:
                if int(packet[i][j][1].split(": ")[1]) == int(packet[i][j][3].split(": ")[1]):
                    time = int(packet[i][j][7].split(": ")[1])
                    byte = int(packet[i][j][5].split(": ")[1])
                    if time not in total_throughput.keys():
                        total_throughput[time] = -byte
                    else:
                        total_throughput[time] -= byte

    total_throughput = dict(sorted(list(total_throughput.items()), key=lambda x: x[0]))
    offered_throughput = dict(sorted(list(offered_throughput.items()), key=lambda x: x[0]))
    offered_throughput_flit = dict(sorted(list(offered_throughput_flit.items()), key=lambda x: x[0]))
    with open(dir + "post/out/total_throughput.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        for cyc, byte in total_throughput.items():
            writer.writerow([cyc, byte])
    with open(dir + "post/out/offered_throughput.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        for cyc, byte in offered_throughput.items():
            writer.writerow([cyc, byte])
    with open(dir + "post/out/offered_throughput_flit.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        for cyc, byte in offered_throughput_flit.items():
            writer.writerow([cyc, byte])


def calculate_throughput_param(packet, dir):
    data = {}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if int(packet[i][j][0].split(": ")[1]) == int(packet[i][j][3].split(": ")[1]):
                byte = int(packet[i][j][5].split(": ")[1])
                if byte not in data.keys():
                    data[byte] = 1
                else:
                    data[byte] += 1
            elif int(packet[i][j][1].split(": ")[1]) == int(packet[i][j][3].split(": ")[1]):
                byte = int(packet[i][j][5].split(": ")[1])
                if byte not in data.keys():
                    data[byte] = 1
                else:
                    data[byte] += 1
    with open(dir + "post/out/throughput_params.csv", "w") as file:
        writer = csv.writer(file)
        for byte, freq in data.items():
            writer.writerow([byte, freq])


def calculate_source_window(dir):
    global throughput_byte
    global src_window
    for src in throughput_byte.keys():
        for cyc in throughput_byte[src].keys():
            for dest in throughput_byte[src][cyc].keys():
                if len(throughput_byte[src][cyc][dest]) not in src_window[src][dest].keys():
                    src_window[src][dest][len(throughput_byte[src][cyc][dest])] = 1
                else:
                    src_window[src][dest][len(throughput_byte[src][cyc][dest])] += 1
    for src in src_window.keys():
        for dst in src_window[src].keys():
            src_window[src][dst] = dict(sorted(src_window[src][dst].items(), key=lambda x: x[0]))

    with open(dir + "post/out/source_window.csv", "w") as file:
        writer = csv.writer(file)
        for src in src_window.keys():
            writer.writerow(["src", src])
            for dest in src_window[src].keys():
                writer.writerow(["dst", dest])
                for byte, freq in src_window[src][dest].items():
                    writer.writerow([byte, freq])


def test():
    ziq = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    for src in throughput_byte.keys():
        for cyc in throughput_byte[src].keys():
            x = 0
            for dest in throughput_byte[src][cyc].keys():
                if len(throughput_byte[src][cyc][dest]) != 0:
                    continue
                else:
                    x += 1
            if x == 2:
                for dest in throughput_byte[src][cyc].keys():
                    if len(throughput_byte[src][cyc][dest]) == 1:
                        if throughput_byte[src][cyc][dest][0] == 8:
                            ziq[src][dest] += 1
    print(ziq[0][1])
    print(ziq[0][2])
    print(ziq[0][3])


def inter_injection(dir):
    global throughput_byte
    start = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    flag = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    for src in throughput_byte.keys():
        for cyc in throughput_byte[src].keys():
            for dest in throughput_byte[src][cyc].keys():
                if len(throughput_byte[src][cyc][dest]) == 0:
                    if flag[src][dest] == 0:
                        start[src][dest] = cyc
                        flag[src][dest] = 1
                    elif flag[src][dest] == 1:
                        continue
                else:
                    if flag[src][dest] == 1:
                        if (cyc - start[src][dest]) not in inter_injection_rate[src][dest].keys():
                            inter_injection_rate[src][dest][(cyc - start[src][dest])] = 1
                        else:
                            inter_injection_rate[src][dest][(cyc - start[src][dest])] += 1
                        flag[src][dest] = 0

    for src in inter_injection_rate.keys():
        for dest in inter_injection_rate[src].keys():
            inter_injection_rate[src][dest] = dict(sorted(inter_injection_rate[src][dest].items(), key=lambda x: x[0]))
    for src in inter_injection_rate.keys():
        for dest in inter_injection_rate[src].keys():
            with open(dir + "post/inter_injection_" + str(src) + "_" + str(dest) + ".csv", "w") as file:
                for duration, freq in inter_injection_rate[src][dest].items():
                    file.write(str(duration) + "," + str(freq) + "\n")


if __name__ == "__main__":
    path = "benchmarks/Rodinia/cfd/"
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
    byte_per_cycle(packet)
    byte_per_cycle_update()
    #test()
    byte_per_cycle_dist(path)
    #calculate_source_window(path)
    #inter_departure_dist(path)
    #generate_packet_type_ratio(path)
    #inter_injection(path)
    #outser(path)
    """generate_packet_latency(packet, path)
    generate_traffic_flow(path)
    generate_link_utilization(packet, path)
    calculate_throughput(packet, path)
    calculate_throughput_param(packet, path)"""
