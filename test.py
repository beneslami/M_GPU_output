import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import csv

if __name__ == "__main__":
    """arr = [
        [0, {136: 61037, 72: 32, 8: 60112}, {}, {136: 122228, 72: 64, 8: 176113}],
        [{8: 182204, 136: 129186}, 0, {8: 59841, 136: 62391}, {}],
        [{}, {8: 173009, 136: 132853}, 0, {136: 58877, 8: 52969}],
        [{8: 59390, 136: 57379}, {}, {136: 124051, 8: 167102, 72: 32}, 0]
    ]
    ticks = []
    string = ""
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if type(arr[i][j]) is dict:
                if len(arr[i][j]) != 0:
                    x = np.arange(len(arr[i][j]))
                    for k in arr[i][j].keys():
                        ticks.append(str(k))
                    plt.bar(x, list(arr[i][j].values()))
                    plt.xticks(x, ticks)
                    plt.xlabel("Packet Length")
                    plt.ylabel("occurrence")
                    string = "chip" + str(i) + " to chip" + str(j)
                    plt.title(string)
                    plt.show()
                    ticks.clear()"""
    constant = {}
    burst = {}
    threshold = 800
    constant_start = constant_end = 0
    burst_start = burst_end = 0
    with open('text_csv.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    for i in range(1, len(lined_list)):
        if int(lined_list[i][0].split(",")[1]) > threshold:
            burst_start = int(lined_list[i][0].split(",")[0])
            constant_end = int(lined_list[i][0].split(",")[0])
            if (constant_end - constant_start) in constant.keys():
                constant[constant_end - constant_start] += 1
            else:
                constant[constant_end - constant_start] = 1
        elif int(lined_list[i][0].split(",")[1]) <= threshold:
            constant_start = int(lined_list[i][0].split(",")[0])
            burst_end = int(lined_list[i][0].split(",")[0])
            if (burst_end - burst_start) in burst.keys():
                burst[burst_end - burst_start] += 1
            else:
                burst[burst_end - burst_start] = 1

    # plt.bar(list(constant.keys()), list(constant.values()))
    plt.bar(list(burst.keys()), list(burst.values()), width=20)
    plt.xlabel("period in cycle")
    plt.ylabel("frequency")
    plt.show()