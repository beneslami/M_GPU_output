import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import numpy as np
import statistics
from scipy.spatial import distance
import warnings
warnings.filterwarnings("ignore")


def phase_clustering(input_, packet):
    base_path = os.path.dirname(input_)
    range_ = {}
    cycle_range = {}
    total_injection = {}
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "request injected":
                source = int(packet[id][j][1].split(": ")[1])
                dest = int(packet[id][j][2].split(": ")[1])
                cycle = int(packet[id][j][5].split(": ")[1])
                byte = int(packet[id][j][7].split(": ")[1])
                if cycle not in range_.keys():
                    range_.setdefault(cycle, {}).setdefault(source, {}).setdefault(dest, {})[byte] = 1
                else:
                    if source not in range_[cycle].keys():
                        range_[cycle].setdefault(source, {}).setdefault(dest, {})[byte] = 1
                    else:
                        if dest not in range_[cycle][source].keys():
                            range_[cycle][source].setdefault(dest, {})[byte] = 1
                        else:
                            if byte not in range_[cycle][source][dest].keys():
                                range_[cycle][source][dest][byte] = 1
                            else:
                                range_[cycle][source][dest][byte] += 1

                if cycle not in total_injection.keys():
                    total_injection[cycle] = byte
                else:
                    total_injection[cycle] += byte

    df = pd.read_csv(base_path + "/data/burst_length_distribution.csv")
    x = df['duration']
    y = df['pdf']
    partial_sum = 0
    for i in range(len(x)):
        partial_sum += x[i]*y[i]
    window = np.floor(partial_sum / sum(y))

    m = np.min(list(range_.keys()))
    M = np.max(list(range_.keys()))
    for i in range(m, M, 1):
        if i not in range_.keys():
            cycle_range[i] = 0
            total_injection[i] = 0
        else:
            cycle_range[i] = range_[i]
    total_injection = dict(sorted(total_injection.items(), key=lambda x: x[0]))

    c = 0
    counter_ = 0
    temp = []
    total_injection_ = {}
    for cycle in total_injection.keys():
        if c != window:
            temp.append(total_injection[cycle])
            c += 1
        elif c == window:
            c = 0
            total_injection_[counter_] = np.mean(temp)
            temp.clear()
            counter_ += 1

    cluster = 5
    centroid = {}
    phase = {}
    feature_vector = {}
    for i in range(1, cluster+1):
        feature_vector.setdefault(i, [])
        centroid.setdefault(i, [])
    for num_cluster in range(1, cluster+1):
        counter = 0
        src = []
        dest = []
        bytes = []
        for cycle in cycle_range.keys():
            if not isinstance(cycle_range[cycle], int):
                for src_ in cycle_range[cycle].keys():
                    src.append(src_)
                    for dest_ in cycle_range[cycle][src_].keys():
                        dest.append(dest_)
                        temp = 0
                        for bytes_, freq in cycle_range[cycle][src_][dest_].items():
                            temp += bytes_*freq
                        bytes.append(temp)
            else:
                src.append(-1)
                dest.append(-1)
                bytes.append(0)

            if counter != window:
                counter += 1
            else:
                counter = 0
                temp = []
                if len(src) != 0:
                    src_mod = statistics.mode(src)
                    temp.append(src_mod)
                if len(dest) != 0:
                    dst_mod = statistics.mode(dest)
                    temp.append(dst_mod)
                if len(bytes) != 0:
                    win_byte = np.mean(bytes)
                    temp.append(win_byte)
                if len(temp) != 0:
                    feature_vector[num_cluster].append(temp)
                src.clear()
                dest.clear()
                bytes.clear()
        kmeans = KMeans(n_clusters=num_cluster)
        kmeans = kmeans.fit(list(feature_vector[num_cluster]))  # Fitting the input data
        labels = kmeans.predict(list(feature_vector[num_cluster]))  # Getting the cluster labels
        centroid[num_cluster].append(kmeans.cluster_centers_)

    fig = plt.figure(figsize=(20, 20))
    fig.tight_layout()
    plt.subplots_adjust(wspace=0.868, hspace=0.798, top=0.962, right=0.958, bottom=0.03, left=0.04)
    ax = fig.subplots(cluster+1, 1)
    for i in range(1, cluster+1):
        phase_counter = 0
        for tup in feature_vector[i]:
            minimum = 1000000
            index = 0
            for c_tup in centroid[i][0]:
                dist = distance.euclidean(tup, c_tup)
                if dist < minimum:
                    phase[phase_counter] = index
                    minimum = dist
                index += 1
            phase_counter += 1
        ax[i-1].step(list(phase.keys()), list(phase.values()), color='black', marker='o', markersize=2, linestyle='--', linewidth=0.01)
        ax[i-1].set_xlabel("intervals")
        ax[i-1].set_ylabel("Cluster ID")
        ax[i-1].set_yticks([j for j in range(0, i)])
        phase.clear()
    ax[cluster].plot(list(total_injection_.keys()), list(total_injection_.values()), color='black')
    ax[cluster].set_xlabel("intervals")
    ax[cluster].set_ylabel("aggregate injected bytes")
    plt.savefig(base_path + "/plots/phase_behavior.jpg")
    plt.close()
