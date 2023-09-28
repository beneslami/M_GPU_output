
import os
import gc
import sys
import matplotlib.pyplot as plt
import numpy as np
sys.path.append("..")
import benchlist
from pathlib import Path
from tabulate import tabulate


def plot_ccdf(sub_path, trace_file, traffic):
    while "kernels" in sub_path:
        sub_path = os.path.dirname(sub_path)
    while True:
        if os.path.exists(sub_path + "/plots/"):
            sub_path += "/plots/"
            break
        else:
            sub_path = os.path.dirname(sub_path)
    if not os.path.exists(sub_path):
        os.mkdir(sub_path)
    kernel_num = -1
    try:
        int(trace_file.split(".")[0][-1])
    except:
        kernel_num = 0
    else:
        kernel_num = int(trace_file.split(".")[0][-1])
    if not os.path.exists(sub_path + str(kernel_num)):
        os.mkdir(sub_path + str(kernel_num))
    sub_path += str(kernel_num)
    burst_length = []
    burst_ratio = []
    burst_length_dist = {}
    burst_amount_dist = {}
    burst_length_value = {}
    burst_length_value_ = {}
    start_flag = 0
    prev_cycle = 0
    aggregate_burst = 0
    for cycle, byte in traffic.items():
        if byte != 0:
            if start_flag == 0:
                start_flag = 1
                prev_cycle = cycle
            aggregate_burst += byte
        elif byte == 0:
            if start_flag == 1:
                burst_length.append(cycle - prev_cycle)
                burst_ratio.append(aggregate_burst / (cycle - prev_cycle))
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

    burst_length_pdf = {}
    burst_amount_pdf = {}
    for length, freq in burst_length_dist.items():
        burst_length_pdf[length] = freq / sum(burst_length_dist.values())
    for amount, freq in burst_amount_dist.items():
        burst_amount_pdf[amount] = freq / sum(burst_amount_dist.values())

    burst_length_cdf = np.array(list(burst_length_dist.values())).cumsum() / np.array(list(burst_length_dist.values())).sum()
    burst_length_ccdf = 1 - burst_length_cdf

    for cycle, byte in burst_length_value.items():
        burst_length_value[cycle] = byte / sum(list(burst_length_value.values()))
    burst_amount_cdf = np.array(list(burst_length_value.values())).cumsum() / np.array(list(burst_length_value.values())).sum()
    burst_amount_ccdf = 1 - burst_amount_cdf
    
    plt.close()
    plt.plot(list(burst_length_dist.keys()), burst_length_ccdf, marker="|", label="burst length fraction")
    plt.plot(list(burst_length_value.keys()), burst_amount_ccdf, marker="*", label="burst volume fraction")
    plt.xlabel("burst length (cycle)")
    plt.ylabel("Fraction")
    plt.title("temporal burstiness analysis")
    plt.legend()
    plt.savefig(sub_path + "/burst_analysis_" + str(kernel_num) + ".jpg")
    plt.close()


def calculate_cov(data):
    cv = np.std(data, ddof=1)/np.mean(data) * 100
    return cv


def plot_dispersion(sub_path, trace_file, traffic):
    while "kernels" in sub_path:
        sub_path = os.path.dirname(sub_path)
    sub_path += "/plots/"
    if not os.path.exists(sub_path):
        os.mkdir(sub_path)
    kernel_num = -1
    try:
        int(trace_file.split(".")[0][-1])
    except:
        kernel_num = 0
    else:
        kernel_num = int(trace_file.split(".")[0][-1])
    if not os.path.exists(sub_path + "/" + str(kernel_num)):
        os.mkdir(sub_path + "/" + str(kernel_num))
    sub_path += "/" + str(kernel_num)
    burst_length = []
    burst_ratio = []
    burst_length_dist = {}
    burst_amount_dist = {}
    burst_length_value_ = {}
    start_flag = 0
    prev_cycle = 0
    aggregate_burst = 0
    for cycle, byte in traffic.items():
        if byte != 0:
            if start_flag == 0:
                start_flag = 1
                prev_cycle = cycle
            aggregate_burst += byte
        elif byte == 0:
            if start_flag == 1:
                burst_length.append(cycle - prev_cycle)
                burst_ratio.append(aggregate_burst / (cycle - prev_cycle))
                #burst_length_dist.append(cycle - prev_cycle)
                #burst_amount_dist.append(aggregate_burst)
                if cycle - prev_cycle not in burst_length_dist.keys():
                    burst_length_dist[cycle - prev_cycle] = 1
                else:
                    burst_length_dist[cycle - prev_cycle] += 1
                if aggregate_burst not in burst_amount_dist.keys():
                    burst_amount_dist[aggregate_burst] = 1
                else:
                    burst_amount_dist[aggregate_burst] += 1
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
    total = sum(list(burst_length_dist.values()))
    for k, v in burst_length_dist.items():
        burst_length_dist[k] = v / total
    total = sum(list(burst_amount_dist.values()))
    for k, v in burst_amount_dist.items():
        burst_amount_dist[k] = v / total

    plt.close()
    fig = plt.figure(figsize=(8, 8))
    grid = plt.GridSpec(4, 4)
    ax_scatter = fig.add_subplot(grid[1:4, 0:3])
    ax_hist_y  = fig.add_subplot(grid[0, 0: 3])
    ax_hist_x  = fig.add_subplot(grid[1: 4, 3])
    for cyc in burst_length_value_.keys():
        temp = []
        for i in range(len(burst_length_value_[cyc].values())):
            temp.append(cyc)
        ax_scatter.scatter(list(temp), list(burst_length_value_[cyc].keys()), color="red")
    ax_scatter.set_xlabel("burst duration (cycle)")
    ax_scatter.set_ylabel("burst volume (byte)")
    ax_hist_y.plot(list(burst_length_dist.keys()), list(burst_length_dist.values()), marker="o")
    ax_hist_y.set_xticks([])
    ax_hist_y.set_ylabel("Density")
    ax_hist_x.plot(list(burst_amount_dist.values()), list(burst_amount_dist.keys()), marker="o")
    ax_hist_x.set_yticks([])
    ax_hist_x.set_xlabel("Density")
    plt.tight_layout()
    plt.savefig(sub_path + "/burst_decomposition_" + str(kernel_num) + ".jpg")
    plt.close()


def interarrival_time_cov(traffic, path, suite, bench, kernel_num):
    start_flag = 0
    iat = []
    dist = {}
    prev_cycle = 0
    for cycle, byte in traffic.items():
        if byte == 0:
            if start_flag == 0:
                start_flag = 1
                prev_cycle = cycle
        elif byte != 0:
            if start_flag == 1:
                start_flag = 0
                iat.append(cycle - prev_cycle)
                if cycle - prev_cycle not in dist. keys():
                    dist[cycle - prev_cycle] = 1
                else:
                    dist[cycle - prev_cycle] += 1
    dist = dict(sorted(dist.items(), key=lambda x: x[0]))
    total = sum(list(dist.values()))
    for k, v in dist.items():
        dist[k] = v / total
    total = 0
    for k, v in dist.items():
        dist[k] = v + total
        total += v
    while "kernels" in path:
        path = os.path.dirname(path)
    if not os.path.exists(path + "/plots/"):
        os.mkdir(path + "/plots/")
    path += "/plots/"
    if not os.path.exists(path + str(kernel_num)):
        os.mkdir(path + str(kernel_num))
    path += str(kernel_num) + "/"
    plt.plot(dist.keys(), dist.values(), marker="o")
    plt.xlabel("inter arrival time")
    plt.ylabel("CDF")
    plt.title(str(suite) + "-" + str(bench) + " Inter Arrival Time")
    plt.tight_layout()
    plt.savefig(path + "IAT_" + str(kernel_num) + ".jpg")
    plt.close()
    cv = calculate_cov(iat)
    return cv


def burst_volume_cov(traffic, path, suite, bench, kernel_num):
    start_flag = 0
    aggregate_burst = 0
    burst_volume = []
    dist = {}
    for cycle, byte in traffic.items():
        if byte != 0:
            if start_flag == 0:
                start_flag = 1
            aggregate_burst += byte
        elif byte == 0:
            if start_flag == 1:
                burst_volume.append(aggregate_burst)
                if aggregate_burst not in dist.keys():
                    dist[aggregate_burst] = 1
                else:
                    dist[aggregate_burst] += 1
                start_flag = 0
                aggregate_burst = 0

    dist = dict(sorted(dist.items(), key=lambda x: x[0]))
    total = sum(list(dist.values()))
    for k, v in dist.items():
        dist[k] = v / total
    total = 0
    for k, v in dist.items():
        dist[k] = v + total
        total += v
    while "kernels" in path:
        path = os.path.dirname(path)
    if not os.path.exists(path + "/plots/"):
        os.mkdir(path + "/plots/")
    path += "/plots/"
    if not os.path.exists(path + str(kernel_num)):
        os.mkdir(path + str(kernel_num))
    path += str(kernel_num) + "/"
    plt.plot(dist.keys(), dist.values(), marker="o")
    plt.xlabel("burst volume")
    plt.ylabel("CDF")
    plt.title(str(suite) + "-" + str(bench) + " Burst Volume")
    plt.tight_layout()
    plt.savefig(path + "burst_vol_" + str(kernel_num) + ".jpg")
    plt.close()
    cv = calculate_cov(burst_volume)
    return cv


def burst_duration_cov(traffic, path, suite, bench, kernel_num):
    start_flag = 0
    burst_duration = []
    prev_cycle = 0
    dist = {}
    for cycle, byte in traffic.items():
        if byte != 0:
            if start_flag == 0:
                start_flag = 1
                prev_cycle = cycle
        elif byte == 0:
            if start_flag == 1:
                burst_duration.append((cycle - prev_cycle))
                if cycle - prev_cycle not in dist.keys():
                    dist[cycle - prev_cycle] = 1
                else:
                    dist[cycle - prev_cycle] += 1
                start_flag = 0

    dist = dict(sorted(dist.items(), key=lambda x: x[0]))
    total = sum(list(dist.values()))
    for k, v in dist.items():
        dist[k] = v / total
    total = 0
    for k, v in dist.items():
        dist[k] = v + total
        total += v
    while "kernels" in path:
        path = os.path.dirname(path)
    if not os.path.exists(path + "/plots/"):
        os.mkdir(path + "/plots/")
    path += "/plots/"
    if not os.path.exists(path + str(kernel_num)):
        os.mkdir(path + str(kernel_num))
    path += str(kernel_num) + "/"
    plt.plot(dist.keys(), dist.values(), marker="o")
    plt.xlabel("burst duration")
    plt.ylabel("CDF")
    plt.title(str(suite) + "-" + str(bench) + " Burst duration")
    plt.tight_layout()
    plt.savefig(path + "burst_duration_" + str(kernel_num) + ".jpg")
    plt.close()
    cv = calculate_cov(burst_duration)
    return cv


def burst_ratio_cov(traffic, path, suite, bench, kernel_num):
    start_flag = 0
    aggregate_burst = 0
    burst_ratio = []
    prev_cycle = 0
    dist = {}
    for cycle, byte in traffic.items():
        if byte != 0:
            if start_flag == 0:
                start_flag = 1
                prev_cycle = cycle
            aggregate_burst += byte
        elif byte == 0:
            if start_flag == 1:
                burst_ratio.append(aggregate_burst / (cycle - prev_cycle))
                if aggregate_burst / (cycle - prev_cycle) not in dist.keys():
                    dist[aggregate_burst / (cycle - prev_cycle)] = 1
                else:
                    dist[aggregate_burst / (cycle - prev_cycle)] += 1
                start_flag = 0
                aggregate_burst = 0

    dist = dict(sorted(dist.items(), key=lambda x: x[0]))
    total = sum(list(dist.values()))
    for k, v in dist.items():
        dist[k] = v / total
    total = 0
    for k, v in dist.items():
        dist[k] = v + total
        total += v
    while "kernels" in path:
        path = os.path.dirname(path)
    if not os.path.exists(path + "/plots/"):
        os.mkdir(path + "/plots/")
    path += "/plots/"
    if not os.path.exists(path + str(kernel_num)):
        os.mkdir(path + str(kernel_num))
    path += str(kernel_num) + "/"
    plt.plot(dist.keys(), dist.values(), marker="o")
    plt.xlabel("burst duration")
    plt.ylabel("CDF")
    plt.title(str(suite) + "-" + str(bench) + " Burst duration")
    plt.tight_layout()
    plt.savefig(path + "burst_duration_" + str(kernel_num) + ".jpg")
    cv = calculate_cov(burst_ratio)
    plt.close()
    return cv


def measure_traffic_fraction(input_, request_packet):
    traffic = {}
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "request injected":
                src = int(request_packet[id][j][1].split(": ")[1])
                dst = int(request_packet[id][j][2].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if cycle not in traffic.keys():
                    traffic[cycle] = byte
                else:
                    traffic[cycle] += byte
    minimum = min(list(traffic.keys()))
    maximum = max(list(traffic.keys()))
    for i in range(minimum, maximum):
        if i not in traffic.keys():
            traffic[i] = 0
    traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
    del(request_packet)
    sub_path = input_
    plot_ccdf(sub_path, input_, traffic)
    plot_dispersion(sub_path, input_, traffic)
    gc.enable()
    gc.collect()


def measure_iat(file_name, suite, bench, kernel_num):
    cv = -1
    if Path(file_name).suffix == '.txt':
        file = open(file_name, "r")
        raw_content = ""
        if file.mode == "r":
            raw_content = file.readlines()
        file.close()
        lined_list = []
        request_packet = {}
        for line in raw_content:
            item = [x for x in line.split("\t") if x not in ['', '\t']]
            lined_list.append(item)
        for i in range(len(lined_list)):
            if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
                if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                    request_packet.setdefault(
                        int(lined_list[i][3].split(": ")[1]), []).append(
                        lined_list[i])
            else:
                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        del (raw_content)
        del (lined_list)
        traffic = {}
        for id in request_packet.keys():
            for j in range(len(request_packet[id])):
                if request_packet[id][j][0] == "request injected":
                    src = int(request_packet[id][j][1].split(": ")[1])
                    dst = int(request_packet[id][j][2].split(": ")[1])
                    cycle = int(request_packet[id][j][5].split(": ")[1])
                    byte = int(request_packet[id][j][7].split(": ")[1])
                    if cycle not in traffic.keys():
                        traffic[cycle] = byte
                    else:
                        traffic[cycle] += byte
        minimum = min(list(traffic.keys()))
        maximum = max(list(traffic.keys()))
        for i in range(minimum, maximum):
            if i not in traffic.keys():
                traffic[i] = 0
        traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
        path = os.path.dirname(file_name) + "/plots/"
        cv = interarrival_time_cov(traffic, path, suite, bench, kernel_num)
    return "{:.2f}".format(cv)


def measure_vol(file_name, suite, bench, kernel_num):
    cv = -1
    if Path(file_name).suffix == '.txt':
        file = open(file_name, "r")
        raw_content = ""
        if file.mode == "r":
            raw_content = file.readlines()
        file.close()
        lined_list = []
        request_packet = {}
        for line in raw_content:
            item = [x for x in line.split("\t") if x not in ['', '\t']]
            lined_list.append(item)
        for i in range(len(lined_list)):
            if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
                if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                    request_packet.setdefault(
                        int(lined_list[i][3].split(": ")[1]), []).append(
                        lined_list[i])
            else:
                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        del (raw_content)
        del (lined_list)
        traffic = {}
        for id in request_packet.keys():
            for j in range(len(request_packet[id])):
                if request_packet[id][j][0] == "request injected":
                    src = int(request_packet[id][j][1].split(": ")[1])
                    dst = int(request_packet[id][j][2].split(": ")[1])
                    cycle = int(request_packet[id][j][5].split(": ")[1])
                    byte = int(request_packet[id][j][7].split(": ")[1])
                    if cycle not in traffic.keys():
                        traffic[cycle] = byte
                    else:
                        traffic[cycle] += byte
        minimum = min(list(traffic.keys()))
        maximum = max(list(traffic.keys()))
        for i in range(minimum, maximum):
            if i not in traffic.keys():
                traffic[i] = 0
        traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
        path = os.path.dirname(file_name) + "/plots/"
        cv = burst_volume_cov(traffic, path, suite, bench, kernel_num)
    return "{:.2f}".format(cv)


def measure_duration(file_name, suite, bench, kernel_num):
    cv = -1
    if Path(file_name).suffix == '.txt':
        file = open(file_name, "r")
        raw_content = ""
        if file.mode == "r":
            raw_content = file.readlines()
        file.close()
        lined_list = []
        request_packet = {}
        for line in raw_content:
            item = [x for x in line.split("\t") if x not in ['', '\t']]
            lined_list.append(item)
        for i in range(len(lined_list)):
            if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
                if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                    request_packet.setdefault(
                        int(lined_list[i][3].split(": ")[1]), []).append(
                        lined_list[i])
            else:
                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        del (raw_content)
        del (lined_list)
        traffic = {}
        for id in request_packet.keys():
            for j in range(len(request_packet[id])):
                if request_packet[id][j][0] == "request injected":
                    src = int(request_packet[id][j][1].split(": ")[1])
                    dst = int(request_packet[id][j][2].split(": ")[1])
                    cycle = int(request_packet[id][j][5].split(": ")[1])
                    byte = int(request_packet[id][j][7].split(": ")[1])
                    if cycle not in traffic.keys():
                        traffic[cycle] = byte
                    else:
                        traffic[cycle] += byte
        minimum = min(list(traffic.keys()))
        maximum = max(list(traffic.keys()))
        for i in range(minimum, maximum):
            if i not in traffic.keys():
                traffic[i] = 0
        traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
        path = os.path.dirname(file_name) + "/plots/"
        cv = burst_duration_cov(traffic, path, suite, bench, kernel_num)
    return "{:.2f}".format(cv)


def measure_burst_ratio(file_name, suite, bench, kernel_num):
    cv = -1
    if Path(file_name).suffix == '.txt':
        file = open(file_name, "r")
        raw_content = ""
        if file.mode == "r":
            raw_content = file.readlines()
        file.close()
        lined_list = []
        request_packet = {}
        for line in raw_content:
            item = [x for x in line.split("\t") if x not in ['', '\t']]
            lined_list.append(item)
        for i in range(len(lined_list)):
            if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
                if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                    request_packet.setdefault(
                        int(lined_list[i][3].split(": ")[1]), []).append(
                        lined_list[i])
            else:
                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        del (raw_content)
        del (lined_list)
        traffic = {}
        for id in request_packet.keys():
            for j in range(len(request_packet[id])):
                if request_packet[id][j][0] == "request injected":
                    src = int(request_packet[id][j][1].split(": ")[1])
                    dst = int(request_packet[id][j][2].split(": ")[1])
                    cycle = int(request_packet[id][j][5].split(": ")[1])
                    byte = int(request_packet[id][j][7].split(": ")[1])
                    if cycle not in traffic.keys():
                        traffic[cycle] = byte
                    else:
                        traffic[cycle] += byte
        minimum = min(list(traffic.keys()))
        maximum = max(list(traffic.keys()))
        for i in range(minimum, maximum):
            if i not in traffic.keys():
                traffic[i] = 0
        traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
        path = os.path.dirname(file_name) + "/plots/"
        cv = burst_ratio_cov(traffic, path, suite, bench, kernel_num)
    return "{:.2f}".format(cv)


if __name__ == "__main__":
    suits = benchlist.suits
    benchmarks = benchlist.nominated_benchmarks
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet_num = benchlist.chiplet_num
    path = benchlist.bench_path
    cov_iat = [["", "NVLink4", "NVLink3", "NVLink2", "NVLink1"]]
    cov_vol = [["", "NVLink4", "NVLink3", "NVLink2", "NVLink1"]]
    cov_rat = [["", "NVLink4", "NVLink3", "NVLink2", "NVLink1"]]
    cov_dur = [["", "NVLink4", "NVLink3", "NVLink2", "NVLink1"]]
    for suite in suits:
        if suite == "deepbench":
            for bench in benchmarks[suite]:
                if bench == "rnn":
                    bench_name_iat = []
                    bench_name_vol = []
                    bench_name_dur = []
                    bench_name_rat = []
                    bench_name_iat.append(bench)
                    bench_name_vol.append(bench)
                    bench_name_dur.append(bench)
                    bench_name_rat.append(bench)
                    for topo in topology:
                        nv_item_iat = []
                        nv_item_vol = []
                        nv_item_rat = []
                        nv_item_dur = []
                        nv_item_iat.append(topo)
                        nv_item_vol.append(topo)
                        nv_item_rat.append(topo)
                        nv_item_dur.append(topo)
                        for nv in NVLink:
                            for ch in chiplet_num:
                                if ch == "4chiplet":
                                    cv_item_iat = []
                                    cv_item_vol = []
                                    cv_item_rat = []
                                    cv_item_dur = []
                                    sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                                    if len(os.listdir(os.path.dirname(os.path.dirname(sub_path)))) != 0:
                                        for trace_file in os.listdir(sub_path):
                                            if Path(trace_file).suffix == '.txt' and os.path.getsize(sub_path + trace_file) > 500000:
                                                file = open(sub_path + trace_file, "r")
                                                raw_content = ""
                                                if file.mode == "r":
                                                    raw_content = file.readlines()
                                                file.close()
                                                lined_list = []
                                                request_packet = {}
                                                for line in raw_content:
                                                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                                                    lined_list.append(item)
                                                for i in range(len(lined_list)):
                                                    if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
                                                        if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                                                            request_packet.setdefault(
                                                                int(lined_list[i][3].split(": ")[1]), []).append(
                                                                lined_list[i])
                                                    else:
                                                        request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
                                                del (raw_content)
                                                del (lined_list)
                                                traffic = {}
                                                for id in request_packet.keys():
                                                    for j in range(len(request_packet[id])):
                                                        if request_packet[id][j][0] == "request injected":
                                                            src = int(request_packet[id][j][1].split(": ")[1])
                                                            dst = int(request_packet[id][j][2].split(": ")[1])
                                                            cycle = int(request_packet[id][j][5].split(": ")[1])
                                                            byte = int(request_packet[id][j][7].split(": ")[1])
                                                            if cycle not in traffic.keys():
                                                                traffic[cycle] = byte
                                                            else:
                                                                traffic[cycle] += byte
                                                minimum = min(list(traffic.keys()))
                                                maximum = max(list(traffic.keys()))
                                                for i in range(minimum, maximum):
                                                    if i not in traffic.keys():
                                                        traffic[i] = 0
                                                traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
                                                #plot_ccdf(sub_path, trace_file, traffic)
                                                plot_dispersion(sub_path, trace_file, traffic)
                                                cv_iat = interarrival_time_cov(traffic)
                                                cv_vol = traffic_volume_cov(traffic)
                                                cv_rat = burst_ratio_cov(traffic)
                                                cv_dur = burst_duration_cov(traffic)
                                                cv_item_iat.append(cv_iat)
                                                cv_item_vol.append(cv_vol)
                                                cv_item_rat.append(cv_rat)
                                                cv_item_dur.append(cv_dur)
                                                print(sub_path+trace_file)
                                    if len(cv_item_iat) != 0:
                                        nv_item_iat.append("{:.2f}".format(np.mean(cv_item_iat)))
                                    else:
                                        nv_item_iat.append(-1)
                                    if len(cv_item_vol) != 0:
                                        nv_item_vol.append("{:.2f}".format(np.mean(cv_item_vol)))
                                    else:
                                        nv_item_vol.append(-1)
                                    if len(cv_item_rat) != 0:
                                        nv_item_rat.append("{:.2f}".format(np.mean(cv_item_rat)))
                                    else:
                                        nv_item_rat.append(-1)
                                    if len(cv_item_dur) != 0:
                                        nv_item_dur.append("{:.2f}".format(np.mean(cv_item_dur)))
                                    else:
                                        nv_item_dur.append(-1)
                        bench_name_iat.append(nv_item_iat)
                        bench_name_vol.append(nv_item_vol)
                        bench_name_rat.append(nv_item_rat)
                        bench_name_dur.append(nv_item_dur)
                    cov_iat.append(bench_name_iat)
                    cov_vol.append(bench_name_vol)
                    cov_rat.append(bench_name_rat)
                    cov_dur.append(bench_name_dur)
    print("cov iat")
    print(tabulate(cov_iat))
    print("\ncov vol")
    print(tabulate(cov_vol))
    print("\ncov ratio")
    print(tabulate(cov_rat))
    print("\ncov duration")
    print(tabulate(cov_dur))
    gc.enable()
    gc.collect()
