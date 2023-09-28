import os
import re
import gc
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tabulate import tabulate
sys.path.append("..")
import benchlist
from pathlib import Path
import homogeneous_mode_generator_engine
ORDER = 2


def frequency_to_cdf(model):
    tot = sum(list(model.values()))
    for k, v in model.items():
        model[k] = v / tot
    tot = 0
    for k, v in model.items():
        model[k] = v + tot
        tot += v
    return model


def slide_window(items, dest):
    temp = str(items[1:]) + str(dest)
    return temp


def generate_random_state(cdf):
    random_num = np.random.uniform(0, 1, 1)
    for freq, prob in cdf.items():
        if random_num <= prob:
            return freq


def autocorr(x, twosided=False, tapered=True):
    nx = len(x)
    xdm = x - x.mean()
    ac = np.correlate(xdm, xdm, mode='full')
    ac /= ac[nx - 1]
    lags = np.arange(-nx + 1, nx)
    if not tapered:  # undo the built-in taper
        taper = 1 - np.abs(lags) / float(nx)
        ac /= taper
    if twosided:
        return lags, ac
    else:
        return lags[nx - 1:], ac[nx - 1:]


def measure_auto_correlation(emp_sequence, iat_sequence, markov_sequence, memoryless_sequence):
    e_sequence = pd.Series(emp_sequence)
    size = len(e_sequence)
    s_sequence_iat = pd.Series(iat_sequence[:size])
    s_sequence_markov = pd.Series(markov_sequence[:size])
    s_sequence_memoryless = pd.Series(memoryless_sequence[:size])

    lag, emp = autocorr(e_sequence)
    plt.plot(lag, emp, label="AccelSim")
    lag, syn_prop = autocorr(s_sequence_iat)
    plt.plot(lag, syn_prop, label="IAT")
    lag, syn_markov = autocorr(s_sequence_markov)
    plt.plot(lag, syn_markov, label=str(ORDER) + " order markov chain")
    lag, syn_memoryless = autocorr(s_sequence_memoryless)
    plt.plot(lag, syn_memoryless, label="memoryless")
    plt.xlabel("lag")
    plt.ylabel("Autocorrelation")
    plt.legend()
    plt.show()


def generate_observed_sequence(spatial):
    sequence = []
    for cycle in spatial.keys():
        for src in spatial[cycle]:
            sequence.append(src)
    return sequence


def generate_model(traffic):
    total_window = {}
    source = {}
    window = {}
    byte = {}
    for cyc in traffic.keys():
        total_win = len(traffic[cyc])
        if len(traffic[cyc]) not in total_window.keys():
            total_window[len(traffic[cyc])] = 1
        else:
            total_window[len(traffic[cyc])] += 1
        for src, byte_list in traffic[cyc].items():
            if src not in source.keys():
                source[src] = 1
            else:
                source[src] += 1
            #if total_win not in window.keys():
                #window.setdefault(total_win, {}).setdefault(src, {})[len(byte_list)] = 1
            #else:
            if src not in window.keys():
                window.setdefault(src, {})[len(byte_list)] = 1
            else:
                if len(byte_list) not in window[src].keys():
                    window[src][len(byte_list)] = 1
                else:
                    window[src][len(byte_list)] += 1
            if src not in byte.keys():
                byte.setdefault(src, {})
            for b in byte_list:
                if b not in byte[src].keys():
                    byte[src][b] = 1
                else:
                    byte[src][b] += 1
    total_window = dict(sorted(total_window.items(), key=lambda x: x[0]))
    byte = dict(sorted(byte.items(), key=lambda x: x[0]))
    for src in byte.keys():
        byte[src] = dict(sorted(byte[src].items(), key=lambda x: x[0]))
    window = dict(sorted(window.items(), key=lambda x: x[0]))
    #for tot in window.keys():
    window = dict(sorted(window.items(), key=lambda x: x[0]))
    for src in window.keys():
        window[src] = dict(sorted(window[src].items(), key=lambda x: x[0]))
        window[src] = frequency_to_cdf(window[src])
    source = dict(sorted(source.items(), key=lambda x: x[0]))
    source = frequency_to_cdf(source)
    for src in byte.keys():
        byte[src] = frequency_to_cdf(byte[src])
    total_window = frequency_to_cdf(total_window)
    return total_window, source, window, byte


def generate_synthetic_sequence(off, byte_markov, burst_duration, burst_volume, byte_per_cycle, source, byte_req, src_window, window):
    i = 0
    prev_burst_duration = list(burst_duration.keys())[0]
    synthetic_traffic = {}
    byte_state = list(byte_markov.keys())[0]
    while i < 30000:
        on_period = generate_random_state(burst_duration[prev_burst_duration])
        prev_burst_duration = on_period
        volume = generate_random_state(burst_volume[on_period])
        temp = []
        j = 0
        while True:
            byte = generate_random_state(byte_markov[byte_state])
            temp.append(byte)
            j += 1
            byte_state = byte
            if j == on_period:
                if volume < sum(temp):
                    residual = sum(temp) - volume
                    j_ = 0
                    while residual > 0:
                        temp_byte = generate_random_state(byte_markov[byte_state])
                        byte_state = temp_byte
                        while temp_byte > residual:
                            temp_byte = generate_random_state(byte_markov[byte_state])
                            byte_state = temp_byte
                        if temp[j_] - temp_byte > 0 and (temp[j_] - temp_byte) in byte_per_cycle:
                            temp[j_] -= temp_byte
                            residual -= temp_byte
                        j_ += 1
                        if j_ == len(temp):
                            j_ = 0
                elif sum(temp) < volume:
                    residual = volume - sum(temp)
                    j_ = 0
                    while residual > 0:
                        temp_byte = generate_random_state(byte_markov[byte_state])
                        byte_state = temp_byte
                        # temp_byte = choose_correct_byte(byte_markov, synthetic_traffic, residual, "increment")
                        while temp_byte > residual:
                            temp_byte = generate_random_state(byte_markov[byte_state])
                            byte_state = temp_byte
                            # temp_byte = choose_correct_byte(byte_markov, synthetic_traffic, residual, "increment")
                        if temp[j_] + temp_byte in byte_per_cycle:
                            temp[j_] += temp_byte
                            residual -= temp_byte
                        j_ += 1
                        # print("vol: " + str(volume) + "\tperiod: " + str(on_period) + "\tgen: " + str(sum(temp)) + "\tresidual: " + str(residual) + "\tbyte: " + str(temp_byte))
                        if j_ == len(temp):
                            j_ = 0
                if sum(temp) in burst_volume[on_period].keys():
                    break
                else:
                    temp = []

        j = 0
        while j < on_period:
            while temp[j] > 0:
                src = generate_random_state(source)
                win = generate_random_state(window[src])
                for k in range(win):
                    b = generate_random_state(byte_req[src])
                    if i + j not in synthetic_traffic.keys():
                        synthetic_traffic.setdefault(i + j, {}).setdefault(src, []).append(b)
                    else:
                        if src not in synthetic_traffic[i + j].keys():
                            synthetic_traffic[i + j].setdefault(src, []).append(b)
                        else:
                            synthetic_traffic[i + j][src].append(b)
                    temp[j] -= b
            j += 1
        i += on_period

        off_period = generate_random_state(off)
        for j in range(off_period):
            pass
        i += off_period

    gc.enable()
    gc.collect()

    return synthetic_traffic

def measure_throughput(traffic):
    temp = {}
    throughput = {}
    for cyc in traffic.keys():
        for src, byte_list in traffic[cyc].items():
            if src not in temp.keys():
                temp.setdefault(src, []).append(sum(byte_list))
            else:
                temp[src].append(sum(byte_list))
    for src, byte_list in temp.items():
        throughput[src] = np.mean(byte_list)
    throughput = dict(sorted(throughput.items(), key=lambda x: x[0]))
    return throughput


if __name__ == "__main__":
    suits = benchlist.suits
    benchmarks = benchlist.single_kernels
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet_num = benchlist.chiplet_num
    path = benchlist.bench_path
    req_window = {}
    total_window_per_cycle = {}
    error = [['', '0', '1', '2', '3']]

    for suite in suits:
        if suite == "parboil":
            for bench in benchmarks[suite]:
                if bench != "aaa":
                    for topo in topology:
                        if topo == "torus":
                            for nv in NVLink:
                                if nv == "NVLink4":
                                    for ch in chiplet_num:
                                        if ch == "4chiplet":
                                            sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                                            print(sub_path)
                                            if len(os.listdir(os.path.dirname(os.path.dirname(sub_path)))) != 0:
                                                for trace_file in os.listdir(sub_path):
                                                    if Path(trace_file).suffix == '.txt':
                                                        file = open(sub_path + trace_file, "r")
                                                        raw_content = ""
                                                        if file.mode == "r":
                                                            raw_content = file.readlines()
                                                        file.close()
                                                        lined_list = []
                                                        for line in raw_content:
                                                            item = [x for x in line.split("\t") if x not in ['', '\t']]
                                                            lined_list.append(item)
                                                        request_packet = {}
                                                        for i in range(len(lined_list)):
                                                            if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
                                                                if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                                                                    request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
                                                            else:
                                                                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
                                                        del (raw_content)
                                                        del (lined_list)
                                                        request_traffic = {}
                                                        traffic = {}
                                                        reply_traffic = {}
                                                        for id in request_packet.keys():
                                                            for j in range(len(request_packet[id])):
                                                                if request_packet[id][j][0] == "request injected":
                                                                    src = int(request_packet[id][j][1].split(": ")[1])
                                                                    dst = int(request_packet[id][j][2].split(": ")[1])
                                                                    cycle = int(request_packet[id][j][5].split(": ")[1])
                                                                    byte = int(request_packet[id][j][7].split(": ")[1])
                                                                    if cycle not in request_traffic.keys():
                                                                        request_traffic.setdefault(cycle, {}).setdefault(src, []).append(byte)
                                                                    else:
                                                                        if src not in request_traffic[cycle].keys():
                                                                            request_traffic[cycle].setdefault(src, []).append(byte)
                                                                        else:
                                                                            request_traffic[cycle][src].append(byte)
                                                                    if cycle not in traffic.keys():
                                                                        traffic[cycle] = byte
                                                                    else:
                                                                        traffic[cycle] += byte
                                                                    if cycle not in req_window.keys():
                                                                        req_window.setdefault(cycle, {}).setdefault(src,[]).append(byte)
                                                                    else:
                                                                        if src not in req_window[cycle].keys():
                                                                            req_window[cycle].setdefault(src, []).append(byte)
                                                                        else:
                                                                            req_window[cycle][src].append(byte)
                                                        minimum = min(list(request_traffic.keys()))
                                                        maximum = max(list(request_traffic.keys()))
                                                        for i in range(minimum, maximum):
                                                            if i not in traffic.keys():
                                                                traffic[i] = 0
                                                        for cyc in req_window.keys():
                                                            win = len(req_window[cyc])
                                                            agg_byte = 0
                                                            for src in req_window[cyc].keys():
                                                                agg_byte += sum(req_window[cyc][src])
                                                            if agg_byte not in total_window_per_cycle.keys():
                                                                total_window_per_cycle.setdefault(agg_byte, {})[win] = 1
                                                            else:
                                                                if win not in total_window_per_cycle[agg_byte].keys():
                                                                    total_window_per_cycle[agg_byte][win] = 1
                                                                else:
                                                                    total_window_per_cycle[agg_byte][win] += 1
                                                        total_window = dict(sorted(total_window_per_cycle.items(), key=lambda x: x[0]))
                                                        for ag in total_window_per_cycle.keys():
                                                            total_window_per_cycle[ag] = dict(sorted(total_window_per_cycle[ag].items(), key=lambda x: x[0]))
                                                            total_window_per_cycle[ag] = frequency_to_cdf(total_window_per_cycle[ag])
                                                        traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
                                                        off, byte_markov, burst_duration, burst_volume, byte_per_cycle = homogeneous_mode_generator_engine.generate_traffic_characteristics(traffic, "request")

                                                        observed_throughput = measure_throughput(request_traffic)
                                                        total_window, source, window, byte = generate_model(request_traffic)
                                                        synthetic_traffic = generate_synthetic_sequence(off, byte_markov, burst_duration, burst_volume, byte_per_cycle, source, byte, total_window_per_cycle, window)
                                                        synthetic_throughput = measure_throughput(synthetic_traffic)
                                                        abs_error = {}
                                                        temp = []
                                                        temp.append(bench)
                                                        for i in error[0][1:]:
                                                            if int(i) in observed_throughput.keys():
                                                                temp.append(100*((observed_throughput[int(i)] - synthetic_throughput[int(i)])/observed_throughput[int(i)]))
                                                            else:
                                                                temp.append(0)
                                                        error.append(temp)
                                                        gc.enable()
                                                        gc.collect()
    print(tabulate(error))
