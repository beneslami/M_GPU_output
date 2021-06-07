import csv
import math
import matplotlib.pyplot as plt
from scipy.stats import stats
import numpy as np
import pandas as pd
from hurst import compute_Hc, random_walk


def RS(lined_list):
    time_byte = {}
    windows = {}
    duration = 1000000
    M = math.ceil(math.log(duration, 2))

    for i in range(1, len(lined_list)):
        if int(lined_list[i][0].split(",")[0]) in time_byte.keys():
            time_byte[int(lined_list[i][0].split(",")[0])] += float(lined_list[i][0].split(",")[1])
        else:
            time_byte[int(lined_list[i][0].split(",")[0])] = float(lined_list[i][0].split(",")[1])

    j = 1
    for wnd in range(1, M):
        for key, value in time_byte.items():
            if key <= j * int(duration / wnd):
                if wnd in windows.keys():
                    if j in windows[wnd].keys():
                        windows[wnd][j].append(value)
                    else:
                        windows.setdefault(wnd, {}).setdefault(j, []).append(value)
                else:
                    windows.setdefault(wnd, {})
                    windows[wnd].setdefault(j, []).append(value)
            else:
                if j < wnd:
                    j += 1
                if wnd in windows.keys():
                    if j in windows[wnd].keys():
                        windows[wnd][j].append(value)
                    else:
                        windows.setdefault(wnd, {}).setdefault(j, []).append(value)
                else:
                    windows.setdefault(wnd, {})
                    windows[wnd].setdefault(j, []).append(value)
        j = 1

    mean_set = {}
    for w in range(1, M):
        for i in windows[w].keys():
            mean_temp = np.mean(windows[w][i])
            if w in mean_set.keys():
                if i in mean_set[w].keys():
                    mean_set[w][i] = mean_temp
                else:
                    mean_set[w][i] = mean_temp
            else:
                mean_set.setdefault(w, {})[i] = mean_temp

    y = {}
    for w in range(1, M):
        for i in windows[w].keys():
            sum_ = np.cumsum(windows[w][i])
            for item in range(len(sum_)):
                sum_[item] = sum_[item] - (item+1)*mean_set[w][i]
            if w in y.keys():
                y[w][i] = sum_
            else:
                y.setdefault(w, {})[i] = sum_

    range_set = {}
    for w in range(1, M):
        for i in y[w].keys():
            max = y[w][i][0]
            min = y[w][i][0]
            for j in range(1, len(y[w][i])):
                if y[w][i][j] > max:
                    max = y[w][i][j]
                    continue
                elif y[w][i][j] < min:
                    min = y[w][i][j]
                    continue
            if w in range_set.keys():
                range_set[w][i] = max - min
            else:
                range_set.setdefault(w, {})[i] = max - min

    sd_set = {}
    for w in range(1, M):
        for i in windows[w].keys():
            temp = np.std(windows[w][i])
            if w in sd_set.keys():
                sd_set[w][i] = temp
            else:
                sd_set.setdefault(w, {})[i] = temp

    rs = {}
    for w in range(1, M):
        for i in windows[w].keys():
            temp = range_set[w][i]/sd_set[w][i]
            if w in rs.keys():
                rs[w][i] = temp
            else:
                rs.setdefault(w, {})[i] = temp

    E = {}
    for i in rs.keys():
        temp = 0
        for j in rs[i].keys():
            temp += rs[i][j]
        E[math.log(len(rs[i]), 10)] = math.log(temp, 10)

    slope, intercept, r, p, std_err = stats.linregress(list(E.keys()), list(E.values()))
    arr = []
    x1 = np.linspace(0, 2.7, 20)
    y1 = x1
    y2 = x1/2
    for i in E.keys():
        arr.append(slope*i + intercept)
    plt.scatter(list(E.keys()), list(E.values()))
    #plt.plot(list(E.keys()), arr, color="red", linewidth=2)
    plt.plot(x1, y1)
    plt.plot(x1, y2)
    plt.text(0, 4.250, "slope = " + str("{:.3f}".format(slope)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    plt.xlabel("log-window")
    plt.ylabel("log-R/S")
    plt.show()


def hurst(lined_list):
    time_byte = {}
    for i in range(1, len(lined_list)):
        if int(lined_list[i][0].split(",")[0]) in time_byte.keys():
            time_byte[int(lined_list[i][0].split(",")[0])] += float(lined_list[i][0].split(",")[1])
        else:
            time_byte[int(lined_list[i][0].split(",")[0])] = float(lined_list[i][0].split(",")[1])
    H, c, data = compute_Hc(list(time_byte.values()), simplified=True)
    f, ax = plt.subplots()
    ax.plot(data[0], c * data[0] ** H, color="deepskyblue")
    ax.scatter(data[0], data[1], color="purple")
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.text(10000, 5, "slope = " + str("{:.3f}".format(H)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax.set_xlabel('Time interval')
    ax.set_ylabel('R/S ratio')
    #ax.grid(True)
    plt.show()
    print("H={:.4f}, c={:.4f}".format(H, c))


if __name__ == "__main__":
    with open('synthetic.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    arr = {}
    for i in range(1, len(lined_list)):
        arr[int(lined_list[i][0].split(",")[0])] = float(lined_list[i][0].split(",")[1])

    plt.figure(figsize=(25, 5))
    plt.plot(list(arr.keys()), list(arr.values()))
    plt.show()