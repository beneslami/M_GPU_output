import csv
import math
from statistics import mode
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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


def window(packet):
    index = 5
    real_e = {}
    real_v = {}
    counter = 0
    w_counter = 0
    arr = []
    for i in packet.keys():
        if counter == index - 1:
            real_e[w_counter] = np.mean(arr)
            real_v[w_counter] = np.sqrt(np.var(arr))
            w_counter += 1
            counter = 0
            arr.clear()
        elif counter < index:
            arr.append(int(packet[i]))
            counter += 1
    with open("atax.model", "w") as file:
        for i in real_e.keys():
            file.write(str(i) + "- " + str(real_e[i]) + ": " + str(real_v[i]) + "\n")


if __name__ == "__main__":
    file2 = open("report_syrk.txt", "r")
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

    """for i in p.keys():
        for j in range(len(p[i])):
            if p[i][j][0] == "injection buffer":
                print("src: " + str(p[i][j][1].split(": ")[1]) + "\tdst: " + str(p[i][j][2].split(": ")[1]) + "\tbyte: " + str(p[i][j][7].split(": ")[1]) + "\tcycle: " + str(p[i][j][5].split(": ")[1]))
    """
    overall = {}
    for i in p.keys():
        for j in range(len(p[i])):
            if p[i][j][0] == "injection buffer":
                if int(p[i][j][5].split(": ")[1]) in overall.keys():
                    overall[int(p[i][j][5].split(": ")[1])] += int(p[i][j][7].split(": ")[1])
                else:
                    overall[int(p[i][j][5].split(": ")[1])] = int(p[i][j][7].split(": ")[1])
    for i in overall.keys():
        overall[i] = overall[i] / (4*3)
    overall_update = {}
    flag = 0
    prev = 0
    for i in overall.keys():
        if i > 0:
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
    mean_overall = np.mean(list(overall_update.values()))
    median_overall = np.median(list(overall_update.values()))
    s0 = {}
    s1 = {}
    s_0 = s_1 = 0
    for i in overall_update.keys():
        if overall_update[i] > mean_overall:
            s_1 += 1
            if overall_update[i] in s1.keys():
                s1[overall_update[i]] += 1
            else:
                s1[overall_update[i]] = 1
        else:
            s_0 += 1
            if overall_update[i] in s0.keys():
                s0[overall_update[i]] += 1
            else:
                s0[overall_update[i]] = 1

    print(s1)