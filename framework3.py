import csv
import threading
import os

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
traffic = {0: {}, 1: {}, 2: {}, 3: {}}
injection_rate = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
initial_state = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}

th = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
state_nums = {0: {}, 1: {}, 2: {}, 3: {}}
inj_rate = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
window_size = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
dest_window_size = {0: {}, 1: {}, 2: {}, 3: {}}
window_size_t = {0: {}, 1: {}, 2: {}, 3: {}}
packet_type = {0: {}, 1: {}, 2: {}, 3: {}}
destination = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
packet_freq = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
temp = {0: {}, 1: {}, 2: {}, 3: {}}
processing_time = {0: {}, 1: {}, 2: {}, 3: {}}
main_transitions = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
cycle_transision = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
iat = {0: {}, 1: {}, 2: {}, 3: {}}
inter_injection_rate = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}


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


def update_traffic():
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            list_ = [0, 1, 2, 3]
            list_.remove(src)
            for dest in traffic[src][cyc].keys():
                list_.remove(dest)
            if len(list_) != 0:
                for i in list_:
                    traffic[src][cyc].setdefault(i, [])
    for src in traffic.keys():
        traffic[src] = dict(sorted(traffic[src].items(), key=lambda x: x[0]))
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            traffic[src][cyc] = dict(sorted(traffic[src][cyc].items(), key=lambda x: x[0]))


def generate_real_traffic_per_core(source, dest, packet):
    global traffic
    for cycle, byte in packet.items():
        if cycle not in traffic[source].keys():
            traffic[source].setdefault(cycle, {})
            if dest not in traffic[source][cycle].keys():
                traffic[source][cycle][dest] = byte
            else:
                for b in byte:
                    traffic[source][cycle][dest].append(b)
        else:
            if dest not in traffic[source][cycle].keys():
                traffic[source][cycle][dest] = byte
            else:
                for b in byte:
                    traffic[source][cycle][dest].append(b)
    """flag = prev = 0
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
                    prev = cyc"""


def calculate_injection_rate():
    global traffic
    global injection_rate
    on = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    total = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    for source in traffic.keys():
        for cyc in traffic[source].keys():
            for dest in traffic[source][cyc].keys():
                if len(traffic[source][cyc][dest]) != 0:
                    on[source][dest] += 1
                total[source][dest] += 1

    for src in on.keys():
        for dest in on[src].keys():
            injection_rate[src][dest] = on[src][dest] / total[src][dest]
    on.clear()


def calculate_inter_injection_rate():
    global traffic
    global inter_injection_rate
    start = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    flag = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    """for src in traffic.keys():
        for cyc in traffic[src].keys():
            for dest in traffic[src][cyc].keys():
                if len(traffic[src][cyc][dest]) == 0:
                    if flag[src][dest] == 0:
                        start[src][dest] = cyc
                        flag[src][dest] = 1
                    elif flag[src][dest] == 1:
                        continue
                else:
                    if flag[src][dest] == 1:
                        if (cyc - start[src][dest]) not in inter_injection_rate[src][dest].keys():
                            inter_injection_rate[src][dest][(cyc - start[src][dest])] = 1
                        else:
                            inter_injection_rate[src][dest][(cyc - start[src][dest])] += 1
                        flag[src][dest] = 0"""

    for src in traffic.keys():
        for cyc in traffic[src].keys():
            for dest in traffic[src][cyc].keys():
                if len(traffic[src][cyc][dest]) == 0:
                    if flag[src][dest] == 0:
                        start[src][dest] += 1
                        flag[src][dest] = 1
                    else:
                        start[src][dest] += 1
                else:
                    if flag[src][dest] == 1:
                        if start[src][dest] not in inter_injection_rate[src][dest].keys():
                            inter_injection_rate[src][dest][start[src][dest]] = 1
                        else:
                            inter_injection_rate[src][dest][start[src][dest]] += 1
                        start[src][dest] = 0
                        flag[src][dest] = 0
                    else:
                        continue

    for src in inter_injection_rate.keys():
        for dest in inter_injection_rate[src].keys():
            inter_injection_rate[src][dest] = dict(sorted(inter_injection_rate[src][dest].items(), key=lambda x: x[0]))


def packet_type_frequency():
    global traffic
    global packet_freq
    for source in traffic.keys():
        for cycle in traffic[source].keys():
            for dest, bytes in traffic[source][cycle].items():
                if len(bytes) != 0:
                    for i in bytes:
                        if i not in packet_freq[source][dest].keys():
                            packet_freq[source][dest][i] = 1
                        else:
                            packet_freq[source][dest][i] += 1
                else:
                    if 0 not in packet_freq[source][dest].keys():
                        packet_freq[source][dest][0] = 1
                    else:
                        packet_freq[source][dest][0] += 1
    for src in packet_freq.keys():
        for dest in packet_freq[src].keys():
            packet_freq[src][dest] = dict(sorted(packet_freq[src][dest].items(), key=lambda x: x[0]))


def calculate_destination_window(subpath):
    global dest_window_size
    for source in range(0, 4):
        path = subpath + "pre/out/dest_win_" + str(source) + ".txt"
        file = open(path, "r")
        raw_content = ""
        if file.mode == "r":
            raw_content = file.readlines()
        for line in raw_content:
            item = [x for x in line.split("\t") if x not in ['', '\t']]
            y = len(item[1].split("\n")[0][1:][:-1].split(", "))
            if y not in dest_window_size[source].keys():
                dest_window_size[source][y] = 1
            else:
                dest_window_size[source][y] += 1

        dest_window_size[source] = dict(sorted(dest_window_size[source].items(), key=lambda x: x[0]))


def generate_processing_time(subpath):
    global processing_time
    for source in range(0, 4):
        path = subpath + "pre/out/processing_time_" + str(source) + ".txt"
        file = open(path, "r")
        raw_content = ""
        if file.mode == "r":
            raw_content = file.readlines()
        lined_list = {}
        for line in raw_content:
            item = [x for x in line.split("\t") if x not in ['', '\t']]
            lined_list[int(item[0])] = int(item[1])
        processing_time[source] = lined_list
        processing_time[source] = dict(sorted(processing_time[source].items(), key=lambda x: x[0]))


def inter_arrival_time():
    global iat
    """for source in range(0, 4):
        with open(subpath + "pre/out/iat_" + str(source) + ".csv") as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            for item in reader:
                iat[source][int(item[0])] = int(item[1])"""
    flag = 0
    start = -1
    for source in traffic.keys():
        for cycle in traffic[source].keys():
            if flag == 0:
                start = cycle
                flag = 1
            elif flag == 1:
                if (cycle - start) not in iat[source].keys():
                    iat[source][cycle - start] = 1
                else:
                    iat[source][cycle - start] += 1
                start = cycle
    for source in iat.keys():
        iat[source] = dict(sorted(iat[source].items(), key=lambda x: x[0]))


def generate_per_core_packet_number_per_cycle():
    global traffic
    global window_size
    for source in traffic.keys():
        for cycle in traffic[source].keys():
            for dest in traffic[source][cycle].keys():
                if len(traffic[source][cycle][dest]) not in window_size[source][dest].keys():
                    window_size[source][dest][len(traffic[source][cycle][dest])] = 1
                else:
                    window_size[source][dest][len(traffic[source][cycle][dest])] += 1

    for source in window_size.keys():
        for dest in window_size[source].keys():
            window_size[source][dest] = dict(sorted(window_size[source][dest].items(), key=lambda x: x[0]))


def destination_choose():
    global traffic
    global destination
    for core in traffic.keys():
        for cyc in traffic[core].keys():
            for dest, byte in traffic[core][cyc].items():
                if len(traffic[core][cyc][dest]) != 0:
                    if dest not in destination[core].keys():
                        destination[core][dest] = 1
                    else:
                        destination[core][dest] += 1
    for src in destination.keys():
        destination[src] = dict(sorted(destination[src].items(), key=lambda x: x[0]))


def generate_markov_state(source, dest):
    global throughput
    global throughput_update
    global packet_type
    for cycle in throughput_update[source][dest].keys():
        if throughput_update[source][dest][cycle][0] == 0:
            continue
        else:
            for i in throughput_update[source][dest][cycle]:
                if i not in packet_type[source].keys():
                    packet_type[source][i] = 1
                else:
                    packet_type[source][i] += 1


def generate_transition_states(source, dest):
    global throughput
    global throughput_update
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


def state_number():
    global traffic
    global state_nums
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            temp = 0
            for dest in traffic[src][cyc].keys():
                if len(traffic[src][cyc][dest]) != 0:
                    temp += 1
            if temp not in state_nums[src].keys():
                state_nums[src][temp] = 1
            else:
                state_nums[src][temp] += 1
    for src in state_nums.keys():
        destination[src] = dict(sorted(destination[src].items(), key=lambda x: x[0]))


if __name__ == "__main__":
    model_name = "cfd"
    subpath = "benchmarks/Rodinia/" + model_name + "/"
    for src in range(0, 4):
        for dest in range(0, 4):
            if src != dest:
                path = subpath + "pre/out/pre_" + str(src) + "_" + str(dest) + ".txt"
                file2 = open(path, "r")
                raw_content = ""
                if file2.mode == "r":
                    raw_content = file2.readlines()
                file2.close()
                lined_list = {}
                for line in raw_content:
                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                    y = len(item[1].split("\n")[0][1:][:-1].split(","))
                    for index in range(y):
                        if int(item[0]) not in lined_list.keys():
                            lined_list.setdefault(int(item[0]), []).append(int(item[1].split("\n")[0][1:][:-1].split(",")[index]))
                        else:
                            lined_list[int(item[0])].append(int(item[1].split("\n")[0][1:][:-1].split(",")[index]))
                del (raw_content)
                generate_real_traffic_per_core(src, dest, lined_list)
                del(lined_list)
    update_traffic()
    t0 = threading.Thread(target=calculate_injection_rate, args=())
    t1 = threading.Thread(target=generate_per_core_packet_number_per_cycle, args=())
    t2 = threading.Thread(target=packet_type_frequency, args=())
    t3 = threading.Thread(target=calculate_destination_window, args=(subpath,))
    t4 = threading.Thread(target=inter_arrival_time, args=())
    t5 = threading.Thread(target=generate_processing_time, args=(subpath,))
    t6 = threading.Thread(target=calculate_inter_injection_rate, args=())
    t7 = threading.Thread(target=state_number, args=())
    t8 = threading.Thread(target=destination_choose, args=())
    t0.start()
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t7.start()
    t8.start()
    t0.join()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
    t7.join()
    t8.join()
    for i in range(0, 4):
        filename = subpath + model_name + "_core_" + str(i) + str(".model")
        with open(filename, "w") as file:
            file.write("core " + str(i) + "\n\n")
            file.write("injection_rate_begin\n")
            for dest, prob in injection_rate[i].items():
                file.write(str(dest) + "\t" + str(prob) + "\n")
            file.write("injection_rate_end\n")

            file.write("\nwindow_size_begin\n")
            for dest in window_size[i].keys():
                file.write("destination " + str(dest) + "\n")
                for size, freq in window_size[i][dest].items():
                    file.write(str(size) + "\t" + str(freq) + "\n")
            file.write("window_size_end\n\n")

            file.write("packet_distribution_begin\n")
            for dest, data in packet_freq[i].items():
                file.write("destination " + str(dest) + "\n")
                for pack, freq in data.items():
                    file.write(str(pack) + "\t" + str(freq) + "\n")
            file.write("packet_distribution_end\n\n")

            file.write("destination_begin\n")
            for dest, freq in destination[i].items():
                file.write(str(dest) + "\t" + str(freq) + "\n")
            file.write("destination_end\n\n")

            file.write("destination_window_begin\n")
            for size, freq in dest_window_size[i].items():
                file.write(str(size) + "\t" + str(freq) + "\n")
            file.write("destination_window_end\n\n")

            file.write("processing_time_begin\n")
            for time, freq in processing_time[i].items():
                file.write(str(time) + "\t" + str(freq) + "\n")
            file.write("processing_time_end\n\n")

            file.write("Inter_arrival_time_begin\n")
            for duration, freq in iat[i].items():
                file.write(str(duration) + "\t" + str(freq) + "\n")
            file.write("Inter_arrival_time_end\n")

            file.write("\nInter_injection_time_begin\n")
            for dest in inter_injection_rate[i].keys():
                file.write("destination" + "\t" + str(dest) + "\n")
                for duration, freq in inter_injection_rate[i][dest].items():
                    file.write(str(duration) + "\t" + str(freq) + "\n")
            file.write("Inter_injection_time_end\n")

            file.write("\nstate_number_begin\n")
            for dest, freq in state_nums[i].items():
                file.write(str(dest) + "\t" + str(freq) + "\n")
            file.write("state_number_end\n")

    """file.write("cycle_transition_begin\n")
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
        file.write("line_transition_end\n\n")"""

