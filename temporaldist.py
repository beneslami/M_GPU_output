from statistics import variance

import numpy as np
from numpy import average
import matplotlib.pyplot as plt
import csv

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


def inter_packet_distribution(packet):
    arr = {
        0: {
            "departure": {},
            "arrival": {}
        },
        1: {
            "departure": {},
            "arrival": {}
        },
        2: {
            "departure": {},
            "arrival": {}
        },
        3: {
            "departure": {},
            "arrival": {}
        }
    }
    previous_departure = [1, 1, 1, 1]
    previous_arrival = [1, 1, 1, 1]
    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "injection buffer":  # for sending request
                temp = int(packet[i][j][5].split(": ")[1]) - previous_departure[
                    chip_select(int(packet[i][j][1].split(": ")[1]))]
                if temp in arr[chip_select(int(packet[i][j][1].split(": ")[1]))]["departure"].keys():
                    arr[chip_select(int(packet[i][j][1].split(": ")[1]))]["departure"][temp] += 1
                else:
                    arr[chip_select(int(packet[i][j][1].split(": ")[1]))]["departure"][temp] = 1
                previous_departure[chip_select(int(packet[i][j][1].split(": ")[1]))] = int(
                    packet[i][j][5].split(": ")[1])
            elif packet[i][j][0] == "L2_icnt_pop":  # for sending response
                temp = int(packet[i][j][5].split(": ")[1]) - previous_departure[
                    chip_select(int(packet[i][j][1].split(": ")[1]))]
                if temp in arr[chip_select(int(packet[i][j][1].split(": ")[1]))]["departure"].keys():
                    arr[chip_select(int(packet[i][j][1].split(": ")[1]))]["departure"][temp] += 1
                else:
                    arr[chip_select(int(packet[i][j][1].split(": ")[1]))]["departure"][temp] = 1
                previous_departure[chip_select(int(packet[i][j][1].split(": ")[1]))] = int(
                    packet[i][j][5].split(": ")[1])
            elif packet[i][j][0] == "SM boundary buffer push":  # for receiving response
                temp = int(packet[i][j][5].split(": ")[1]) - previous_arrival[
                    chip_select(int(packet[i][j][1].split(": ")[1]))]
                if temp in arr[chip_select(int(packet[i][j][1].split(": ")[1]))]["arrival"].keys():
                    arr[chip_select(int(packet[i][j][1].split(": ")[1]))]["arrival"][temp] += 1
                else:
                    arr[chip_select(int(packet[i][j][1].split(": ")[1]))]["arrival"][temp] = 1
                previous_arrival[chip_select(int(packet[i][j][1].split(": ")[1]))] = int(
                    packet[i][j][5].split(": ")[1])
            elif packet[i][j][0] == "inter_icnt_pop_llc_push":  # for receiving request
                temp = int(packet[i][j][5].split(": ")[1]) - previous_arrival[
                    chip_select(int(packet[i][j][1].split(": ")[1]))]
                if temp in arr[chip_select(int(packet[i][j][1].split(": ")[1]))]["arrival"].keys():
                    arr[chip_select(int(packet[i][j][1].split(": ")[1]))]["arrival"][temp] += 1
                else:
                    arr[chip_select(int(packet[i][j][1].split(": ")[1]))]["arrival"][temp] = 1
                previous_arrival[chip_select(int(packet[i][j][1].split(": ")[1]))] = int(
                    packet[i][j][5].split(": ")[1])


    for i in arr.keys():
        key = []
        value = []
        sort_orders = sorted(arr[i]["departure"].items(), key=lambda x: x[0])
        for j in range(len(sort_orders)):
            key.append(sort_orders[j][0])
            value.append(sort_orders[j][1])
        plt.plot(key, value, "r--", label="departure-time")
        key.clear()
        value.clear()
        sort_orders = sorted(arr[i]["arrival"].items(), key=lambda x: x[0])
        for j in range(len(sort_orders)):
            key.append(sort_orders[j][0])
            value.append(sort_orders[j][1])
        plt.plot(key, value, "k--", label="arrival-time")
        key.clear()
        value.clear()
        string = "chiplet " + str(i)
        plt.title(string)
        plt.xlabel("time")
        plt.ylabel("Frequency")
        plt.legend(loc="best")
        plt.show()
    sum = 0
    coef = 0
    Mean_interval_time = []
    for i in arr.keys():
        for j in arr[i]["departure"]:
            sum += arr[i]["departure"][j] * j
            coef += arr[i]["departure"][j]
        for j in arr[i]["arrival"]:
            sum += arr[i]["arrival"][j] * j
            coef += arr[i]["arrival"][j]
        Mean_interval_time.append(sum / coef)
    print(Mean_interval_time)


def injection_per_cycle(packet):
    ingress = {}
    ingress_byte = {}
    egress = {}
    egress_byte = {}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "injection buffer" or packet[i][j][0] == "L2_icnt_pop":
                if i not in ingress.keys():
                    ingress[i] = 1
                else:
                    ingress[i] += 1
                if i not in ingress_byte.keys():
                    if packet[i][j][0] == "L2_icnt_pop":
                        ingress_byte[i] = int(packet[i][j][7].split(":")[1])
                    elif packet[i][j][0] == "injection buffer":
                        ingress_byte[i] = int(packet[i][j][7].split(": ")[1])
                else:
                    if packet[i][j][0] == "L2_icnt_pop":
                        ingress_byte[i] += int(packet[i][j][7].split(":")[1])
                    elif packet[i][j][0] == "injection buffer":
                        ingress_byte[i] += int(packet[i][j][7].split(": ")[1])

            elif packet[i][j][0] == "inter_icnt_pop_llc_push" or packet[i][j][0] == "SM boundary buffer push":
                if i not in egress.keys():
                    egress[i] = 1
                else:
                    egress[i] += 1
                if i not in egress_byte.keys():
                    egress_byte[i] = int(packet[i][j][7].split(": ")[1])
                else:
                    egress_byte[i] += int(packet[i][j][7].split(": ")[1])

    """plt.plot(list(ingress.keys()), list(ingress.values()), "b", label="ingress")
    plt.plot(list(egress.keys()), list(egress.values()), "r", label="egress")
    plt.xlabel("Time (Cycle)")
    plt.ylabel("Number of packet")
    plt.legend(loc="best")
    plt.show()

    plt.plot(list(ingress_byte.keys()), list(ingress_byte.values()), "b", label="ingress")
    plt.plot(list(egress_byte.keys()), list(egress_byte.values()), "r", label="egress")
    plt.xlabel("Time (Cycle)")
    plt.ylabel("Number of bytes")
    plt.legend(loc="best")
    plt.show()

    byte_distribution = {}
    for i in ingress_byte.keys():
        if ingress_byte[i] in byte_distribution.keys():
            byte_distribution[ingress_byte[i]] += 1
        else:
            byte_distribution[ingress_byte[i]] = 1
    plt.bar(list(byte_distribution.keys()), list(byte_distribution.values()), width=10)
    plt.xlabel("Byte")
    plt.xlim([-100., 6000.])
    plt.ylim([0., 7000.])
    plt.ylabel("Distribution")
    plt.show()"""


def ingress_egress_per_packet(packet):
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
    with open("atax.csv", "w", newline='') as file_csv:
        field = ['cycle', 'byte']
        writer = csv.DictWriter(file_csv, fieldnames=field)
        writer.writeheader()
        for i in range(len(sort_orders)):
            writer.writerow({"cycle": sort_orders[i][0], "byte": sort_orders[i][1]})


def self_similarity(packet):
    gress_byte = 0
    prev_cycle = 0
    scale = 1
    ingress_byte_scaled = {}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if check_local_or_remote(packet[i][j]):
                if packet[i][j][0] == "L2_icnt_pop":
                    gress_byte += int(packet[i][j][7].split(":")[1])
                elif packet[i][j][0] == "injection buffer":
                    gress_byte += int(packet[i][j][7].split(": ")[1])
                elif packet[i][j][0] == "inter_icnt_pop_llc_push":
                    gress_byte += -int(packet[i][j][7].split(": ")[1])
                elif packet[i][j][0] == "SM boundary buffer push":
                    gress_byte += -int(packet[i][j][7].split(": ")[1])
        if i - prev_cycle >= scale:
            if i in ingress_byte_scaled.keys():
                ingress_byte_scaled[i] += gress_byte
            else:
                ingress_byte_scaled[i] = gress_byte
            prev_cycle = i
            gress_byte = 0
        else:
            continue
    traffic_mean = average(list(ingress_byte_scaled.values()))
    traffic_vars = variance(list(ingress_byte_scaled.values()))
    traffic_std = np.sqrt(traffic_vars)
    plt.plot(list(ingress_byte_scaled.keys()), list(ingress_byte_scaled.values()))
    string = "mean: " + str(traffic_mean) + "\n" + "variance: " + str(traffic_vars) + "\n" + "stdev: " + str(
        traffic_std)
    plt.text(100000, -3200, string, bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
    plt.xlabel("Time (Cycle)")
    plt.ylabel("ingress/egress bytes")
    plt.show()

    with open("syrk.csv", "w", newline='') as file_csv:
        field = ['cycle', 'byte']
        writer = csv.DictWriter(file_csv, fieldnames=field)
        writer.writeheader()
        for i in ingress_byte_scaled.keys():
            writer.writerow({"cycle": i, "byte": ingress_byte_scaled[i]})


if __name__ == "__main__":
    file = open("report_syrk.txt", "r")
    raw_content = ""
    if file.mode == "r":
        raw_content = file.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    packet = {}

    """for i in range(len(lined_list)):  # packet based classification
        if int(lined_list[i][3].split(": ")[1]) in packet.keys():
            if lined_list[i] not in packet[int(lined_list[i][3].split(": ")[1])]:
                packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        else:
            packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])"""

    for i in range(len(lined_list)):  # cycle based classification
        if lined_list[i][0] != "Instruction cache miss":
            if chip_select(int(lined_list[i][1].split(": ")[1])) != chip_select(int(lined_list[i][2].split(": ")[1])):
                if int(lined_list[i][5].split(": ")[1]) in packet.keys():
                    if lined_list[i] not in packet[int(lined_list[i][5].split(": ")[1])]:
                        packet.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])
                else:
                    packet.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])

    # inter_packet_distribution(packet)
    # injection_per_cycle(packet)
    self_similarity(packet)
    # ingress_egress_per_packet(packet)