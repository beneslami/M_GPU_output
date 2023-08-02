import os
import re
import gc
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tabulate import tabulate

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


def generate_synthetic_sequence(total_window, source, window, byte):
    j = 0
    traffic = {}
    while j < 50000:
        total_win = generate_random_state(total_window)
        i = 0
        source_list = []
        while i < total_win:
            src = generate_random_state(source)
            if src not in source_list:
                source_list.append(src)
                i += 1
        for src in source_list:
            src_win = generate_random_state(window[src])
            for k in range(src_win):
                b = generate_random_state(byte[src])
                if j not in traffic.keys():
                    traffic.setdefault(j, {}).setdefault(src, []).append(b)
                else:
                    if src not in traffic[j].keys():
                        traffic[j].setdefault(src, []).append(b)
                    else:
                        traffic[j][src].append(b)
        j += 1
    return traffic


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
    benchlist = []
    emp = "../benchmarks/stencil/torus/NVLink4/4chiplet/parboil-stencil_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/b+tree/torus/NVLink4/4chiplet/b+tree-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/spmv/torus/NVLink4/4chiplet/parboil-spmv_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/hotspot3D/torus/NVLink4/4chiplet/hotspot3D-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/3mm/new/torus/NVLink4/4chiplet/polybench-3mm_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/mri-gridding/torus/NVLink4/4chiplet/parboil-mri-gridding_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/2mm/torus/NVLink4/4chiplet/polybench-2mm_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/lavaMD/torus/NVLink4/4chiplet/lavaMD-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/kmeans/torus/NVLink4/4chiplet/kmeans-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/hybridsort/torus/NVLink4/4chiplet/hybridsort-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/2DConvolution/torus/NVLink4/4chiplet/polybench-2DConvolution_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/AlexNet/torus/NVLink4/4chiplet/tango-alexnet_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/streamcluster/torus/NVLink4/4chiplet/streamcluster-rodinia-2.0-ft_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/atax/torus/NVLink4/4chiplet/polybench-atax_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    emp = "../benchmarks/bicg/torus/NVLink4/4chiplet/polybench-bicg_NV4_1vc_4ch_2Dtorus_trace.txt"
    benchlist.append(emp)
    #emp = "../benchmarks/correlation/torus/NVLink4/4chiplet/polybench-correlation_NV4_1vc_4ch_2Dtorus_trace.txt"
    #benchlist.append(emp)
    #emp = "../benchmarks/covariance/torus/NVLink4/4chiplet/polybench-covariance_NV4_1vc_4ch_2Dtorus_trace.txt"
    #benchlist.append(emp)
    error = [['', '0', '1', '2', '3']]
    for emp in benchlist:
        temp = []
        chiplet_num = -1
        request_packet = {}
        sub_str = os.path.basename(emp).split("_")
        temp.append(sub_str[0])
        for sub_s in sub_str:
            if sub_str.index(sub_s) != 0:
                if sub_s.__contains__("ch"):
                    chiplet_num = int(re.split(r'(\d+)', sub_s)[1])
                    break
        file = open(emp, "r")
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
                    request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
            else:
                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        del (raw_content)
        del (lined_list)

        gc.enable()
        gc.collect()

        traffic = {}
        for id in request_packet.keys():
            for j in range(len(request_packet[id])):
                if request_packet[id][j][0] == "request injected":
                    src = int(request_packet[id][j][1].split(": ")[1])
                    dst = int(request_packet[id][j][2].split(": ")[1])
                    cycle = int(request_packet[id][j][5].split(": ")[1])
                    byte = int(request_packet[id][j][7].split(": ")[1])
                    if cycle not in traffic.keys():
                        traffic.setdefault(cycle, {}).setdefault(src, []).append(byte)
                    else:
                        if src not in traffic[cycle].keys():
                            traffic[cycle].setdefault(src, []).append(byte)
                        else:
                            traffic[cycle][src].append(byte)

        observed_throughput = measure_throughput(traffic)
        total_window, source, window, byte = generate_model(traffic)
        synthetic_traffic = generate_synthetic_sequence(total_window, source, window, byte)
        synthetic_throughput = measure_throughput(synthetic_traffic)
        abs_error = {}
        for i in error[0][1:]:
            if int(i) in observed_throughput.keys():
                temp.append(100*(np.abs(observed_throughput[int(i)] - synthetic_throughput[int(i)])/observed_throughput[int(i)]))
            else:
                temp.append(0)
        error.append(temp)
        gc.enable()
        gc.collect()
    print(tabulate(error))
