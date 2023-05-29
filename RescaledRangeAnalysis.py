import math
import sys

import matplotlib.pyplot as plt
import scipy
from scipy.stats import stats
import numpy as np
from hurst import compute_Hc


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


def hurst(base_path, lined_list, string):
    H, c, data = compute_Hc(lined_list, simplified=True)
    f, ax = plt.subplots()
    ax.plot(data[0], c * data[0] ** H, color="deepskyblue")
    ax.scatter(data[0], data[1], color="purple")
    ax.set_xscale('log')
    ax.set_yscale('log')
    min_xdim, max_xdim = plt.xlim()
    min_ydim, max_ydim = plt.ylim()
    plt.text((min_xdim+max_xdim)/3, (min_ydim+max_ydim)/3, "slope = " + str("{:.3f}".format(H)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax.set_xlabel('Time interval')
    ax.set_ylabel('R/S ratio')
    #ax.grid(True)
    plt.savefig(base_path + "/plots/hurst_" + string + ".jpg")
    plt.close()
    print("H={:.4f}, c={:.4f}".format(H, c))


def hurst_compute(base_path, overall, string):
    burst_length = []
    burst_ratio = []
    burst_length_dist = {}
    burst_amount_dist = {}
    burst_length_value = {}
    burst_length_value_ = {}
    start_flag = 0
    prev_cycle = 0
    aggregate_burst = 0
    for cycle, byte in overall.items():
        if byte != 0:
            if start_flag == 0:
                start_flag = 1
                prev_cycle = cycle
            aggregate_burst += byte
        elif byte == 0:
            if start_flag == 1:
                burst_length.append(cycle - prev_cycle)
                burst_ratio.append(aggregate_burst/(cycle - prev_cycle))
                if cycle - prev_cycle not in burst_length_dist.keys():
                    burst_length_dist[cycle - prev_cycle] = 1
                else:
                    burst_length_dist[cycle - prev_cycle] += 1
                if aggregate_burst not in burst_amount_dist.keys():
                    burst_amount_dist[aggregate_burst] = 1
                else:
                    burst_amount_dist[aggregate_burst] += 1
                if cycle - prev_cycle not in burst_length_value.keys():
                    burst_length_value[cycle - prev_cycle] = aggregate_burst
                else:
                    burst_length_value[cycle - prev_cycle] += aggregate_burst

                if cycle - prev_cycle not in burst_length_value_.keys():
                    burst_length_value_.setdefault(cycle - prev_cycle, {})[aggregate_burst] = 1
                else:
                    if aggregate_burst not in burst_length_value_[cycle - prev_cycle].keys():
                        burst_length_value_[cycle - prev_cycle][aggregate_burst] = 1
                    else:
                        burst_length_value_[cycle - prev_cycle][aggregate_burst] += 1
                start_flag = 0
                aggregate_burst = 0

    burst_length_dist = dict(sorted(burst_length_dist.items(), key=lambda x: x[0]))
    burst_amount_dist = dict(sorted(burst_amount_dist.items(), key=lambda x: x[0]))
    burst_length_value = dict(sorted(burst_length_value.items(), key=lambda x: x[0]))
    burst_length_value_ = dict(sorted(burst_length_value_.items(), key=lambda x: x[0]))
    for c in burst_length_value_.keys():
        burst_length_value_[c] = dict(sorted(burst_length_value_[c].items(), key=lambda x: x[0]))

    with open(base_path + "/data/burst_length_value_dependency.csv", "w") as file:
        file.write("burst,amount,freq\n")
        for c in burst_length_value_.keys():
            file.write(str(c) + ",")
            flag = 0
            for byte, freq in burst_length_value_[c].items():
                if flag == 0:
                    file.write(str(byte) + "," + str(freq) + "\n")
                    flag = 1
                elif flag == 1:
                    file.write("," + str(byte) + "," + str(freq) + "\n")

    burst_length_pdf = {}
    burst_amount_pdf = {}
    for length, freq in burst_length_dist.items():
        burst_length_pdf[length] = freq / sum(burst_length_dist.values())
    for amount, freq in burst_amount_dist.items():
        burst_amount_pdf[amount] = freq / sum(burst_amount_dist.values())
    with open(base_path + "/data/burst_length_distribution.csv", "w") as file:
        file.write("duration,pdf\n")
        for k, v in burst_length_pdf.items():
            file.write(str(k) + "," + str(v) + "\n")
    with open(base_path + "/data/burst_amount_distribution.csv", "w") as file:
        file.write("duration,pdf\n")
        for k, v in burst_amount_pdf.items():
            file.write(str(k) + "," + str(v) + "\n")
    
    burst_length_cdf = np.array(list(burst_length_dist.values())).cumsum() / np.array(list(burst_length_dist.values())).sum()
    burst_length_ccdf = 1 - burst_length_cdf

    for cycle, byte in burst_length_value.items():
        burst_length_value[cycle] = byte / sum(list(burst_length_value.values()))
    burst_amount_cdf = np.array(list(burst_length_value.values())).cumsum() / np.array(list(burst_length_value.values())).sum()
    burst_amount_ccdf = 1 - burst_amount_cdf

    plt.plot(list(burst_length_dist.keys()), burst_length_ccdf, marker="+", label="latency fraction")
    plt.plot(list(burst_length_value.keys()), burst_amount_ccdf, marker="*", label="traffic fraction")
    plt.xlabel("burst length (cycle)")
    plt.ylabel("Fraction")
    plt.title("Traffic and latency fractions")
    plt.legend()
    plt.savefig(base_path + "/plots/traffic_latency_fraction.jpg")
    plt.close()
    
    plt.plot(burst_length_pdf.keys(), burst_length_pdf.values(), marker="*")
    plt.xlabel("burst length")
    plt.ylabel("PDF")
    plt.savefig(base_path + "/plots/injected_burst_length_distribution.jpg")
    plt.close()
    plt.plot(burst_amount_pdf.keys(), burst_amount_pdf.values(), marker="*")
    plt.xlabel("burst amount")
    plt.ylabel("PDF")
    plt.savefig(base_path + "/plots/injected_burst_amount_distribution.jpg")
    plt.close()

    with open(base_path + "/data/burst_ratio.csv", "w") as file:
        file.write("ratio\n")
        for r in burst_ratio:
            file.write(str(r) + "\n")
    hurst(base_path, burst_ratio, "temporal_burstiness")
