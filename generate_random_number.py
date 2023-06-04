from sklearn.cluster import KMeans
import statistics
import math
import numpy as np
import scipy


def clustering(packet):
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
    maximum = list(traffic_.keys())[len(traffic_.keys()) - 1]
    for i in range(minimum, maximum):
        if i not in traffic_.keys():
            traffic_[i] = 0

    traffic_ = dict(sorted(traffic_.items(), key=lambda x: x[0]))
    traffic = {}
    for i in traffic_.keys():
        traffic[i - minimum] = traffic_[i]
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
    print(markov_chain)


if __name__ == '__main__':
    input_ = "../benchmarks/mri-gridding/torus/NVLink4/4chiplet/parboil-mri-gridding_NV4_1vc_4ch_2Dtorus_trace.txt"
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
    clustering(request_packet)
    centroid = [[2.50000000e-02, 1.45375000e+02, 4.21613273e+01, 3.43529487e+01,
                 3.68500000e+01, 2.60500000e+01, 7.96372321e-01, 3.21481221e-01],
                [2.22044605e-16, 2.84217094e-14, 0.00000000e+00, 1.42108547e-14,
                 -2.84217094e-14, 7.10542736e-15, 1.00000000e+06, 1.00000000e+06],
                [6.23376623e-01, 2.51387013e+02, 8.75763693e+01, 5.30408562e+01,
                 8.22025974e+01, 6.71792208e+01, 5.54217050e-01, 1.87271013e-02],
                [1.96226415e+00, 3.46968553e+02, 1.23299765e+02, 6.85507558e+01,
                 1.16226415e+02, 9.70062893e+01, 5.93571458e-01, 2.51335084e-01],
                [0.00000000e+00, 4.00000000e+01, 1.27744511e-01, 2.22746145e+00,
                 0.00000000e+00, 0.00000000e+00, 1.83657394e+01, 3.45703205e+02]]
    markov_chain = {0: {0: 236, 1: 3, 2: 62, 3: 3, 4: 1}, 1: {0: 4, 1: 8, 4: 3}, 2: {0: 63, 2: 242, 3: 82},
                    3: {0: 3, 2: 82, 3: 86}, 4: {1: 4, 4: 1}}

    features = centroid[0]
    global_space = []
    min_val = features[0]
    max_val = features[1]
    number = int(np.floor(min_val))
    while number <= max_val:
        residual = 0
        if number % 8 < 0.5:
            residual = 0
        else:
            residual = 1
        global_space.append(int(np.floor(number / 8)) * 8 + residual)
        number += 8
    avg = features[2]
    std = features[3]
    median = features[4]
    mode = features[5]
    skew = features[6]
    kurt = features[7]

    print(global_space)
    print("Mean: " + str(avg))
    print("std: " + str(std))
    print("median: " + str(median))
    print("mode: " + str(mode))
    print("-----------")
    min_avg = max_val
    min_std = 0
    min_median = max_val
    min_mode = max_val
    new_avg = 0
    new_median = 0
    new_mode = 0
    for item in global_space:
        if np.abs(avg - item) < min_avg:
            min_avg = np.abs(avg - item)
            new_avg = item
        if np.abs(median - item) < min_median:
            min_median = np.abs(median - item)
            new_median = item
        if np.abs(mode - item) < min_mode:
            min_mode = np.abs(mode - item)
            new_mode = item
    avg = new_avg
    median = new_median
    mode = new_mode
    std = 0
    for item in global_space:
        std += (item - avg) ** 2
    std = np.sqrt(std / len(global_space))

    print("Mean: " + str(avg))
    print("std: " + str(std))
    print("median: " + str(median))
    print("mode: " + str(mode))

    global_mean_index = int(global_space.index(avg))
    global_median_index = int(global_space.index(median))
    global_mode_index = int(global_space.index(mode))
    sample_space = []
    sample_space.append(mode)
    sample_space.append(median)
    sample_space.append(avg)
    for i in range(1000):
        if np.mean(sample_space) <= avg:
            median_index = int(sample_space.index(int(np.median(sample_space))))
            if len(sample_space[:median_index]) <= len(sample_space[median_index + 1:]):
                # generate number from first half between median and mean
                x = global_space[global_median_index: global_mean_index + 1]
                byte = np.random.choice(x)
                sample_space.append(byte)
            else:
                x = global_space[global_median_index:]
                byte = np.random.choice(x)
                sample_space.append(byte)
                # generate number from second half
        else:
            median_index = int(sample_space.index(int(np.median(sample_space))))
            if len(sample_space[:median_index]) <= len(sample_space[median_index + 1:]):
                x = global_space[:global_median_index]
                byte = np.random.choice(x)
                sample_space.append(byte)
                # generate number from first half
            else:
                x = global_space[global_median_index: global_mean_index + 1]
                byte = np.random.choice(x)
                sample_space.append(byte)
                # generate number from first half between median and mean
        sample_space = sorted(sample_space)
    plt.hist(sample_space)
    plt.show()