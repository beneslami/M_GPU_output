import math
from statistics import mean, stdev
import matplotlib.pyplot as plt
from scipy.stats import stats
from sklearn.linear_model import LinearRegression
import numpy as np

def RS(lined_list):
    time_byte = {}
    windows = {}
    duration = 200000
    M = math.ceil(math.log(duration, 2))

    for i in range(1, len(lined_list)):
        if int(lined_list[i][0].split(",")[0]) in time_byte.keys():
            time_byte[int(lined_list[i][0].split(",")[0])] += int(lined_list[i][0].split(",")[1])
        else:
            time_byte[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])

    j = 1
    for wnd in range(1, M):
        for key, value in time_byte.items():
            if key <= j * int(duration / wnd):
                if wnd in windows.keys():
                    if j in windows[wnd].keys():
                        windows[wnd].setdefault(j, []).append(value)
                    else:
                        windows.setdefault(wnd, {}).setdefault(j, []).append(value)
                else:
                    windows.setdefault(wnd, {})
                    windows[wnd].setdefault(j, []).append(value)
            else:
                if j < wnd:
                    j += 1
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
    thresh = 0
    sum_ = 0
    for w in range(1, M):
        for i in windows[w].keys():
            for j in range(len(windows[w][i])):
                sum_ += windows[w][i][j]
                if j == thresh:
                    if w in y.keys():
                        if i in y[w].keys():
                            y[w][i][thresh+1] = sum_ - (j+1)*mean_set[w][i]
                        else:
                            y[w].setdefault(i, {})[thresh+1] = sum_ - (j+1)*mean_set[w][i]
                    else:
                        y.setdefault(w, {}).setdefault(i, {})[thresh+1] = sum_ - (j+1)*mean_set[w][i]
                thresh += 1
            thresh = 0
            sum_ = 0

    range_set = {}
    for w in range(1, M):
        for i in y[w].keys():
            max = y[w][i][1]
            min = y[w][i][1]
            for j in range(1, len(y[w][i])):
                if y[w][i][j] > max:
                    max = y[w][i][j]
                    continue
                elif y[w][i][j] < min:
                    min = y[w][i][j]
                    continue
            if w in range_set.keys():
                if i in range_set[w].keys():
                    range_set[w][i] = max - min
                else:
                    range_set[w][i] = max - min
            else:
                range_set.setdefault(w, {})[i] = max - min

    sd_set = {}
    for w in range(1, M):
        for i in windows[w].keys():
            temp = np.std(windows[w][i])
            if w in sd_set.keys():
                if i in sd_set[w].keys():
                    sd_set[w][i] = temp
                else:
                    sd_set[w][i] = temp
            else:
                sd_set.setdefault(w, {})[i] = temp

    rs = {}
    for w in range(1, M):
        for i in windows[w].keys():
            temp = range_set[w][i]/sd_set[w][i]
            if w in rs.keys():
                if i in rs[w].keys():
                    rs[w][i] = temp
                else:
                    rs[w][i] = temp
            else:
                rs.setdefault(w, {})[i] = temp

    E = {}
    for i in rs.keys():
        temp = 0
        for j in rs[i].keys():
            temp += rs[i][j]
        E[math.log(len(rs[i]), 10)] = math.log(temp/len(rs[i]), 10)

    slope, intercept, r, p, std_err = stats.linregress(list(E.keys()), list(E.values()))
    arr = []
    for i in E.keys():
        arr.append(slope*i + intercept)
    plt.scatter(list(E.keys()), list(E.values()))
    plt.plot(list(E.keys()), arr, color="red", linewidth=2)
    plt.text(0.8, 3.60, "slope = " + str("{:.3f}".format(slope)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    plt.xlabel("log-window")
    plt.ylabel("log-R/S")
    plt.show()


if __name__ == "__main__":
    with open('atax.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    RS(lined_list)