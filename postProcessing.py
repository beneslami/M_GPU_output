import matplotlib.pyplot as plt
import seaborn as sns
from hurst import compute_Hc
from scipy import stats

chiplet = []
chiplet_0 = dict(
    SM_ID=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
           28, 29, 30, 31],
    LLC_ID=[128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143], port=192)

link_01 = 0
chiplet_1 = dict(
    SM_ID=[32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
           59, 60, 61, 62, 63],
    LLC_ID=[144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159], port=193)

chiplet_2 = dict(
    SM_ID=[64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
           91, 92, 93, 94, 95],
    LLC_ID=[160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175], port=194)

link_12 = 0
chiplet_2 = dict(
    SM_ID=[64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
           91, 92, 93, 94],
    LLC_ID=[160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174], port=194)
link_23 = 0

chiplet_3 = dict(
    SM_ID=[96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117,
           118, 119, 120, 121, 122, 123, 124, 125, 126, 127],
    LLC_ID=[176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191], port=195)
link_30 = 0
chiplet.append(chiplet_0)
chiplet.append(chiplet_1)
chiplet.append(chiplet_2)
chiplet.append(chiplet_3)
injection = {0: {}, 1: {}, 2: {}, 3: {}}
throughput_update = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
                  3: {0: {}, 1: {}, 2: {}}}
throughput = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
              3: {0: {}, 1: {}, 2: {}}}


def check_local_or_remote(x):  # 0 for local, 1 for remote
    for i in range(len(chiplet)):
        if (int(x[1].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[1].split(": ")[1]) in chiplet[i]["LLC_ID"]):
            if (int(x[2].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[2].split(": ")[1]) in chiplet[i]["LLC_ID"]):
                return 0
        return 1


def chip_select(x):
    if x == 192:
        return 0
    elif x == 193:
        return 1
    elif x == 194:
        return 2
    elif x == 195:
        return 3


def hurst(packet):
    out = {0: {}, 1: {}, 2: {}, 3: {}}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if len(packet[i][j]) > 7:
                continue
            else:
                if int(packet[i][j][5].split(": ")[1]) == 0 or int(packet[i][j][5].split(": ")[1]) == 2:
                    source = int(packet[i][j][0].split(": ")[1])
                    time = int(packet[i][j][6].split(": ")[1])
                    byte = int(packet[i][j][4].split(": ")[1])
                    if time not in out[source].keys():
                        out[source][time] = byte
                    else:
                        out[source][time] += byte

    H_192, c_192, data_192 = compute_Hc(list(out[0].values()))
    H_193, c_193, data_193 = compute_Hc(list(out[1].values()))
    H_194, c_194, data_194 = compute_Hc(list(out[2].values()))
    H_195, c_195, data_195 = compute_Hc(list(out[3].values()))

    f, ax = plt.subplots(2, 2, figsize=(12, 12))
    ax[0, 0].plot(data_192[0], c_192 * data_192[0] ** H_192, color="deepskyblue")
    ax[0, 0].scatter(data_192[0], data_192[1], color="purple")
    ax[0, 0].set_xscale('log')
    ax[0, 0].set_yscale('log')
    ax[0, 0].text(100, 2, "slope = " + str("{:.3f}".format(H_192)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax[0, 0].set_title("core 0")

    ax[0, 1].plot(data_193[0], c_193 * data_193[0] ** H_193, color="deepskyblue")
    ax[0, 1].scatter(data_193[0], data_193[1], color="purple")
    ax[0, 1].set_xscale('log')
    ax[0, 1].set_yscale('log')
    ax[0, 1].text(200, 2, "slope = " + str("{:.3f}".format(H_193)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax[0, 1].set_title("core 1")

    ax[1, 0].plot(data_194[0], c_194 * data_194[0] ** H_194, color="deepskyblue")
    ax[1, 0].scatter(data_194[0], data_194[1], color="purple")
    ax[1, 0].set_xscale('log')
    ax[1, 0].set_yscale('log')
    ax[1, 0].text(100, 2, "slope = " + str("{:.3f}".format(H_194)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax[1, 0].set_title("core 2")

    ax[1, 1].plot(data_195[0], c_195 * data_195[0] ** H_195, color="deepskyblue")
    ax[1, 1].scatter(data_195[0], data_195[1], color="purple")
    ax[1, 1].set_xscale('log')
    ax[1, 1].set_yscale('log')
    ax[1, 1].text(100, 2, "slope = " + str("{:.3f}".format(H_195)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax[1, 1].set_title("core 3")

    plt.show()


def flit_per_cycle(packet):
    out = {0: {}, 1: {}, 2: {}, 3: {}}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if len(packet[i][j]) > 7:
                continue
            else:
                if int(packet[i][j][5].split(": ")[1]) == 0 or int(packet[i][j][5].split(": ")[1]) == 2:
                    source = int(packet[i][j][0].split(": ")[1])
                    time = int(packet[i][j][6].split(": ")[1])
                    byte = int(packet[i][j][4].split(": ")[1])
                    flit = 0
                    if byte == 8:
                        flit = 1
                    elif byte == 136:
                        flit = 5
                    if time not in out[source].keys():
                        out[source][time] = flit
                    else:
                        out[source][time] += flit

    fig, ax = plt.subplots(4, 1, figsize=(18, 5), dpi=200)
    ax[0].bar(list(out[0].keys()), list(out[0].values()), width=3)
    ax[0].set_ylim(0, 50)
    ax[1].bar(list(out[1].keys()), list(out[1].values()), width=3)
    ax[1].set_ylim(0, 50)
    ax[2].bar(list(out[2].keys()), list(out[2].values()), width=3)
    ax[2].set_ylim(0, 50)
    ax[3].bar(list(out[3].keys()), list(out[3].values()), width=3)
    ax[3].set_ylim(0, 50)
    plt.show()


def byte_per_cycle(packet):
    out1 = {0: {}, 1: {}, 2: {}, 3: {}}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if len(packet[i][j]) > 7:
                continue
            else:
                if int(packet[i][j][5].split(": ")[1]) == 0 or int(packet[i][j][5].split(": ")[1]) == 2:
                    source = int(packet[i][j][0].split(": ")[1])
                    time = int(packet[i][j][6].split(": ")[1])
                    byte = int(packet[i][j][4].split(": ")[1])
                    if time not in out1[source].keys():
                        out1[source][time] = byte
                    else:
                        out1[source][time] += byte

    fig, ax = plt.subplots(4, 1, figsize=(18, 5), dpi=200)
    ax[0].bar(list(out1[0].keys()), list(out1[0].values()), width=3)
    ax[1].bar(list(out1[1].keys()), list(out1[1].values()), width=3)
    ax[2].bar(list(out1[2].keys()), list(out1[2].values()), width=3)
    ax[3].bar(list(out1[3].keys()), list(out1[3].values()), width=3)
    plt.show()


def byte_per_cycle_dist(packet):
    out1 = {0: {}, 1: {}, 2: {}, 3: {}}
    dist = {0: [], 1: [], 2: [], 3: []}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if len(packet[i][j]) > 7:
                continue
            else:
                if int(packet[i][j][5].split(": ")[1]) == 0 or int(packet[i][j][5].split(": ")[1]) == 2:
                    source = int(packet[i][j][0].split(": ")[1])
                    time = int(packet[i][j][6].split(": ")[1])
                    byte = int(packet[i][j][4].split(": ")[1])
                    if time not in out1[source].keys():
                        out1[source][time] = byte
                    else:
                        out1[source][time] += byte

    for core in out1.keys():
        for cycle, byte in out1[core].items():
            dist[core].append(byte)
    
    sns.set(style="dark", palette="muted", color_codes=True)
    fig, ax = plt.subplots(2, 2, figsize=(15, 15), sharex=True)
    sns.distplot(list(dist[0]), kde=True, hist=True, ax=ax[0, 0])
    ax[0, 0].set_title("core 0")
    ax[0, 0].set_xlim(-50, 1000)
    sns.distplot(list(dist[1]), kde=True, hist=True, ax=ax[0, 1])
    ax[0, 1].set_title("core 1")
    ax[0, 1].set_xlim(-50, 1000)
    sns.distplot(list(dist[2]), kde=True, hist=True, ax=ax[1, 0])
    ax[1, 0].set_title("core 2")
    ax[1, 0].set_xlim(-50, 1000)
    sns.distplot(list(dist[3]), kde=True, hist=True, ax=ax[1, 1])
    ax[1, 1].set_title("core 3")
    ax[1, 1].set_xlim(-50, 1000)
    plt.setp(ax, yticks=[])
    plt.tight_layout()
    plt.show()


def inter_departure_dist(packet):
    dist = {0: [], 1: [], 2: [], 3: []}
    flag = 0
    start = end = 0
    for i in packet.keys():
        for j in range(len(packet[i])):
            if len(packet[i][j]) > 7:
                continue
            else:
                if int(packet[i][j][5].split(": ")[1]) == 0 or int(packet[i][j][5].split(": ")[1]) == 2:
                    source = int(packet[i][j][0].split(": ")[1])
                    time = int(packet[i][j][6].split(": ")[1])
                    byte = int(packet[i][j][4].split(": ")[1])
                    if time not in injection[source].keys():
                        injection[source][time] = byte
                    else:
                        injection[source][time] += byte
    _injection = {0: {}, 1: {}, 2: {}, 3: {}}
    for core in injection.keys():
        _injection[core] = dict(sorted(injection[core].items(), key=lambda x: x[0]))

    for core in _injection.keys():
        for cyc, byte in _injection[core].items():
            if flag == 0:
                start = cyc
                flag = 1
            else:
                if cyc - start > 1:
                    if flag == 1:
                        dist[core].append(cyc - start)
                        start = cyc
                else:
                    continue
        flag = start = 0

    sns.set(style="dark", palette="muted", color_codes=True)
    fig, ax = plt.subplots(2, 2, figsize=(15, 15), sharex=True)
    sns.distplot(list(dist[0]), kde=True, hist=True, ax=ax[0, 0])
    ax[0, 0].set_title("core 0")
    #ax[0, 0].set_xlim(-20, 700)
    sns.distplot(list(dist[1]), kde=True, hist=True, ax=ax[0, 1])
    ax[0, 1].set_title("core 1")
    #ax[0, 1].set_xlim(-20, 700)
    sns.distplot(list(dist[2]), kde=True, hist=True, ax=ax[1, 0])
    ax[1, 0].set_title("core 2")
    #ax[1, 0].set_xlim(-20, 700)
    sns.distplot(list(dist[3]), kde=True, hist=True, ax=ax[1, 1])
    ax[1, 1].set_title("core 3")
    #ax[1, 1].set_xlim(-20, 700)
    plt.setp(ax, yticks=[])
    plt.tight_layout()
    plt.show()


def outser(packet):
    for i in packet.keys():
        for j in range(len(packet[i])):
            if len(packet[i][j]) > 7:
                continue
            else:
                if int(packet[i][j][5].split(": ")[1]) == 0 or int(packet[i][j][5].split(": ")[1]) == 2:
                    source = int(packet[i][j][0].split(": ")[1])
                    dest = int(packet[i][j][1].split(": ")[1])
                    time = int(packet[i][j][6].split(": ")[1])
                    byte = int(packet[i][j][4].split(": ")[1])
                    if time not in throughput[source][dest].keys():
                        throughput[source][dest].setdefault(time, []).append(byte)
                    else:
                        throughput[source][dest][time].append(byte)
    flag = prev = 0
    for source in throughput.keys():
        for dest in throughput[source].keys():
            for cyc in throughput[source][dest].keys():
                if flag == 0:
                    throughput_update[source][dest][cyc] = throughput[source][dest][cyc]
                    prev = cyc
                    flag = 1
                elif flag == 1:
                    if cyc - prev > 1:
                        for k in range(prev + 1, cyc):
                            throughput_update[source][dest].setdefault(k, []).append(0)
                    throughput_update[source][dest][cyc] = throughput[source][dest][cyc]
                    prev = cyc

    for core in throughput.keys():
        for dest in throughput[core].keys():
            path = "out/post_" + str(core) + "_" + str(dest) + ".txt"
            with open(path, "w") as file:
                for cycle, byte in throughput[core][dest].items():
                    file.write(str(cycle) + "\t" + str(byte) + "\n")


def per_core_comparison():
    real_core = synthetic_core = 0
    real_dest = synthetic_dest = 1
    real_path = "out/pre_" + str(real_core) + "_" + str(real_dest) + ".txt"
    synthetic_path = "out/post_" + str(synthetic_core) + "_" + str(synthetic_dest) + ".txt"
    real_list = {}
    syn_list = {}
    with open(real_path, "r") as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    for item in lined_list:
        if int(item[1]) != 0:
            if int(item[1]) not in real_list.keys():
                real_list[int(item[1])] = 1
            else:
                real_list[int(item[1])] += 1

    with open(synthetic_path, "r") as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    for item in lined_list:
        if int(item[1]) not in syn_list.keys():
            syn_list[int(item[1])] = 1
        else:
            syn_list[int(item[1])] += 1
    real_list = dict(sorted(real_list.items(), key=lambda x:x[0]))
    syn_list = dict(sorted(syn_list.items(), key=lambda x:x[0]))

    # Generating CDF
    _sum = 0
    for byte in real_list.keys():
        _sum += real_list[byte]
    for byte in real_list.keys():
        real_list[byte] = real_list[byte]/_sum
    real_cum = {}
    prev = 0
    for byte in real_list.keys():
        real_cum[byte] = real_list[byte] + prev
        prev = real_cum[byte]

    _sum = 0
    for byte in syn_list.keys():
        _sum += syn_list[byte]
    for byte in syn_list.keys():
        syn_list[byte] = syn_list[byte] / _sum
    syn_cum = {}
    prev = 0
    for byte in syn_list.keys():
        syn_cum[byte] = syn_list[byte] + prev
        prev = syn_cum[byte]

    print(real_cum)
    print(syn_cum)
    plt.plot(list(real_cum.keys()), list(real_cum.values()), label="Real")
    plt.plot(list(syn_cum.keys()), list(syn_cum.values()), label="Synthetic")
    plt.legend(loc="best")
    plt.title("CDF of bytes from core " + str(real_core) + " to core " + str(real_dest))
    plt.show()


if __name__ == "__main__":
    with open('out.txt', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    packet = {}
    for i in range(len(lined_list)):
        if int(lined_list[i][2].split(": ")[1]) in packet.keys():
            packet.setdefault(int(lined_list[i][2].split(": ")[1]), []).append(lined_list[i])
        else:
            packet.setdefault(int(lined_list[i][2].split(": ")[1]), []).append(lined_list[i])
    flit_per_cycle(packet)
    byte_per_cycle_dist(packet)
    inter_departure_dist(packet)
    outser(packet)
    per_core_comparison()