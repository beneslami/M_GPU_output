import csv
import gc
import os
import sys
import numpy as np

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

throughput_update = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
                  3: {0: {}, 1: {}, 2: {}}}
throughput = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
              3: {0: {}, 1: {}, 2: {}}}
processing_time = {0: {}, 1: {}, 2: {}, 3: {}}
dest_window = {0: {}, 1: {}, 2: {}, 3: {}}
iat_dist_csv = {0: {}, 1: {}, 2: {}, 3: {}}
byte_dist_csv = {0: {}, 1: {}, 2: {}, 3: {}}
packet_type_ratio = {0: {0: 0, 1: 0, 2: 0, 3: 0}, 1: {0: 0, 1: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 2: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0, 3: 0}}
link_utilization = {0: {1: {}, 2: {}, 3: {}}, 1: {0:{}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
packet_latency = {0: {1: [], 2: [], 3: []}, 1: {0: [], 2: [], 3: []}, 2: {0: [], 1: [], 3: []}, 3: {0: [], 1: [], 2: []}}
network_latency = {0: {1: [], 2: [], 3: []}, 1: {0: [], 2: [], 3: []}, 2: {0: [], 1: [], 3: []}, 3: {0: [], 1: [], 2: []}}
offered_throughput = {0: {}, 1: {}, 2: {}, 3: {}}
total_throughput = {}
data = {0: {}, 1: {}, 2: {}, 3: {}}
traffic_flow = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}


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


def injection_per_core(cycle):
    global throughput
    global throughput_update
    for i in cycle.keys():
        for j in range(len(cycle[i])):
            if 192 <= int(cycle[i][j][1].split(": ")[1]) <= 195 and 192 <= int(cycle[i][j][2].split(": ")[1]) <= 195:
                if cycle[i][j][0] == "injection buffer":
                    if int(cycle[i][j][5].split(": ")[1]) not in throughput[chip_select(int(cycle[i][j][1].split(": ")[1]))][chip_select(int(cycle[i][j][2].split(": ")[1]))].keys():
                        throughput[chip_select(int(cycle[i][j][1].split(": ")[1]))][chip_select(int(cycle[i][j][2].split(": ")[1]))].setdefault(int(cycle[i][j][5].split(": ")[1]), []).append(int(cycle[i][j][7].split(": ")[1]))
                    else:
                        throughput[chip_select(int(cycle[i][j][1].split(": ")[1]))][chip_select(int(cycle[i][j][2].split(": ")[1]))][int(cycle[i][j][5].split(": ")[1])].append(int(cycle[i][j][7].split(": ")[1]))

    zero = {0: 0, 1: 0, 2: 0, 3: 0}
    flag = prev = 0

    for source in throughput.keys():
        for dest in throughput[source].keys():
            for cyc in throughput[source][dest].keys():
                if flag == 0:
                    throughput_update[source][dest][cyc] = throughput[source][dest][cyc]
                    prev = cyc
                    flag = 1
                elif flag == 1:
                    if cyc - prev > 1:
                        for k in range(prev + 1, cyc):
                            zero[source] += 1
                            throughput_update[source][dest].setdefault(k, []).append(0)
                    throughput_update[source][dest][cyc] = throughput[source][dest][cyc]
                    prev = cyc


def byte_per_cycle_dist():
    global throughput
    global throughput_update
    global byte_dist_csv
    for src in range(0, 4):
        if os.path.isfile("pre/out/byte_" + str(src) + ".csv"):
            with open("pre/out/byte_" + str(src) + ".csv", "r") as csv_file:
                csvreader = csv.reader(csv_file)
                header = next(csvreader)
                for row in csvreader:
                    byte_dist_csv[src][int(row[0])] = int(row[1])

    for source in throughput.keys():
        for dest in throughput[source].keys():
            for cycle, byte in throughput[source][dest].items():
                if byte[0] == 0:
                    continue
                else:
                    if sum(byte) not in byte_dist_csv[source].keys():
                        byte_dist_csv[source][sum(byte)] = 1
                    else:
                        byte_dist_csv[source][sum(byte)] += 1

    for src in range(0, 4):
        fields = ['byte', 'freq']
        byte_dist_csv[src] = dict(sorted(byte_dist_csv[src].items(), key=lambda x: x[0]))
        with open("pre/out/byte_" + str(src) + ".csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(fields)
            for byte, freq in byte_dist_csv[src].items():
                writer.writerow([byte, freq])


def inter_departure_dist():
    global throughput
    global throughput_update
    global iat_dist_csv
    flag = 0
    start = -1
    for core in throughput.keys():
        for dest in throughput[core].keys():
            throughput[core][dest] = dict(sorted(throughput[core][dest].items(), key=lambda x: x[0]))

    for src in range(0, 4):
        if os.path.isfile("pre/out/iat_" + str(src) + ".csv"):
            with open("pre/out/iat_" + str(src) + ".csv") as csv_file:
                csvreader = csv.reader(csv_file)
                header = next(csvreader)
                for row in csvreader:
                    iat_dist_csv[src][int(row[0])] = int(row[1])

    for core in throughput.keys():
        for dest in throughput[core].keys():
            for cyc, byte in throughput[core][dest].items():
                if flag == 0:
                    start = cyc
                    flag = 1
                else:
                    if (cyc - start) not in iat_dist_csv[core].keys():
                        iat_dist_csv[core][cyc - start] = 1
                    else:
                        iat_dist_csv[core][cyc - start] += 1
                    start = cyc

    for src in iat_dist_csv.keys():
        iat_dist_csv[src] = dict(sorted(iat_dist_csv[src].items(), key=lambda x: x[0]))

    fields = ['IAT', 'dist']
    for src in iat_dist_csv.keys():
        with open("pre/out/iat_" + str(src) + ".csv", "w") as file:
            writer = csv.writer(file)
            writer.writerow(fields)
            for duration, freq in iat_dist_csv[src].items():
                writer.writerow([duration, freq])


def destination_window_size(cycle):
    global dest_window
    for src in range(0, 4):
        if os.path.isfile("pre/out/dest_win_" + str(src) + ".txt"):
            with open("pre/out/dest_win_" + str(src) + ".txt") as file:
                raw_c = file.readlines()
            for line in raw_c:
                item = [x for x in line.split("\t") if x not in ['', '\t']]
                for i in range(len(item[1].split("\n")[0][1:][:-1].split(", "))):
                    dest_window[src].setdefault(int(item[0]), []).append(int(item[1].split("\n")[0][1:][:-1].split(", ")[i]))

    for i in cycle.keys():
        for j in range(len(cycle[i])):
            if cycle[i][j][0] == "L2_icnt_pop":
                if 192 <= int(cycle[i][j][1].split(": ")[1]) <= 195:
                    if i not in dest_window[chip_select(int(cycle[i][j][1].split(": ")[1]))].keys():
                        dest_window[chip_select(int(cycle[i][j][1].split(": ")[1]))].setdefault(i, []).append(int(cycle[i][j][7].split(": ")[1]))
                    else:
                        dest_window[chip_select(int(cycle[i][j][1].split(": ")[1]))][i].append(int(cycle[i][j][7].split(": ")[1]))

    for core in dest_window.keys():
        path = "pre/out/dest_win_" + str(core) + ".txt"
        with open(path, "w") as file:
            for cycle, byte in dest_window[core].items():
                file.write(str(cycle) + "\t" + str(byte) + "\n")
    del(dest_window)


def outser():
    global throughput
    global throughput_update
    for core in throughput.keys():
        for dest in throughput[core].keys():
            path = "pre/out/pre_" + str(core) + "_" + str(dest) + ".txt"
            with open(path, "a") as file:
                for cycle, byte in throughput[core][dest].items():
                    file.write(str(cycle) + "\t" + str(byte) + "\n")


def generate_packet_type_ratio(packet):
    global packet_type_ratio
    if os.path.isfile("pre/out/packet_ratio.csv"):
        with open("pre/out/packet_ratio.csv") as csv_file:
            csvreader = csv.reader(csv_file)
            header = next(csvreader)
            for row in csvreader:
                if len(row) == 1:
                    src = int(row[0])
                else:
                    packet_type_ratio[src][int(row[0])] = int(row[1])

    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "injection buffer" or packet[i][j][0] == "L2_icnt_pop":
                packet_type_ratio[chip_select(int(packet[i][j][1].split(": ")[1]))][int(packet[i][j][4].split(": ")[1])] += 1
    fields = ['packet_type', 'frequency']
    with open("pre/out/packet_ratio.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for core in packet_type_ratio.keys():
            writer.writerow([str(core)])
            for type, freq in packet_type_ratio[core].items():
                writer.writerow([type, freq])


def generate_link_utilization(packet):
    for src in link_utilization.keys():
        for dest in link_utilization[src].keys():
            if os.path.isfile("pre/out/link_usage" + str(src) + "_" + str(dest) + "_per_cycle.txt"):
                with open("pre/out/link_usage" + str(src) + "_" + str(dest) + "_per_cycle.txt", "r") as file:
                    raw_content = file.readlines()
                for line in raw_content:
                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                    bytes = item[1][1:][:-2].split(", ")
                    if int(item[0]) not in link_utilization[src][dest].keys():
                        for y in bytes:
                            link_utilization[src][dest].setdefault(int(item[0]), []).append(int(y))
                    else:
                        for y in bytes:
                            link_utilization[src][dest][int(item[0])].append(int(y))

    for i in packet.keys():
        src = dest = -1
        for j in range(len(packet[i])):
            if True:
                if packet[i][j][0] == "injection buffer":
                    src = int(packet[i][j][6].split(": ")[1])
                    time = int(packet[i][j][8].split(": ")[1])
                    byte = int(packet[i][j][7].split(": ")[1])
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "FW push" and (int(packet[i][k][4].split(": ")[1]) == 0 or int(packet[i][k][4].split(": ")[1]) == 1):
                            dest = int(packet[i][k][6].split(": ")[1])
                            if time not in link_utilization[src][dest].keys():
                                link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                link_utilization[src][dest][time].append(byte)
                            break
                        elif packet[i][k][0] == "rop push" and (int(packet[i][k][4].split(": ")[1]) == 0 or int(packet[i][k][4].split(": ")[1]) == 1):
                            dest = int(packet[i][k][6].split(": ")[1])
                            if time not in link_utilization[src][dest].keys():
                                link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                link_utilization[src][dest][time].append(byte)
                            break

                elif packet[i][j][0] == "FW pop":
                    src = int(packet[i][j][6].split(": ")[1])
                    time = int(packet[i][j][8].split(": ")[1])
                    byte = int(packet[i][j][7].split(": ")[1])
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "rop push" and int(packet[i][k][4].split(": ")[1]) == 0 or int(packet[i][k][4].split(": ")[1]) == 1:
                            dest = int(packet[i][k][6].split(": ")[1])
                            if time not in link_utilization[src][dest].keys():
                                link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                link_utilization[src][dest][time].append(byte)
                            break
                        elif packet[i][k][0] == "SM pop" and int(packet[i][k][4].split(": ")[1]) == 2 or int(packet[i][k][4].split(": ")[1]) == 3:
                            dest = int(packet[i][k][6].split(": ")[1])
                            if time not in link_utilization[src][dest].keys():
                                link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                link_utilization[src][dest][time].append(byte)
                            break

                elif packet[i][j][0] == "L2_icnt_push":
                    src = int(packet[i][j][6].split(": ")[1])
                    time = int(packet[i][j][8].split(": ")[1])
                    byte = int(packet[i][j][7].split(":")[1])
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "FW push" and int(packet[i][k][4].split(": ")[1]) == 2 or int(packet[i][k][4].split(": ")[1]) == 3:
                            dest = int(packet[i][k][6].split(": ")[1])
                            if time not in link_utilization[src][dest].keys():
                                link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                link_utilization[src][dest][time].append(byte)
                            break
                        elif packet[i][k][0] == "SM pop" and int(packet[i][k][4].split(": ")[1]) == 2 or int(packet[i][k][4].split(": ")[1]) == 3:
                            dest = int(packet[i][k][6].split(": ")[1])
                            if time not in link_utilization[src][dest].keys():
                                link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                link_utilization[src][dest][time].append(byte)
                            break

    for src in link_utilization.keys():
        for dest in link_utilization[src].keys():
            with open("pre/out/link_usage" + str(src) + "_" + str(dest) + "_per_cycle.txt", "w") as file:
                for cycle, byte in link_utilization[src][dest].items():
                    file.write(str(cycle) + "\t" + str(byte) + "\n")


def calculate_link_usage():
    link_usage_ = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    link_usage = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    for i in range(0, 4):
        for j in range(0, 4):
            if i != j:
                with open("pre/out/link_usage" + str(i) + "_" + str(j) + "_per_cycle.txt", "r") as file:
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
                    if cycle not in link_usage_[i][j].keys():
                        link_usage_[i][j][cycle] = sum(temp)
                    else:
                        link_usage_[i][j][cycle] += sum(temp)



    for src in link_usage_.keys():
        for dest in link_usage_[src].keys():
            with open("pre/out/link_usage" + str(src) + str(dest) + ".csv", "w") as file:
                for cyc, byte in link_usage_[src][dest].items():
                    file.write((str(byte)) + "\n")


def generate_throughput(cycle):
    global total_throughput
    global offered_throughput
    if os.path.isfile("pre/out/total_throughput.txt"):
        with open("pre/out/total_throughput.txt", "r") as csv_file:
            rows = csv_file.readlines()
            for line in rows:
                row = [x for x in line.split(",")]
                total_throughput[int(row[0])] = int(row[1])

    if os.path.isfile("pre/out/offered_throughput.txt"):
        with open("pre/out/offered_throughput.txt", "r") as csv_file:
            rows = csv_file.readlines()
            for line in rows:
                row = [x for x in line.split(",")]
                offered_throughput[int(row[0])] = int(row[1])

    for i in cycle.keys():
        for j in range(len(cycle[i])):
            if 192 <= int(cycle[i][j][1].split(": ")[1]) <= 195 and 192 <= int(cycle[i][j][2].split(": ")[1]) <= 195:
                if cycle[i][j][0] == "injection buffer":
                    if int(cycle[i][j][8].split(": ")[1]) not in total_throughput.keys():
                        total_throughput[int(cycle[i][j][8].split(": ")[1])] = int(cycle[i][j][7].split(": ")[1])
                    else:
                        total_throughput[int(cycle[i][j][8].split(": ")[1])] += int(cycle[i][j][7].split(": ")[1])
                    if int(cycle[i][j][8].split(": ")[1]) not in offered_throughput[chip_select(int(cycle[i][j][1].split(": ")[1]))].keys():
                        offered_throughput[chip_select(int(cycle[i][j][1].split(": ")[1]))][int(cycle[i][j][8].split(": ")[1])] = int(cycle[i][j][7].split(": ")[1])
                    else:
                        offered_throughput[chip_select(int(cycle[i][j][1].split(": ")[1]))][int(cycle[i][j][8].split(": ")[1])] += int(cycle[i][j][7].split(": ")[1])

                elif cycle[i][j][0] == "rop push":
                    if int(cycle[i][j][8].split(": ")[1]) not in total_throughput.keys():
                        total_throughput[int(cycle[i][j][8].split(": ")[1])] = -int(cycle[i][j][7].split(": ")[1])
                    else:
                        total_throughput[int(cycle[i][j][8].split(": ")[1])] -= int(cycle[i][j][7].split(": ")[1])

                elif cycle[i][j][0] == "L2_icnt_push":
                    if int(cycle[i][j][8].split(": ")[1]) not in total_throughput.keys():
                        total_throughput[int(cycle[i][j][8].split(": ")[1])] = int(cycle[i][j][7].split(":")[1])
                    else:
                        total_throughput[int(cycle[i][j][8].split(": ")[1])] += int(cycle[i][j][7].split(":")[1])
                    if int(cycle[i][j][8].split(": ")[1]) not in offered_throughput[chip_select(int(cycle[i][j][1].split(": ")[1]))].keys():
                        offered_throughput[chip_select(int(cycle[i][j][1].split(": ")[1]))][int(cycle[i][j][8].split(": ")[1])] = int(cycle[i][j][7].split(":")[1])
                    else:
                        offered_throughput[chip_select(int(cycle[i][j][1].split(": ")[1]))][int(cycle[i][j][8].split(": ")[1])] += int(cycle[i][j][7].split(":")[1])

                elif cycle[i][j][0] == "SM pop":
                    if int(cycle[i][j][8].split(": ")[1]) not in total_throughput.keys():
                        total_throughput[int(cycle[i][j][8].split(": ")[1])] = -int(cycle[i][j][7].split(": ")[1])
                    else:
                        total_throughput[int(cycle[i][j][8].split(": ")[1])] -= int(cycle[i][j][7].split(": ")[1])

    total_throughput = dict(sorted(total_throughput.items(), key=lambda x: x[0]))

    with open("pre/out/total_throughput.txt", "w") as csv_file:
        for cyc, byte in total_throughput.items():
            csv_file.write(str(cyc) + "," + str(byte) + "\n")

    with open("pre/out/offerred_throughput.txt", "w") as csv_file:
        for cyc, byte in offered_throughput.items():
            csv_file.write(str(cyc) + "," + str(byte) + "\n")


def calculate_overall_throughput():
    global data
    global offered_throughput
    if os.path.isfile("pre/out/throughput_param.csv"):
        with open("pre/out/throughput_param.csv", "r") as csv_file:
            rows = csv_file.readlines()
            src = -1
            for line in rows:
                row = [x for x in line.split(",")]
                if len(row) == 1:
                    src = int(row[0])
                else:
                    data[src][int(row[0])] = int(row[1])

    for src in offered_throughput.keys():
        for time, byte in offered_throughput[src].items():
            if byte not in data[src].keys():
                data[src][byte] = 1
            else:
                data[src][byte] += 1
    with open("pre/out/throughput_param.csv", "w") as file:
        for src in data.keys():
            file.write(str(src) + "\n")
            for byte, dist in data[src].items():
                file.write(str(byte) + "," + str(dist)  + "\n")


def generate_traffic_flow():
    global traffic_flow
    for core in range(0, 4):
        for dest in range(0, 4):
            if core != dest:
                file2 = open("pre/out/pre_" + str(core) + "_" + str(dest) + ".txt", "r")
                raw_content = ""
                if file2.mode == "r":
                    raw_content = file2.readlines()
                for line in raw_content:
                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                    byte_list = item[1][1:][:-2].split(", ")
                    temp = []
                    for byte in byte_list:
                        temp.append(int(byte))
                    traffic_flow[core][dest] += sum(temp)
    with open("pre/out/traffic_flow.csv", "w") as file:
        for src in traffic_flow.keys():
            file.write("source: " + str(src) + "\n")
            for dest in traffic_flow[src].keys():
                file.write(str(dest) + ", " + str(traffic_flow[src][dest]) + "\n")


def generate_destination_trace(packet):
    dest_throughput = {0: {}, 1: {}, 2: {}, 3: {}}
    for src in range(0, 4):
        if os.path.isfile("pre/out/pre_dest_" + str(src) + ".txt"):
            with open("pre/out/pre_dest_" + str(src) + ".txt") as csv_file:
                lines = csv_file.readlines()
                for line in lines:
                    item = line.split("\t")
                    bytes_ = item[1][1:][:-1].split(",")
                    if int(item[0]) not in dest_throughput[src].keys():
                        dest_throughput[src].setdefault(int(item[0]), [])
                        for b in bytes_:
                            dest_throughput[src][int(item[0])].append(b)
                    else:
                        for b in bytes_:
                            dest_throughput[src][int(item[0])].append(b)

    for i in packet.keys():
        for j in range(len(packet[i])):
            if 192 <= int(packet[i][j][1].split(": ")[1]) <= 195 and 192 <= int(packet[i][j][2].split(": ")[1]) <= 195:
                if packet[i][j][0] == "L2_icnt_pop":
                    src = chip_select(int(packet[i][j][1].split(": ")[1]))
                    dest = chip_select(int(packet[i][j][2].split(": ")[1]))
                    time = int(packet[i][j][5].split(": ")[1])
                    byte = int(packet[i][j][7].split(": ")[1])
                    if time not in dest_throughput[src].keys():
                        dest_throughput[src].setdefault(time, []).append(byte)
                    else:
                        dest_throughput[src][time].append(byte)

    for src in range(0, 4):
        with open("pre/out/pre_dest_" + str(src) + ".txt", "w") as file:
            for time, byte in dest_throughput[src].items():
                file.write(str(time) + "\t" + str(byte) + "\n")


def calculate_hop_delay(packet):
    delay = {"FW": {0: {}, 1: {}, 2: {}, 3: {}}, "SM": {0: {}, 1: {}, 2: {}, 3: {}}, "llc": {0: {}, 1: {}, 2: {}, 3: {}}, "icnt": {0: {}, 1: {}, 2: {}, 3: {}}}
    delay_ = {"FW": {0: {}, 1: {}, 2: {}, 3: {}}, "SM": {0: {}, 1: {}, 2: {}, 3: {}}, "llc": {0: {}, 1: {}, 2: {}, 3: {}}, "icnt": {0: {}, 1: {}, 2: {}, 3: {}}}
    for buff in delay.keys():
        for chip in delay[buff].keys():
            if os.path.isfile("pre/out/" + str(buff) + str(chip) + ".csv"):
                with open("pre/out/" + str(buff) + str(chip) + ".csv", "r") as file:
                    lines = file.readlines()
                    for line in lines:
                        item = line.split(",")
                        delay[buff][chip][int(item[0])] = int(item[1])

    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "FW push":
                start = int(packet[id][j][8].split(": ")[1])
                for k in range(j + 1, len(packet[id])):
                    if packet[id][k][0] == "FW pop":
                        if (int(packet[id][k][8].split(": ")[1]) - start) not in delay["FW"][int(packet[id][j][6].split(": ")[1])].keys():
                            delay["FW"][int(packet[id][j][6].split(": ")[1])][int(packet[id][k][8].split(": ")[1]) - start] = 1
                        else:
                            delay["FW"][int(packet[id][j][6].split(": ")[1])][int(packet[id][k][8].split(": ")[1]) - start] += 1
                        break


            elif packet[id][j][0] == "icnt_llc_push":
                start = int(packet[id][j][8].split(": ")[1])
                for k in range(j + 1, len(packet[id])):
                    if packet[id][k][0] == "rop push":
                        if (int(packet[id][k][8].split(": ")[1]) - start) not in delay["icnt"][int(packet[id][j][6].split(": ")[1])].keys():
                            delay["icnt"][int(packet[id][j][6].split(": ")[1])][int(packet[id][k][8].split(": ")[1]) - start] = 1
                        else:
                            delay["icnt"][int(packet[id][j][6].split(": ")[1])][int(packet[id][k][8].split(": ")[1]) - start] += 1
                        break


            elif packet[id][j][0] == "SM push":
                start = int(packet[id][j][8].split(": ")[1])
                for k in range(j + 1, len(packet[id])):
                    if packet[id][k][0] == "SM pop":
                        if (int(packet[id][k][8].split(": ")[1]) - start) not in delay["SM"][int(packet[id][j][6].split(": ")[1])].keys():
                            delay["SM"][int(packet[id][j][6].split(": ")[1])][int(packet[id][k][8].split(": ")[1]) - start] = 1
                        else:
                            delay["SM"][int(packet[id][j][6].split(": ")[1])][int(packet[id][k][8].split(": ")[1]) - start] += 1
                        break

            elif packet[id][j][0] == "L2_icnt_push":
                start = int(packet[id][j][8].split(":")[1])
                for k in range(j + 1, len(packet[id])):
                    if packet[id][k][0] == "L2_icnt_pop":
                        if (int(packet[id][k][8].split(": ")[1]) - start) not in delay["llc"][int(packet[id][k][6].split(": ")[1])].keys():
                            delay["llc"][int(packet[id][k][6].split(": ")[1])][int(packet[id][k][8].split(": ")[1]) - start] = 1
                        else:
                            delay["llc"][int(packet[id][k][6].split(": ")[1])][int(packet[id][k][8].split(": ")[1]) - start] += 1
                        break

    for buff in delay.keys():
        for chip in delay[buff].keys():
            delay[buff][chip] = dict(sorted(delay[buff][chip].items(), key= lambda x: x[0]))


    for buff in delay.keys():
        for chip in delay[buff].keys():
            with open("pre/out/" + str(buff) + str(chip) + ".csv", "w") as file:
                for cyc, freq in delay[buff][chip].items():
                    file.write(str(cyc) + "," + str(freq) + "\n")


def cache_access(packet):
    hit_latency = {0: {}, 1: {}, 2: {}, 3: {}}
    miss_latency = {0: {}, 1: {}, 2: {}, 3: {}}
    access = {0: {"hit": 0, "miss": 0}, 1: {"hit": 0, "miss": 0}, 2: {"hit": 0, "miss": 0}, 3: {"hit": 0, "miss": 0}}
    lines = ""
    for i in hit_latency.keys():
        if os.path.isfile("pre/out/cache_access_hit" + str(i) + ".csv"):
            with open("pre/out/cache_access_hit" + str(i) + ".csv", "r") as file:
                lines = file.readlines()
            for line in lines:
                item = line.split(",")
                hit_latency[i][int(item[0])] = int(item[1])

    lines = ""
    for i in miss_latency.keys():
        if os.path.isfile("pre/out/cache_access_miss" + str(i) + ".csv"):
            with open("pre/out/cache_access_miss" + str(i) + ".csv", "r") as file:
                lines = file.readlines()
            for line in lines:
                item = line.split(",")
                miss_latency[i][int(item[0])] = int(item[1])

    lines = ""
    for i in access.keys():
        if os.path.isfile("pre/out/cache_access" + ".csv"):
            with open("pre/out/cache_access" + ".csv", "r") as file:
                lines = file.readlines()
            for line in lines:
                chip = int(line.split("-")[0])
                items = line.split("-")[1].split(",")
                access[chip]["hit"] += int(items[0].split(":")[1])
                access[chip]["miss"] += int(items[1].split(":")[1])

    del(lines)
    for i in packet.keys():
        chip = -1
        start = -1
        end = -1
        flag = -1
        for j in range(len(packet[i])):
            if packet[i][j][0] == "rop push":
                chip = int(packet[i][j][6].split(": ")[1])
                start = int(packet[i][j][8].split(": ")[1])
                flag = 1
            elif packet[i][j][0] == "L2_icnt_push" and flag == 1:
                end = int(packet[i][j][8].split(": ")[1])
                if "L2" in packet[i][j][9]:
                    if (end - start) not in hit_latency[chip].keys():
                        hit_latency[chip][end-start] = 1
                    else:
                        hit_latency[chip][end-start] += 1
                    access[chip]["hit"] += 1
                elif "DRAM" in packet[i][j][9]:
                    if (end - start) not in miss_latency[chip].keys():
                        miss_latency[chip][end-start] = 1
                    else:
                        miss_latency[chip][end-start] += 1
                    access[chip]["miss"] += 1
                    flag = 0
                break


    for i in hit_latency.keys():
        hit_latency[i] = dict(sorted(hit_latency[i].items(), key=lambda x: x[0]))
    for i in hit_latency.keys():
        with open("pre/out/cache_access_hit" + str(i) + ".csv", "w") as file:
            for duration, freq in hit_latency[i].items():
                file.write(str(duration) + ", " +  str(freq) + "\n") 

    for i in miss_latency.keys():
        miss_latency[i] = dict(sorted(miss_latency[i].items(), key=lambda x: x[0]))
    for i in miss_latency.keys():
        with open("pre/out/cache_access_miss" + str(i) + ".csv", "w") as file:
            for duration, freq in miss_latency[i].items():
                file.write(str(duration) + ", " +  str(freq) + "\n") 

    with open("pre/out/cache_access" + ".csv", "w") as file:
        for i in access.keys():
            file.write(str(i) + "-")
            for acc, freq in access[i].items():
                file.write( str(acc) +":"+ str(freq) + ",")
            file.write("\n")


if __name__ == '__main__':
    input_ = sys.argv[1]
    file2 = open(input_, "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]

        lined_list.append(item)
    cycle = {}
    del(raw_content)

    for i in range(len(lined_list)):  # cycle based classification
        if check_local_or_remote(lined_list[i]):
            if int(lined_list[i][8].split(": ")[1]) in cycle.keys():
                if lined_list[i] not in cycle[int(lined_list[i][8].split(": ")[1])]:
                    cycle.setdefault(int(lined_list[i][8].split(": ")[1]), []).append(lined_list[i])
            else:
                cycle.setdefault(int(lined_list[i][8].split(": ")[1]), []).append(lined_list[i])
    lined_list.clear()
    #destination_window_size(cycle)
    generate_throughput(cycle)
    calculate_overall_throughput()
    gc.collect()
    print("cycle start")
    injection_per_core(cycle)
    byte_per_cycle_dist()
    outser()
    del (throughput)
    gc.collect()
    del (throughput_update)
    gc.collect()
    del(cycle)

    print("packet start")
    packet = {}
    for i in range(len(lined_list)):  # packet based classification
        if check_local_or_remote(lined_list[i]):
            if int(lined_list[i][3].split(": ")[1]) in packet.keys():
                if lined_list[i] not in packet[int(lined_list[i][3].split(": ")[1])]:
                    packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
            else:
                packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
    #cache_access(packet)
    generate_link_utilization(packet)
    calculate_link_usage()
    generate_csv()
    del(iat_dist_csv)
    del(byte_dist_csv)
    generate_packet_type_ratio(packet)
    del(packet_type_ratio)
    del(link_utilization)
    generate_destination_trace(packet)
    del(packet)
    generate_traffic_flow()
