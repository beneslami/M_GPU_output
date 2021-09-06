import csv
import math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

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

def chip_select(num):
    out = -1
    if num < 4:
        return num
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
    for i in range(len(chiplet)):
        if (int(x[1].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[1].split(": ")[1]) in chiplet[i]["LLC_ID"]):
            if (int(x[2].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[2].split(": ")[1]) in chiplet[i]["LLC_ID"]):
                return 0
        return 1


def state_change_distribution(traf, order):
    flag = 0
    point = 0
    inter_arrival = {}
    l = sorted(order.items(), key=lambda x: x[0])
    for i in range(len(l)):
        for cycle, byte in traf.items():
            if l[i][0] == byte and flag == 0:
                point = cycle
                flag = 1
            elif l[i][0] == byte and flag == 1:
                pass
            elif l[i][0] != byte and flag == 1:
                if byte not in inter_arrival.keys():
                    inter_arrival.setdefault(l[i][0], []).append(cycle - point)
                else:
                    inter_arrival.setdefault(l[i][0], []).append(cycle - point)
                flag = 0

    for i in inter_arrival.keys():
        dist = {}
        for j in range(len(inter_arrival[i])):
            if inter_arrival[i][j] in dist.keys():
                dist[inter_arrival[i][j]] += 1
            else:
                dist[inter_arrival[i][j]] = 1
        file.write("BYTE_" + str("{:.3f}".format(i)) + "_INTERARRIVAL_DISTRIBUTION-BEGIN\n")
        orders = sorted(dist.items(), key=lambda x: x[0])
        for j in range(len(orders)):
            file.write(str(orders[j][0]) + " " + str(orders[j][1]) + "\n")
        file.write("BYTE_" + str("{:.3f}".format(i)) + "_INTERARRIVAL_DISTRIBUTION-END\n\n")


if __name__ == "__main__":
    file2 = open("report_syrk.txt", "r")
    file = open("syrk.model", "w")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    p = {}
    for i in range(len(lined_list)):  # cycle based classification
        if lined_list[i][0] != "Instruction cache miss":
            if chip_select(int(lined_list[i][1].split(": ")[1])) != chip_select(int(lined_list[i][2].split(": ")[1])):
                if int(lined_list[i][5].split(": ")[1]) in p.keys():
                    if lined_list[i] not in p[int(lined_list[i][5].split(": ")[1])]:
                        p.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])
                else:
                    p.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])
    overall = {}
    for i in p.keys():
        for j in range(len(p[i])):
            if p[i][j][0] == "injection buffer":
                if int(p[i][j][5].split(": ")[1]) in overall.keys():
                    overall[int(p[i][j][5].split(": ")[1])] += int(p[i][j][7].split(": ")[1])
                else:
                    overall[int(p[i][j][5].split(": ")[1])] = int(p[i][j][7].split(": ")[1])
    for i in overall.keys():
        overall[i] = overall[i]/(4*3)
    overall_update = {}
    flag = 0
    prev = 0
    for i in overall.keys():
        if i > 1100:
            if flag == 0:
                overall_update[i] = overall[i]
                prev = i
                flag = 1
            elif flag == 1:
                if i - prev > 1:
                    for j in range(i - prev):
                        overall_update[prev + j + 1] = 0
                    overall_update[i] = overall[i]
                    prev = i
                else:
                    overall_update[i] = overall[i]
                    prev = i

    with open("example2.txt", "w") as ff:
        for i in overall_update.keys():
            ff.write(str(i) + ": " + str(overall_update[i]) + "\n")


    """file.write("DESTINATION_DISTRIBUTION-BEGIN\n")
    file.write("uniform\n")
    file.write("DESTINATION_DISTRIBUTION-END\n\n")
    dist = {}
    for i in overall_update.values():
        if i in dist.keys():
            dist[i] += 1
        else:
            dist[i] = 1
    file.write("BYTE_DISTRIBUTION-BEGIN\n")
    sort_orders = sorted(dist.items(), key=lambda x: x[0])
    for i in sort_orders:
        file.write(str("{:.3f}".format(i[0])) + " " + str(i[1]) + "\n")
    file.write("BYTE_DISTRIBUTION-END\n\n")
    state_change_distribution(overall_update, dist)
    dist.clear()"""

