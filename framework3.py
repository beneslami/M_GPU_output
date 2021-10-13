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
throughput_update = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
throughput = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
th = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
injection_rate = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
window_size = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
window_size_t = {0: {}, 1: {}, 2: {}, 3: {}}
packet_type = {0: {}, 1: {}, 2: {}, 3: {}}
destination = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
packet_freq = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
temp = {0: {}, 1: {}, 2: {}, 3: {}}
processing_time = {0: {}, 1: {}, 2: {}, 3: {}}
main_transitions = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
cycle_transision = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}


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


def generate_real_traffic_per_core(source, dest, packet):
    for cycle, byte in packet.items():
        if cycle not in throughput[source][dest].keys():
            throughput[source][dest][cycle] = byte
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


def calculate_injection_rate(source, dest):
    off = 0
    total = 0
    for cyc in throughput_update[source][dest].keys():
        if throughput_update[source][dest][cyc][0] == 0:
            off += 1
        total += 1
    injection_rate[source][dest] = 1 - off/total


def generate_per_core_packet_number_per_cycle(source, dest):
    for cycle in throughput_update[source][dest].keys():
        if throughput_update[source][dest][cycle][0] == 0:
            continue
        else:
            if len(throughput_update[source][dest][cycle]) not in window_size[source][dest].keys():
                window_size[source][dest][len(throughput_update[source][dest][cycle])] = 1
            else:
                window_size[source][dest][len(throughput_update[source][dest][cycle])] += 1
            """if len(throughput_update[src][dest][cycle]) not in window_size_t[src].keys():
                window_size_t[src][len(throughput_update[src][dest][cycle])] = 1
            else:
                window_size_t[src][len(throughput_update[src][dest][cycle])] += 1"""
    window_size[source][dest] = dict(sorted(window_size[source][dest].items(), key=lambda x: x[0]))


def destination_choose(packet):
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "injection buffer":
                destination[chip_select(int(packet[id][j][1].split(": ")[1]))][chip_select(int(packet[id][j][2].split(": ")[1]))] += 1


def packet_type_frequency(source, dest):
    for cycle, bytes in throughput_update[source][dest].items():
        if bytes[0] != 0:
            for i in bytes:
                if i not in packet_freq[source][dest].keys():
                    packet_freq[source][dest][i] = 1
                else:
                    packet_freq[source][dest][i] += 1


def generate_markov_state(source, dest):
    for cycle in throughput_update[source][dest].keys():
        if throughput_update[source][dest][cycle][0] == 0:
            continue
        else:
            for i in throughput_update[source][dest][cycle]:
                if i not in packet_type[source].keys():
                    packet_type[source][i] = 1
                else:
                    packet_type[source][i] += 1


def generate_processing_time(source):
    if 1 not in processing_time[source].keys():
        processing_time[source][1] = 1
    else:
        processing_time[source][1] += 1


def generate_transition_states(source, dest):
    tmp = {source: {dest: {}}}
    single = {source: {dest: {}}}
    overall = {source: {dest: {}}}
    overall_single = {source: {dest: {}}}
    prev_line = 0
    prev_cycle = 0
    for packet in packet_freq[source][dest].keys():
        if packet not in tmp[source][dest].keys():
            tmp[source][dest].setdefault(packet, {})
            single[source][dest].setdefault(packet, {})

    for packet1 in packet_freq[source][dest].keys():
        for packet2 in packet_freq[source][dest].keys():
            if packet2 not in tmp[source][dest][packet1].keys():
                tmp[source][dest][packet1][packet2] = 0
                single[source][dest][packet1][packet2] = 0

    for cycle in throughput[source][dest].keys():
        if throughput[source][dest][cycle][0] == 0:
            continue
        else:
            if len(throughput[source][dest][cycle]) > 1:
                for i in range(len(throughput[source][dest][cycle])):
                    if i == 0:
                        prev_line = throughput[source][dest][cycle][i]
                    else:
                        if throughput[source][dest][cycle][i] not in tmp[source][dest][prev_line].keys():
                            tmp[source][dest][prev_line][throughput[source][dest][cycle][i]] = 1
                        else:
                            tmp[source][dest][prev_line][throughput[source][dest][cycle][i]] += 1
                        if prev_line not in overall[source][dest].keys():
                            overall[source][dest][prev_line] = 1
                        else:
                            overall[source][dest][prev_line] += 1
                        prev_line = throughput[source][dest][cycle][i]
            elif len(throughput[source][dest][cycle]) == 1:
                if prev_cycle == 0:
                    prev_cycle = throughput[source][dest][cycle][0]
                else:
                    if throughput[source][dest][cycle][0] not in single[source][dest][prev_cycle].keys():
                        single[source][dest][prev_cycle][throughput[source][dest][cycle][0]] = 1
                    else:
                        single[source][dest][prev_cycle][throughput[source][dest][cycle][0]] += 1
                    if prev_cycle not in overall_single[source][dest].keys():
                        overall_single[source][dest][prev_cycle] = 1
                    else:
                        overall_single[source][dest][prev_cycle] += 1
                    prev_cycle = throughput[source][dest][cycle][0]

    for state in tmp[source][dest].keys():
        for next_state in tmp[source][dest][state].keys():
            tmp[source][dest][state][next_state] = tmp[source][dest][state][next_state] / overall[source][dest][state]
    main_transitions[source][dest] = tmp[source][dest]
    for state in single[source][dest].keys():
        for next_state in single[source][dest][state].keys():
            single[source][dest][state][next_state] = single[source][dest][state][next_state] / overall_single[source][dest][state]

    cycle_transision[source][dest] = single[source][dest]


if __name__ == "__main__":
    model_name = "syrk"
    for src in range(0, 4):
        for dest in range(0, 4):
            if src != dest:
                path = "out/pre_" + str(src) + "_" + str(dest) + ".txt"
                file2 = open(path, "r")
                raw_content = ""
                if file2.mode == "r":
                    raw_content = file2.readlines()
                lined_list = {}
                for line in raw_content:
                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                    y = len(item[1].split("\n")[0][1:][:-1].split(","))
                    for index in range(y):
                        if int(item[0]) not in lined_list.keys():
                            lined_list.setdefault(int(item[0]), []).append(
                                int(item[1].split("\n")[0][1:][:-1].split(",")[index]))
                        else:
                            lined_list[int(item[0])].append(int(item[1].split("\n")[0][1:][:-1].split(",")[index]))

                generate_real_traffic_per_core(src, dest, lined_list)
                calculate_injection_rate(src, dest)
                generate_per_core_packet_number_per_cycle(src, dest)
                #destination_choose()
                packet_type_frequency(src, dest)
                generate_markov_state(src, dest)
                generate_processing_time(src)
                generate_transition_states(src, dest)

    for i in range(0, 4):
        filename = model_name + "_core_" + str(i) + str(".model")
        with open(filename, "w") as file:
            file.write("core " + str(i) + "\n")

            file.write("injection_rate_begin\n")
            for dest in injection_rate[i].keys():
                file.write(str(dest) + "\t" + str(injection_rate[i][dest]) + "\n")
            file.write("injection_rate_end\n")

            file.write("window_size_begin\n")
            for dest in window_size[i].keys():
                file.write("destination " + str(dest) + "\n")
                for size, freq in window_size[i][dest].items():
                    file.write(str(size) + "\t" + str(freq) + "\n")
            file.write("window_size_end\n\n")

            file.write("packet_distribution_begin\n")
            for dest, data in packet_freq[i].items():
                file.write(str(dest) + ":\t")
                for pack, freq in data.items():
                    file.write(str(pack) + "\t" + str(freq) + "\t")
                file.write("\n")
            file.write("packet_distribution_end\n\n")

            #file.write("destination_begin\n")
            #for dest, freq in destination[i].items():
                #file.write(str(dest) + "\t" + str(freq) + "\n")
            #file.write("destination_end\n\n")

            file.write("cycle_transition_begin\n")
            for dest in cycle_transision[i].keys():
                file.write("destination " + str(dest) + "\n")
                for source in cycle_transision[i][dest].keys():
                    file.write("\t\t" + str(source))
                file.write("\n")
                for source in cycle_transision[i][dest].keys():
                    file.write(str(source) + str("\t\t"))
                    for d in cycle_transision[i][dest][source].keys():
                        file.write(str("{:.3f}".format(cycle_transision[i][dest][source][d])) + "\t\t")
                    file.write("\n")
            file.write("cycle_transition_end\n\n")

            file.write("line_transition_begin\n")
            for dest in main_transitions[i].keys():
                file.write("destination " + str(dest) + "\n")
                for source in main_transitions[i][dest].keys():
                    file.write("\t\t" + str(source))
                file.write("\n")
                for source in main_transitions[i][dest].keys():
                    file.write(str(source) + str("\t\t"))
                    for d in main_transitions[i][dest][source].keys():
                        file.write(str("{:.3f}".format(main_transitions[i][dest][source][d])) + "\t\t")
                    file.write("\n")
            file.write("line_transition_end\n\n")

            file.write("processing_time_begin\n")
            for time, freq in processing_time[i].items():
               """file.write(str(time) + "\t" + str(freq) + "\n")"""
            file.write("processing_time_end\n\n")