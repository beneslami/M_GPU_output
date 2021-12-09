import csv
import numpy as np
import matplotlib.pyplot as plt
from hurst import compute_Hc
import warnings

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

traffic = {0: {}, 1: {}, 2: {}, 3: {}}
iat = {0: {}, 1: {}, 2: {}, 3: {}}
byte_dist = {0: {}, 1: {}, 2: {}, 3: {}}
byte_dist_ = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
window_size = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
packet_type = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
injection_rate = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
inter_injection_rate = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
state_nums = {0: {}, 1: {}, 2: {}, 3: {}}
destination_choose = {0: {}, 1: {}, 2: {}, 3: {}}


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


def calculate_injection_rate():
    start = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    flag = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            for dest in traffic[src][cyc].keys():
                if len(traffic[src][cyc][dest]) == 0:
                    if flag[src][dest] == 0:
                        start[src][dest] = cyc
                        flag[src][dest] = 1
                    elif flag[src][dest] == 1:
                        continue
                else:
                    if flag[src][dest] == 1:
                        if (cyc - start[src][dest]) not in injection_rate[src][dest].keys():
                            injection_rate[src][dest][(cyc - start[src][dest])] = 1
                        else:
                            injection_rate[src][dest][(cyc - start[src][dest])] += 1
                        flag[src][dest] = 0

    for src in injection_rate.keys():
        for dest in injection_rate[src].keys():
            injection_rate[src][dest] = dict(sorted(injection_rate[src][dest].items(), key=lambda x: x[0]))

    with open(dir + "injection_rate.csv", "w") as file:
        for src in injection_rate.keys():
            file.write(str(src) + "\n")
            for dest in injection_rate[src].keys():
                file.write(str(dest) + "\n")
                for duration, freq in injection_rate[src][dest].items():
                    file.write(str(duration) + "," + str(freq) + "\n")


def update_traffic():
    global traffic
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            list_ = [0, 1, 2, 3]
            list_.remove(src)
            for dest in traffic[src][cyc].keys():
                list_.remove(dest)
            if len(list_) != 0:
                for i in list_:
                    traffic[src][cyc].setdefault(i, [])
    for src in traffic.keys():
        traffic[src] = dict(sorted(traffic[src].items(), key=lambda x: x[0]))
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            traffic[src][cyc] = dict(sorted(traffic[src][cyc].items(), key=lambda x: x[0]))


def generate_real_traffic_per_core(source, dest, packet):
    global traffic
    for cycle, byte in packet.items():
        if cycle not in traffic[source].keys():
            traffic[source].setdefault(cycle, {})
            if dest not in traffic[source][cycle].keys():
                traffic[source][cycle][dest] = byte
            else:
                for b in byte:
                    traffic[source][cycle][dest].append(b)
        else:
            if dest not in traffic[source][cycle].keys():
                traffic[source][cycle][dest] = byte
            else:
                for b in byte:
                    traffic[source][cycle][dest].append(b)


def IAT():
    global traffic
    flag = 0
    start = -1
    for source in traffic.keys():
        for cycle in traffic[source].keys():
            if flag == 0:
                start = cycle
                flag = 1
            elif flag == 1:
                if (cycle - start) not in iat[source].keys():
                    iat[source][cycle - start] = 1
                else:
                    iat[source][cycle - start] += 1
                start = cycle
        start = -1
        flag = 0
    for source in iat.keys():
        iat[source] = dict(sorted(iat[source].items(), key=lambda x: x[0]))


def byte_distribution(dir):
    global traffic
    global byte_dist
    for src in traffic.keys():
        for cycle in traffic[src].keys():
            temp = 0
            for dest in traffic[src][cycle].keys():
                if len(traffic[src][cycle][dest]) == 0:
                    if 0 not in byte_dist_[src][dest].keys():
                        byte_dist_[src][dest][0] = 1
                    else:
                        byte_dist_[src][dest][0] += 1
                else:
                    temp += sum(traffic[src][cycle][dest])
                    if sum(traffic[src][cycle][dest]) not in byte_dist_[src][dest].keys():
                        byte_dist_[src][dest][sum(traffic[src][cycle][dest])] = 1
                    else:
                        byte_dist_[src][dest][sum(traffic[src][cycle][dest])] += 1
            if temp not in byte_dist[src].keys():
                byte_dist[src][temp] = 1
            else:
                byte_dist[src][temp] += 1

    for src in byte_dist.keys():
        byte_dist[src] = dict(sorted(byte_dist[src].items()), key=lambda x: x[0])
    for src in byte_dist_.keys():
        for dest in byte_dist_[src].keys():
            byte_dist_[src][dest] = dict(sorted(byte_dist_[src][dest].items(), key=lambda x: x[0]))

    for src in byte_dist_.keys():
        for dest in byte_dist_[src].keys():
            with open(dir +"byte_" + str(src) + "_" + str(dest) + ".csv", "w") as file:
                for byte, dist in byte_dist_[src][dest].items():
                    file.write(str(byte) + "," + str(dist) + "\n")


def calculate_window_size(dir):
    global traffic
    global window_size
    dist = {}
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            if src == 3:
                by = {}
                counter = 0
                for dest in traffic[src][cyc].keys():
                    if len(traffic[src][cyc][dest]) != 0:
                        counter += 1
                        for b in traffic[src][cyc][dest]:
                            if b not in by.keys():
                                by[b] = 1
                            else:
                                by[b] += 1
                if counter not in dist.keys():
                    dist[counter] = by
                else:
                    temp = dist[counter]
                    for it in by.keys():
                        if it in temp.keys():
                            temp[it] += by[it]
                        else:
                            temp[it] = by[it]
                    dist[counter] = temp

            for dest in traffic[src][cyc].keys():
                if len(traffic[src][cyc][dest]) != 0:
                    if len(traffic[src][cyc][dest]) not in window_size[src][dest].keys():
                        window_size[src][dest][len(traffic[src][cyc][dest])] = 1
                    else:
                        window_size[src][dest][len(traffic[src][cyc][dest])] += 1
    for src in window_size.keys():
        for dest in window_size[src].keys():
            window_size[src][dest] = dict(sorted(window_size[src][dest].items(), key=lambda x: x[0]))

    with open(dir + "window_size.csv", "w") as file:
        for src in window_size.keys():
            file.write(str(src) + "\n")
            for dest in window_size[src].keys():
                file.write(str(dest) + "\n")
                for win, freq in window_size[src][dest].items():
                    file.write(str(win) + "," + str(freq) + "\n")


def generate_packet_type_ratio():
    global traffic
    global packet_type
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            for dest in traffic[src][cyc].keys():
                if len(traffic[src][cyc][dest]) == 0:
                    if 0 not in packet_type[src][dest].keys():
                        packet_type[src][dest][0] = 1
                    else:
                        packet_type[src][dest][0] += 1
                else:
                    for byte in traffic[src][cyc][dest]:
                        if byte not in packet_type[src][dest].keys():
                            packet_type[src][dest][byte] = 1
                        else:
                            packet_type[src][dest][byte] += 1
    with open(dir + "packet_ratio.csv", "w") as file:
        for src in packet_type.keys():
            file.write(str(src) + "\n")
            for dest in packet_type[src].keys():
                file.write(str(dest) + "\n")
                for packet, freq in packet_type[src][dest].items():
                    file.write(str(packet) + "," + str(freq) + "\n")


def outser(dir):
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            for dest in traffic[src][cyc].keys():
                with open(dir + "pre_" + str(src) + "_" + str(dest) + ".txt", "a") as file:
                    file.write(str(cyc) + "\t" + str(traffic[src][cyc][dest]) + "\n")


def test():
    global traffic
    global state_nums
    dist = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            for dest, byte in traffic[src][cyc].items():
                if len(byte) != 0:
                    for b in byte:
                        if b not in dist[src][dest].keys():
                            dist[src][dest][b] = 1
                        else:
                            dist[src][dest][b] += 1
    print(dist)


def destination():
    global traffic
    global destination_choose
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            for dest in traffic[src][cyc].keys():
                if len(traffic[src][cyc][dest]) != 0:
                    if dest not in destination_choose[src].keys():
                        destination_choose[src][dest] = 1
                    else:
                        destination_choose[src][dest] += 1
    print(destination_choose)


def calculate_inter_injection_rate(dir):
    global traffic
    global inter_injection_rate
    start = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    flag = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            for dest in traffic[src][cyc].keys():
                if len(traffic[src][cyc][dest]) == 0:
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
        for s in start.keys():
            for d in start[s].keys():
                start[s][d] = 0
                flag[s][d] = 0

    for src in inter_injection_rate.keys():
        for dest in inter_injection_rate[src].keys():
            inter_injection_rate[src][dest] = dict(sorted(inter_injection_rate[src][dest].items(), key=lambda x: x[0]))

    for src in inter_injection_rate.keys():
        for dest in inter_injection_rate[src].keys():
            with open(dir + "inter_injection_" + str(src) + "_" + str(dest) + ".csv", "w") as file:
                for duration, freq in inter_injection_rate[src][dest].items():
                    file.write(str(duration) + "," + str(freq) + "\n")


if __name__ == '__main__':
    dir = "benchmarks/Rodinia/cfd/pre/"
    for src in range(0, 4):
        for dst in range(0, 4):
            if src != dst:
                lined_list = {}
                raw = ""
                with open(dir + "out/pre_" + str(src) +"_" + str(dst) + ".txt", "r") as file:
                    raw = file.readlines()
                for line in raw:
                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                    y = len(item[1].split("\n")[0][1:][:-1].split(","))
                    for index in range(y):
                        if int(item[0]) not in lined_list.keys():
                            lined_list.setdefault(int(item[0]), []).append(
                                int(item[1].split("\n")[0][1:][:-1].split(",")[index]))
                        else:
                            lined_list[int(item[0])].append(int(item[1].split("\n")[0][1:][:-1].split(",")[index]))
                generate_real_traffic_per_core(src, dst, lined_list)
    update_traffic()
    #IAT()
    #calculate_inter_injection_rate()
    #calculate_injection_rate()
    test()
    #destination()
    #byte_distribution(dir)
    #calculate_window_size(dir)
    #generate_packet_type_ratio()
    #outser(dir)
    #calculate_inter_injection_rate(dir)

    for i in range(0, 4):
        """filename = dir + "IAT" + "_core_" + str(i) + str(".csv")
        with open(filename, "w") as file:
            file.write("Inter_arrival_time_begin\n")
            for duration, freq in iat[i].items():
                file.write(str(duration) + "," + str(freq) + "\n")
            file.write("Inter_arrival_time_end\n")"""

        """filename = dir + "byte" + "_core_" + str(i) + str(".csv")
        with open(filename, "w") as file:
            file.write("Byte_distribution_begin\n")
            for byte, freq in byte_dist[i].items():
                file.write(str(byte) + "," + str(freq) + "\n")
            file.write("Byte_distribution_end\n")"""

        """filename = dir + "window" + "_core_" + str(i) + str(".csv")
        with open(filename, "w") as file:
            file.write("window_size_begin\n")
            for dest in window_size[i].keys():
                file.write("destination " + str(dest) + "\n")
                for win, freq in window_size[i][dest].items():
                    file.write(str(win) + "," + str(freq) + "\n")
            file.write("window_size_end\n")"""

        """filename = dir + "packet_type" + "_core_" + str(i) + str(".csv")
        with open(filename, "w") as file:
            file.write("packet_type_begin\n")
            for dest in packet_type[i].keys():
                file.write("destination " + str(dest) + "\n")
                for type, freq in packet_type[i][dest].items():
                    file.write(str(type) + "," + str(freq) + "\n")
            file.write("packet_type_end\n")"""

        """filename = dir + "Inter_injection_rate" + "_core_" + str(i) + str(".csv")
        with open(filename, "w") as file:
            file.write("inter_Injection_rate_begin\n")
            for dest in inter_injection_rate[i].keys():
                file.write("destination " + str(dest) + "\n")
                for duration, freq in inter_injection_rate[i][dest].items():
                    file.write(str(duration) + "," + str(freq) + "\n")
            file.write("inter_Injection_rate_begin\n")"""