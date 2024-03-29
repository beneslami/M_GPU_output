import os
import re
import gc
import math
import sys
sys.path.append("..")
from scipy.stats import ttest_ind, kstest
import homogeneous_mode_generator_engine
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tabulate import tabulate
import benchlist
from pathlib import Path

ORDER = 1


def MAPE(emp, syn):
    summation = 0
    length = 0
    assert len(emp) == len(syn)
    if not math.isnan(emp[0]) and not math.isnan(syn[0]):
        for item1, item2 in zip(emp, syn):
            summation += np.abs((item1 - item2)/item1)
            length += 1
    else:
        return 0
    return summation/length


def MAE(emp, syn):
    summation = 0
    length = 0
    assert len(emp) == len(syn)
    if not math.isnan(emp[0]) and not math.isnan(syn[0]):
        for item1, item2 in zip(emp, syn):
            summation += np.abs((item1 - item2))
            length += 1
    else:
        return 0
    return summation / length


def MSE(emp, syn):
    summation = 0
    length = 0
    assert len(emp) == len(syn)
    if not math.isnan(emp[0]) and not math.isnan(syn[0]):
        for item1, item2 in zip(emp, syn):
            summation += (item1 - item2)**2
            length += 1
    else:
        return 0
    return summation / length


def T_test(emp, syn):
    df_emp = pd.DataFrame(emp.items(), columns=['burst', 'CDF'])
    df_syn = pd.DataFrame(syn.items(), columns=['burst', 'CDF'])
    stat, p_value = ttest_ind(df_emp, df_syn)
    return p_value


def KS_test(emp, syn):
    df_emp = pd.DataFrame(emp.items(), columns=['burst', 'CDF'])
    df_syn = pd.DataFrame(syn.items(), columns=['burst', 'CDF'])
    stat, p_value = kstest(df_emp, df_syn)
    return p_value


def kullback_leibler_divergence(emp, syn):
    summation = 0
    length = 0
    assert len(emp) == len(syn)
    if not math.isnan(emp[0]) and not math.isnan(syn[0]):
        for item1, item2 in zip(emp, syn):
            summation += item2*np.log((item2 - item1)/item1)
            length += 1
    else:
        return 0
    return summation / length


def generate_random_state(cdf):
    random_num = np.random.uniform(0, 1, 1)
    for freq, prob in cdf.items():
        if random_num <= prob:
            return freq


def slide_window(items, dest):
    temp = str(items[1:]) + str(dest)
    return temp


def generate_markov_pdf(spatial):
    chain = {}
    for src in spatial.keys():
        if src not in chain.keys():
            chain.setdefault(src, {})
        window = []
        for cyc, dest_list in spatial[src].items():
            for dest in dest_list:
                if len(window) == ORDER:
                    prev = ""
                    for i in window:
                        prev += str(i)
                    if prev not in chain[src].keys():
                        chain[src].setdefault(prev, {})[dest] = 1
                    else:
                        if dest not in chain[src][prev].keys():
                            chain[src][prev][dest] = 1
                        else:
                            chain[src][prev][dest] += 1
                    temp = []
                    while len(window) != 0:
                        d = window.pop()
                        temp.append(d)
                    temp.pop()
                    while len(temp) != 0:
                        d = temp.pop()
                        window.append(d)
                    window.append(dest)
                else:
                    window.append(dest)

    chain = dict(sorted(chain.items(), key=lambda x: x[0]))
    for prev in chain.keys():
        chain[prev] = dict(sorted(chain[prev].items(), key=lambda x: x[0]))
        for next in chain[prev].keys():
            chain[prev][next] = dict(sorted(chain[prev][next].items(), key=lambda x: x[0]))
    for src in chain.keys():
        for prev in chain[src].keys():
            total = sum(list(chain[src][prev].values()))
            for dest, freq in chain[src][prev].items():
                chain[src][prev][dest] = freq / total
    for src in chain.keys():
        for prev in chain[src].keys():
            total = 0
            for dest, freq in chain[src][prev].items():
                chain[src][prev][dest] = freq + total
                total += freq
    """for p in chain.keys():
        chain[p] = dict(sorted(chain[p].items(), key=lambda x: x[0]))
        for c in chain[p].keys():
            chain[p][c] = dict(sorted(chain[p][c].items(), key=lambda x: x[0]))
    for src in chain.keys():
        for prev in chain[src].keys():
            total = sum(list(chain[src][prev].values()))
            for dest, freq in chain[src][prev].items():
                chain[src][prev][dest] = freq / total
    for src in chain.keys():
        for prev in chain[src].keys():
            total = 0
            for dest, freq in chain[src][prev].items():
                chain[src][prev][dest] = freq + total
                total += freq"""
    return chain


def generate_memoryless_pdf(spatial):
    sequence = {}
    for src in spatial.keys():
        if src not in sequence.keys():
            sequence.setdefault(src, [])
        for cyc in spatial[src].keys():
            for dest, byte in spatial[src][cyc].items():
                sequence[src].append(dest)
    pdf = {}
    for src, dest_list in sequence.items():
        if src not in pdf.keys():
            pdf.setdefault(src, {})
        for dest in dest_list:
            if dest not in pdf[src].keys():
                pdf[src][dest] = 1
            else:
                pdf[src][dest] += 1
    for src in pdf.keys():
        total = sum(list(pdf[src].values()))
        for dest, freq in pdf[src].items():
            pdf[src][dest] = freq / total
    for src in pdf.keys():
        total = 0
        for dest, freq in pdf[src].items():
            pdf[src][dest] = freq + total
            total += freq
    return pdf


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


def measure_cross_correlation(emp_sequence, syn_sequence_memory_less, syn_sequence_markov):
    print("---cross correlation (memoryless)---")
    for src in emp_sequence.keys():
        e_sequence = pd.Series(emp_sequence[src])
        size = len(e_sequence)
        s_sequence = pd.Series(syn_sequence_memory_less[src][:size])
        print("chiplet " + str(src) + ": " + str(e_sequence.corr(s_sequence)))
    print("---cross correlation (markov)---")
    for src in emp_sequence.keys():
        e_sequence = pd.Series(emp_sequence[src])
        size = len(e_sequence)
        s_sequence = pd.Series(syn_sequence_markov[src][:size])
        print("chiplet " + str(src) + ": " + str(e_sequence.corr(s_sequence)))


def measure_statistics(chiplet, lag, emp, mem, mark):
    size = np.where(lag == 10)[0][0]
    print("---chiplet " + str(chiplet) + "---")
    print("memoryless: ")
    print("MAE: " + str(MAE(emp[:size], mem[:size])))
    print("MSE: " + str(MSE(emp[:size], mem[:size])))
    print("MAPE: " + str(MAPE(emp[:size], mem[:size])))
    print("KL: " + str(kullback_leibler_divergence(emp[:size], mem[:size])))
    print("markov: ")
    print("MAE: " + str(MAE(emp[:size], mark[:size])))
    print("MSE: " + str(MSE(emp[:size], mark[:size])))
    print("MAPE: " + str(MAPE(emp[:size], mark[:size])))
    print("KL: " + str(kullback_leibler_divergence(emp[:size], mark[:size])))


def measure_auto_correlation(emp_sequence, syn_sequence_memory_less, syn_sequence_markov):
    for src in emp_sequence.keys():
        e_sequence = pd.Series(emp_sequence[src])
        size = len(e_sequence)
        s_sequence_mem = pd.Series(syn_sequence_memory_less[src][:size])
        s_sequence_mark = pd.Series(syn_sequence_markov[src][:size])
        #s_sequence_prop = pd.Series(syn_sequence_proposed[src][:size])
        lag, emp = autocorr(e_sequence)
        lag, syn_mem = autocorr(s_sequence_mem)
        lag, syn_mark = autocorr(s_sequence_mark)
        #lag, syn_prop = autocorr(s_sequence_prop)
        #measure_statistics(src, lag, emp, syn_mem, syn_mark)
        plt.plot(lag, emp, 'b', label="AccelSim")
        plt.plot(lag, syn_mem, 'r', label="memoryless")
        plt.plot(lag, syn_mark, 'g', label=str(ORDER) + " order markov chain")
        #plt.plot(lag, syn_prop, label="proposed")
        plt.xlabel("lag")
        plt.ylabel("Autocorrelation")
        plt.title("chiplet " + str(src))
        plt.legend()
        plt.show()


def measure_temporal_locality(sequence):
    locality = {}
    for src in sequence.keys():
        if src not in locality.keys():
            locality.setdefault(src, {})
        temp = max(sequence[src])
        destination = []
        for i in range(temp+1):
            destination.append(i)
        for i in destination:
            if i not in locality[src].keys():
                locality[src].setdefault(i, {})
            flag = 0
            start_position = -1
            counter = 0
            for dest in sequence[src]:
                if dest == i:
                    if flag == 0:
                        flag = 1
                        start_position = counter
                else:
                    if flag == 1:
                        if counter - start_position not in locality[src][i].keys():
                            locality[src][i][counter - start_position] = 1
                        else:
                            locality[src][i][counter - start_position] += 1
                        flag = 0
                counter += 1
    locality = dict(sorted(locality.items(), key=lambda x: x[0]))
    for src in locality.keys():
        locality[src] = dict(sorted(locality[src].items(), key=lambda x: x[0]))
        for dest in locality[src].keys():
            locality[src][dest] = dict(sorted(locality[src][dest].items(), key=lambda x: x[0]))
    for src in locality.keys():
        for dest in locality[src].keys():
            total = sum(list(locality[src][dest].values()))
            for k, v in locality[src][dest].items():
                locality[src][dest][k] = v / total
    for src in locality.keys():
        for dest in locality[src].keys():
            total = 0
            for k, v in locality[src][dest].items():
                locality[src][dest][k] = v + total
                total += v
    return locality


def compare_temporal_locality(observed, memoryless, markov, proposed):
    for src in observed.keys():
        for dest in observed[src].keys():
            plt.plot(observed[src][dest].keys(), observed[src][dest].values(), marker="o", label="AccelSim")
            plt.plot(memoryless[src][dest].keys(), memoryless[src][dest].values(), marker="o", label="memoryless")
            plt.plot(markov[src][dest].keys(), markov[src][dest].values(), marker="o", label=str(ORDER) + " order markov chain")
            plt.plot(proposed[src][dest].keys(), proposed[src][dest].values(), marker="o", label="proposed")
            plt.xlabel("locality in time")
            plt.ylabel("CDF")
            plt.title("chiplet " + str(src) + " to chiplet " + str(dest))
            plt.legend()
            plt.show()
    gc.enable()
    gc.collect()


def measure_observed_throughput(spatial):
    temp = {}
    for src in spatial.keys():
        for cycle in spatial[src].keys():
            for dest, byte in spatial[src][cycle].items():
                if dest not in temp.keys():
                    temp.setdefault(dest, {})[cycle] = byte
                else:
                    if cycle not in temp[dest].keys():
                        temp[dest][cycle] = byte
                    else:
                        temp[dest][cycle] += byte
    throughput = {}
    for src in temp.keys():
        throughput[src] = sum(list(temp[src].values()))/(max(list(temp[src].keys())) - min(list(temp[src].keys())))
    throughput = dict(sorted(throughput.items(), key=lambda x: x[0]))
    return throughput


def frequency_to_cdf(model):
    tot = sum(list(model.values()))
    for k, v in model.items():
        model[k] = v / tot
    tot = 0
    for k, v in model.items():
        model[k] = v + tot
        tot += v
    return model


def generate_model(traffic):
    destination = {}
    total_window = {}
    source = {}
    window = {}
    byte = {}
    prev_dest = {}
    dest_windw = {}
    for cyc in traffic.keys():
        for src in traffic[cyc].keys():
            for dest in traffic[cyc][src].keys():
                if src not in prev_dest.keys():
                    prev_dest[src] = dest

    for cyc in traffic.keys():
        total_byte = 0
        for src in traffic[cyc].keys():
            if src not in destination.keys():
                destination.setdefault(src, {})
            if src not in byte.keys():
                byte.setdefault(src, {})
            if src not in dest_windw.keys():
                dest_windw.setdefault(src, {})
            for dest, byte_list in traffic[cyc][src].items():
                #if prev_dest[src] not in destination[src].keys():
                    #destination[src].setdefault(prev_dest[src], {})[dest] = 1
                #else:
                total_byte += sum(byte_list)
                if dest not in destination[src].keys():
                    destination[src][dest] = 1
                else:
                    destination[src][dest] += 1
                prev_dest[src] = dest
                for b in byte_list:
                    if dest not in byte[src].keys():
                        byte[src].setdefault(dest, {})[b] = 1
                    else:
                        if b not in byte[src][dest].keys():
                            byte[src][dest][b] = 1
                        else:
                            byte[src][dest][b] += 1
        if total_byte not in total_window.keys():
            total_window.setdefault(total_byte, {})[len(traffic[cyc])] = 1
        else:
            if len(traffic[cyc]) not in total_window[total_byte].keys():
                total_window[total_byte][len(traffic[cyc])] = 1
            else:
                total_window[total_byte][len(traffic[cyc])] += 1
        for src, dest in traffic[cyc].items():
            if src not in source.keys():
                source[src] = 1
            else:
                source[src] += 1
        for src in traffic[cyc].keys():
            src_win = 0
            for dest, byte_list in traffic[cyc][src].items():
                src_win += len(byte_list)
                if dest not in dest_windw[src].keys():
                    dest_windw[src].setdefault(dest, {})[len(byte_list)] = 1
                else:
                    if len(byte_list) not in dest_windw[src][dest].keys():
                        dest_windw[src][dest][len(byte_list)] = 1
                    else:
                        dest_windw[src][dest][len(byte_list)] += 1
            if src not in window.keys():
                window.setdefault(src, {})[src_win] = 1
            else:
                if src_win not in window[src].keys():
                    window[src][src_win] = 1
                else:
                    window[src][src_win] += 1

    source = dict(sorted(source.items(), key=lambda x: x[0]))
    window = dict(sorted(window.items(), key=lambda x: x[0]))
    total_window = dict(sorted(total_window.items(), key=lambda x: x[0]))
    for b in total_window.keys():
        total_window[b] = dict(sorted(total_window[b].items(), key=lambda x: x[0]))
        total_window[b] = frequency_to_cdf(total_window[b])
    destination = dict(sorted(destination.items(), key=lambda x: x[0]))
    byte = dict(sorted(byte.items(), key=lambda x: x[0]))
    dest_windw = dict(sorted(dest_windw.items(), key=lambda x: x[0]))
    for src in byte.keys():
        destination[src] = dict(sorted(destination[src].items(), key=lambda x: x[0]))
        byte[src] = dict(sorted(byte[src].items(), key=lambda x: x[0]))
        window[src] = dict(sorted(window[src].items(), key=lambda x: x[0]))
        dest_windw[src] = dict(sorted(dest_windw[src].items(), key=lambda x: x[0]))
        for dest in byte[src].keys():
            byte[src][dest] = dict(sorted(byte[src][dest].items(), key=lambda x: x[0]))

    for src in destination.keys():
        #for prev in destination[src].keys():
        destination[src] = frequency_to_cdf(destination[src])
    for src in byte.keys():
        for dest in byte[src].keys():
            byte[src][dest] = frequency_to_cdf(byte[src][dest])
    for src in window.keys():
        window[src] = frequency_to_cdf(window[src])
        for dest in dest_windw[src].keys():
            dest_windw[src][dest] = frequency_to_cdf(dest_windw[src][dest])
    source = frequency_to_cdf(source)
    return total_window, source, window, destination, byte, dest_windw


def generate_synthetic_sequence(off, byte_markov, burst_duration, burst_volume, byte_per_cycle, total_window, source, window, destination, byte_dist, dest_window):
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
                    dest = generate_random_state(destination[src])
                    b = generate_random_state(byte_dist[src][dest])
                    if 1: #temp[j] - b >= 0:
                        if i + j not in synthetic_traffic.keys():
                            synthetic_traffic.setdefault(i + j, {}).setdefault(src, {}).setdefault(dest, []).append(b)
                        else:
                            if src not in synthetic_traffic[i + j].keys():
                                synthetic_traffic[i + j].setdefault(src, {}).setdefault(dest, []).append(b)
                            else:
                                if dest not in synthetic_traffic[i + j][src].keys():
                                    synthetic_traffic[i + j][src].setdefault(dest, []).append(b)
                                else:
                                    synthetic_traffic[i + j][src][dest].append(b)
                        temp[j] -= b
                    if temp[j] == 0:
                        break
            j += 1
        i += on_period

    off_period = generate_random_state(off)
    i += off_period


    gc.enable()
    gc.collect()

    return synthetic_traffic


def measure_destination_throughput(traffic):
    temp = {}
    throughput = {}
    for cyc in traffic.keys():
        for src in traffic[cyc].keys():
            for dest, byte_list in traffic[cyc][src].items():
                for byte in byte_list:
                    if src not in temp.keys():
                        temp.setdefault(src, {}).setdefault(dest, {}).setdefault(cyc, []).append(byte)
                    else:
                        if dest not in temp[src].keys():
                            temp[src].setdefault(dest, {}).setdefault(cyc, []).append(byte)
                        else:
                            if cyc not in temp[src][dest].keys():
                                temp[src][dest].setdefault(cyc, []).append(byte)
                            else:
                                temp[src][dest][cyc].append(byte)
    partial_th = {}
    for src in temp.keys():
        if src not in partial_th.keys():
            partial_th.setdefault(src, {})
        for dest in temp[src].keys():
            if dest not in partial_th[src].keys():
                partial_th[src].setdefault(dest, [])
            for cyc, byte_list in temp[src][dest].items():
                partial_th[src][dest].append(sum(byte_list))

    for src in partial_th.keys():
        if src not in throughput.keys():
            throughput.setdefault(src, {})
        for dest, sums in partial_th[src].items():
            throughput[src][dest] = np.mean(sums)
    throughput = dict(sorted(throughput.items(), key=lambda x: x[0]))
    for src in throughput.keys():
        throughput[src] = dict(sorted(throughput[src].items(), key=lambda x: x[0]))
    return throughput


def measure_source_throughput(traffic):
    temp = {}
    throughput = {}
    for cyc in traffic.keys():
        for src in traffic[cyc].keys():
            total = 0
            for dest, byte_list in traffic[cyc][src].items():
                total += sum(byte_list)
            if src not in temp.keys():
                temp.setdefault(src, []).append(total)
            else:
                temp[src].append(total)
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
    request_packet = {}
    req_window = {}
    total_window_per_cycle = {}
    src_error = [['', '0', '1', '2', '3']]
    dst_error = [['', '0', '1', '2', '3']]

    for suite in suits:
        if suite == "parboil":
            for bench in benchmarks[suite]:
                if bench != "adfa":
                    for topo in topology:
                        if topo == "torus":
                            for nv in NVLink:
                                if nv == "NVLink4":
                                    for ch in chiplet_num:
                                        if ch == "4chiplet":
                                            sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                                            if len(os.listdir(os.path.dirname(os.path.dirname(sub_path)))) != 0:
                                                for trace_file in os.listdir(sub_path):
                                                    if Path(trace_file).suffix == '.txt':
                                                        print(sub_path + trace_file)
                                                        file = open(sub_path + trace_file, "r")
                                                        raw_content = ""
                                                        if file.mode == "r":
                                                            raw_content = file.readlines()
                                                        file.close()
                                                        lined_list = []
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
                                                                        request_traffic.setdefault(cycle, {}).setdefault(
                                                                            src, {}).setdefault(dst, []).append(byte)
                                                                    else:
                                                                        if src not in request_traffic[cycle].keys():
                                                                            request_traffic[cycle].setdefault(src, {}).setdefault(dst, []).append(byte)
                                                                        else:
                                                                            if dst not in request_traffic[cycle][src].keys():
                                                                                request_traffic[cycle][src].setdefault(dst, []).append(byte)
                                                                            else:
                                                                                request_traffic[cycle][src][dst].append(byte)
                                                                    if cycle not in traffic.keys():
                                                                        traffic[cycle] = byte
                                                                    else:
                                                                        traffic[cycle] += byte
                                                        minimum = min(list(request_traffic.keys()))
                                                        maximum = max(list(request_traffic.keys()))
                                                        for i in range(minimum, maximum):
                                                            if i not in traffic.keys():
                                                                traffic[i] = 0
                                                        traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
                                                        off, byte_markov, burst_duration, burst_volume, byte_per_cycle = homogeneous_mode_generator_engine.generate_traffic_characteristics(traffic, "request")
                                                        destination_observed_throughput = measure_destination_throughput(request_traffic)
                                                        source_observed_throughput = measure_source_throughput(request_traffic)
                                                        total_window, source, window, destination, byte, dest_window = generate_model(request_traffic)
                                                        synthetic_traffic = generate_synthetic_sequence(off, byte_markov, burst_duration, burst_volume, byte_per_cycle, total_window, source, window, destination, byte, dest_window)
                                                        destination_synthetic_throughput = measure_destination_throughput(synthetic_traffic)
                                                        source_synthetic_throughput = measure_source_throughput(synthetic_traffic)
                                                        abs_error = {}
                                                        dest_temp = []
                                                        dest_temp.append(bench)
                                                        for i in dst_error[0][1:]:
                                                            numbers = []
                                                            if int(i) in destination_observed_throughput.keys():
                                                                for j in dst_error[0][1:]:
                                                                    if int(j) in destination_observed_throughput[int(i)].keys():
                                                                        numbers.append(((destination_observed_throughput[int(i)][int(j)] - destination_synthetic_throughput[int(i)][int(j)])))
                                                                    else:
                                                                        numbers.append(0)
                                                            else:
                                                                numbers.append(0)
                                                            dest_temp.append(numbers)
                                                        dst_error.append(dest_temp)

                                                        abs_error = {}
                                                        src_temp = []
                                                        src_temp.append(bench)
                                                        for i in src_error[0][1:]:
                                                            if int(i) in source_observed_throughput.keys():
                                                                src_temp.append(((source_observed_throughput[int(i)] - source_synthetic_throughput[int(i)])))
                                                            else:
                                                                src_temp.append(0)
                                                        src_error.append(src_temp)
                                                        gc.enable()
                                                        gc.collect()
    print(tabulate(src_error))
    print("")
    print(tabulate(dst_error))
