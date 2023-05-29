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

    on_off_cdf, _ = calculate_on_off_period(traffic)
    min_off_period = int(np.floor(1/max(list(on_off_cdf.keys()))))
    off_period = {}
    on_period = {}
    burst = {}
    prev_macro_cycle = list(traffic.keys())[0]
    prev_micro_cycle = list(traffic.keys())[0]
    macro_phase_flag = 0
    micro_phase_flag = 0
    for cycle, byte in traffic.items():
        if byte != 0:
            if byte not in burst.keys():
                burst[byte] = 1
            else:
                burst[byte] += 1
            if micro_phase_flag == 0:
                if macro_phase_flag == 1:
                    prev_micro_cycle = cycle
                else:
                    if cycle - prev_micro_cycle >= 1:
                        if (cycle - prev_micro_cycle) not in on_period.keys():
                            on_period[cycle - prev_micro_cycle] = 1
                        else:
                            on_period[cycle - prev_micro_cycle] += 1
                        if 0 not in burst.keys():
                            burst[0] = 1
                        else:
                            burst[0] = cycle - prev_micro_cycle
                    prev_micro_cycle = cycle

            if macro_phase_flag == 1:
                macro_phase_flag = 0
                if (cycle - prev_macro_cycle) not in off_period.keys():
                    off_period[cycle - prev_macro_cycle] = 1
                else:
                    off_period[cycle - prev_macro_cycle] += 1

            micro_phase_flag = 1
            prev_macro_cycle = cycle
        else:
            if cycle - prev_macro_cycle >= min_off_period:
                macro_phase_flag = 1
            if micro_phase_flag == 1:
                micro_phase_flag = 0

    on_period = dict(sorted(on_period.items(), key=lambda x: x[0]))
    off_period = dict(sorted(off_period.items(), key=lambda x: x[0]))
    burst = dict(sorted(burst.items(), key=lambda x: x[0]))
    total = sum(list(on_period.values()))
    for period, freq in on_period.items():
        on_period[period] = freq / total
    total = sum(list(off_period.values()))
    for period, freq in off_period.items():
        off_period[period] = freq / total
    total = sum(list(burst.values()))
    for b, freq in burst.items():
        burst[b] = freq / total
    prev = 0
    for period, pdf in on_period.items():
        on_period[period] = pdf + prev
        prev += pdf
    prev = 0
    for period, pdf in off_period.items():
        off_period[period] = pdf + prev
        prev += pdf
    prev = 0
    for b, pdf in burst.items():
        burst[b] = pdf + prev
        prev += pdf

    return off_period, on_period, burst, traffic


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
