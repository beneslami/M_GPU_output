
import os
import gc
import sys
import matplotlib.pyplot as plt
import numpy as np
sys.path.append("..")
import benchlist
from pathlib import Path
from tabulate import tabulate
from re_arrange_benchmark import kernel_is_valid


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
        int(trace_file.split(".")[0].split("_")[-1])
    except:
        kernel_num = 0
    else:
        kernel_num = int(trace_file.split(".")[0].split("_")[-1])
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
    cv = -1
    if len(data) > 1:
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
        int(trace_file.split(".")[0].split("_")[-1])
    except:
        kernel_num = 0
    else:
        kernel_num = int(trace_file.split(".")[0].split("_")[-1])
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
                if cycle - prev_cycle not in dist.keys():
                    dist[cycle - prev_cycle] = 1
                else:
                    dist[cycle - prev_cycle] += 1
    dist = dict(sorted(dist.items(), key=lambda x: x[0]))
    while "kernels" in path:
        path = os.path.dirname(path)
    if not os.path.exists(path + "/data/"):
        os.mkdir(path + "/data/")
    if len(dist) > 0:
        with open(path + "/data/iat_" + str(kernel_num) + ".csv", "w") as file:
            for k, v in dist.items():
                file.write(str(k) + "," + str(v) + "\n")
        total = sum(list(dist.values()))
        for k, v in dist.items():
            dist[k] = v / total
        total = 0
        for k, v in dist.items():
            dist[k] = v + total
            total += v
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
    while "kernels" in path:
        path = os.path.dirname(path)
    if len(burst_volume) > 0:
        with open(path + "/data/burst-vol_" + str(kernel_num) + ".csv", "w") as file:
            for k, v in dist.items():
                file.write(str(k) + "," + str(v) + "\n")
        total = sum(list(dist.values()))
        for k, v in dist.items():
            dist[k] = v / total
        total = 0
        for k, v in dist.items():
            dist[k] = v + total
            total += v
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
    while "kernels" in path:
        path = os.path.dirname(path)
    if len(burst_duration) > 0:
        with open(path + "/data/burst-dur_" + str(kernel_num) + ".csv", "w") as file:
            for k, v in dist.items():
                file.write(str(k) + "," + str(v) + "\n")
        total = sum(list(dist.values()))
        for k, v in dist.items():
            dist[k] = v / total
        total = 0
        for k, v in dist.items():
            dist[k] = v + total
            total += v
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
    while "kernels" in path:
        path = os.path.dirname(path)
    if len(burst_ratio) > 0:
        with open(path + "/data/burst-ratio_" + str(kernel_num) + ".csv", "w") as file:
            for k, v in dist.items():
                file.write(str(k) + "," + str(v) + "\n")
        total = sum(list(dist.values()))
        for k, v in dist.items():
            dist[k] = v / total
        total = 0
        for k, v in dist.items():
            dist[k] = v + total
            total += v

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
    cv = calculate_cov(burst_ratio)
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
        if len(traffic) > 0:
            minimum = min(list(traffic.keys()))
            maximum = max(list(traffic.keys()))
            for i in range(minimum, maximum):
                if i not in traffic.keys():
                    traffic[i] = 0
            traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
            path = os.path.dirname(file_name) + "/plots/"
            cv = interarrival_time_cov(traffic, path, suite, bench, kernel_num)
            return "{:.2f}".format(cv)
        else:
            return -1


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
        if len(traffic) > 0:
            minimum = min(list(traffic.keys()))
            maximum = max(list(traffic.keys()))
            for i in range(minimum, maximum):
                if i not in traffic.keys():
                    traffic[i] = 0
            traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
            path = os.path.dirname(file_name) + "/plots/"
            cv = burst_volume_cov(traffic, path, suite, bench, kernel_num)
            return "{:.2f}".format(cv)
        else:
            return -1


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
        if len(traffic) > 0:
            minimum = min(list(traffic.keys()))
            maximum = max(list(traffic.keys()))
            for i in range(minimum, maximum):
                if i not in traffic.keys():
                    traffic[i] = 0
            traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
            path = os.path.dirname(file_name) + "/plots/"
            cv = burst_duration_cov(traffic, path, suite, bench, kernel_num)
            return "{:.2f}".format(cv)
        else:
            return -1


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
        if len(traffic) > 0:
            minimum = min(list(traffic.keys()))
            maximum = max(list(traffic.keys()))
            for i in range(minimum, maximum):
                if i not in traffic.keys():
                    traffic[i] = 0
            traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
            path = os.path.dirname(file_name) + "/plots/"
            cv = burst_ratio_cov(traffic, path, suite, bench, kernel_num)
            return "{:.2f}".format(cv)
        else:
            return -1


def find_the_number_of_fucking_kernels(suite, bench, ch):
    k_list = []
    for topo in benchlist.topology:
        for nv in benchlist.NVLink:
            if os.path.exists(benchlist.bench_path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/bench_info.csv"):
                info = pd.read_csv(benchlist.bench_path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/bench_info.csv")
                k_list.append(list(info["kernel_num"]))
    nominated_list = k_list[0]
    for kernel_list in k_list:
        if len(kernel_list) < len(nominated_list):
            nominated_list = kernel_list
    return nominated_list


def measure_average(data):
    if len(data) > 0:
        partial_sum = 0
        summation = sum(list(data.values()))
        for k, v in data.items():
            partial_sum += k*v
        return partial_sum / summation
    else:
        return -1


def measure_std(data, mu):
    if len(data) > 0:
        summation = sum(list(data.values()))
        partial_sum = 0
        for k, v in data.items():
            partial_sum += (k - mu)**2
        return math.sqrt(partial_sum/summation)
    else:
        return -1


def measure_skewness(data, mu, std):
    if len(data) > 0:
        partial_sum = 0
        summation = 0
        for k, v in data.items():
            partial_sum += (k - mu)**3
            summation += v
        return partial_sum/((summation-1)*(std**3))
    else:
        return -1


def measure_kurtosis(data, mu, std):
    if len(data) > 0:
        partial_sum = 0
        summation = 0
        for k, v in data.items():
            partial_sum += (k - mu) ** 4
            summation += v
        return partial_sum / ((summation - 1) * (std ** 4))
    else:
        return -1


def burstiness_statistics(path, kernel_num):
    iat_file = path + "iat_" + str(kernel_num) + ".csv"
    burst_vol_file = path + "burst-vol_" + str(kernel_num) + ".csv"
    burst_dur_file = path + "burst-dur_" + str(kernel_num) + ".csv"
    burst_intensity_file = path + "burst-ratio_" + str(kernel_num) + ".csv"
    data = {"iat": [], "vol": [], "dur": [], "intensity": []}
    iat = {}
    vol = {}
    dur = {}
    intensity = {}
    with open(iat_file, "r") as file:
        content = file.readlines()
    if len(content) > 1:
        for item in content:
            k = int(item.split(",")[0])
            v = int(item.split(",")[1])
            iat[k] = v
    with open(burst_vol_file, "r") as file:
        content = file.readlines()
    if len(content) > 1:
        for item in content:
            k = int(item.split(",")[0])
            v = int(item.split(",")[1])
            vol[k] = v
    with open(burst_dur_file, "r") as file:
        content = file.readlines()
    if len(content) > 1:
        for item in content:
            k = int(item.split(",")[0])
            v = int(item.split(",")[1])
            dur[k] = v
    with open(burst_intensity_file, "r") as file:
        content = file.readlines()
    if len(content) > 1:
        for item in content:
            k = float(item.split(",")[0])
            v = int(item.split(",")[1])
            intensity[k] = v

    iat_avg = measure_average(iat)
    iat_std = measure_std(iat, iat_avg)
    iat_skw = measure_skewness(iat, iat_avg, iat_std)
    iat_kur = measure_kurtosis(iat, iat_avg, iat_std)
    data["iat"].append(iat_avg)
    data["iat"].append(iat_std)
    data["iat"].append(iat_skw)
    data["iat"].append(iat_kur)

    vol_avg = measure_average(vol)
    vol_std = measure_std(vol, vol_avg)
    vol_skw = measure_skewness(vol, vol_avg, vol_std)
    vol_kur = measure_kurtosis(vol, vol_avg, vol_std)
    data["vol"].append(vol_avg)
    data["vol"].append(vol_std)
    data["vol"].append(vol_skw)
    data["vol"].append(vol_kur)

    dur_avg = measure_average(dur)
    dur_std = measure_std(dur, dur_avg)
    dur_skw = measure_skewness(dur, dur_avg, dur_std)
    dur_kur = measure_kurtosis(dur, dur_avg, dur_std)
    data["dur"].append(dur_avg)
    data["dur"].append(dur_std)
    data["dur"].append(dur_skw)
    data["dur"].append(dur_kur)

    int_avg = measure_average(intensity)
    int_std = measure_std(intensity, int_avg)
    int_skw = measure_skewness(intensity, int_avg, int_std)
    int_kur = measure_kurtosis(intensity, int_avg, int_std)
    data["intensity"].append(int_avg)
    data["intensity"].append(int_std)
    data["intensity"].append(int_skw)
    data["intensity"].append(int_kur)
    return data

if __name__ == "__main__":
    """suits = benchlist.suits
    benchmarks = benchlist.benchmarks
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet_num = benchlist.chiplet_num
    path = benchlist.bench_path
    for suite in suits:
        if suite == "rodinia":
            for bench in benchmarks[suite]:
                for topo in topology:
                    for nv in NVLink:
                        for ch in chiplet_num:
                            if ch == "4chiplet" and bench == "heartwall":
                                sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                                if len(os.listdir(os.path.dirname(os.path.dirname(sub_path)))) != 0:
                                    for trace_file in os.listdir(sub_path):
                                        if Path(trace_file).suffix == '.txt':
                                            kernel_num = int(trace_file.split(".")[0].split("_")[-1])
                                            if kernel_is_valid(sub_path, trace_file):
                                                cv_iat = measure_iat(sub_path + trace_file, suite, bench, kernel_num)
                                                print(bench + " " + nv  + " iat done")
                                                cv_vol = measure_vol(sub_path + trace_file, suite, bench, kernel_num)
                                                print(bench + " " + nv + " vol done")
                                                cv_rat = measure_duration(sub_path + trace_file, suite, bench, kernel_num)
                                                print(bench + " " + nv + " ratio done")
                                                cv_dur = measure_burst_ratio(sub_path + trace_file, suite, bench, kernel_num)
                                                print(bench + " " + nv + " duration done")"""

    """for nv in NVLink:
        suite_list = []
        bench_list = []
        kernel_list = []
        topo_list = []
        hurst_list = []
        iat_mean = []
        iat_std = []
        iat_ske = []
        iat_kur = []
        iat_cov = []
        vol_mean = []
        vol_std = []
        vol_ske = []
        vol_kur = []
        vol_cov = []
        dur_mean = []
        dur_std = []
        dur_ske = []
        dur_kur = []
        dur_cov = []
        for suite in suits:
            for bench in benchmarks[suite]:
                k = find_the_number_of_fucking_kernels(suite, bench, ch)
                for kernel_num in k:
                    for topo in topology:
                        if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/bench_info.csv"):
                            info = pd.read_csv(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/bench_info.csv")
                            sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/data/"
                            data = burstiness_statistics(sub_path, kernel_num)
                            suite_list.append(suite)
                            bench_list.append(bench)
                            kernel_list.append(kernel_num)
                            topo_list.append(topo)
                            for i in info.index:
                                if info["kernel_num"][i] == kernel_num:
                                    hurst_list.append("{:.2f}".format(info["hurst"][i]))
                            for item, list_item in data.items():
                                if item == "iat":
                                    iat_mean.append("{:.2f}".format(list_item[0]))
                                    iat_std.append("{:.2f}".format(list_item[1]))
                                    iat_ske.append("{:.2f}".format(list_item[2]))
                                    iat_kur.append("{:.2f}".format(list_item[3]))
                                    for i in info.index:
                                        if info["kernel_num"][i] == kernel_num:
                                            iat_cov.append("{:.2f}".format(info["IAT CoV"][i]))
                                elif item == "vol":
                                    vol_mean.append("{:.2f}".format(list_item[0]))
                                    vol_std.append("{:.2f}".format(list_item[1]))
                                    vol_ske.append("{:.2f}".format(list_item[2]))
                                    vol_kur.append("{:.2f}".format(list_item[3]))
                                    for i in info.index:
                                        if info["kernel_num"][i] == kernel_num:
                                            vol_cov.append("{:.2f}".format(info["Vol CoV"][i]))
                                elif item == "dur":
                                    dur_mean.append("{:.2f}".format(list_item[0]))
                                    dur_std.append("{:.2f}".format(list_item[1]))
                                    dur_ske.append("{:.2f}".format(list_item[2]))
                                    dur_kur.append("{:.2f}".format(list_item[3]))
                                    flag = 0
                                    for i in info.index:
                                        if info["kernel_num"][i] == kernel_num:
                                            dur_cov.append("{:.2f}".format(info["dur CoV"][i]))
                                            flag = 1
                                            break
                                    if flag == 0:
                                        print(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/bench_info.csv    " + str(kernel_num))

                        else:
                            print("WARNING:  " + path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/bench_info.csv")

        table = {"suite": suite_list, "benchmark": bench_list, "kernel": kernel_list, "topology": topo_list,
                 "hurst": hurst_list, "IAT_mean": iat_mean, "IAT_std": iat_std, "IAT_skewness": iat_ske,
                 "IAT_kurtosis": iat_kur, "IAT_CoV": iat_cov, "vol_mean": vol_mean, "vol_std": vol_std, "vol_skewness": vol_ske,
                 "vol_kurtosis": vol_kur, "vol_CoV": vol_cov, "dur_mean": dur_mean, "dur_std": dur_std, "dur_skewness": dur_ske,
                 "dur_kurtosis": dur_kur, "dur_CoV": dur_cov
        }
        df = pd.DataFrame(table)
        df.set_index(["suite", "benchmark", "kernel", "topology",
                 "hurst", "IAT_mean", "IAT_std", "IAT_skewness", "IAT_kurtosis", "IAT_CoV", "vol_mean", "vol_std", "vol_skewness",
                 "vol_kurtosis", "vol_CoV", "dur_mean", "dur_std", "dur_skewness", "dur_kurtosis", "dur_CoV"], inplace=True)

        df.to_html(path + "burst_stats_" + nv + ".html")
        df.to_csv(path + "burst_stats_" + nv + ".csv")"""