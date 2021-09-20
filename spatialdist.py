import csv
from _csv import writer
from statistics import mode, multimode
from scipy.stats import describe
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits import mplot3d
import pints.toy
from scipy.stats import ttest_ind
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


def chip_select(num):
    out = -1
    if num < 4:
        return num
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
    for i in range(len(chiplet)):
        if (int(x[1].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[1].split(": ")[1]) in chiplet[i]["LLC_ID"]):
            if (int(x[2].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[2].split(": ")[1]) in chiplet[i]["LLC_ID"]):
                return 0
        return 1


def find_distribution(l):
    dist = {}
    print(describe(l))
    for i in range(len(l)):
        if l[i] in dist.keys():
            dist[l[i]] += 1
        else:
            dist[l[i]] = 1
    sns.displot(l, kind="hist")
    plt.show()


def byte_injection_distribution_per_core(p):
    packet = {
        0: {
            1: {},
            2: {},
            3: {}
        },
        1: {
            0: {},
            2: {},
            3: {}
        },
        2: {
            0: {},
            1: {},
            3: {}
        },
        3: {
            0: {},
            1: {},
            2: {}
        }
    }

    for i in p.keys():
        for j in range(len(p[i])):
            if p[i][j][0] == "injection buffer":
                if check_local_or_remote(p[i][j]):
                    if chip_select(int(p[i][j][1].split(": ")[1])) != chip_select(int(p[i][j][2].split(": ")[1])):
                        if int(p[i][j][5].split(": ")[1]) in packet[chip_select(int(p[i][j][1].split(": ")[1]))][
                            chip_select(int(p[i][j][2].split(": ")[1]))].keys():
                            packet[chip_select(int(p[i][j][1].split(": ")[1]))][
                                chip_select(int(p[i][j][2].split(": ")[1]))][int(p[i][j][5].split(": ")[1])] += int(
                                p[i][j][7].split(": ")[1])
                        else:
                            packet[chip_select(int(p[i][j][1].split(": ")[1]))][
                                chip_select(int(p[i][j][2].split(": ")[1]))][int(p[i][j][5].split(": ")[1])] = int(
                                p[i][j][7].split(": ")[1])
            elif p[i][j][0] == "L2_icnt_pop":
                if check_local_or_remote(p[i][j]):
                    if chip_select(int(p[i][j][1].split(": ")[1])) != chip_select(int(p[i][j][2].split(": ")[1])):
                        if int(p[i][j][5].split(": ")[1]) in packet[chip_select(int(p[i][j][1].split(": ")[1]))][
                            chip_select(int(p[i][j][2].split(": ")[1]))].keys():
                            packet[chip_select(int(p[i][j][1].split(": ")[1]))][
                                chip_select(int(p[i][j][2].split(": ")[1]))][int(p[i][j][5].split(": ")[1])] += int(
                                p[i][j][7].split(":")[1])
                        else:
                            packet[chip_select(int(p[i][j][1].split(": ")[1]))][
                                chip_select(int(p[i][j][2].split(": ")[1]))][int(p[i][j][5].split(": ")[1])] = int(
                                p[i][j][7].split(":")[1])
    chip_0 = {1: packet[0][1], 2: packet[0][2], 3: packet[0][3]}
    chip_1 = {0: packet[0][1], 2: packet[0][2], 3: packet[0][3]}
    # table = pd.DataFrame(chip_0)
    # table.plot()

    s = sns.kdeplot(list(chip_0[1].values()), shade=True, label="to chip 1")
    s = sns.kdeplot(list(chip_0[2].values()), shade=True, label="to chip 2")
    s = sns.kdeplot(list(chip_0[3].values()), shade=True, label="to chip 3")
    plt.legend(loc="best")
    #plt.xlim(-1000, 20000)
    plt.show()


def byte_injection_ejection_per_core(p):
    packet = {0: {}, 1: {}, 2: {}, 3: {}}
    for i in p.keys():
        for j in range(len(p[i])):
            if p[i][j][0] == "injection buffer":
                if check_local_or_remote(p[i][j]):
                    if chip_select(int(p[i][j][1].split(": ")[1])) != chip_select(int(p[i][j][2].split(": ")[1])):
                        if i in packet[chip_select(int(p[i][j][1].split(": ")[1]))].keys():
                            packet[chip_select(int(p[i][j][1].split(": ")[1]))][i] += int(p[i][j][7].split(": ")[1])
                        else:
                            packet[chip_select(int(p[i][j][1].split(": ")[1]))][i] = int(p[i][j][7].split(": ")[1])
            elif p[i][j][0] == "L2_icnt_pop":
                if check_local_or_remote(p[i][j]):
                    if chip_select(int(p[i][j][1].split(": ")[1])) != chip_select(int(p[i][j][2].split(": ")[1])):
                        if i in packet[chip_select(int(p[i][j][1].split(": ")[1]))].keys():
                            packet[chip_select(int(p[i][j][1].split(": ")[1]))][i] += int(p[i][j][7].split(":")[1])
                        else:
                            packet[chip_select(int(p[i][j][1].split(": ")[1]))][i] = int(p[i][j][7].split(":")[1])
            elif p[i][j][0] == "SM boundary buffer push":
                if check_local_or_remote(p[i][j]):
                    if chip_select(int(p[i][j][1].split(": ")[1])) != chip_select(int(p[i][j][2].split(": ")[1])):
                        if i in packet[chip_select(int(p[i][j][6].split(": ")[1]))].keys():
                            packet[chip_select(int(p[i][j][6].split(": ")[1]))][i] += -int(p[i][j][7].split(": ")[1])
                        else:
                            packet[chip_select(int(p[i][j][6].split(": ")[1]))][i] = -int(p[i][j][7].split(": ")[1])
            elif p[i][j][0] == "inter_icnt_pop_llc_push":
                if check_local_or_remote(p[i][j]):
                    if chip_select(int(p[i][j][1].split(": ")[1])) != chip_select(int(p[i][j][2].split(": ")[1])):
                        if i in packet[chip_select(int(p[i][j][2].split(": ")[1]))].keys():
                            packet[chip_select(int(p[i][j][6].split(": ")[1]))][i] += -int(p[i][j][7].split(": ")[1])
                        else:
                            packet[chip_select(int(p[i][j][6].split(": ")[1]))][i] = -int(p[i][j][7].split(": ")[1])

    fix, ax = plt.subplots(1, 1, figsize=(18, 4))
    with open("syrk_chip_0.txt", "w") as file:
        for i in packet[0].keys():
            string = str(i) + "," + str(packet[0][i])
            file.write(string + "\n")
    ax.plot(list(packet[0].keys()), list(packet[0].values()))
    plt.show()
    find_distribution(list(packet[0].values()))
    return packet[0]


def byte_injection_ejection_NoC(p):
    packet = {}
    for i in p.keys():
        for j in range(len(p[i])):
            if p[i][j][0] == "injection buffer":
                if check_local_or_remote(p[i][j]):
                    if chip_select(int(p[i][j][1].split(": ")[1])) != chip_select(int(p[i][j][2].split(": ")[1])):
                        if int(p[i][j][5].split(": ")[1]) in packet.keys():
                            packet[int(p[i][j][5].split(": ")[1])] += int(p[i][j][7].split(": ")[1])
                        else:
                            packet[int(p[i][j][5].split(": ")[1])] = int(p[i][j][7].split(": ")[1])
            elif p[i][j][0] == "L2_icnt_pop":
                if check_local_or_remote(p[i][j]):
                    if chip_select(int(p[i][j][1].split(": ")[1])) != chip_select(int(p[i][j][2].split(": ")[1])):
                        if int(p[i][j][5].split(": ")[1]) in packet.keys():
                            packet[int(p[i][j][5].split(": ")[1])] += int(p[i][j][7].split(":")[1])
                        else:
                            packet[int(p[i][j][5].split(": ")[1])] = int(p[i][j][7].split(":")[1])
            elif p[i][j][0] == "SM boundary buffer push":
                if check_local_or_remote(p[i][j]):
                    if chip_select(int(p[i][j][1].split(": ")[1])) != chip_select(int(p[i][j][2].split(": ")[1])):
                        if int(p[i][j][5].split(": ")[1]) in packet.keys():
                            packet[int(p[i][j][5].split(": ")[1])] += -int(p[i][j][7].split(": ")[1])
                        else:
                            packet[int(p[i][j][5].split(": ")[1])] = -int(p[i][j][7].split(": ")[1])
            elif p[i][j][0] == "inter_icnt_pop_llc_push":
                if check_local_or_remote(p[i][j]):
                    if chip_select(int(p[i][j][1].split(": ")[1])) != chip_select(int(p[i][j][2].split(": ")[1])):
                        if int(p[i][j][5].split(": ")[1]) in packet.keys():
                            packet[int(p[i][j][5].split(": ")[1])] += -int(p[i][j][7].split(": ")[1])
                        else:
                            packet[int(p[i][j][5].split(": ")[1])] = -int(p[i][j][7].split(": ")[1])
    for i in packet.keys():
        packet[i] = packet[i]/4
    fig, ax = plt.subplots(1, 1, figsize=(18, 4))
    ax.plot(list(packet.keys()), list(packet.values()))
    plt.show()
    return packet


def injection_flow(packet):
    arr = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]  # for heatmap plot
    arr2 = [["", 0, 0, 0, 0], ["", 0, 0, 0, 0], ["", 0, 0, 0, 0], ["", 0, 0, 0, 0]]  # for stacked plot
    arr3 = {0: {1: {0: [], 1: [], 2: [], 3: []},
                2: {0: [], 1: [], 2: [], 3: []},
                3: {0: [], 1: [], 2: [], 3: []}
                },
            1: {0: {0: [], 1: [], 2: [], 3: []},
                2: {0: [], 1: [], 2: [], 3: []},
                3: {0: [], 1: [], 2: [], 3: []}
                },
            2: {0: {0: [], 1: [], 2: [], 3: []},
                1: {0: [], 1: [], 2: [], 3: []},
                3: {0: [], 1: [], 2: [], 3: []}
                },
            3: {0: {0: [], 1: [], 2: [], 3: []},
                1: {0: [], 1: [], 2: [], 3: []},
                2: {0: [], 1: [], 2: [], 3: []}
                }
    } # message type distribution
    for i in packet.keys():
        for j in range(len(packet[i])):
            if check_local_or_remote(p[i][j]):
                if chip_select(int(p[i][j][1].split(": ")[1])) != chip_select(int(p[i][j][2].split(": ")[1])):
                    if packet[i][j][0] == "injection buffer":
                        src = chip_select(int(packet[i][j][1].split(": ")[1]))
                        dst = chip_select(int(packet[i][j][2].split(": ")[1]))
                        #arr[3 - src][dst] += 1
                        #arr2[src][dst+1] += 1
                        arr3[src][dst][int(packet[i][j][4].split(": ")[1])].append(int(packet[i][j][7].split(": ")[1]))
                        continue
                    elif packet[i][j][0] == "L2_icnt_pop":
                        src = chip_select(int(packet[i][j][1].split(": ")[1]))
                        dst = chip_select(int(packet[i][j][2].split(": ")[1]))
                        #arr[3 - src][dst] += 1
                        #arr2[src][dst+1] += 1
                        arr3[src][dst][int(packet[i][j][4].split(": ")[1])].append(int(packet[i][j][7].split(":")[1]))
                        break

    """Index = [0, 1, 2, 3]  # heatmap begin
    Cols = [3, 2, 1, 0]
    plt.xticks(ticks=np.arange(len(Index)), labels=Index)
    plt.yticks(ticks=np.arange(len(Cols)), labels=Cols)
    hm = plt.imshow(arr, cmap='gray_r', interpolation="nearest")
    plt.colorbar(hm)
    plt.xlabel("Source")
    plt.ylabel("Destination")
    plt.title("spatial Distribution of Injection Flows")
    plt.show()   # heatmap end"""

    """df = pd.DataFrame(arr2, columns=["chip", "0", "1", "2", "3"])  # stacked bar chart
    print(df)
    df.plot(x="chip", kind="bar", stacked=True)
    plt.xticks([0, 1, 2, 3], [0, 1, 2, 3])
    plt.show()"""

    chips_mean = {
                0: {1: {0: np.mean(arr3[0][1][0]), 1: np.mean(arr3[0][1][1]), 2: np.mean(arr3[0][1][2]), 3: np.mean(arr3[0][1][3])},
                    2: {0: np.mean(arr3[0][2][0]), 1: np.mean(arr3[0][2][1]), 2: np.mean(arr3[0][2][2]), 3: np.mean(arr3[0][2][3])},
                    3: {0: np.mean(arr3[0][3][0]), 1: np.mean(arr3[0][3][1]), 2: np.mean(arr3[0][3][2]), 3: np.mean(arr3[0][3][3])}
                    }
                }
    chips_variance = {
        0: {1: {0: np.var(arr3[0][1][0]), 1: np.var(arr3[0][1][1]), 2: np.var(arr3[0][1][2]),
                3: np.var(arr3[0][1][3])},
            2: {0: np.var(arr3[0][2][0]), 1: np.var(arr3[0][2][1]), 2: np.var(arr3[0][2][2]),
                3: np.var(arr3[0][2][3])},
            3: {0: np.var(arr3[0][3][0]), 1: np.var(arr3[0][3][1]), 2: np.var(arr3[0][3][2]),
                3: np.var(arr3[0][3][3])}
            }
    }

    df = {"Read Req": arr3[0][1][0], "Write Req": arr3[0][1][1], "Read Rep": arr3[0][1][2], "Write Rep": arr3[0][1][3]}
    sns.displot(df)
    plt.savefig("/Users/Ben/Desktop/0_1_random.png")

    df = {"Read Req": arr3[1][2][0], "Write Req": arr3[1][2][1], "Read Rep": arr3[1][2][2], "Write Rep": arr3[1][2][3]}
    sns.displot(df)
    plt.savefig("/Users/Ben/Desktop/1_2_random.png")

    df = {"Read Req": arr3[3][0][0], "Write Req": arr3[3][0][1], "Read Rep": arr3[3][0][2], "Write Rep": arr3[3][0][3]}
    sns.displot(df)
    plt.savefig("/Users/Ben/Desktop/3_0_random.png")

    df = {"Read Req": arr3[2][3][0], "Write Req": arr3[2][3][1], "Read Rep": arr3[2][3][2], "Write Rep": arr3[2][3][3]}
    sns.displot(df)
    plt.savefig("/Users/Ben/Desktop/2_3_random.png")
    plt.show()


def traffic_share(packet):
    chips = {0: 0, 1: 0, 2: 0, 3: 0}
    cycle = {}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if check_local_or_remote(packet[i][j]):
                if chip_select(int(packet[i][j][1].split(": ")[1])) != chip_select(int(packet[i][j][2].split(": ")[1])):
                    if packet[i][j][0] == "injection buffer" or packet[i][j][0] == "L2_icnt_pop":
                        if 1300 <= int(packet[i][j][5].split(": ")[1]) <= 1400:
                            if check_local_or_remote(packet[i][j]):
                                if chip_select(int(packet[i][j][1].split(": ")[1])) != chip_select(int(packet[i][j][2].split(": ")[1])):
                                    if int(packet[i][j][5].split(": ")[1]) in cycle.keys():
                                        if packet[i][j][0] == "injection buffer":
                                            cycle[int(packet[i][j][5].split(": ")[1])][chip_select(int(packet[i][j][1].split(": ")[1]))] += int(packet[i][j][7].split(": ")[1])
                                        else:
                                            cycle[int(packet[i][j][5].split(": ")[1])][
                                                chip_select(int(packet[i][j][1].split(": ")[1]))] += int(
                                                packet[i][j][7].split(":")[1])
                                    else:
                                        chips = {0: 0, 1: 0, 2: 0, 3: 0}
                                        if packet[i][j][0] == "injection buffer":
                                            chips[chip_select(int(packet[i][j][1].split(": ")[1]))] += int(
                                                packet[i][j][7].split(": ")[1])
                                        else:
                                            chips[chip_select(int(packet[i][j][1].split(": ")[1]))] += int(packet[i][j][7].split(":")[1])
                                        cycle[int(packet[i][j][5].split(": ")[1])] = chips
                    elif packet[i][j][0] == "SM boundary buffer push" or packet[i][j][0] == "inter_icnt_pop_llc_push":
                        if 1300 <= int(packet[i][j][5].split(": ")[1]) <= 1400:
                            if check_local_or_remote(packet[i][j]):
                                if chip_select(int(packet[i][j][1].split(": ")[1])) != chip_select(int(packet[i][j][2].split(": ")[1])):
                                    if int(packet[i][j][5].split(": ")[1]) in cycle.keys():
                                        cycle[int(packet[i][j][5].split(": ")[1])][chip_select(int(packet[i][j][1].split(": ")[1]))] += -(int(packet[i][j][7].split(": ")[1]))
                                    else:
                                        chips = {0: 0, 1: 0, 2: 0, 3: 0}
                                        chips[chip_select(int(packet[i][j][1].split(": ")[1]))] += -(int(packet[i][j][7].split(": ")[1]))
                                        cycle[int(packet[i][j][5].split(": ")[1])] = chips
    zero = {}
    one = {}
    two = {}
    three = {}
    for i in cycle.keys():
        zero[i] = cycle[i][0]
        one[i] = cycle[i][1]
        two[i] = cycle[i][2]
        three[i] = cycle[i][3]

    plt.bar(list(cycle.keys()), list(zero.values()), label="chip_0")
    plt.bar(list(cycle.keys()), list(one.values()), bottom=list(zero.values()), label="chip_1")
    plt.bar(list(cycle.keys()), list(two.values()), bottom=list(one.values()), label="chip_2")
    plt.bar(list(cycle.keys()), list(three.values()), bottom=list(two.values()), label="chip_3")
    plt.legend(loc="best")
    plt.show()


def byte_distribution(packet):
    index = 5
    temp = {0: [], 1: [], 2: [], 3: []}
    chips_mean = {0: {}, 1: {}, 2: {}, 3: {}}
    chips_std = {0: {}, 1: {}, 2: {}, 3: {}}
    remainder = {0: 0, 1: 0, 2: 0, 3: 0}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "injection buffer":
                temp[chip_select(int(packet[i][j][1].split(": ")[1]))].append(int(packet[i][j][7].split(": ")[1]))
                remainder.pop(chip_select(int(packet[i][j][1].split(": ")[1])))
                for i in remainder.keys():
                    temp[i].append(0)
            elif packet[i][j][0] == "L2_icnt_pop":
                temp[chip_select(int(packet[i][j][1].split(": ")[1]))].append(int(packet[i][j][7].split(":")[1]))
                remainder.pop(chip_select(int(packet[i][j][1].split(": ")[1])))
                for i in remainder.keys():
                    temp[i].append(0)
            elif packet[i][j][0] == "SM boundary buffer push":
                temp[chip_select(int(packet[i][j][1].split(": ")[1]))].append(-int(packet[i][j][7].split(": ")[1]))
                remainder.pop(chip_select(int(packet[i][j][1].split(": ")[1])))
                for i in remainder.keys():
                    temp[i].append(0)
            elif packet[i][j][0] == "inter_icnt_pop_llc_push":
                temp[chip_select(int(packet[i][j][1].split(": ")[1]))].append(-int(packet[i][j][7].split(": ")[1]))
                remainder.pop(chip_select(int(packet[i][j][1].split(": ")[1])))
                for i in remainder.keys():
                    temp[i].append(0)
            remainder = {0: 0, 1: 0, 2: 0, 3: 0}

    for i in temp.keys():
        tmp = []
        for j in range(len(temp[i])):
            if j + index <= len(temp[i]):
                for k in range(index):
                    tmp.append(temp[i][j+k])
                if np.mean(tmp) != 0:
                    chips_mean[i][j] = np.mean(tmp)
                    chips_std[i][j] = np.sqrt(np.var(tmp))
                else:
                    chips_mean[i][j] = 0
                    chips_std[i][j] = 0
                j += index
                tmp.clear()
            else:
                for k in range(len(temp[i]) - j):
                    tmp.append(temp[i][j+k])
                chips_mean[i][j] = np.mean(tmp)
                chips_std[i][j] = np.sqrt(np.var(tmp))
    mean_dist = {0: {}, 1: {}, 2: {}, 3: {}}
    for i in chips_mean.keys():
        for j in chips_mean[i].keys():
            if chips_mean[i][j] in mean_dist[i].keys():
                mean_dist[i][chips_mean[i][j]] += 1
            else:
                mean_dist[i][chips_mean[i][j]] = 1
    print(mean_dist[0].keys())
    print(mean_dist[0].values())
    plt.bar(list(mean_dist[0].keys()), list(mean_dist[0].values()))
    plt.show()
    #sns.displot(data=list(chips_mean[2].values()), kind="kde", fill=True)
    #sns.distplot(list(chips_mean[0].values()))
    #plt.show()


def injection_rate(packet):
    arr = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    dst = -1
    src = -1
    for i in packet.keys():
        if chip_select(int(packet[i][0][1].split(": ")[1])) != chip_select(int(packet[i][0][2].split(": ")[1])):
            for j in range(len(packet[i])):
                if packet[i][j][0] == "injection buffer" and int(packet[i][j][4].split(": ")[1]) == 0:
                    src = chip_select(int(packet[i][j][1].split(": ")[1]))
                    for k in range(j, len(packet[i])):
                        if packet[i][k][0] == "inter_icnt_pop_llc_push" and int(packet[i][k][4].split(": ")[1]) == 0:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            arr[3 - src][dst] += 1
                            break
                        elif packet[i][k][0] == "forward_waiting_push" and int(packet[i][k][4].split(": ")[1]) == 0:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            arr[3 - src][dst] += 1
                            break

                if packet[i][j][0] == "forward_waiting_push" and int(packet[i][j][4].split(": ")[1]) == 0:
                    src = chip_select(int(packet[i][j][6].split(": ")[1]))
                    for k in range(j, len(packet[i])):
                        if packet[i][k][0] == "inter_icnt_pop_llc_push" and int(packet[i][k][4].split(": ")[1]) == 0:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            arr[3 - src][dst] += 1
                            break

                if packet[i][j][0] == "L2_icnt_pop" and int(packet[i][j][4].split(": ")[1]) == 2:
                    src = chip_select(int(packet[i][j][1].split(": ")[1]))
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "forward_waiting_push" and int(packet[i][k][4].split(": ")[1]) == 2:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            arr[3 - src][dst] += 1
                            break
                        elif packet[i][k][0] == "SM boundary buffer push" and int(packet[i][k][4].split(": ")[1]) == 2:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            arr[3 - src][dst] += 1
                            break

                if packet[i][j][0] == "forward_waiting_push" and int(packet[i][j][4].split(": ")[1]) == 2:
                    src = chip_select(int(packet[i][j][6].split(": ")[1]))
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "SM boundary buffer push" and int(packet[i][k][4].split(": ")[1]) == 2:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            arr[3 - src][dst] += 1
                            break
    print(arr)
    # {6: 56226, 8: 31585, 7: 72748, 4: 49984, 9: 38302, 5: 8, 3: 36, 2: 18}
    Index = [0, 1, 2, 3]
    Cols = [3, 2, 1, 0]
    plt.xticks(ticks=np.arange(len(Index)), labels=Index)
    plt.yticks(ticks=np.arange(len(Cols)), labels=Cols)
    hm = plt.imshow(arr, cmap='gray_r', interpolation="nearest")
    plt.colorbar(hm)
    plt.xlabel("Source")
    plt.ylabel("Destination")
    plt.title("spatial Distribution of traffics among links")
    plt.show()


def hop_fraction(packet):
    one_hop = 0
    two_hop = 0
    sum = 0
    for i in packet.keys():
        if chip_select(int(packet[i][0][1].split(": ")[1])) != chip_select(int(packet[i][0][2].split(": ")[1])):
            if abs(int(packet[i][0][1].split(": ")[1]) - int(packet[i][0][2].split(": ")[1])) == 1 or abs(
                    int(packet[i][0][1].split(": ")[1]) - int(packet[i][0][2].split(": ")[1])) == len(chiplet) - 1:
                one_hop += 1
            else:
                two_hop += 1
            sum += 1
    print("one hop: " + str(one_hop / sum))
    print("two hop: " + str(two_hop / sum))


def byte_flow(packet):
    read_req_chip_flow = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]
    read_rep_chip_flow = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]
    write_req_chip_flow = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]
    write_rep_chip_flow = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]
    arr = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]
    modules = {
        0: {

        },
        1: {

        },
        2: {

        },
        3: {

        }
    }
    dst = -1
    src = -1
    for i in packet.keys():
        if chip_select(int(packet[i][0][1].split(": ")[1])) != chip_select(int(packet[i][0][2].split(": ")[1])):
            for j in range(len(packet[i])):
                if packet[i][j][0] == "injection buffer":
                    src = chip_select(int(packet[i][j][1].split(": ")[1]))
                    dst = chip_select(int(packet[i][j][2].split(": ")[1]))
                    arr[3 - src][dst].append(int(packet[i][j][7].split(": ")[1]))

                    if int(packet[i][j][4].split(": ")[1]) == 0:
                        read_req_chip_flow[3 - src][dst].append(int(packet[i][j][7].split(": ")[1]))
                        if int(packet[i][j][7].split(": ")[1]) in modules[src]:
                            modules[src][int(packet[i][j][7].split(": ")[1])] += 1
                        else:
                            modules[src][int(packet[i][j][7].split(": ")[1])] = 1

                    elif int(packet[i][j][4].split(": ")[1]) == 1:
                        write_req_chip_flow[3 - src][dst].append(int(packet[i][j][7].split(": ")[1]))

                        if int(packet[i][j][7].split(": ")[1]) in modules[src]:
                            modules[src][int(packet[i][j][7].split(": ")[1])] += 1
                        else:
                            modules[src][int(packet[i][j][7].split(": ")[1])] = 1

                    elif int(packet[i][j][4].split(": ")[1]) == 2:
                        read_rep_chip_flow[3 - src][dst].append(int(packet[i][j][7].split(": ")[1]))

                        if int(packet[i][j][7].split(": ")[1]) in modules[src]:
                            modules[src][int(packet[i][j][7].split(": ")[1])] += 1
                        else:
                            modules[src][int(packet[i][j][7].split(": ")[1])] = 1

                    elif int(packet[i][j][4].split(": ")[1]) == 3:
                        write_rep_chip_flow[3 - src][dst].append(int(packet[i][j][7].split(": ")[1]))

                        if int(packet[i][j][7].split(": ")[1]) in modules[src]:
                            modules[src][int(packet[i][j][7].split(": ")[1])] += 1
                        else:
                            modules[src][int(packet[i][j][7].split(": ")[1])] = 1
                    continue

                elif packet[i][j][0] == "L2_icnt_pop":
                    src = chip_select(int(packet[i][j][1].split(": ")[1]))
                    dst = chip_select(int(packet[i][j][2].split(": ")[1]))
                    arr[3 - src][dst].append(int(packet[i][j][7].split(":")[1]))
                    if int(packet[i][j][4].split(": ")[1]) == 0:
                        read_req_chip_flow[3 - src][dst].append(int(packet[i][j][7].split(":")[1]))
                        if int(packet[i][j][7].split(":")[1]) in modules[src]:
                            modules[src][int(packet[i][j][7].split(":")[1])] += 1
                        else:
                            modules[src][int(packet[i][j][7].split(":")[1])] = 1
                    elif int(packet[i][j][4].split(": ")[1]) == 1:
                        write_req_chip_flow[3 - src][dst].append(int(packet[i][j][7].split(":")[1]))
                        if int(packet[i][j][7].split(":")[1]) in modules[src]:
                            modules[src][int(packet[i][j][7].split(":")[1])] += 1
                        else:
                            modules[src][int(packet[i][j][7].split(":")[1])] = 1
                    elif int(packet[i][j][4].split(":")[1]) == 2:
                        read_rep_chip_flow[3 - src][dst].append(int(packet[i][j][7].split(":")[1]))
                        if int(packet[i][j][7].split(":")[1]) in modules[src]:
                            modules[src][int(packet[i][j][7].split(":")[1])] += 1
                        else:
                            modules[src][int(packet[i][j][7].split(":")[1])] = 1
                    elif int(packet[i][j][4].split(":")[1]) == 3:
                        write_rep_chip_flow[3 - src][dst].append(int(packet[i][j][7].split(":")[1]))
                        if int(packet[i][j][7].split(":")[1]) in modules[src]:
                            modules[src][int(packet[i][j][7].split(":")[1])] += 1
                        else:
                            modules[src][int(packet[i][j][7].split(":")[1])] = 1
                    continue

    """#3D distribution
    data = {}
    for i in modules.keys():
        for j in sorted(modules[i].keys()):
                data.setdefault(j, []).append(modules[i][j])
    df = pd.DataFrame(data, index=["chip0", "chip1", "chip2", "chip3"])
    ax = df.plot.bar()"""

    # 3D
    D_arr = [[], [], [], []]
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if len(arr[i][j]) != 0:
                D_arr[i].append(np.mean(arr[i][j]))
            else:
                D_arr[i].append(0)
    ax = plt.axes(projection='3d')
    data_array = np.array(D_arr)
    x_data, y_data = np.meshgrid(np.arange(data_array.shape[1]), np.arange(data_array.shape[0]))
    for i in range(len(x_data)):
        x_data[i] = x_data[i][::-1]
    x_data = x_data.flatten()
    y_data = y_data.flatten()
    z_data = data_array.flatten()
    ax.bar3d(x_data, y_data, np.zeros(len(z_data)), 0.7, 0.7, z_data, alpha=0.9)
    ax.set_xlabel('Source')
    ax.set_ylabel('Destination')
    ax.set_zlabel('Mean Injection Flow')

    plt.show()


def link_rate(packet):
    arr = [
        [0, {}, {}, {}],
        [{}, 0, {}, {}],
        [{}, {}, 0, {}],
        [{}, {}, {}, 0]
    ]
    dst = -1
    src = -1
    temp = {}
    for i in packet.keys():
        if chip_select(int(packet[i][0][1].split(": ")[1])) != chip_select(int(packet[i][0][2].split(": ")[1])):
            for j in range(len(packet[i])):
                if packet[i][j][0] == "injection buffer" and int(packet[i][j][4].split(": ")[1]) == 0:
                    src = chip_select(int(packet[i][j][1].split(": ")[1]))
                    for k in range(j, len(packet[i])):
                        if packet[i][k][0] == "inter_icnt_pop_llc_push" and int(packet[i][k][4].split(": ")[1]) == 0:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            temp = arr[src][dst]
                            if type(temp) is dict:
                                if int(packet[i][j][7].split(": ")[1]) in temp.keys():
                                    temp[int(packet[i][j][7].split(": ")[1])] += 1
                                else:
                                    temp[int(packet[i][j][7].split(": ")[1])] = 1
                            arr[src][dst] = temp
                            break
                        elif packet[i][k][0] == "forward_waiting_push" and int(packet[i][k][4].split(": ")[1]) == 0:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            temp = arr[src][dst]
                            if type(temp) is dict:
                                if int(packet[i][j][7].split(": ")[1]) in temp.keys():
                                    temp[int(packet[i][j][7].split(": ")[1])] += 1
                                else:
                                    temp[int(packet[i][j][7].split(": ")[1])] = 1
                            arr[src][dst] = temp
                            break

                if packet[i][j][0] == "injection buffer" and int(packet[i][j][4].split(": ")[1]) == 1:
                    src = chip_select(int(packet[i][j][1].split(": ")[1]))
                    for k in range(j, len(packet[i])):
                        if packet[i][k][0] == "inter_icnt_pop_llc_push" and int(packet[i][k][4].split(": ")[1]) == 1:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            temp = arr[src][dst]
                            if type(temp) is dict:
                                if int(packet[i][j][7].split(": ")[1]) in temp.keys():
                                    temp[int(packet[i][j][7].split(":")[1])] += 1
                                else:
                                    temp[int(packet[i][j][7].split(":")[1])] = 1
                            arr[src][dst] = temp
                            break
                        elif packet[i][k][0] == "forward_waiting_push" and int(packet[i][k][4].split(": ")[1]) == 1:
                            dst = chip_select(int(packet[i][j][6].split(": ")[1]))
                            temp = arr[src][dst]
                            if type(temp) is dict:
                                if int(packet[i][k][7].split(": ")[1]) in temp.keys():
                                    temp[int(packet[i][j][7].split(": ")[1])] += 1
                                else:
                                    temp[int(packet[i][j][7].split(": ")[1])] = 1
                            arr[src][dst] = temp
                            break

                if packet[i][j][0] == "forward_waiting_push" and int(packet[i][j][4].split(": ")[1]) == 0:
                    src = chip_select(int(packet[i][j][6].split(": ")[1]))
                    for k in range(j, len(packet[i])):
                        if packet[i][k][0] == "inter_icnt_pop_llc_push" and int(packet[i][k][4].split(": ")[1]) == 0:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            temp = arr[src][dst]
                            if type(temp) is dict:
                                if 8 in temp.keys():
                                    temp[8] += 1
                                else:
                                    temp[8] = 1
                            arr[src][dst] = temp
                            break

                if packet[i][j][0] == "forward_waiting_push" and int(packet[i][j][4].split(": ")[1]) == 1:
                    src = chip_select(int(packet[i][j][6].split(": ")[1]))
                    for k in range(j, len(packet[i])):
                        if packet[i][k][0] == "inter_icnt_pop_llc_push" and int(packet[i][k][4].split(": ")[1]) == 1:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            temp = arr[src][dst]
                            if type(temp) is dict:
                                if 136 in temp.keys():
                                    temp[136] += 1
                                else:
                                    temp[136] = 1
                            arr[src][dst] = temp
                            break

                if packet[i][j][0] == "L2_icnt_pop" and int(packet[i][j][4].split(": ")[1]) == 2:
                    src = chip_select(int(packet[i][j][1].split(": ")[1]))
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "forward_waiting_push" and int(packet[i][k][4].split(": ")[1]) == 2:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            temp = arr[src][dst]
                            if type(temp) is dict:
                                if int(packet[i][j][7].split(":")[1]) in temp.keys():
                                    temp[int(packet[i][j][7].split(":")[1])] += 1
                                else:
                                    temp[int(packet[i][j][7].split(":")[1])] = 1
                            arr[src][dst] = temp
                            break
                        elif packet[i][k][0] == "SM boundary buffer push" and int(packet[i][k][4].split(": ")[1]) == 2:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            temp = arr[src][dst]
                            if type(temp) is dict:
                                if int(packet[i][k][7].split(": ")[1]) in temp.keys():
                                    temp[int(packet[i][k][7].split(": ")[1])] += 1
                                else:
                                    temp[int(packet[i][k][7].split(": ")[1])] = 1
                            arr[src][dst] = temp
                            break

                if packet[i][j][0] == "L2_icnt_pop" and int(packet[i][j][4].split(": ")[1]) == 3:
                    src = chip_select(int(packet[i][j][1].split(": ")[1]))
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "forward_waiting_push" and int(packet[i][k][4].split(": ")[1]) == 3:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            temp = arr[src][dst]
                            if type(temp) is dict:
                                if int(packet[i][j][7].split(":")[1]) in temp.keys():
                                    temp[int(packet[i][j][7].split(":")[1])] += 1
                                else:
                                    temp[int(packet[i][j][7].split(":")[1])] = 1
                            arr[src][dst] = temp
                            break
                        elif packet[i][k][0] == "SM boundary buffer push" and int(packet[i][k][4].split(": ")[1]) == 3:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            temp = arr[src][dst]
                            if type(temp) is dict:
                                if int(packet[i][k][7].split(": ")[1]) in temp.keys():
                                    temp[int(packet[i][k][7].split(": ")[1])] += 1
                                else:
                                    temp[int(packet[i][k][7].split(": ")[1])] = 1
                            arr[src][dst] = temp
                            break

                if packet[i][j][0] == "forward_waiting_push" and int(packet[i][j][4].split(": ")[1]) == 2:
                    src = chip_select(int(packet[i][j][6].split(": ")[1]))
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "SM boundary buffer push" and int(packet[i][k][4].split(": ")[1]) == 2:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            temp = arr[src][dst]
                            if type(temp) is dict:
                                if int(packet[i][k][7].split(": ")[1]) in temp.keys():
                                    temp[int(packet[i][k][7].split(": ")[1])] += 1
                                else:
                                    temp[int(packet[i][k][7].split(": ")[1])] = 1
                            arr[src][dst] = temp
                            break

                if packet[i][j][0] == "forward_waiting_push" and int(packet[i][j][4].split(": ")[1]) == 3:
                    src = chip_select(int(packet[i][j][6].split(": ")[1]))
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "SM boundary buffer push" and int(packet[i][k][4].split(": ")[1]) == 3:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            temp = arr[src][dst]
                            if type(temp) is dict:
                                if int(packet[i][k][7].split(": ")[1]) in temp.keys():
                                    temp[int(packet[i][k][7].split(": ")[1])] += 1
                                else:
                                    temp[int(packet[i][k][7].split(": ")[1])] = 1
                            arr[src][dst] = temp
                            break

    for i in range(len(arr)):
        print(i)
        for j in range(len(arr[i])):
            print(arr[i][j])


def find_message_type_distribution(packet):
    message = {
        0: {},
        1: {},
        2: {},
        3: {}
    }
    for i in packet.keys():
        if chip_select(int(packet[i][0][1].split(": ")[1])) != chip_select(int(packet[i][0][2].split(": ")[1])):
            for j in range(len(packet[i])):
                if "injection buffer" == packet[i][j][0]:
                    if chip_select(int(packet[i][j][1].split(": ")[1])) in message.keys():
                        if int(packet[i][j][4].split(": ")[1]) in message[
                            chip_select(int(packet[i][j][1].split(": ")[1]))].keys():
                            message[chip_select(int(packet[i][j][1].split(": ")[1]))][
                                int(packet[i][j][4].split(": ")[1])] += 1
                        else:
                            message[chip_select(int(packet[i][j][1].split(": ")[1]))][
                                int(packet[i][j][4].split(": ")[1])] = 1

                elif "L2_icnt_pop" == packet[i][j][0]:
                    if int(packet[i][j][4].split(": ")[1]) in message[
                        chip_select(int(packet[i][j][1].split(": ")[1]))].keys():
                        message[chip_select(int(packet[i][j][1].split(": ")[1]))][
                            int(packet[i][j][4].split(": ")[1])] += 1
                    else:
                        message[chip_select(int(packet[i][j][1].split(": ")[1]))][
                            int(packet[i][j][4].split(": ")[1])] = 1

    mylabels = ["Read Request", "Write Request", "Read Reply", "Write Reply"]
    data = {}
    for i in message.keys():
        for j in sorted(message[i].keys()):
            data.setdefault(j, []).append(message[i][j])
    df = pd.DataFrame(data, index=["chip0", "chip1", "chip2", "chip3"])
    ax = df.plot.bar()
    ax.legend(labels=mylabels)
    plt.show()


def find_destination_node_distribution(packet):
    arr = {}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if chip_select(int(packet[i][j][1].split(": ")[1])) != chip_select(int(packet[i][j][2].split(": ")[1])):
                if packet[i][j][0] == "injection buffer":
                    if chip_select(int(packet[i][j][2].split(": ")[1])) in arr.keys():
                        arr[chip_select(int(packet[i][j][2].split(": ")[1]))] += 1
                    else:
                        arr[chip_select(int(packet[i][j][2].split(": ")[1]))] = 1

    plt.bar(list(arr.keys()), list(arr.values()))
    plt.xticks([0, 1, 2, 3], [0, 1, 2, 3])
    plt.xlabel("destination node")
    plt.ylabel("Frequency of generating request")
    plt.show()


if __name__ == "__main__":
    file = open("report_syrk.txt", "r")
    raw_content = ""
    if file.mode == "r":
        raw_content = file.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    p = {}
    zer = {}
    """for i in range(len(lined_list)):  # packet based classification
        if check_local_or_remote(lined_list[i]):
            if int(lined_list[i][3].split(": ")[1]) in p.keys():
                p.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
            else:
                p.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])"""

    for i in range(len(lined_list)):  # cycle based classification
        if lined_list[i][0] != "Instruction cache miss":
            if chip_select(int(lined_list[i][1].split(": ")[1])) != chip_select(int(lined_list[i][2].split(": ")[1])):
                if int(lined_list[i][5].split(": ")[1]) in p.keys():
                    if lined_list[i] not in p[int(lined_list[i][5].split(": ")[1])]:
                        p.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])
                else:
                    p.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])
    win = 0
    zer = {}
    counter = 1
    temp_overall = {}
    overall = {}
    zero = {}
    temp_zero = {}
    one = {}
    temp_one = {}
    two = {}
    temp_two = {}
    three = {}
    temp_three = {}
    for i in p.keys():
        for j in range(len(p[i])):
            if p[i][j][0] == "injection buffer" and int(p[i][j][1].split(": ")[1]) == 192:
                if int(p[i][j][5].split(": ")[1]) in temp_overall.keys():
                    temp_overall[int(p[i][j][5].split(": ")[1])] += int(p[i][j][7].split(": ")[1])
                else:
                    temp_overall[int(p[i][j][5].split(": ")[1])] = int(p[i][j][7].split(": ")[1])

                if int(p[i][j][5].split(": ")[1]) in temp_zero.keys():
                    temp_zero[int(p[i][j][5].split(": ")[1])] += int(p[i][j][7].split(": ")[1])
                else:
                    temp_zero[int(p[i][j][5].split(": ")[1])] = int(p[i][j][7].split(": ")[1])

            elif p[i][j][0] == "injection buffer" and int(p[i][j][1].split(": ")[1]) == 193:
                if int(p[i][j][5].split(": ")[1]) in temp_one.keys():
                    temp_one[int(p[i][j][5].split(": ")[1])] += int(p[i][j][7].split(": ")[1])
                else:
                    temp_one[int(p[i][j][5].split(": ")[1])] = int(p[i][j][7].split(": ")[1])
                if int(p[i][j][5].split(": ")[1]) in temp_overall.keys():
                    temp_overall[int(p[i][j][5].split(": ")[1])] += int(p[i][j][7].split(": ")[1])
                else:
                    temp_overall[int(p[i][j][5].split(": ")[1])] = int(p[i][j][7].split(": ")[1])

            elif p[i][j][0] == "injection buffer" and int(p[i][j][1].split(": ")[1]) == 194:
                if int(p[i][j][5].split(": ")[1]) in temp_two.keys():
                    temp_two[int(p[i][j][5].split(": ")[1])] += int(p[i][j][7].split(": ")[1])
                else:
                    temp_two[int(p[i][j][5].split(": ")[1])] = int(p[i][j][7].split(": ")[1])
                if int(p[i][j][5].split(": ")[1]) in temp_overall.keys():
                    temp_overall[int(p[i][j][5].split(": ")[1])] += int(p[i][j][7].split(": ")[1])
                else:
                    temp_overall[int(p[i][j][5].split(": ")[1])] = int(p[i][j][7].split(": ")[1])

            elif p[i][j][0] == "injection buffer" and int(p[i][j][1].split(": ")[1]) == 195:
                if int(p[i][j][5].split(": ")[1]) in temp_three.keys():
                    temp_three[int(p[i][j][5].split(": ")[1])] += int(p[i][j][7].split(": ")[1])
                else:
                    temp_three[int(p[i][j][5].split(": ")[1])] = int(p[i][j][7].split(": ")[1])
                if int(p[i][j][5].split(": ")[1]) in temp_overall.keys():
                    temp_overall[int(p[i][j][5].split(": ")[1])] += int(p[i][j][7].split(": ")[1])
                else:
                    temp_overall[int(p[i][j][5].split(": ")[1])] = int(p[i][j][7].split(": ")[1])

    with open("example2.txt", "w") as file:
        for i in temp_one.keys():
            file.write(str(i) + "," + str(temp_one[i]) + "\n")