import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy import signal
import math
from scipy.spatial import distance
import re
import os
import gc


def MAPE(emp, syn):
    summation = 0
    length = 0
    for k, v in syn.items():
        if k in emp.keys() and emp[k] > 0:
            summation += np.abs((emp[k] - v)/emp[k])
            length += 1
    return summation/length


def MAE(emp, syn):
    summation = 0
    length = 0
    for k, v in syn.items():
        if k in emp.keys() and emp[k] > 0:
            summation += np.abs((emp[k] - v))
            length += 1
    return summation / length


def MSE(emp, syn):
    summation = 0
    length = 0
    for k, v in syn.items():
        if k in emp.keys() and emp[k] > 0:
            summation += (emp[k] - v)**2
            length += 1
    return summation / length


def kullback_leibler_divergence(emp, syn):
    sum = 0
    for item in syn.keys():
        if item in emp.keys() and emp[item] > 0:
            p = emp[item]
            q = syn[item]
            sum += p*(np.log(p/q))
    gc.enable()
    gc.collect()
    return sum


def check_markov_chain(byte_markov):
    states = list(byte_markov.keys())
    matrix = []
    for s in states:
        for next_state, prob in byte_markov[s].items():
            if next_state not in states:
                states.append(next_state)
    states.sort()
    for src in states:
        temp = []
        if src not in byte_markov.keys():
            for dst in states:
                temp.append(0)
        else:
            for dst in states:
                if dst not in byte_markov[src].keys():
                    temp.append(0)
                else:
                    temp.append(byte_markov[src][dst])
        matrix.append(temp)


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


def generate_first_level_cdf(pack):
    cdf = {}
    for s in pack.keys():
        temp = 0
        for b, freq in pack[s].items():
            temp += len(freq)
        cdf[s] = temp
    total = sum(list(cdf.values()))
    for k, v in cdf.items():
        cdf[k] = v / total
    prev = 0
    for k, v in cdf.items():
        cdf[k] = v + prev
        prev += v
    gc.enable()
    gc.collect()
    return cdf


def generate_second_level_cdf(pack):
    cdf = {}
    total = sum(list(pack.values()))
    for k, v in pack.items():
        cdf[k] = v / total
    prev = 0
    for k, v in cdf.items():
        cdf[k] = v + prev
        prev += v
    gc.enable()
    gc.collect()
    return cdf


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


def generate_burst_volume(burst, length):
    items_ = burst[length]
    dist = {}
    for vol, markovs in items_.items():
        dist[vol] = len(markovs)
    total = sum(list(dist.values()))
    for k, v in dist.items():
        dist[k] = v/total
    prev = 0
    for k, v in dist.items():
        dist[k] = v + prev
        prev += v
    num = generate_random_state(dist)
    gc.enable()
    gc.collect()
    return num


def decompose(variation, burst_length, burst_volume):
    duration = 0
    volume = 0
    minimum = 10000000
    for length in burst_length:
        for vol in burst_volume:
            if np.abs((vol/length)-variation) < minimum:
                minimum = np.abs((vol/length)-variation)
                duration = length
                volume = vol
    return duration, volume


def select_byte(ratio, sequence):
    minimum = 10000000
    selected_byte = 0
    for byte in sequence:
        if np.abs(byte - ratio) < minimum:
            selected_byte = byte
            minimum = np.abs(byte - ratio)
    return selected_byte


def choose_correct_byte(byte_markov, synthetic_traffic, residual, string):
    current_dist = {}
    for cyc, byte in synthetic_traffic.items():
        if byte > 0:
            if byte not in current_dist.keys():
                current_dist[byte] = 1
            else:
                current_dist[byte] += 1
    total = sum(list(current_dist.values()))
    for k, v in current_dist.items():
        current_dist[k] = v / total
    current_dist = dict(sorted(current_dist.items(), key=lambda x: x[0]))
    byte = 0
    if len(current_dist) == 0:
        byte = generate_random_state(byte_markov)
    else:
        if string == "decrement":
            for k in current_dist.keys():
                if current_dist[k] > byte_markov[k]:
                    byte = k
                    break
        elif string == "increment":
            for k in current_dist.keys():
                if current_dist[k] < byte_markov[k]:
                    byte = k
                    break
        print("residual: " + str(residual) + "\tbyte: " + str(byte) + "\t" + string)
        for k, v in current_dist.items():
            print(str(k) + "\t" + str(v))
    return byte


def generate_synthetic_traffic(off, byte_markov, burst_duration, burst_volume, byte_per_cycle):
    i = 0
    prev_burst_duration = list(burst_duration.keys())[0]
    synthetic_traffic = {}
    while i < 30000:
        on_period = generate_random_state(burst_duration[prev_burst_duration])
        prev_burst_duration = on_period
        volume = generate_random_state(burst_volume[on_period])
        temp = []
        j = 0
        while True:
            byte = generate_random_state(byte_markov)
            temp.append(byte)
            j += 1
            if j == on_period:
                if volume < sum(temp):
                    residual = sum(temp) - volume
                    j_ = 0
                    while residual > 0:
                        temp_byte = generate_random_state(byte_markov)
                        # temp_byte = choose_correct_byte(byte_markov, synthetic_traffic, residual, "decrement")
                        while temp_byte > residual:
                            temp_byte = generate_random_state(byte_markov)
                            # temp_byte = choose_correct_byte(byte_markov, synthetic_traffic, residual, "decrement")
                        if temp[j_] - temp_byte > 0:
                            temp[j_] -= temp_byte
                            residual -= temp_byte
                        j_ += 1
                        if j_ == len(temp):
                            j_ = 0
                elif sum(temp) < volume:
                    residual = volume - sum(temp)
                    j_ = 0
                    while residual > 0:
                        temp_byte = generate_random_state(byte_markov)
                        # temp_byte = choose_correct_byte(byte_markov, synthetic_traffic, residual, "increment")
                        while temp_byte > residual:
                            temp_byte = generate_random_state(byte_markov)
                            # temp_byte = choose_correct_byte(byte_markov, synthetic_traffic, residual, "increment")
                        if temp[j_] + temp_byte <= max(byte_per_cycle):
                            temp[j_] += temp_byte
                            residual -= temp_byte
                        j_ += 1
                        # print("vol: " + str(volume) + "\tperiod: " + str(on_period) + "\tgen: " + str(sum(temp)) + "\tresidual: " + str(residual) + "\tbyte: " + str(temp_byte))
                        if j_ == len(temp):
                            j_ = 0
                break

        j = 0
        while j < on_period:
            synthetic_traffic[i+j] = temp[j]
            j += 1
        i += on_period

        off_period = generate_random_state(off)
        for j in range(off_period):
            synthetic_traffic[i+j] = 0
        i += off_period

    gc.enable()
    gc.collect()

    return synthetic_traffic


def compare_traffic_byte(empirical_traffic, synthetic_traffic):
    emp_dist = {}
    for cyc, byte in empirical_traffic.items():
        if byte > 0:
            if byte not in emp_dist.keys():
                emp_dist[byte] = 1
            else:
                emp_dist[byte] += 1
    syn_dist = {}
    for cyc, byte in synthetic_traffic.items():
        if byte > 0:
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
    plt.plot(syn_dist.keys(), syn_dist.values(), marker="o", color='blue', linestyle='dashed', label='synthetic traffic')
    plt.title("byte distribution CDF")
    plt.legend()
    print("----byte----")
    hellinger_distance(list(emp_dist.values()), list(syn_dist.values()))
    print("KL: " + str(kullback_leibler_divergence(emp_dist, syn_dist)))
    print("MSE: " + str(MSE(emp_dist, syn_dist)))
    print("MAE: " + str(MAE(emp_dist, syn_dist)))
    print("MAPE: " + str(MAPE(emp_dist, syn_dist)))
    plt.show()
    plt.close()
    gc.enable()
    gc.collect()


def compare_burst(emp_injected_traffic, syn_injected_traffic):
    emp_burst = {}
    syn_burst = {}
    flag = 0
    total_burst = 0
    start_cycle = 0

    for cyc, temp in emp_injected_traffic.items():
        if temp == 0:
            if flag == 1:
                flag = 0
                if total_burst / (cyc - start_cycle) not in emp_burst.keys():
                    emp_burst[total_burst / (cyc - start_cycle)] = 1
                else:
                    emp_burst[total_burst / (cyc - start_cycle)] += 1
                total_burst = 0
        else:
            if flag == 0:
                start_cycle = cyc
                flag = 1
            total_burst += temp

    flag = 0
    total_burst = 0
    start_cycle = 0
    for cyc, temp in syn_injected_traffic.items():
        if temp == 0:
            if flag == 1:
                flag = 0
                if total_burst / (cyc - start_cycle) not in syn_burst.keys():
                    syn_burst[total_burst / (cyc - start_cycle)] = 1
                else:
                    syn_burst[total_burst / (cyc - start_cycle)] += 1
                total_burst = 0
        else:
            if flag == 0:
                start_cycle = cyc
                flag = 1
            total_burst += temp
    syn_burst = dict(sorted(syn_burst.items(), key=lambda x: x[0]))
    emp_burst = dict(sorted(emp_burst.items(), key=lambda x: x[0]))

    total = sum(list(emp_burst.values()))
    for burst, freq in emp_burst.items():
        emp_burst[burst] = freq / total
    total = sum(list(syn_burst.values()))
    for burst, freq in syn_burst.items():
        syn_burst[burst] = freq / total

    syn_burst = dict(sorted(syn_burst.items(), key=lambda x: x[0]))
    emp_burst = dict(sorted(emp_burst.items(), key=lambda x: x[0]))

    prev = 0
    for burst, pdf in emp_burst.items():
        emp_burst[burst] = pdf + prev
        prev += pdf
    prev = 0
    for burst, pdf in syn_burst.items():
        syn_burst[burst] = pdf + prev
        prev += pdf
    plt.plot(list(emp_burst.keys()), list(emp_burst.values()), color='green', linestyle='--', marker='o',
             label="AccelSim")
    plt.plot(list(syn_burst.keys()), list(syn_burst.values()), color='orange', linestyle='-', marker='*',
             label="Synthetic")
    plt.legend()
    plt.xlabel("burst per unit time")
    plt.ylabel("CDF")
    plt.title("network burst variation")
    print("----burst----")
    hellinger_distance(list(emp_burst.values()), list(syn_burst.values()))
    print("KL: " + str(kullback_leibler_divergence(emp_burst, syn_burst)))
    print("MSE: " + str(MSE(emp_burst, syn_burst)))
    print("MAE: " + str(MAE(emp_burst, syn_burst)))
    print("MAPE: " + str(MAPE(emp_burst, syn_burst)))
    plt.show()
    plt.close()
    gc.enable()
    gc.collect()


def compare_off_state(emp_injected_traffic, syn_injected_traffic):
    emp_burst = {}
    syn_burst = {}
    flag = 0
    start_cycle = 0

    for cyc, temp in emp_injected_traffic.items():
        if temp == 0:
            if flag == 0:
                flag = 1
                start_cycle = cyc
        else:
            if flag == 1:
                flag = 0
                if cyc - start_cycle not in emp_burst.keys():
                    emp_burst[cyc - start_cycle] = 1
                else:
                    emp_burst[cyc - start_cycle] += 1
    flag = 0
    start_cycle = 0
    for cyc, temp in syn_injected_traffic.items():
        if temp == 0:
            if flag == 0:
                flag = 1
                start_cycle = cyc
        else:
            if flag == 1:
                flag = 0
                if cyc - start_cycle not in syn_burst.keys():
                    syn_burst[cyc - start_cycle] = 1
                else:
                    syn_burst[cyc - start_cycle] += 1
    syn_burst = dict(sorted(syn_burst.items(), key=lambda x: x[0]))
    emp_burst = dict(sorted(emp_burst.items(), key=lambda x: x[0]))

    total = sum(list(emp_burst.values()))
    for burst, freq in emp_burst.items():
        emp_burst[burst] = freq / total
    total = sum(list(syn_burst.values()))
    for burst, freq in syn_burst.items():
        syn_burst[burst] = freq / total

    syn_burst = dict(sorted(syn_burst.items(), key=lambda x: x[0]))
    emp_burst = dict(sorted(emp_burst.items(), key=lambda x: x[0]))

    prev = 0
    for burst, pdf in emp_burst.items():
        emp_burst[burst] = pdf + prev
        prev += pdf
    prev = 0
    for burst, pdf in syn_burst.items():
        syn_burst[burst] = pdf + prev
        prev += pdf
    plt.plot(list(emp_burst.keys()), list(emp_burst.values()), color='red', linestyle='--', marker='o',
             label="AccelSim")
    plt.plot(list(syn_burst.keys()), list(syn_burst.values()), color='blue', linestyle='-', marker='*',
             label="Synthetic")
    plt.legend()
    plt.xlabel("off duration")
    plt.ylabel("CDF")
    plt.title("network off state")
    print("----offState----")
    hellinger_distance(list(emp_burst.values()), list(syn_burst.values()))
    print("KL: " + str(kullback_leibler_divergence(emp_burst, syn_burst)))
    print("MSE: " + str(MSE(emp_burst, syn_burst)))
    print("MAE: " + str(MAE(emp_burst, syn_burst)))
    print("MAPE: " + str(MAPE(emp_burst, syn_burst)))
    plt.show()
    plt.close()
    gc.enable()
    gc.collect()


def markov_matrix_generator(sequence):
    states = []
    transitions = {}
    prev_state = list(sequence.values())[0]
    states.append(prev_state)
    for cycle, state in sequence.items():
        if state not in states:
            states.append(state)
        if prev_state not in transitions.keys():
            transitions.setdefault(prev_state, {})[state] = 1
        else:
            if state not in transitions[prev_state].keys():
                transitions[prev_state][state] = 1
            else:
                transitions[prev_state][state] += 1
        prev_state = state
    transitions = dict(sorted(transitions.items(), key=lambda x: x[0]))
    for c in transitions.keys():
        transitions[c] = dict(sorted(transitions[c].items(), key=lambda x: x[0]))
    del(states)
    for s in transitions.keys():
        total = sum(list(transitions[s].values()))
        for d, freq in transitions[s].items():
            transitions[s][d] = freq/total
    prev = 0
    for s in transitions.keys():
        for d, pdf in transitions[s].items():
            transitions[s][d] = pdf + prev
            prev += pdf
    gc.enable()
    gc.collect()
    return transitions


def list_markov_matrix_generator(sequence):
    prev = sequence[0]
    cdf = {}
    for s in sequence:
        if prev not in cdf.keys():
            cdf.setdefault(prev, {})[s] = 1
        else:
            if s not in cdf[prev].keys():
                cdf[prev][s] = 1
            else:
                cdf[prev][s] += 1
        prev = s
    for s in cdf.keys():
        total = sum(list(cdf[s].values()))
        for k, v in cdf[s].items():
            cdf[s][k] = v/total
    for s in cdf.keys():
        prev = 0
        for k, v in cdf[s].items():
            cdf[s][k] = v + prev
            prev += v
    cdf = dict(sorted(cdf.items(), key=lambda x: x[0]))
    gc.enable()
    gc.collect()
    return cdf


def memoryless_distribution_generator(sequence):
    cdf = {}
    for cyc, duration in sequence.items():
        if duration not in cdf.keys():
            cdf[duration] = 1
        else:
            cdf[duration] += 1
    total = sum(list(cdf.values()))
    for k, v in cdf.items():
        cdf[k] = v/total
    prev = 0
    for k, v in cdf.items():
        cdf[k] = v + prev
        prev += v
    gc.enable()
    gc.collect()
    return cdf


def generate_traffic_characteristics(traffic, string):
    off_cycle = 0
    on_cycle = 0
    off_counter = 0
    off_burst_sequence = {}
    burst_variation = {}
    burst_volume = {}
    byte_per_cycle = []
    big_byte_markov_chain = {}
    on_burst = {}
    off_flag = 0
    on_flag = 0
    total_burst = 0
    start_generating = 0
    prev = 0
    on_prev = 1
    if string == "request":
        for cyc, byte in traffic.items():
            if byte == 0:
                if off_flag == 0:
                    off_cycle = cyc
                    off_flag = 1
                if on_flag == 1:
                    on_flag = 0
                    if on_prev not in on_burst.keys():
                        on_burst.setdefault(on_prev, {})[cyc - on_cycle] = 1
                    else:
                        if cyc - on_cycle not in on_burst[on_prev].keys():
                            on_burst[on_prev][cyc - on_cycle] = 1
                        else:
                            on_burst[on_prev][cyc - on_cycle] += 1
                    if cyc - on_cycle not in burst_volume.keys():
                        burst_volume.setdefault(cyc - on_cycle, {})[total_burst] = 1
                    else:
                        if total_burst not in burst_volume[cyc - on_cycle].keys():
                            burst_volume[cyc - on_cycle][total_burst] = 1
                        else:
                            burst_volume[cyc - on_cycle][total_burst] += 1
                    total_burst = 0
                    on_prev = cyc - on_cycle
            elif byte != 0:
                if off_flag == 1:
                    off_flag = 0
                    if cyc - off_cycle not in off_burst_sequence.keys():
                        off_burst_sequence[cyc - off_cycle] = 1
                    else:
                        off_burst_sequence[cyc - off_cycle] += 1
                if on_flag == 0:
                    on_flag = 1
                    on_cycle = cyc
                total_burst += byte
                if byte not in byte_per_cycle:
                    byte_per_cycle.append(byte)
                if byte not in big_byte_markov_chain.keys():
                    big_byte_markov_chain[byte] = 1
                else:
                    big_byte_markov_chain[byte] += 1
                """if start_generating == 0:
                    prev = byte
                    start_generating = 1
                else:
                    if prev not in big_byte_markov_chain.keys():
                        big_byte_markov_chain.setdefault(prev, {})[byte] = 1
                    else:
                        if byte not in big_byte_markov_chain[prev].keys():
                            big_byte_markov_chain[prev][byte] = 1
                        else:
                            big_byte_markov_chain[prev][byte] += 1
                prev = byte"""
        off_burst_sequence = dict(sorted(off_burst_sequence.items(), key=lambda x: x[0]))
        byte_per_cycle.sort()
        on_burst = dict(sorted(on_burst.items(), key=lambda x: x[0]))
        for p in on_burst.keys():
            total = sum(list(on_burst[p].values()))
            for k, v in on_burst[p].items():
                on_burst[p][k] = v / total
        for p in on_burst.keys():
            total = 0
            for k, v in on_burst[p].items():
                on_burst[p][k] = v + total
                total += v

        burst_volume = dict(sorted(burst_volume.items(), key=lambda x: x[0]))
        for p in burst_volume.keys():
            total = sum(list(burst_volume[p].values()))
            for k, v in burst_volume[p].items():
                burst_volume[p][k] = v / total
        for p in burst_volume.keys():
            total = 0
            for k, v in burst_volume[p].items():
                burst_volume[p][k] = v + total
                total += v
        total = sum(list(off_burst_sequence.values()))
        for k, v in off_burst_sequence.items():
            off_burst_sequence[k] = v / total

        """for p in big_byte_markov_chain.keys():
            total = sum(list(big_byte_markov_chain[p].values()))
            for k, v in big_byte_markov_chain[p].items():
                big_byte_markov_chain[p][k] = v / total
        for p in big_byte_markov_chain.keys():
            total = 0
            for k, v in big_byte_markov_chain[p].items():
                big_byte_markov_chain[p][k] = v + total
                total += v"""

        total = sum(list(big_byte_markov_chain.values()))
        for k, v in big_byte_markov_chain.items():
            big_byte_markov_chain[k] = v / total
        total = 0
        for k, v in big_byte_markov_chain.items():
            big_byte_markov_chain[k] = v + total
            total += v

        total = 0
        for k, v in off_burst_sequence.items():
            off_burst_sequence[k] = v + total
            total += v
        #check_markov_chain(big_byte_markov_chain)

        """with open("model.txt", "w") as file:
            file.write("off_begin\n")
            for k, v in off_transitions.items():
                file.write(str(k) + "\t" + str(v) + "\n")
            file.write("off_end\n\n")

            file.write("burst_begin\n")
            for burst_length in on_burst.keys():
                file.write("period\t" + str(burst_length) + "\n")
                for val, markov in on_burst[burst_length].items():
                    file.write("burst\t" + str(val) + "\n")
                    file.write(str(markov) + "\n")
            file.write("burst_end\n\n")"""
    elif string == "reply":
        for cyc, byte in traffic.items():
            if byte == 0:
                if off_flag == 0:
                    off_cycle = cyc
                    off_flag = 1
                if on_flag == 1:
                    on_flag = 0
                    if on_prev not in on_burst.keys():
                        on_burst.setdefault(on_prev, {})[cyc - on_cycle] = 1
                    else:
                        if cyc - on_cycle not in on_burst[on_prev].keys():
                            on_burst[on_prev][cyc - on_cycle] = 1
                        else:
                            on_burst[on_prev][cyc - on_cycle] += 1
                    if cyc - on_cycle not in burst_volume.keys():
                        burst_volume.setdefault(cyc - on_cycle, {})[total_burst] = 1
                    else:
                        if total_burst not in burst_volume[cyc - on_cycle].keys():
                            burst_volume[cyc - on_cycle][total_burst] = 1
                        else:
                            burst_volume[cyc - on_cycle][total_burst] += 1
                    total_burst = 0
                    on_prev = cyc - on_cycle
            elif byte != 0:
                if off_flag == 1:
                    off_flag = 0
                    if cyc - off_cycle not in off_burst_sequence.keys():
                        off_burst_sequence[cyc - off_cycle] = 1
                    else:
                        off_burst_sequence[cyc - off_cycle] += 1
                if on_flag == 0:
                    on_flag = 1
                    on_cycle = cyc
                total_burst += byte
                if byte not in byte_per_cycle:
                    byte_per_cycle.append(byte)
                if byte not in big_byte_markov_chain.keys():
                    big_byte_markov_chain[byte] = 1
                else:
                    big_byte_markov_chain[byte] += 1
        off_burst_sequence = dict(sorted(off_burst_sequence.items(), key=lambda x: x[0]))
        byte_per_cycle.sort()
        on_burst = dict(sorted(on_burst.items(), key=lambda x: x[0]))
        for p in on_burst.keys():
            total = sum(list(on_burst[p].values()))
            for k, v in on_burst[p].items():
                on_burst[p][k] = v / total
        for p in on_burst.keys():
            total = 0
            for k, v in on_burst[p].items():
                on_burst[p][k] = v + total
                total += v

        burst_volume = dict(sorted(burst_volume.items(), key=lambda x: x[0]))
        for p in burst_volume.keys():
            total = sum(list(burst_volume[p].values()))
            for k, v in burst_volume[p].items():
                burst_volume[p][k] = v / total
        for p in burst_volume.keys():
            total = 0
            for k, v in burst_volume[p].items():
                burst_volume[p][k] = v + total
                total += v
        total = sum(list(off_burst_sequence.values()))
        for k, v in off_burst_sequence.items():
            off_burst_sequence[k] = v / total
        total = sum(list(big_byte_markov_chain.values()))
        for k, v in big_byte_markov_chain.items():
            big_byte_markov_chain[k] = v / total
        total = 0
        for k, v in big_byte_markov_chain.items():
            big_byte_markov_chain[k] = v + total
            total += v
        total = 0
        for k, v in off_burst_sequence.items():
            off_burst_sequence[k] = v + total
            total += v
    plt.figure(figsize=(20, 7))
    plt.plot(traffic.keys(), traffic.values())
    plt.show()
    plt.close()
    return off_burst_sequence, big_byte_markov_chain, on_burst, burst_volume, byte_per_cycle


if __name__ == "__main__":
    #emp = "../benchmarks/b+tree/torus/NVLink4/4chiplet/b+tree-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/spmv/torus/NVLink4/4chiplet/parboil-spmv_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/mri-gridding/torus/NVLink4/4chiplet/parboil-mri-gridding_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/2DConvolution/torus/NVLink4/4chiplet/polybench-2DConvolution_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/AlexNet/torus/NVLink4/4chiplet/tango-alexnet_NV4_1vc_4ch_2Dtorus_trace.txt"
    chiplet_num = -1
    request_packet = {}
    sub_str = os.path.basename(emp).split("_")
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
    request_traffic = {}
    reply_traffic = {}
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "request injected":
                src = int(request_packet[id][j][1].split(": ")[1])
                dst = int(request_packet[id][j][2].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if cycle not in request_traffic.keys():
                    request_traffic[cycle] = byte
                else:
                    request_traffic[cycle] += byte
            if request_packet[id][j][0] == "reply injected":
                src = int(request_packet[id][j][2].split(": ")[1])
                dst = int(request_packet[id][j][1].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if cycle not in reply_traffic.keys():
                    reply_traffic[cycle] = byte
                else:
                    reply_traffic[cycle] += byte

    minimum = min(list(request_traffic.keys()))
    maximum = max(list(request_traffic.keys()))
    for i in range(minimum, maximum):
        if i not in request_traffic.keys():
            request_traffic[i] = 0
    request_traffic = dict(sorted(request_traffic.items(), key=lambda x: x[0]))
    minimum = min(list(reply_traffic.keys()))
    maximum = max(list(reply_traffic.keys()))
    for i in range(minimum, maximum):
        if i not in reply_traffic.keys():
            reply_traffic[i] = 0
    reply_traffic = dict(sorted(reply_traffic.items(), key=lambda x: x[0]))

    off, byte_markov, burst_duration, burst_volume, byte_per_cycle = generate_traffic_characteristics(request_traffic, "request")
    synthetic_traffic = generate_synthetic_traffic(off, byte_markov, burst_duration, burst_volume, byte_per_cycle)
    compare_traffic_byte(request_traffic, synthetic_traffic)
    compare_burst(request_traffic, synthetic_traffic)
    compare_off_state(request_traffic, synthetic_traffic)
    off, byte_markov, burst_duration, burst_volume, byte_per_cycle = generate_traffic_characteristics(reply_traffic, "reply")
    synthetic_traffic = generate_synthetic_traffic(off, byte_markov, burst_duration, burst_volume, byte_per_cycle)
    compare_traffic_byte(reply_traffic, synthetic_traffic)
    compare_burst(reply_traffic, synthetic_traffic)
    compare_off_state(reply_traffic, synthetic_traffic)