import numpy as np
import matplotlib.pyplot as plt
import scipy
import pandas as pd
from scipy.signal import find_peaks, spectrogram
from scipy.fft import fft, fftfreq
from scipy import signal
import statistics
import math
import statsmodels.api as sm
from sklearn.cluster import KMeans
from scipy.spatial import distance
from gensim.matutils import hellinger


def calculate_on_off_period(traffic):
    freq, pdensity = signal.periodogram(list(traffic.values()))
    spectrum = {}
    for i in range(len(freq)):
        if pdensity[i] < 1:
            continue
        else:
            spectrum[freq[i]] = pdensity[i]
    spectrum = dict(sorted(spectrum.items(), key=lambda x: x[0]))
    index, _ = find_peaks(list(spectrum.values()), prominence=2, height=20)
    peaks = {}
    for i in index:
        peaks[list(spectrum.keys())[i]] = list(spectrum.values())[i]

    plt.plot(peaks.keys(), peaks.values(), 'ko')
    plt.plot(spectrum.keys(), spectrum.values())
    plt.xlabel("period")
    plt.ylabel("Density")
    plt.show()
    plt.close()

    period = {}
    minimum = np.inf
    for f, peak in peaks.items():
        if peak < minimum:
            period[f] = peak
            minimum = peak
        else:
            break
    total = sum(period.values())
    for f, d in period.items():
        period[f] = d / total
    prev = 0
    cdf = {}
    for f, d in period.items():
        cdf[f] = d + prev
        prev += d
    plt.plot(cdf.keys(), cdf.values(), marker="*")
    plt.show()
    plt.close()
    # print("on_off: " + str(1 / freq[list(pdensity).index(max(pdensity))]))
    return cdf, int(np.floor(1 / freq[list(pdensity).index(max(pdensity))]))


def generate_random_byte(cdf):
    minimum = min(list(cdf.values()))
    maximum = max(list(cdf.values()))
    random_num = np.random.uniform(0, maximum, 1)
    for freq, prob in cdf.items():
        if random_num <= prob:
            return freq


def generate_random_state(cdf):
    random_num = np.random.uniform(0, 1, 1)
    for freq, prob in cdf.items():
        if random_num <= prob:
            return freq


def measure_distance(p, q):
    if len(p) != len(q):
        return 0
    dist = distance.euclidean(p, q)
    if dist < 0.2:
        return 1
    else:
        return 0


def hellinger_distance(p, q):
    if len(p) != len(q):
        index = 0
        for n in q:
            if n not in p:
                index = q.index(n)
                break
        q = q[:index+1]
    list_of_squares = []
    for p_i, q_i in zip(p, q):
        s = (math.sqrt(p_i) - math.sqrt(q_i)) ** 2
        list_of_squares.append(s)
    sosq = math.sqrt(sum(list_of_squares)/2)
    print("H(p,q): " + str(sosq))


def clustering(cluster, dist, overall_byte_cdf):
    result = 0
    for id, cdf in cluster.items():
        result = measure_distance(list(cdf.values()), list(dist.values()))
        if result == 1:
            new_cdf = {}
            for byte, prob in cdf.items():
                new_cdf[byte] = overall_byte_cdf[byte]
            for byte, prob in dist.items():
                new_cdf[byte] = overall_byte_cdf[byte]
            cluster[id] = new_cdf
            return 1, id
    if result == 0:
        return 0, -1


def overall_injection_traffic(packet):
    traffic_ = {}
    overall_dist = {}
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "request injected":
                cycle = int(packet[id][j][5].split(": ")[1])
                byte = int(packet[id][j][7].split(": ")[1])
                if cycle not in traffic_.keys():
                    traffic_[cycle] = byte
                else:
                    traffic_[cycle] += byte
    minimum = list(traffic_.keys())[0]
    maximum = list(traffic_.keys())[len(traffic_.keys()) - 1]
    for i in range(minimum, maximum):
        if i not in traffic_.keys():
            traffic_[i] = 0

    traffic_ = dict(sorted(traffic_.items(), key=lambda x: x[0]))
    traffic = {}
    for i in traffic_.keys():
        if i < 400000:
            traffic[i - minimum] = traffic_[i]

    plt.figure(figsize=(20, 7))
    plt.plot(traffic.keys(), traffic.values(), marker="*")
    plt.title("AccelSim traffic")
    plt.show()
    plt.close()

    """with open("byte.csv", "w") as file:
        file.write("cycle,byte\n")
        for cyc, byte in traffic.items():
            if 145750 <= cyc <= 146250:
                file.write(str(cyc) + "," + str(byte) + "\n")"""

    for cyc, byte in traffic.items():
        if byte not in overall_dist.keys():
            overall_dist[byte] = 1
        else:
            overall_dist[byte] += 1
    overall_dist = dict(sorted(overall_dist.items(), key=lambda x: x[0]))
    total = sum(list(overall_dist.values()))
    for byte, freq in overall_dist.items():
        overall_dist[byte] = freq / total
    prev = 0
    for byte, pdf in overall_dist.items():
        overall_dist[byte] = pdf + prev
        prev += pdf

    return traffic, overall_dist


def generate_statistics_based_on_interval_sttistics_calculation_clustering_markov_chain(traffic):
    counter = 0
    markov_chain = {}
    chain = {}
    window = 1000
    i = 0
    temp = []
    for cyc, byte in traffic.items():
        temp.append(byte)
        if i < window:
            i += 1
        else:
            i = 0
            state = temp[0]
            for j in range(1, len(temp)):
                if state not in chain.keys():
                    chain.setdefault(state, {})[temp[j]] = 1
                else:
                    if temp[j] not in chain[state].keys():
                        chain[state][temp[j]] = 1
                    else:
                        chain[state][temp[j]] += 1
                state = temp[j]
            temp.clear()
            markov_chain[counter] = chain
            counter += 1

    markov_chain = dict(sorted(markov_chain.items(), key=lambda x: x[0]))
    for s in markov_chain.keys():
        markov_chain[s] = dict(sorted(markov_chain[s].items(), key=lambda x: x[0]))
        for st in markov_chain[s].keys():
            markov_chain[s][st] = dict(sorted(markov_chain[s][st].items(), key=lambda x: x[0]))

    for counter in markov_chain.keys():
        for cur in markov_chain[counter].keys():
            tot = sum(list(markov_chain[counter][cur].values()))
            for next, freq in markov_chain[counter][cur].items():
                markov_chain[counter][cur][next] = freq / tot
    for counter in markov_chain.keys():
        for cur in markov_chain[counter].keys():
            prev = 0
            for next, pdf in markov_chain[counter][cur].items():
                markov_chain[counter][cur][next] = pdf + prev
                prev += pdf

    return markov_chain


def generate_statistics_based_on_overall_random_behavior(traffic, overall_byte_cdf):
    cluster = {}
    markov_chain = {}
    cluster[0] = overall_byte_cdf
    markov_chain.setdefault(0, {})[0] = 1
    return cluster, markov_chain


def generate_synthetic_traffic(markov_chain):
    i = 0
    window = 1000
    synthetic_traffic = {}
    while i < 355000:
        period = i + window
        intervals = list(markov_chain.keys())
        interval = np.random.choice(intervals)
        byte = list(markov_chain[interval].keys())[0]
        while i < period:
            synthetic_traffic[i] = byte
            i += 1
            byte = generate_random_state(markov_chain[interval][byte])

    plt.figure(figsize=(20, 7))
    plt.plot(synthetic_traffic.keys(), synthetic_traffic.values(), marker='*')
    plt.title("synthetic traffic")
    plt.show()
    plt.close()
    return synthetic_traffic


def compare_traffic_byte(empirical_traffic, synthetic_traffic):
    emp_dist = {}
    for cyc, byte in empirical_traffic.items():
        if byte not in emp_dist.keys():
            emp_dist[byte] = 1
        else:
            emp_dist[byte] += 1
    syn_dist = {}
    for cyc, byte in synthetic_traffic.items():
        if byte not in syn_dist.keys():
            syn_dist[byte] = 1
        else:
            syn_dist[byte] += 1

    total = sum(list(emp_dist.values()))
    for byte, freq in emp_dist.items():
        emp_dist[byte] = freq / total
    total = sum(list(syn_dist.values()))
    for byte, freq in syn_dist.items():
        syn_dist[byte] = freq / total
    emp_dist = dict(sorted(emp_dist.items(), key=lambda x: x[0]))
    syn_dist = dict(sorted(syn_dist.items(), key=lambda x: x[0]))
    plt.plot(emp_dist.keys(), emp_dist.values(), marker="*", color='red', label='AccelSim traffic')
    plt.plot(syn_dist.keys(), syn_dist.values(), marker="o", color='blue', linestyle='dashed',
             label='synthetic traffic')
    plt.legend()
    hellinger_distance(list(emp_dist.values()), list(syn_dist.values()))
    plt.show()


if __name__ == '__main__':
    #input_ = "../benchmarks/mri-gridding/torus/NVLink4/4chiplet/parboil-mri-gridding_NV4_1vc_4ch_2Dtorus_trace.txt"
    #input_ = "../benchmarks/spmv/torus/NVLink4/4chiplet/parboil-spmv_NV4_1vc_4ch_2Dtorus_trace.txt"
    #input_ = "../benchmarks/2DConvolution/torus/NVLink4/4chiplet/polybench-2DConvolution_NV4_1vc_4ch_2Dtorus_trace.txt"
    #input_ = "../benchmarks/3mm/torus/NVLink4/4chiplet/polybench-3mm_NV4_1vc_4ch_2Dtorus_trace.txt"
    #input_ = "../benchmarks/atax/torus/NVLink4/4chiplet/polybench-atax_NV4_1vc_4ch_2Dtorus_trace.txt"
    #input_ = "../benchmarks/bicg/torus/NVLink4/4chiplet/polybench-bicg_NV4_1vc_4ch_2Dtorus_trace.txt"
    input_ = "../benchmarks/b+tree/torus/NVLink4/4chiplet/b+tree-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    file2 = open(input_, "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    file2.close()
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

    empirical_traffic, _ = overall_injection_traffic(request_packet)
    markov_chain = generate_statistics_based_on_interval_sttistics_calculation_clustering_markov_chain(empirical_traffic)
    synthetic_traffic = generate_synthetic_traffic(markov_chain)
    compare_traffic_byte(empirical_traffic, synthetic_traffic)
