import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


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

initial_state = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
injection_core = {0: {}, 1: {}, 2: {}, 3: {}}
injection_core_update = {0: {}, 1: {}, 2: {}, 3: {}}
throughput_update = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
throughput = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
th = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
injection_rate = {0: 0, 1: 0, 2: 0, 3: 0}
window_size = {0: {}, 1: {}, 2: {}, 3: {}}
packet_type = {0: {}, 1: {}, 2: {}, 3: {}}
destination = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
packet_freq = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
temp = {0: {}, 1: {}, 2: {}, 3: {}}
processing_time = {0: {}, 1: {}, 2: {}, 3: {}}
transitions = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}


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


def generate_real_traffic_per_core(packet):
    for i in packet.keys():
        for j in range(len(packet[i])):
            if 192 <= int(packet[i][j][1].split(": ")[1]) <= 195 and 192 <= int(packet[i][j][2].split(": ")[1]) <= 195:
                if packet[i][j][0] == "injection buffer":
                    if int(packet[i][j][5].split(": ")[1]) not in \
                            throughput[chip_select(int(packet[i][j][1].split(": ")[1]))][
                                chip_select(int(packet[i][j][2].split(": ")[1]))].keys():
                        throughput[chip_select(int(packet[i][j][1].split(": ")[1]))][
                            chip_select(int(packet[i][j][2].split(": ")[1]))].setdefault(
                            int(packet[i][j][5].split(": ")[1]), []).append(int(packet[i][j][7].split(": ")[1]))
                        th[chip_select(int(packet[i][j][1].split(": ")[1]))][
                            chip_select(int(packet[i][j][2].split(": ")[1]))][
                            int(packet[i][j][5].split(": ")[1])] = (int(packet[i][j][7].split(": ")[1]))
                        injection_core[chip_select(int(packet[i][j][1].split(": ")[1]))].setdefault(int(packet[i][j][5].split(": ")[1]), []).append(int(packet[i][j][7].split(": ")[1]))

                    else:
                        throughput[chip_select(int(packet[i][j][1].split(": ")[1]))][
                            chip_select(int(packet[i][j][2].split(": ")[1]))][
                            int(packet[i][j][5].split(": ")[1])].append(int(packet[i][j][7].split(": ")[1]))
                        th[chip_select(int(packet[i][j][1].split(": ")[1]))][
                            chip_select(int(packet[i][j][2].split(": ")[1]))][
                            int(packet[i][j][5].split(": ")[1])] += (int(packet[i][j][7].split(": ")[1]))
                        injection_core[chip_select(int(packet[i][j][1].split(": ")[1]))].setdefault(
                            int(packet[i][j][5].split(": ")[1]), []).append(int(packet[i][j][7].split(": ")[1]))
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

    flag = prev = 0
    for source in injection_core.keys():
        for cyc in injection_core[source].keys():
            if flag == 0:
                injection_core_update[source][cyc] = injection_core[source][cyc]
                prev = cyc
                flag = 1
            elif flag == 1:
                if cyc - prev > 1:
                    for k in range(prev + 1, cyc):
                        injection_core_update[source].setdefault(k, []).append(0)
                injection_core_update[source][cyc] = injection_core[source][cyc]
                prev = cyc


def calculate_injection_rate():
    for source in injection_core_update.keys():
        on = off = 0
        for cycle, window in injection_core_update[source].items():
            if len(window) == 1 and window[0] == 0:
                off += 1
            else:
                on += 1
        injection_rate[source] = on / (off + on)
        print(injection_rate[source])
    print("-------\n")


def generate_per_core_packet_number_per_cycle():
    for src in throughput_update.keys():
        for dest in throughput_update[src].keys():
            for cycle in throughput_update[src][dest].keys():
                if len(throughput_update[src][dest][cycle]) == 1 and throughput_update[src][dest][cycle][0] == 0:
                    continue
                else:
                    if len(throughput_update[src][dest][cycle]) not in window_size[src].keys():
                        window_size[src][len(throughput_update[src][dest][cycle])] = 1
                    else:
                        window_size[src][len(throughput_update[src][dest][cycle])] += 1
                temp[src][cycle] = len(throughput_update[src][dest][cycle])


def destination_choose(packet):
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "injection buffer":
                destination[chip_select(int(packet[id][j][1].split(": ")[1]))][chip_select(int(packet[id][j][2].split(": ")[1]))] += 1


def packet_type_frequency():
    for src in throughput_update.keys():
        for dest in throughput_update[src].keys():
            for cycle, bytes in throughput_update[src][dest].items():
                if bytes[0] != 0:
                    for i in bytes:
                        if i not in packet_freq[src][dest].keys():
                            packet_freq[src][dest][i] = 1
                        else:
                            packet_freq[src][dest][i] += 1


def generate_markov_state():
    for src in throughput_update.keys():
        for dest in throughput_update[src].keys():
            for cycle in throughput_update[src][dest].keys():
                if len(throughput_update[src][dest][cycle]) == 1 and throughput_update[src][dest][cycle][0] == 0:
                    continue
                else:
                    for i in throughput_update[src][dest][cycle]:
                        if i not in packet_type.keys():
                            packet_type[src][i] = 1
                        else:
                            packet_type[src][i] += 1


def generate_processing_time(packet):
    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "rop push":
                for k in range(j + 1, len(packet[i])):
                    if packet[i][k][0] == "L2_icnt_push":
                        if int(packet[i][k][6].split(": ")[1]) == int(packet[i][j][6].split(": ")[1]):
                            duration = int(packet[i][k][5].split(": ")[1]) - int(packet[i][j][5].split(": ")[1])
                            if duration in processing_time[int(packet[i][j][6].split(": ")[1])].keys():
                                processing_time[int(packet[i][j][6].split(": ")[1])][duration] += 1
                            else:
                                processing_time[int(packet[i][j][6].split(": ")[1])][duration] = 1
                        break


def generate_transition_states():
    for core in packet_freq.keys():
        for dest in packet_freq[core].keys():
            overall = 0
            for packet, freq in packet_freq[core][dest].items():
                overall += freq
            for packet in packet_freq[core][dest].keys():
                transitions[core][dest][packet] = packet_freq[core][dest][packet]/overall


if __name__ == "__main__":
    file2 = open("report.txt", "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    cycle = {}
    packet = {}

    for i in range(len(lined_list)):  # cycle based classification
        if lined_list[i][0] != "Instruction cache miss":
            if chip_select(int(lined_list[i][1].split(": ")[1])) != chip_select(int(lined_list[i][2].split(": ")[1])):
                if int(lined_list[i][5].split(": ")[1]) in cycle.keys():
                    if lined_list[i] not in cycle[int(lined_list[i][5].split(": ")[1])]:
                        cycle.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])
                else:
                    cycle.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])
                    
    for i in range(len(lined_list)):  # packet based classification
        if lined_list[i][0] != "Instruction cache miss":
            if check_local_or_remote(lined_list[i]):
                if chip_select(int(lined_list[i][1].split(": ")[1])) != chip_select(int(lined_list[i][2].split(": ")[1])):
                    if int(lined_list[i][3].split(": ")[1]) in packet.keys():
                        if lined_list[i] not in packet[int(lined_list[i][3].split(": ")[1])]:
                            packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
                    else:
                        packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])

    generate_real_traffic_per_core(cycle)
    calculate_injection_rate()
    generate_per_core_packet_number_per_cycle()


    """ 
    generate_markov_state()
    destination_choose(packet)
    packet_type_frequency()
    generate_processing_time(packet)
    generate_transition_states()

    for i in range(0, 4):
        filename = "syrk_core_" + str(i) + str(".model")
        with open(filename, "w") as file:
            file.write("core " + str(i) + "\n")

            file.write("window_size_begin\n")
            for size, freq in window_size[i].items():
                file.write(str(size) + "\t" + str(freq) + "\n")
            file.write("window_size_end\n\n")

            file.write("packet_distribution_begin\n")
            for dest, data in packet_freq[i].items():
                file.write(str(dest) + ":\t")
                for pack, freq in data.items():
                    file.write(str(pack) + "\t" + str(freq) + "\t")
                file.write("\n")
            file.write("\npacket_distribution_end\n\n")

            file.write("destination_begin\n")
            for dest, freq in destination[i].items():
                file.write(str(dest) + "\t" + str(freq) + "\n")
            file.write("destination_end\n\n")

            file.write("transition_begin\n")
            for dest in transitions[i].keys():
                file.write("destination\t" + str(dest) + "\n")
                for byte in transitions[i][dest].keys():
                    file.write("\t\t" + str(byte) + "\t")
                file.write("\n")
                for byte in transitions[i][dest].keys():
                    file.write(str(byte) + "\t\t")
                    for byte2 in transitions[i][dest].keys():
                        file.write(str("{:.4f}".format(transitions[i][dest][byte2])) + "\t")
                    file.write("\n")
            file.write("transition_end\n\n")

            file.write("processing_time_begin\n")
            for time, freq in processing_time[i].items():
                file.write(str(time) + "\t" + str(freq) + "\n")
            file.write("processing_time_end\n\n")
    """