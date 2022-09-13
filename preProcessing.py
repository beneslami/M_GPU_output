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

TIME = 8
TIME_2 = 8
request_injection = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
response_injection = {0: {}, 1: {}, 2: {}, 3: {}}
offered_throughput = {0: {}, 1: {}, 2: {}, 3: {}}
total_throughput = {}

dest_window = {0: {}, 1: {}, 2: {}, 3: {}}
iat_dist_csv = {0: {}, 1: {}, 2: {}, 3: {}}
byte_dist_csv = {0: {}, 1: {}, 2: {}, 3: {}}
packet_type_ratio = {0: {0: 0, 1: 0, 2: 0, 3: 0}, 1: {0: 0, 1: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 2: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0, 3: 0}}
link_utilization = {0: {1: {}, 2: {}, 3: {}}, 1: {0:{}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
req_link_utilization = {0: {1: {}, 2: {}, 3: {}}, 1: {0:{}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
resp_link_utilization = {0: {1: {}, 2: {}, 3: {}}, 1: {0:{}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
packet_latency = {0: {1: [], 2: [], 3: []}, 1: {0: [], 2: [], 3: []}, 2: {0: [], 1: [], 3: []}, 3: {0: [], 1: [], 2: []}}
network_latency = {0: {1: [], 2: [], 3: []}, 1: {0: [], 2: [], 3: []}, 2: {0: [], 1: [], 3: []}, 3: {0: [], 1: [], 2: []}}
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


def request_byte_per_core(packet):
    global request_injection
    for core in request_injection.keys():
        for dest in request_injection[core].keys():
            if os.path.isfile("pre/request_injection/pre_" + str(core) + "_" + str(dest) + ".txt"):
                with open("pre/request_injection/pre_" + str(core) + "_" + str(dest) + ".txt", "r") as file:
                    lines = file.readlines()
                for line in lines:
                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                    cycle = int(item[0])
                    byte = item[1].split("\n")[0][1:][:-1].split(", ")
                    request_injection[core][dest].setdefault(cycle, [])
                    for b in byte:
                        request_injection[core][dest][cycle].append(int(b))

    for i in packet.keys():
        for j in range(len(packet[i])):
            if 192 <= int(packet[i][j][1].split(": ")[1]) <= 195 and 192 <= int(packet[i][j][2].split(": ")[1]) <= 195:
                if packet[i][j][0] == "injection buffer":
                    source = chip_select(int(packet[i][j][1].split(": ")[1]))
                    dest = chip_select(int(packet[i][j][2].split(": ")[1]))
                    time = int(packet[i][j][TIME].split(": ")[1])
                    byte = int(packet[i][j][7].split(": ")[1])
                    if time not in request_injection[source][dest].keys():
                        request_injection[source][dest].setdefault(time, []).append(byte)
                    else:
                        request_injection[source][dest][time].append(byte)


def request_byte_per_core_out():
    global request_injection
    for core in request_injection.keys():
        for dest in request_injection[core].keys():
            path = "pre/request_injection/pre_" + str(core) + "_" + str(dest) + ".txt"
            with open(path, "w") as file:
                for cycle, byte in request_injection[core][dest].items():
                    file.write(str(cycle) + "\t" + str(byte) + "\n")


def response_byte_per_core(packet):
    global response_injection
    for core in response_injection.keys():
        if os.path.isfile("pre/response_injection/pre_" + str(core) + ".txt"):
            with open("pre/response_injection/pre_" + str(core) + ".txt", "r") as file:
                lines = file.readlines()
            for line in lines:
                item = [x for x in line.split("\t") if x not in ['', '\t']]
                cycle = int(item[0])
                byte = item[1].split("\n")[0][1:][:-1].split(", ")
                response_injection[core].setdefault(cycle, [])
                for b in byte:
                    response_injection[core][cycle].append(int(b))

    for i in packet.keys():
        for j in range(len(packet[i])):
            if 192 <= int(packet[i][j][1].split(": ")[1]) <= 195 and 192 <= int(packet[i][j][2].split(": ")[1]) <= 195:
                if packet[i][j][0] == "L2_icnt_pop":
                    source = chip_select(int(packet[i][j][1].split(": ")[1]))
                    time = int(packet[i][j][TIME].split(": ")[1])
                    byte = int(packet[i][j][7].split(": ")[1])
                    if time not in response_injection[source].keys():
                        response_injection[source].setdefault(time, []).append(byte)
                    else:
                        response_injection[source][time].append(byte)


def response_byte_per_core_out():
    global response_injection
    for core in response_injection.keys():
        path = "pre/response_injection/pre_" + str(core) + ".txt"
        with open(path, "w") as file:
            for cycle, byte in response_injection[core].items():
                file.write(str(cycle) + "\t" + str(byte) + "\n")


def cache_access(packet):
    hit_latency = {0: {}, 1: {}, 2: {}, 3: {}}
    miss_latency = {0: {}, 1: {}, 2: {}, 3: {}}
    access = {0: {"hit": 0, "miss": 0}, 1: {"hit": 0, "miss": 0}, 2: {"hit": 0, "miss": 0}, 3: {"hit": 0, "miss": 0}}
    lines = ""

    for i in hit_latency.keys():
        if os.path.isfile("pre/cache_access/cache_access_hit" + str(i) + ".csv"):
            with open("pre/cache_access/cache_access_hit" + str(i) + ".csv", "r") as file:
                lines = file.readlines()
            for line in lines:
                item = line.split(",")
                hit_latency[i][int(item[0])] = int(item[1])

    lines = ""
    for i in miss_latency.keys():
        if os.path.isfile("pre/cache_access/cache_access_miss" + str(i) + ".csv"):
            with open(    "pre/cache_access/cache_access_miss" + str(i) + ".csv", "r") as file:
                lines = file.readlines()
            for line in lines:
                item = line.split(",")
                miss_latency[i][int(item[0])] = int(item[1])

    lines = ""
    for i in access.keys():
        if os.path.isfile("pre/cache_access/cache_access" + ".csv"):
            with open("pre/cache_access/cache_access" + ".csv", "r") as file:
                lines = file.readlines()
            for line in lines:
                chip = int(line.split("-")[0])
                items = line.split("-")[1].split(",")
                access[chip]["hit"] += int(items[0].split(":")[1])
                access[chip]["miss"] += int(items[1].split(":")[1])

    for i in packet.keys():
        chip = -1
        start = -1
        end = -1
        flag = -1
        for j in range(len(packet[i])):
            if packet[i][j][0] == "rop push":
                chip = int(packet[i][j][6].split(": ")[1])
                start = int(packet[i][j][TIME].split(": ")[1])
                flag = 1
            elif packet[i][j][0] == "L2_icnt_push" and flag == 1:
                end = int(packet[i][j][TIME].split(": ")[1])
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
                    flag = -1
                break

    for i in hit_latency.keys():
        hit_latency[i] = dict(sorted(hit_latency[i].items(), key=lambda x: x[0]))
    for i in hit_latency.keys():
        with open("pre/cache_access/cache_access_hit" + str(i) + ".csv", "w") as file:
            for duration, freq in hit_latency[i].items():
                file.write(str(duration) + ", " + str(freq) + "\n")

    for i in miss_latency.keys():
        miss_latency[i] = dict(sorted(miss_latency[i].items(), key=lambda x: x[0]))
    for i in miss_latency.keys():
        with open("pre/cache_access/cache_access_miss" + str(i) + ".csv", "w") as file:
            for duration, freq in miss_latency[i].items():
                file.write(str(duration) + ", " + str(freq) + "\n")

    with open("pre/cache_access/cache_access" + ".csv", "w") as file:
        for i in access.keys():
            file.write(str(i) + "-")
            for acc, freq in access[i].items():
                file.write(str(acc) + ":" + str(freq) + ",")
            file.write("\n")


def generate_link_utilization(packet):

    for src in link_utilization.keys():
        for dest in link_utilization[src].keys():
            if os.path.isfile("pre/link_utilization/total/link_usage" + str(src) + "_" + str(dest) + "_per_cycle.txt"):
                with open("pre/link_utilization/total/link_usage" + str(src) + "_" + str(dest) + "_per_cycle.txt", "r") as file:
                    raw_content = file.readlines()
                for line in raw_content:
                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                    cycle = int(item[0])
                    bytes = item[1].split("\n")[0][1:][:-1].split(", ")
                    link_utilization[src][dest].setdefault(cycle, [])
                    for b in bytes:
                        link_utilization[src][dest][cycle].append(int(b))

            if os.path.isfile("pre/link_utilization/request/req_link_usage" + str(src) + "_" + str(dest) + "_per_cycle.txt"):
                with open(    "pre/link_utilization/request/req_link_usage" + str(src) + "_" + str(dest) + "_per_cycle.txt", "r") as file:
                    raw_content = file.readlines()
                for line in raw_content:
                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                    cycle = int(item[0])
                    bytes = item[1].split("\n")[0][1:][:-1].split(", ")
                    req_link_utilization[src][dest].setdefault(cycle, [])
                    for b in bytes:
                        req_link_utilization[src][dest][cycle].append(int(b))

            if os.path.isfile("pre/link_utilization/response/resp_link_usage" + str(src) + "_" + str(dest) + "_per_cycle.txt"):
                with open("pre/link_utilization/response/resp_link_usage" + str(src) + "_" + str(dest) + "_per_cycle.txt", "r") as file:
                    raw_content = file.readlines()
                for line in raw_content:
                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                    cycle = int(item[0])
                    bytes = item[1].split("\n")[0][1:][:-1].split(", ")
                    resp_link_utilization[src][dest].setdefault(cycle, [])
                    for b in bytes:
                        resp_link_utilization[src][dest][cycle].append(int(b))
    for i in packet.keys():
        src = dest = -1
        for j in range(len(packet[i])):
            if True:
                if packet[i][j][0] == "injection buffer":
                    src = int(packet[i][j][6].split(": ")[1])
                    time = int(packet[i][j][TIME_2].split(": ")[1])
                    byte = int(packet[i][j][7].split(": ")[1])
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "FW push" and (
                                int(packet[i][k][4].split(": ")[1]) == 0 or int(packet[i][k][4].split(": ")[1]) == 1):
                            dest = int(packet[i][k][6].split(": ")[1])
                            if time not in link_utilization[src][dest].keys():
                                link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                link_utilization[src][dest][time].append(byte)
                            if time not in req_link_utilization[src][dest].keys():
                                req_link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                req_link_utilization[src][dest][time].append(byte)
                            break
                        elif packet[i][k][0] == "rop push" and (
                                int(packet[i][k][4].split(": ")[1]) == 0 or int(packet[i][k][4].split(": ")[1]) == 1):
                            dest = int(packet[i][k][6].split(": ")[1])
                            if time not in link_utilization[src][dest].keys():
                                link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                link_utilization[src][dest][time].append(byte)
                            if time not in req_link_utilization[src][dest].keys():
                                req_link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                req_link_utilization[src][dest][time].append(byte)
                            break

                elif packet[i][j][0] == "FW pop":
                    src = int(packet[i][j][6].split(": ")[1])
                    time = int(packet[i][j][TIME_2].split(": ")[1])
                    byte = int(packet[i][j][7].split(": ")[1])
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "rop push" and (
                                int(packet[i][k][4].split(": ")[1]) == 0 or int(packet[i][k][4].split(": ")[1]) == 1):
                            dest = int(packet[i][k][6].split(": ")[1])
                            if time not in link_utilization[src][dest].keys():
                                link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                link_utilization[src][dest][time].append(byte)
                            if time not in req_link_utilization[src][dest].keys():
                                req_link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                req_link_utilization[src][dest][time].append(byte)
                            break
                        elif packet[i][k][0] == "SM pop" and (
                                int(packet[i][k][4].split(": ")[1]) == 2 or int(packet[i][k][4].split(": ")[1]) == 3):
                            dest = int(packet[i][k][6].split(": ")[1])
                            if time not in link_utilization[src][dest].keys():
                                link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                link_utilization[src][dest][time].append(byte)
                            if time not in resp_link_utilization[src][dest].keys():
                                resp_link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                resp_link_utilization[src][dest][time].append(byte)
                            break
                elif packet[i][j][0] == "L2_icnt_pop":
                    src = int(packet[i][j][6].split(": ")[1])
                    time = int(packet[i][j][TIME_2].split(": ")[1])
                    byte = int(packet[i][j][7].split(": ")[1])
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "FW push" and (
                                int(packet[i][k][4].split(": ")[1]) == 2 or int(packet[i][k][4].split(": ")[1]) == 3):
                            dest = int(packet[i][k][6].split(": ")[1])
                            if time not in link_utilization[src][dest].keys():
                                link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                link_utilization[src][dest][time].append(byte)
                            if time not in resp_link_utilization[src][dest].keys():
                                resp_link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                resp_link_utilization[src][dest][time].append(byte)
                            break
                        elif packet[i][k][0] == "SM pop" and (
                                int(packet[i][k][4].split(": ")[1]) == 2 or int(packet[i][k][4].split(": ")[1]) == 3):
                            dest = int(packet[i][k][6].split(": ")[1])
                            if time not in link_utilization[src][dest].keys():
                                link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                link_utilization[src][dest][time].append(byte)
                            if time not in resp_link_utilization[src][dest].keys():
                                resp_link_utilization[src][dest].setdefault(time, []).append(byte)
                            else:
                                resp_link_utilization[src][dest][time].append(byte)
                            break

    for src in req_link_utilization.keys():
        for dest in req_link_utilization[src].keys():
            with open("pre/link_utilization/request/req_link_usage" + str(src) + "_" + str(dest) + "_per_cycle.txt", "w") as file:
                for cycle, byte in req_link_utilization[src][dest].items():
                    file.write(str(cycle) + "\t" + str(byte) + "\n")

    for src in resp_link_utilization.keys():
        for dest in resp_link_utilization[src].keys():
            with open("pre/link_utilization/response/resp_link_usage" + str(src) + "_" + str(dest) + "_per_cycle.txt", "w") as file:
                for cycle, byte in resp_link_utilization[src][dest].items():
                    file.write(str(cycle) + "\t" + str(byte) + "\n")

    for src in link_utilization.keys():
        for dest in link_utilization[src].keys():
            with open("pre/link_utilization/total/link_usage" + str(src) + "_" + str(dest) + "_per_cycle.txt", "w") as file:
                for cycle, byte in link_utilization[src][dest].items():
                    file.write(str(cycle) + "\t" + str(byte) + "\n")


def generate_throughput(packet):
    global total_throughput
    global offered_throughput
    if os.path.isfile("pre/throughput/total_throughput.txt"):
        with open("pre/throughput/total_throughput.txt", "r") as csv_file:
            rows = csv_file.readlines()
            for line in rows:
                row = [x for x in line.split(",")]
                total_throughput[int(row[0])] = int(row[1])

    for i in packet.keys():
        for j in range(len(packet[i])):
            if 192 <= int(packet[i][j][1].split(": ")[1]) <= 195 and 192 <= int(packet[i][j][2].split(": ")[1]) <= 195:
                if packet[i][j][0] == "injection buffer":
                    if int(packet[i][j][TIME_2].split(": ")[1]) not in total_throughput.keys():
                        total_throughput[int(packet[i][j][TIME_2].split(": ")[1])] = int(packet[i][j][7].split(": ")[1])
                    else:
                        total_throughput[int(packet[i][j][TIME_2].split(": ")[1])] += int(packet[i][j][7].split(": ")[1])
                    if int(packet[i][j][TIME_2].split(": ")[1]) not in offered_throughput[chip_select(int(packet[i][j][1].split(": ")[1]))].keys():
                        offered_throughput[chip_select(int(packet[i][j][1].split(": ")[1]))][int(packet[i][j][TIME_2].split(": ")[1])] = int(packet[i][j][7].split(": ")[1])
                    else:
                        offered_throughput[chip_select(int(packet[i][j][1].split(": ")[1]))][int(packet[i][j][TIME_2].split(": ")[1])] += int(packet[i][j][7].split(": ")[1])

                elif packet[i][j][0] == "rop push":
                    if int(packet[i][j][TIME_2].split(": ")[1]) not in total_throughput.keys():
                        total_throughput[int(packet[i][j][TIME_2].split(": ")[1])] = -int(packet[i][j][7].split(": ")[1])
                    else:
                        total_throughput[int(packet[i][j][TIME_2].split(": ")[1])] -= int(packet[i][j][7].split(": ")[1])

                elif packet[i][j][0] == "L2_icnt_push":
                    if int(packet[i][j][TIME_2].split(": ")[1]) not in total_throughput.keys():
                        total_throughput[int(packet[i][j][TIME_2].split(": ")[1])] = int(packet[i][j][7].split(":")[1])
                    else:
                        total_throughput[int(packet[i][j][TIME_2].split(": ")[1])] += int(packet[i][j][7].split(":")[1])
                    if int(packet[i][j][TIME_2].split(": ")[1]) not in offered_throughput[chip_select(int(packet[i][j][1].split(": ")[1]))].keys():
                        offered_throughput[chip_select(int(packet[i][j][1].split(": ")[1]))][int(packet[i][j][TIME_2].split(": ")[1])] = int(packet[i][j][7].split(":")[1])
                    else:
                        offered_throughput[chip_select(int(packet[i][j][1].split(": ")[1]))][int(packet[i][j][TIME_2].split(": ")[1])] += int(packet[i][j][7].split(":")[1])

                elif packet[i][j][0] == "SM pop":
                    if int(packet[i][j][TIME_2].split(": ")[1]) not in total_throughput.keys():
                        total_throughput[int(packet[i][j][TIME_2].split(": ")[1])] = -int(packet[i][j][7].split(": ")[1])
                    else:
                        total_throughput[int(packet[i][j][TIME_2].split(": ")[1])] -= int(packet[i][j][7].split(": ")[1])

    total_throughput = dict(sorted(total_throughput.items(), key=lambda x: x[0]))

    with open("pre/throughput/total_throughput.txt", "w") as csv_file:
        for cyc, byte in total_throughput.items():
            csv_file.write(str(cyc) + "," + str(byte) + "\n")


def calculate_overall_throughput():
    global data
    global offered_throughput
    if os.path.isfile("pre/throughput/throughput_param.csv"):
        with open("pre/throughput/throughput_param.csv", "r") as csv_file:
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
    with open("pre/throughput/throughput_param.csv", "w") as file:
        for src in data.keys():
            file.write(str(src) + "\n")
            for byte, dist in data[src].items():
                file.write(str(byte) + "," + str(dist) + "\n")


def rop_buffer(packet):
    window = {0 : {}, 1: {}, 2: {}, 3: {}}
    lines = ""
    for src in window.keys():
        if os.path.isfile("pre/buffers/rop_buffer_" + str(src) + ".txt"):
            with open("pre/buffers/rop_buffer_" + str(src) + ".txt", "r") as file:
                lines = file.readlines()
            for line in lines:
                item = [x for x in line.split("\t") if x not in ['', '\t']]
                time = int(item[0])
                byte = item[1].split("\n")[0][1:][:-1].split(", ")
                window[src].setdefault(time, [])
                for b in byte:
                    window[src][time].append(int(b))

    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "rop push":
                chip = int(packet[i][j][6].split(": ")[1])
                time = int(packet[i][j][TIME].split(": ")[1])
                byte = int(packet[i][j][7].split(": ")[1])
                if time not in window[chip].keys():
                    window[chip].setdefault(time, []).append(byte)
                else:
                    window[chip][time].append(byte)

    for src in window.keys():
        with open("pre/buffers/rop_buffer_" + str(src) + ".txt", "w") as file:
            for time, byte in window[src].items():
                file.write(str(time) + "\t" + str(byte) + "\n")


def sm_buffer(packet):
    window = {0 : {}, 1: {}, 2: {}, 3: {}}
    lines = ""
    for src in window.keys():
        if os.path.isfile("pre/buffers/sm_buffer_" + str(src) + ".txt"):
            with open("pre/buffers/sm_buffer_" + str(src) + ".txt", "r") as file:
                lines = file.readlines()
            for line in lines:
                item = [x for x in line.split("\t") if x not in ['', '\t']]
                time = int(item[0])
                byte = item[1].split("\n")[0][1:][:-1].split(", ")
                window[src].setdefault(time, [])
                for b in byte:
                    window[src][time].append(int(b))

    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "SM pop":
                chip = int(packet[i][j][6].split(": ")[1])
                time = int(packet[i][j][TIME].split(": ")[1])
                byte = int(packet[i][j][7].split(": ")[1])
                if time not in window[chip].keys():
                    window[chip].setdefault(time, []).append(byte)
                else:
                    window[chip][time].append(byte)
                break

    for src in window.keys():
        with open("pre/buffers/sm_buffer_" + str(src) + ".txt", "w") as file:
            for time, byte in window[src].items():
                file.write(str(time) + "\t" + str(byte) + "\n")


def fw_buffer(packet):
    window = {0 : {}, 1: {}, 2: {}, 3: {}}
    lines = ""
    for src in window.keys():
        if os.path.isfile("pre/buffers/fw_buffer_" + str(src) + ".txt"):
            with open("pre/buffers/fw_buffer_" + str(src) + ".txt", "r") as file:
                lines = file.readlines()
            for line in lines:
                item = [x for x in line.split("\t") if x not in ['', '\t']]
                time = int(item[0])
                byte = item[1].split("\n")[0][1:][:-1].split(", ")
                window[src].setdefault(time, [])
                for b in byte:
                    window[src][time].append(int(b))

    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "FW pop":
                chip = int(packet[i][j][6].split(": ")[1])
                time = int(packet[i][j][TIME_2].split(": ")[1])
                byte = int(packet[i][j][7].split(": ")[1])
                if time not in window[chip].keys():
                    window[chip].setdefault(time, []).append(byte)
                else:
                    window[chip][time].append(byte)
                break

    for src in window.keys():
        with open("pre/buffers/fw_buffer_" + str(src) + ".txt", "w") as file:
            for time, byte in window[src].items():
                file.write(str(time) + "\t" + str(byte) + "\n")


def pending_buffer(packet):
    window = {0 : {}, 1: {}, 2: {}, 3: {}}
    lines = ""
    for src in window.keys():
        if os.path.isfile("pre/buffers/pending_buffer_" + str(src) + ".txt"):
            with open("pre/buffers/pending_buffer_" + str(src) + ".txt", "r") as file:
                lines = file.readlines()
            for line in lines:
                item = [x for x in line.split("\t") if x not in ['', '\t']]
                time = int(item[0])
                byte = item[1].split("\n")[0][1:][:-1].split(", ")
                window[src].setdefault(time, [])
                for b in byte:
                    window[src][time].append(int(b))

    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "L2_icnt_pop":
                chip = int(packet[i][j][6].split(": ")[1])
                time = int(packet[i][j][TIME].split(": ")[1])
                byte = int(packet[i][j][7].split(": ")[1])
                if time not in window[chip].keys():
                    window[chip].setdefault(time, []).append(byte)
                else:
                    window[chip][time].append(byte)
                break

    for src in window.keys():
        window[src] = dict(sorted(window[src].items(), key=lambda x: x[0]))

    for src in window.keys():
        with open("pre/buffers/pending_buffer_" + str(src) + ".txt", "w") as file:
            for time, byte in window[src].items():
                file.write(str(time) + "\t" + str(byte) + "\n")


def calculate_packet_type(packet):
    type_ = {0: {0: 0, 1: 0, 2: 0, 3: 0}, 1: {0: 0, 1: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 2: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0, 3: 0}}
    for src in type_.keys():
        lines = ""
        if os.path.isfile("pre/throughput/packet_type_" + str(src) + ".txt"):
            with open("pre/throughput/packet_type_" + str(src) + ".txt", "r") as file:
                lines = file.readlines()
            for line in lines:
                t = int(line.split(",")[0])
                v = int(line.split(",")[1])
                type_[src][t] += v

    for i in packet.keys():
        for j in range(len(packet[i])):
            src = int(packet[i][j][6].split(": ")[1])
            t = int(packet[i][j][4].split(": ")[1])
            if packet[i][j][0] == "injection buffer":
                type_[src][t] += 1
            elif packet[i][j][0] == "L2_icnt_push":
                type_[src][t] += 1

    for src in type_.keys():
        with open("pre/throughput/packet_type_" + str(src) + ".txt", "w") as file:
            for t, v in type_[src].items():
                file.write(str(t) + "," + str(v) + "\n")


def fw_injection_rate(packet):
    forwarding = {0: 0, 1: 0, 2: 0, 3: 0}
    fw = {0: {}, 1: {}, 2: {}, 3: {}}

    if os.path.isfile("pre/forwarding.txt"):
        lines = ""
        with open("pre/forwarding.txt", "r") as file:
            lines = file.readlines()
        for line in lines:
            items = line.split(", ")
            forwarding[int(items[0])] = int(items[1])

    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "FW pop":
                 src = int(packet[i][j][6].split(": ")[1])
                 time = int(packet[i][j][8].split(": ")[1])
                 byte = int(packet[i][j][7].split(": ")[1])
                 if time not in fw[src].keys():
                     fw[src].setdefault(time, []).append(byte)
                 else:
                     fw[src][time].append(byte)
    for src in fw.keys():
        for time, byte in fw[src].items():
            forwarding[src] += 1

    with open("pre/forwarding.txt", "w") as file:
         for src in forwarding.keys():
            file.write(str(src) + ", " + str(forwarding[src]) +"\n")


def fw_iat(packet,):
    temp = {0: {}, 1: {}, 2: {}, 3: {}}
    prev = 0
    for src in temp.keys():
        lines = ""
        with open("pre/request_injection/fw_iat_" + str(src) + ".csv", "r") as file:
            lines = file.readlines()
        for line in lines:
            items = line.split(", ")
            duration = int(items[0])
            freq     = int(items[1])
            temp[duration] = freq

    for src in packet.keys():
        for j in range(len(packet[src])):
            if packet[src][j][0] == "FW pop":
                time = int(packet[src][j][TIME].split(": ")[1])
                if(time - prev) not in temp[src].keys():
                    temp[src][time - prev] = 1
                else:
                    temp[src][time - prev] += 1
                prev = time

    for src in temp.keys():
        with open("pre/request_injection/fw_iat_" + str(src) + ".csv", "w") as file:
            for duration, freq in temp[src].items():
                file.write(str(duration) + ", " + str(freq) + "\n")


def l2_icnt_push(packet):
    pending = {0: {}, 1: {}, 2: {}, 3: {}}
    dist = {0: {}, 1: {}, 2: {}, 3: {}}
    for src in dist.keys():
        if os.path.isfile("pre/response_injection/l2_icnt_" + str(src) + ".csv"):
            lines = ""
            with open("pre/response_injection/l2_icnt_" + str(src) + ".csv", "r") as file:
                lines = file.readlines()
            for line in lines:
                items = line.split(",")
                win = int(items[0])
                freq = int(items[1])
                dist[src][win] = freq

    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "L2_icnt_push":
                src = int(packet[i][j][6].split(": ")[1])
                time = int(packet[i][j][8].split(": ")[1])
                byte = int(packet[i][j][7].split(":")[1])
                if time not in pending[src].keys():
                    pending[src][time] = 1
                else:
                    pending[src][time] += 1
    for src in pending.keys():
        for time, freq in pending[src].items():
            if freq not in dist[src].keys():
                dist[src][freq] = 1
            else:
                dist[src][freq] += 1
    for src in dist.keys():
        dist[src] = dict(sorted(dist[src].items(), key=lambda x: x[0]))

    for src in dist.keys():
        with open("pre/response_injection/l2_icnt_" + str(src) + ".csv", "w") as file:
            for win, freq in dist[src].items():
                file.write(str(win) + "," + str(freq) + "\n")


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
    del(raw_content)

    if not os.path.isdir("pre/buffers/"):
        os.mkdir("pre/buffers/")
        os.mkdir("pre/cache_access/")
        os.mkdir("pre/link_utilization/")
        os.mkdir("pre/request_injection/")
        os.mkdir("pre/response_injection/")
        os.mkdir("pre/throughput/")
    if not os.path.isdir("pre/link_utilization/total"):
        os.mkdir("pre/link_utilization/total/")
        os.mkdir("pre/link_utilization/request/")
        os.mkdir("pre/link_utilization/response/")

    packet = {}
    for i in range(len(lined_list)):  # packet based classification
        if check_local_or_remote(lined_list[i]):
            if int(lined_list[i][3].split(": ")[1]) in packet.keys():
                if lined_list[i] not in packet[int(lined_list[i][3].split(": ")[1])]:
                    packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
            else:
                packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])

    request_byte_per_core(packet)
    request_byte_per_core_out()
    response_byte_per_core(packet)
    response_byte_per_core_out()
    generate_link_utilization(packet)
    generate_throughput(packet)
    calculate_overall_throughput()
    calculate_packet_type(packet)

    rop_buffer(packet)
    sm_buffer(packet)
    fw_buffer(packet)
    pending_buffer(packet)
    cache_access(packet)
    fw_injection_rate(packet)
    l2_icnt_push(packet)