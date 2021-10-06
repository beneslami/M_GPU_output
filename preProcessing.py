import matplotlib.pyplot as plt
from hurst import compute_Hc
import seaborn as sns

chiplet = []
chiplet_0 = dict(
    SM_ID=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
           28, 29, 30, 31],
    LLC_ID=[128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143], port=192)

chiplet_1 = dict(
    SM_ID=[32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
           59, 60, 61, 62, 63],
    LLC_ID=[144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159], port=193)

chiplet_2 = dict(
    SM_ID=[64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
           91, 92, 93, 94, 95],
    LLC_ID=[160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175], port=194)

chiplet_3 = dict(
    SM_ID=[96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117,
           118, 119, 120, 121, 122, 123, 124, 125, 126, 127],
    LLC_ID=[176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191], port=195)

chiplet.append(chiplet_0)
chiplet.append(chiplet_1)
chiplet.append(chiplet_2)
chiplet.append(chiplet_3)

throughput_update = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
                  3: {0: {}, 1: {}, 2: {}}}
throughput = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
              3: {0: {}, 1: {}, 2: {}}}


def chip_select(num):
    out = -1
    for i in range(len(chiplet)):
        if num in chiplet[i]["SM_ID"]:
            out = i
            break
        if num in chiplet[i]["LLC_ID"]:
            out = i
            break
        if num == chiplet[i]["port"]:
            out = i
            break
    return out


def check_local_or_remote(x):  # 0 for local, 1 for remote
    """for i in range(len(chiplet)):
        if (int(x[1].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[1].split(": ")[1]) in chiplet[i]["LLC_ID"]):
            if (int(x[2].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[2].split(": ")[1]) in chiplet[i]["LLC_ID"]):
                return 0
        return 1"""
    if int(x[1].split(": ")[1]) >= 192 or int(x[1].split(": ")[1]) <= 195:
        if int(x[2].split(": ")[1]) >= 192 or int(x[2].split(": ")[1]) <= 195:
            return 1
    return 0


def hurst():
    out = {0: {}, 1: {}, 2: {}, 3: {}}
    for core in throughput_update.keys():
        for dest in throughput_update[core].keys():
            for cycle, byte in throughput_update[core][dest].items():
                s = sum(byte)
                if cycle not in out[core].keys():
                    out[core][cycle] = s
                else:
                    out[core][cycle] += s

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


def injection_per_core(packet):
    for i in packet.keys():
        for j in range(len(packet[i])):
            if 192 <= int(packet[i][j][1].split(": ")[1]) <= 195 and 192 <= int(
                    packet[i][j][2].split(": ")[1]) <= 195:
                if packet[i][j][0] == "injection buffer":
                    if int(packet[i][j][5].split(": ")[1]) not in \
                            throughput[chip_select(int(packet[i][j][1].split(": ")[1]))][
                                chip_select(int(packet[i][j][2].split(": ")[1]))].keys():
                        throughput[chip_select(int(packet[i][j][1].split(": ")[1]))][
                            chip_select(int(packet[i][j][2].split(": ")[1]))].setdefault(
                            int(packet[i][j][5].split(": ")[1]), []).append(int(packet[i][j][7].split(": ")[1]))
                    else:
                        throughput[chip_select(int(packet[i][j][1].split(": ")[1]))][
                            chip_select(int(packet[i][j][2].split(": ")[1]))][
                            int(packet[i][j][5].split(": ")[1])].append(int(packet[i][j][7].split(": ")[1]))

    zero = {0: 0, 1: 0, 2: 0, 3: 0}
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
                            zero[source] += 1
                            throughput_update[source][dest].setdefault(k, []).append(0)
                    throughput_update[source][dest][cyc] = throughput[source][dest][cyc]
                    prev = cyc


def injection_rate_per_core():
    off = {0: 0, 1: 0, 2: 0, 3: 0}
    total = {0: 0, 1: 0, 2: 0, 3: 0}
    injection_rate = {0: 0, 1: 0, 2: 0, 3: 0}
    for core in throughput_update.keys():
        for dest in throughput_update[core].keys():
            for cyc in throughput_update[core][dest].keys():
                if len(throughput_update[core][dest][cyc]) == 1 and throughput_update[core][dest][cyc][0] == 0:
                    print(throughput_update[core][dest][cyc])
                    off[core] += 1
                total[core] += 1
    for core in injection_rate.keys():
        injection_rate[core] = 1 - (off[core]/total[core])

    print(injection_rate)


def flit_per_cycle(cycle):
    out = {0: {}, 1: {}, 2: {}, 3: {}}
    for i in cycle.keys():
        for j in range(len(cycle[i])):
            if 192 <= int(cycle[i][j][1].split(": ")[1]) <= 195 and 192 <= int(cycle[i][j][2].split(": ")[1]) <= 195:
                if cycle[i][j][0] == "injection buffer" and (
                        int(cycle[i][j][4].split(": ")[1]) == 0 or int(cycle[i][j][4].split(": ")[1]) == 1):
                    source = chip_select(int(cycle[i][j][1].split(": ")[1]))
                    time = int(cycle[i][j][5].split(": ")[1])
                    byte = int(cycle[i][j][7].split(": ")[1])
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


def byte_per_cycle(cycle):
    out1 = {0: {}, 1: {}, 2: {}, 3: {}}
    for i in cycle.keys():
        for j in range(len(cycle[i])):
            if 192 <= int(cycle[i][j][1].split(": ")[1]) <= 195 and 192 <= int(cycle[i][j][2].split(": ")[1]) <= 195:
                if cycle[i][j][0] == "injection buffer" and (
                        int(cycle[i][j][4].split(": ")[1]) == 0 or int(cycle[i][j][4].split(": ")[1]) == 1):
                    source = chip_select(int(cycle[i][j][1].split(": ")[1]))
                    time = int(cycle[i][j][5].split(": ")[1])
                    byte = int(cycle[i][j][7].split(": ")[1])
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


def zero_state_dist():
    _time = {0: {}, 1: {}, 2: {}, 3: {}}
    for core in throughput_update.keys():
        start = end = 0
        flag = 0
        for dest in throughput_update[core].keys():
            for cyc in throughput_update[core][dest].keys():
                if len(throughput_update[core][dest][cyc]) == 1 and throughput_update[core][dest][cyc][0] == 0:
                    if flag == 0:
                        start = cyc
                        flag = 1
                    elif flag == 1:
                        continue
                else:
                    if flag == 1:
                        end = cyc
                        flag = 0
                        if (end - start) not in _time[core].keys():
                            _time[core][end - start] = 1
                        else:
                            _time[core][end - start] += 1
                        end = start = 0

    for core in _time.keys():
        print("core: " + str(core))
        for k, v in _time[core].items():
            print(str(k) + " " + str(v))
        print("\n")


def byte_per_cycle_dist(packet):
    out1 = {0: {}, 1: {}, 2: {}, 3: {}}
    dist = {0: [], 1: [], 2: [], 3: []}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if 192 <= int(packet[i][j][1].split(": ")[1]) <= 195 and 192 <= int(packet[i][j][2].split(": ")[1]) <= 195:
                if packet[i][j][0] == "injection buffer" and (
                        int(packet[i][j][4].split(": ")[1]) == 0 or int(packet[i][j][4].split(": ")[1]) == 1):
                    source = chip_select(int(packet[i][j][1].split(": ")[1]))
                    time = int(packet[i][j][5].split(": ")[1])
                    byte = int(packet[i][j][7].split(": ")[1])
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
    sns.distplot(list(dist[1]), kde=True, hist=True, ax=ax[0, 1])
    ax[0, 1].set_title("core 1")
    sns.distplot(list(dist[2]), kde=True, hist=True, ax=ax[1, 0])
    ax[1, 0].set_title("core 2")
    sns.distplot(list(dist[3]), kde=True, hist=True, ax=ax[1, 1])
    ax[1, 1].set_title("core 3")
    plt.setp(ax, yticks=[])
    plt.tight_layout()
    plt.show()


def inter_departure_dist():
    dist = {0: [], 1: [], 2: [], 3: []}
    flag = 0
    start = end = 0
    sorted_throughput_update = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
                  3: {0: {}, 1: {}, 2: {}}}
    for core in throughput_update.keys():
        for dest in throughput_update[core].keys():
            sorted_throughput_update[core][dest] = dict(sorted(throughput_update[core][dest].items(), key=lambda x:x[0]))

    for core in sorted_throughput_update.keys():
        for dest in throughput_update[core].keys():
            for cyc, byte in throughput_update[core][dest].items():
                if len(byte) == 1 and byte[0] == 0:
                    if flag == 0:
                        start = cyc
                        flag = 1
                    else:
                        continue
                else:
                    if flag == 1:
                        end = cyc
                        dist[core].append(end - start)
                        flag = 0
                    else:
                        continue
            flag = end = start = 0

    sns.set(style="dark", palette="muted", color_codes=True)
    fig, ax = plt.subplots(2, 2, figsize=(15, 15), sharex=True)
    sns.distplot(list(dist[0]), kde=True, hist=True, ax=ax[0, 0])
    ax[0, 0].set_title("core 0")
    ax[0, 0].set_xlim(-20, 300)
    sns.distplot(list(dist[1]), kde=True, hist=True, ax=ax[0, 1])
    ax[0, 1].set_title("core 1")
    ax[0, 1].set_xlim(-20, 300)
    sns.distplot(list(dist[2]), kde=True, hist=True, ax=ax[1, 0])
    ax[1, 0].set_title("core 2")
    ax[1, 0].set_xlim(-20, 300)
    sns.distplot(list(dist[3]), kde=True, hist=True, ax=ax[1, 1])
    ax[1, 1].set_title("core 3")
    ax[1, 1].set_xlim(-20, 300)
    plt.setp(ax, yticks=[])
    plt.tight_layout()
    plt.show()


def outser():
    for core in throughput.keys():
        for dest in throughput[core].keys():
            path = "out/pre_" + str(core) + "_" + str(dest) + ".txt"
            with open(path, "w") as file:
                for cycle, byte in throughput[core][dest].items():
                    temp = 0
                    for b in byte:
                        temp += b
                    file.write(str(cycle) + "\t" + str(temp) + "\n")


if __name__ == '__main__':
    file2 = open("report.txt", "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    packet = {}
    cycle = {}
    for i in range(len(lined_list)):  # packet based classification
        if lined_list[i][0] != "Instruction cache miss":
            if check_local_or_remote(lined_list[i]):
                if int(lined_list[i][3].split(": ")[1]) in packet.keys():
                    if lined_list[i] not in packet[int(lined_list[i][3].split(": ")[1])]:
                        packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
                else:
                    packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])

    for i in range(len(lined_list)):  # cycle based classification
        if lined_list[i][0] != "Instruction cache miss":
            if check_local_or_remote(lined_list[i]):
                if int(lined_list[i][5].split(": ")[1]) in cycle.keys():
                    if lined_list[i] not in cycle[int(lined_list[i][5].split(": ")[1])]:
                        cycle.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])
                else:
                    cycle.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])

    injection_per_core(cycle)
    inter_departure_dist()