import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def generate_traffic_trace(packet):
    traffic = {}
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "request injected":
                src = int(packet[id][j][1].split(": ")[1])
                dst = int(packet[id][j][2].split(": ")[1])
                cycle = int(packet[id][j][5].split(": ")[1])
                byte = int(packet[id][j][7].split(": ")[1])
                if cycle not in traffic.keys():
                    traffic.setdefault(cycle, {}).setdefault(src, {})[dst] = byte
                else:
                    if src not in traffic[cycle].keys():
                        traffic[cycle].setdefault(src, {})[dst] = byte
                    else:
                        if dst not in traffic[cycle][src].keys():
                            traffic[cycle][src][dst] = byte
                        else:
                            traffic[cycle][src][dst] += byte

    # generating bar plot (very time-consuming)
    """agg_traffic = []
        cycle = []
        plt.figure(figsize=(20, 7))
        for cyc in traffic.keys():
            cycle.append(cyc)
            temp = [0, 0, 0, 0]
            for src in traffic[cyc].keys():
                agg_byte = sum(list(traffic[cyc][src].values()))
                temp[src] = agg_byte
            agg_traffic.append(temp)
        agg_traffic = np.array(agg_traffic)

        bt = []
        flag = 0
        label_name = ""
        for j in range(4):
            y = []
            if j == 0:
                label_name = "chiplet 0"
            elif j == 1:
                label_name = "chiplet 1"
            elif j == 2:
                label_name = "chiplet 2"
            elif j == 3:
                label_name = "chiplet 3"
            for i in range(len(agg_traffic)):
                y.append(agg_traffic[i][j])
                if flag == 0:
                    bt.append(0)
            plt.bar(cycle, y, bottom=bt, label=label_name)
            flag = 1
            for k in range(len(y)):
                bt[k] += y[k]
        plt.legend()
        plt.show()"""
    return traffic


def burst_window_dependency(traffic):
    burst_window_dist = {}
    for cyc in traffic.keys():
        window_size = len(traffic[cyc].keys())
        burst_size = 0
        for src in traffic[cyc].keys():
            for dst, byte in traffic[cyc][src].items():
                burst_size += byte
        if burst_size not in burst_window_dist.keys():
            burst_window_dist.setdefault(burst_size, {})[window_size] = 1
        else:
            if window_size not in burst_window_dist[burst_size].keys():
                burst_window_dist[burst_size][window_size] = 1
            else:
                burst_window_dist[burst_size][window_size] += 1
    burst_window_dist = dict(sorted(burst_window_dist.items(), key=lambda x: x[0]))
    for b in burst_window_dist.keys():
        burst_window_dist[b] = dict(sorted(burst_window_dist[b].items(), key=lambda x: x[0]))
    for b in burst_window_dist.keys():
        tot = sum(list(burst_window_dist[b].values()))
        for win, freq in burst_window_dist[b].items():
            burst_window_dist[b][win] = freq / tot
    for b in burst_window_dist.keys():
        prev = 0
        for win, pdf in burst_window_dist[b].items():
            burst_window_dist[b][win] = pdf + prev
            prev += pdf
    """for b in burst_window_dist.keys():
        print("burst: " + str(b))
        for win, freq in burst_window_dist[b].items():
            print("\t" + str(win) + ": " + str(freq))"""
    return burst_window_dist


def reuse_distance(traffic):
    destination = {}
    for cyc in traffic.keys():
        for src in traffic[cyc].keys():
            if src not in destination.keys():
                destination.setdefault(src, {}).setdefault(cyc, [])
            else:
                if cyc not in destination[src].keys():
                    destination[src].setdefault(cyc, [])
            for dest, byte in traffic[cyc][src].items():
                if dest not in destination[src][cyc]:
                    destination[src][cyc].append(dest)

    reuse_distance = {}
    for src in destination.keys():
        if src not in reuse_distance.keys():
            reuse_distance.setdefault(src, {})
        stack = [destination[src][list(destination[src].keys())[0]][0]]
        for cyc, dest_list in destination[src].items():
            for dest in dest_list:
                if dest not in stack:
                    stack.append(dest)
                else:
                    counter = 0
                    temp = []
                    b = stack.pop()
                    while b != dest:
                        temp.append(b)
                        counter += 1
                        b = stack.pop()
                    temp.append(b)
                    if counter not in reuse_distance[src].keys():
                        reuse_distance[src][counter] = 1
                    else:
                        reuse_distance[src][counter] += 1
                    for b in temp:
                        stack.append(b)
        stack.clear()

    reuse_distance = dict(sorted(reuse_distance.items(), key=lambda x: x[0]))
    for s in reuse_distance.keys():
        reuse_distance[s] = dict(sorted(reuse_distance[s].items(), key=lambda x: x[0]))

    for src in reuse_distance.keys():
        total = sum(list(reuse_distance[src].values()))
        for dist, freq in reuse_distance[src].items():
            reuse_distance[src][dist] = freq / total
    for src in reuse_distance.keys():
        prev = 0
        for dist, pdf in reuse_distance[src].items():
            reuse_distance[src][dist] = pdf + prev
            prev += pdf
    """plt.bar(list(reuse_distance[2].keys()), list(reuse_distance[2].values()), width=0.5)
    plt.xticks([0, 1, 2])
    plt.xlabel("reuse distance")
    plt.ylabel("CDF")
    plt.show()"""
    return reuse_distance


if __name__ == '__main__':
    input_ = "b+tree-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
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

    traffic = generate_traffic_trace(request_packet)
    burst_window_dependency_cdf = burst_window_dependency(traffic)
    reuse_distance_cdf = reuse_distance(traffic)
