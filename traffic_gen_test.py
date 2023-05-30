import numpy as np
import matplotlib.pyplot as plt, mpld3
import scipy
from peakdetect import peakdetect
import pandas as pd
from scipy.signal import find_peaks, spectrogram
from scipy.fft import fft, fftfreq
from scipy import signal
from peakdetect import peakdetect


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
        period[f] = d/ total
    prev = 0
    cdf = {}
    for f, d in period.items():
        cdf[f] = d + prev
        prev += d
    plt.plot(cdf.keys(), cdf.values(), marker="*")
    plt.show()
    plt.close()
    #print("on_off: " + str(1 / freq[list(pdensity).index(max(pdensity))]))
    return cdf, int(np.floor(1 / freq[list(pdensity).index(max(pdensity))]))


def generate_random_number(cdf):
    random_num = np.random.uniform(0, 1, 1)
    for freq, prob in cdf.items():
        if random_num <= prob:
            return freq


def overall_injection_traffic(packet):
    traffic_ = {}
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
    maximum = list(traffic_.keys())[len(traffic_.keys())-1]
    for i in range(minimum, maximum):
        if i not in traffic_.keys():
            traffic_[i] = 0

    traffic_ = dict(sorted(traffic_.items(), key=lambda x: x[0]))
    traffic = {}
    for i in traffic_.keys():
        traffic[i - minimum] = traffic_[i]

    #plt.plot(traffic.keys(), traffic.values())
    #plt.title("AccelSim traffic")
    #plt.show()
    #plt.close()

    #indices = find_peaks(list(traffic.values()), threshold=10)[0]
    #plt.plot(traffic.keys(), traffic.values(), label="AccelSim Traffic")
    #plt.plot(indices, list(traffic[i] for i in indices), 'ko', label="peaks")
    #plt.legend()
    #plt.show()

    feature_vector = []
    window = 500
    i = 0
    temp = []
    for cyc, byte in traffic.items():
        temp.append(byte)
        if i < window:
            i += 1
        else:
            i = 0
            vec = []
            vec.append(min(temp))
            vec.append(max(temp))
            vec.append(np.mean(temp))
            vec.append(np.std(temp))
            vec.append(np.median(temp))
            vec.append(statistics.mode(temp))
            if math.isnan(scipy.stats.skew(np.array(temp))):
                vec.append(1000000)
            else:
                vec.append(scipy.stats.skew(np.array(temp)))
            if math.isnan(scipy.stats.kurtosis(np.array(temp))):
                vec.append(1000000)
            else:
                vec.append(scipy.stats.kurtosis(np.array(temp)))
            feature_vector.append(vec)
            kde = KernelDensity(kernel='gaussian', bandwidth=0.2).fit(temp)
            print(kde)
            plt.hist(temp)
            plt.hist(kde)
            plt.show()
            break
            temp.clear()

    kmeans = KMeans(n_clusters=5)
    kmeans = kmeans.fit(feature_vector)
    print(kmeans.cluster_centers_)
    labels = list(kmeans.labels_)

    markov_chain = {}
    for i in range(len(labels)):
        if i < len(labels) - 1:
            current_label = labels[i]
            next_label = labels[i + 1]
            if current_label not in markov_chain.keys():
                markov_chain.setdefault(current_label, {})[next_label] = 1
            else:
                if next_label not in markov_chain[current_label].keys():
                    markov_chain[current_label][next_label] = 1
                else:
                    markov_chain[current_label][next_label] += 1
    markov_chain = dict(sorted(markov_chain.items(), key=lambda x: x[0]))
    for c in markov_chain.keys():
        markov_chain[c] = dict(sorted(markov_chain[c].items(), key=lambda x: x[0]))


def generate_synthetic_traffic(off, on, burst):
    i = 0
    synthetic_traffic = {}
    while i < 5000000:
        on_period = generate_random_number(on) + i
        while i <= on_period:
            byte = generate_random_number(burst)
            synthetic_traffic[i] = byte
            i += 1
        off_period = generate_random_number(off) + i
        while i <= off_period:
            synthetic_traffic[i] = 0
            i += 1
    plt.plot(synthetic_traffic.keys(), synthetic_traffic.values())
    plt.title("synthetic traffic")
    plt.show()
    plt.close()
    return synthetic_traffic


def compare_traffic_byte(empirical_traffic, synthetic_traffic):
    emp_dist = {}
    for cyc, byte in empirical_traffic.items():
        if byte != 0:
            if byte not in emp_dist.keys():
                emp_dist[byte] = 1
            else:
                emp_dist[byte] += 1
    syn_dist = {}
    for cyc, byte in synthetic_traffic.items():
        if byte != 0:
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
    plt.show()


if __name__ == '__main__':
    input_ = "parboil-mri-gridding_NV4_1vc_4ch_2Dtorus_trace.txt"
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

    off, on, burst, empirical_traffic = overall_injection_traffic(request_packet)
    synthetic_traffic = generate_synthetic_traffic(off, on, burst)
    compare_traffic_byte(empirical_traffic, synthetic_traffic)
