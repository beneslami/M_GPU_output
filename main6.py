import numpy as np
import matplotlib.pyplot as plt


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


def check_local_or_remote(x):  # 0 for local, 1 for remote
    for i in range(len(chiplet)):
        if int(x[5].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[5].split(": ")[1]) in chiplet[i]["LLC_ID"]:
            if int(x[6].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[6].split(": ")[1]) in chiplet[i]["LLC_ID"]:
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


def time_byte_plot():
    with open('rodinia.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    arr = {int(lined_list[1][0].split(",")[0]): int(lined_list[1][0].split(",")[1])}
    prev_time_slot = int(lined_list[1][0].split(",")[0])
    for i in range(2, len(lined_list)):
        if int(lined_list[i][0].split(",")[0]) == prev_time_slot + 1:
            arr[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])
            prev_time_slot = int(lined_list[i][0].split(",")[0])
        else:
            for j in range(prev_time_slot + 1, int(lined_list[i][0].split(",")[0]) + 1):
                arr[j] = 0
            arr[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])
            prev_time_slot = int(lined_list[i][0].split(",")[0])
    fig, ax = plt.subplots(1, 1, figsize=(18, 5), dpi=100)
    ax.plot(list(arr.keys()), list(arr.values()))
    plt.axes([0, 11, 1, 1])
    #ax.set_aspect(aspect=50)
    plt.xlabel("Cycle")
    plt.ylabel("Bytes")
    plt.show()


def cross_correlation():
    with open('synthetic.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    process1 = {}
    for i in range(1, len(lined_list)):
        process1[int(lined_list[i][0].split(",")[0])] = float(lined_list[i][0].split(",")[1])

    with open('atax.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    process2 = {}
    for i in range(1, len(lined_list)):
        process2[int(lined_list[i][0].split(",")[0])] = float(lined_list[i][0].split(",")[1])

    x = len(process1)
    for i in range(1, x):
        if i not in process2.keys():
            process1.pop(i)
        else:
            continue

    process1.pop(len(process1))
    print(len(process1))
    print(len(process2))
    p1_mean = np.mean(list(process1.values()))
    p1_std = np.std(list(process1.values()))
    p2_mean = np.mean(list(process2.values()))
    p2_std = np.std(list(process2.values()))
    fig, ax = plt.subplots(1, 1)
    ax.xcorr(list(process1.values()), list(process2.values()), maxlags=50)
    plt.show()


if __name__ == '__main__':
    """file = open("report.txt", "r")
    raw_content = ""
    if file.mode == "r":
        raw_content = file.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    packet = {}
    for i in range(len(lined_list)):  # cycle based classification
        if lined_list[i][0] != "Instruction cache miss":
            if chip_select(int(lined_list[i][1].split(": ")[1])) != chip_select(int(lined_list[i][2].split(": ")[1])):
                if int(lined_list[i][5].split(": ")[1]) in packet.keys():
                    if lined_list[i] not in packet[int(lined_list[i][5].split(": ")[1])]:
                        packet.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])
                else:
                    packet.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])


    gress_byte = {}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if check_local_or_remote(packet[i][j]):
                if packet[i][j][0] == "L2_icnt_pop":
                    if int(packet[i][j][5].split(": ")[1]) in gress_byte.keys():
                        gress_byte[int(packet[i][j][5].split(": ")[1])] += int(packet[i][j][7].split(":")[1])
                    else:
                        gress_byte[int(packet[i][j][5].split(": ")[1])] = int(packet[i][j][7].split(":")[1])
                elif packet[i][j][0] == "injection buffer":
                    if int(packet[i][j][5].split(": ")[1]) in gress_byte.keys():
                        gress_byte[int(packet[i][j][5].split(": ")[1])] += int(packet[i][j][7].split(": ")[1])
                    else:
                        gress_byte[int(packet[i][j][5].split(": ")[1])] = int(packet[i][j][7].split(": ")[1])
                elif packet[i][j][0] == "inter_icnt_pop_llc_push":
                    if int(packet[i][j][5].split(": ")[1]) in gress_byte.keys():
                        gress_byte[int(packet[i][j][5].split(": ")[1])] += -int(packet[i][j][7].split(": ")[1])
                    else:
                        gress_byte[int(packet[i][j][5].split(": ")[1])] = -int(packet[i][j][7].split(": ")[1])
                elif packet[i][j][0] == "SM boundary buffer push":
                    if int(packet[i][j][5].split(": ")[1]) in gress_byte.keys():
                        gress_byte[int(packet[i][j][5].split(": ")[1])] += -int(packet[i][j][7].split(": ")[1])
                    else:
                        gress_byte[int(packet[i][j][5].split(": ")[1])] = -int(packet[i][j][7].split(": ")[1])

    sort_orders = sorted(gress_byte.items(), key=lambda x: x[0])
    with open("rodinia.csv", "w", newline='') as file_csv:
        field = ['cycle', 'byte']
        writer = csv.DictWriter(file_csv, fieldnames=field)
        writer.writeheader()
        for i in range(len(sort_orders)):
            writer.writerow({"cycle": sort_orders[i][0], "byte": sort_orders[i][1]})"""
    cross_correlation()