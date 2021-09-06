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


if __name__ == "__main__":
    file2 = open("report_syrk.txt", "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    p = {}
    packet = {}

    for i in range(len(lined_list)):  # cycle based classification
        if lined_list[i][0] != "Instruction cache miss":
            if chip_select(int(lined_list[i][1].split(": ")[1])) != chip_select(int(lined_list[i][2].split(": ")[1])):
                if int(lined_list[i][5].split(": ")[1]) in p.keys():
                    if lined_list[i] not in p[int(lined_list[i][5].split(": ")[1])]:
                        p.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])
                else:
                    p.setdefault(int(lined_list[i][5].split(": ")[1]), []).append(lined_list[i])
                    
    for i in range(len(lined_list)):  # packet based classification
        if lined_list[i][0] != "Instruction cache miss":
            if check_local_or_remote(lined_list[i]):
                if int(lined_list[i][3].split(": ")[1]) in packet.keys():
                    packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
                else:
                    packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
                    
    overall = {}
    for i in p.keys():
        for j in range(len(p[i])):
            if p[i][j][0] == "injection buffer" and int(p[i][j][1].split(": ")[1]) == 192 and int(p[i][j][2].split(": ")[1]) == 193:
                if int(p[i][j][5].split(": ")[1]) in overall.keys():
                    overall.setdefault(int(p[i][j][5].split(": ")[1]), []).append(int(p[i][j][7].split(": ")[1]))
                else:
                    overall.setdefault(int(p[i][j][5].split(": ")[1]), []).append(int(p[i][j][7].split(": ")[1]))

    overall_update = {}
    flag = 0
    prev = 0
    for i in overall.keys():
        if i > 0:
            if flag == 0:
                overall_update[i] = overall[i]
                prev = i
                flag = 1
            elif flag == 1:
                if i - prev > 1:
                    for j in range(i - prev):
                        overall_update[prev + j + 1] = 0
                overall_update[i] = overall[i]
                prev = i
    flag = 0
    start = end = 0
    zero_sujornTime = []
    _8_byte = 0
    win_8 = []
    win_136 = []
    window_8 = {1: [], 2: [], 3: [], 4: [], 5: []}
    window_136 = {1: [], 2: [], 3: [], 4: [], 5: []}
    _136_byte = 0
    for k, v in overall_update.items():
        if v == 0 and flag == 0:
            start = k
            flag = 1
        elif v != 0 and flag == 1:
            end = k
            zero_sujornTime.append(end - start)  # write this list as zero sojourn time
            flag = 0
            if v[0] == 8:
                _8_byte += 1
                if len(v) > 1:
                    for i in range(1, len(v)):
                        window_8[i].append(v[i])
                win_8.append(len(v))

            elif v[0] == 136:
                _136_byte += 1
                if len(v) > 1:
                    for i in range(1, len(v)):
                        window_136[i].append(v[i])
                win_136.append(len(v))

    print("number of transition from zero to 8: " + str(_8_byte)) # write this list as transition to state 8 from 0
    print("---------")
    print("number of transition from zero to 136: " + str(_136_byte)) # write this list as transition to state 136 from 0
    print("---------")
    window_elment_8 = {}
    window_elment_136 = {}
    for i in win_8:
        if i in window_elment_8.keys():
            window_elment_8[i] += 1
        else:
            window_elment_8[i] = 1
    for i in win_136:
        if i in window_elment_136.keys():
            window_elment_136[i] += 1
        else:
            window_elment_136[i] = 1
    print("window of the number of packets for state 8: " + str(window_elment_8)) # write this list as window for state 8
    print("---------")
    print("window of the number of packets for state 136: " + str(window_elment_136)) # write this list as window for state 136
    print("---------")
    window_8_size2 = {}
    for i in range(len(window_8[1])):
        if window_8[1][i] in window_8_size2.keys():
            window_8_size2[window_8[1][i]] += 1
        else:
            window_8_size2[window_8[1][i]] = 1

    window_8_size3 = {}
    for i in range(len(window_8[2])):
        if window_8[2][i] in window_8_size3.keys():
            window_8_size3[window_8[2][i]] += 1
        else:
            window_8_size3[window_8[2][i]] = 1

    window_8_size4 = {}
    for i in range(len(window_8[3])):
        if window_8[3][i] in window_8_size4.keys():
            window_8_size4[window_8[3][i]] += 1
        else:
            window_8_size4[window_8[3][i]] = 1

    window_8_size5 = {}
    for i in range(len(window_8[4])):
        if window_8[4][i] in window_8_size5.keys():
            window_8_size5[window_8[4][i]] += 1
        else:
            window_8_size5[window_8[4][i]] = 1

    print("distribution of packet bytes in each location of the window2: " + str(window_8_size2)) # write this list as window for state 8
    print("distribution of packet bytes in each location of the window3: " + str(window_8_size3))
    print("distribution of packet bytes in each location of the window4: " + str(window_8_size4))
    print("distribution of packet bytes in each location of the window5: " + str(window_8_size5))
    print("---------")
    window_136_size2 = {}
    for i in range(len(window_136[1])):
        if window_136[1][i] in window_136_size2.keys():
            window_136_size2[window_136[1][i]] += 1
        else:
            window_136_size2[window_136[1][i]] = 1

    window_136_size3 = {}
    for i in range(len(window_136[2])):
        if window_136[2][i] in window_136_size3.keys():
            window_136_size3[window_136[2][i]] += 1
        else:
            window_136_size3[window_136[2][i]] = 1

    window_136_size4 = {}
    for i in range(len(window_136[3])):
        if window_136[3][i] in window_136_size4.keys():
            window_136_size4[window_136[3][i]] += 1
        else:
            window_136_size4[window_136[3][i]] = 1

    window_136_size5 = {}
    for i in range(len(window_136[4])):
        if window_136[4][i] in window_136_size5.keys():
            window_136_size5[window_136[4][i]] += 1
        else:
            window_136_size5[window_136[4][i]] = 1
    print("distribution of packet bytes in each location of the window2: " + str(window_136_size2)) # write this list as window for state 136
    print("distribution of packet bytes in each location of the window3: " + str(window_136_size3))
    print("distribution of packet bytes in each location of the window4: " + str(window_136_size4))
    print("distribution of packet bytes in each location of the window5: " + str(window_136_size5))
    print("---------")
    s8_sojournTime = []
    s136_sojournTime = []
    s8_to_s136 = 0
    s8_to_s0 = 0
    s136_to_s0 = 0
    s136_to_s8 = 0
    start = end = flag = 0
    for k, v in overall_update.items():
        if not isinstance(v, int):
            if v[0] == 8 and flag == 0:
                start = k
                flag = 1
            elif v[0] == 8 and flag == 1:
                continue
            elif v[0] != 8 and flag == 1:
                end = k
                flag = 0
                s8_sojournTime.append(end - start)
                if v[0] == 136:
                    s8_to_s136 += 1
                end = start = 0
        elif v == 0:
            if flag == 1:
                end = k
                s8_sojournTime.append(end - start)
                s8_to_s0 += 1
                end = start = flag = 0

    flag = 0
    start = end = 0
    for k, v in overall_update.items():
        if not isinstance(v, int):
            if v[0] == 136 and flag == 0:
                start = k
                flag = 1
            elif v[0] == 136 and flag == 1:
                continue
            elif v[0] != 136 and flag == 1:
                end = k
                flag = 0
                s136_sojournTime.append(end - start)
                if v[0] == 8:
                    s136_to_s8 += 1
                end = start = 0
        elif v == 0:
            if flag == 1:
                end = k
                s136_sojournTime.append(end - start)
                s136_to_s0 += 1
                end = start = flag = 0

    print("s136 to s0: " + str(s136_to_s0))
    print("s136 to s8: " + str(s136_to_s8))
    print("s8 to s0: " + str(s8_to_s0))
    print("s8 to s 136: " + str(s8_to_s136))
    print("s136 sojourn time: " + str(s136_sojournTime))
    print("s8 sojourn time: " + str(s8_sojournTime))
    zero_sujornTime_dist = {}
    for i in zero_sujornTime:
        if i in zero_sujornTime_dist.keys():
            zero_sujornTime_dist[i] += 1
        else:
            zero_sujornTime_dist[i] = 1
    zero_sujornTime_dist = sorted(zero_sujornTime_dist.items(), key=lambda x: x[0])

    eight_sojournTime_dist = {}
    for i in s8_sojournTime:
        if i in eight_sojournTime_dist.keys():
            eight_sojournTime_dist[i] += 1
        else:
            eight_sojournTime_dist[i] = 1
    eight_sojournTime_dist = sorted(eight_sojournTime_dist.items(), key=lambda x: x[0])
    onethirtysix_sojournTime_dist = {}
    for i in s136_sojournTime:
        if i in onethirtysix_sojournTime_dist.keys():
            onethirtysix_sojournTime_dist[i] += 1
        else:
            onethirtysix_sojournTime_dist[i] = 1
    onethirtysix_sojournTime_dist = sorted(onethirtysix_sojournTime_dist.items(), key=lambda x: x[0])

    one_hop_cycle = {}
    one_hop_cycle_list = []
    forwarding_cycle = {}
    processing_cycle = {}
    processing_cycle_list = []

    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "injection buffer":
                for k in range(j + 1, len(packet[i])):
                    if packet[i][k][0] == "rop push" or packet[i][k][0] == "forward waiting pop":
                        if int(packet[i][k][1].split(": ")[1]) == int(packet[i][j][1].split(": ")[1]):
                            duration = int(packet[i][k][5].split(": ")[1]) - int(packet[i][j][5].split(": ")[1])
                            if duration in one_hop_cycle.keys():
                                one_hop_cycle[duration] += 1
                            else:
                                one_hop_cycle[duration] = 1
                            one_hop_cycle_list.append(duration)
                        break

            elif packet[i][j][0] == "rop push":
                for k in range(j + 1, len(packet[i])):
                    if packet[i][k][0] == "L2_icnt_pop":
                        if int(packet[i][k][6].split(": ")[1]) == int(packet[i][j][6].split(": ")[1]):
                            duration = int(packet[i][k][5].split(": ")[1]) - int(packet[i][j][5].split(": ")[1])
                            if duration in processing_cycle.keys():
                                processing_cycle[duration] += 1
                            else:
                                processing_cycle[duration] = 1
                            processing_cycle_list.append(duration)
                        break

    with open("syrk.model", "w") as file:
        file.write("zero_state_sojourntime_begin\n")
        for i in range(len(zero_sujornTime_dist)):
            file.write(str(zero_sujornTime_dist[i][0]) + " " + str(zero_sujornTime_dist[i][1]) + "\n")
        file.write("zero_state_sojourntime_end\n\n")

        file.write("eight_state_sojourntime_begin\n")
        for i in range(len(eight_sojournTime_dist)):
            file.write(str(eight_sojournTime_dist[i][0]) + " " + str(eight_sojournTime_dist[i][1]) + "\n")
        file.write("eight_state_sojourntime_end\n\n")

        file.write("onethirtysix_state_sojourntime_begin\n")
        for i in range(len(onethirtysix_sojournTime_dist)):
            file.write(str(onethirtysix_sojournTime_dist[i][0]) + " " + str(onethirtysix_sojournTime_dist[i][1]) + "\n")
        file.write("onethirtysix_state_sojourntime_end\n\n")

        file.write("s0_to_s8: " + str(_8_byte/(_8_byte + _136_byte)) + "\n")
        file.write("s0_to_s136: " + str(_136_byte/(_8_byte + _136_byte)) + "\n")
        file.write("s8_to_s0: " + str(s8_to_s0/(s8_to_s0 + s8_to_s136)) + "\n")
        file.write("s8_to_s136: " + str(s8_to_s136/(s8_to_s0 + s8_to_s136)) + "\n")
        file.write("s136_to_s0: " + str(s136_to_s0/(s136_to_s0 + s136_to_s8)) + "\n")
        file.write("s136_to_s8: " + str(s136_to_s8/(s136_to_s0 + s136_to_s8)) + "\n\n")

        file.write("state_8_window_size_begin\n")
        for k, v in window_elment_8.items():
            file.write(str(k) + " " + str(v) + "\n")
        file.write("state_8_window_size_end\n\n")

        file.write("state_136_window_size_begin\n")
        for k, v in window_elment_136.items():
            file.write(str(k) + " " + str(v) + "\n")
        file.write("state_136_window_size_end\n\n")

        file.write("state_8_window_size2_packet_begin\n")
        for k, v in window_8_size2.items():
           file.write(str(k) + " " + str(v) + "\n")
        file.write("state_8_window_size2_packet_end\n\n")

        file.write("state_8_window_size3_packet_begin\n")
        for k, v in window_8_size3.items():
            file.write(str(k) + " " + str(v) + "\n")
        file.write("state_8_window_size3_packet_end\n\n")

        file.write("state_8_window_size4_packet_begin\n")
        for k, v in window_8_size4.items():
            file.write(str(k) + " " + str(v) + "\n")
        file.write("state_8_window_size4_packet_end\n\n")

        file.write("state_8_window_size5_packet_begin\n")
        for k, v in window_8_size5.items():
            file.write(str(k) + " " + str(v) + "\n")
        file.write("state_8_window_size5_packet_end\n\n")

        file.write("state_136_window_size2_packet_begin\n")
        for k, v in window_136_size2.items():
            file.write(str(k) + " " + str(v) + "\n")
        file.write("state_136_window_size2_packet_end\n\n")

        file.write("state_136_window_size3_packet_begin\n")
        for k, v in window_136_size3.items():
            file.write(str(k) + " " + str(v) + "\n")
        file.write("state_136_window_size3_packet_end\n\n")

        file.write("state_136_window_size4_packet_begin\n")
        for k, v in window_136_size4.items():
            file.write(str(k) + " " + str(v) + "\n")
        file.write("state_136_window_size4_packet_end\n\n")

        file.write("state_136_window_size5_packet_begin\n")
        for k, v in window_136_size5.items():
            file.write(str(k) + " " + str(v) + "\n")
        file.write("state_136_window_size5_packet_end\n\n")

        file.write("one_hop_delay_begin\n")
        for k, v in one_hop_cycle.items():
            file.write(str(k) + " " + str(v) + "\n")
        file.write("one_hop_delay_end\n\n")

        file.write("forwarding_delay_begin\n")
        for k, v in forwarding_cycle.items():
            file.write(str(k) + " " + str(v) + "\n")
        file.write("forwarding_delay_end\n\n")

        file.write("processing_delay_begin\n")
        for k, v in processing_cycle.items():
            file.write(str(k) + " " + str(v) + "\n")
        file.write("processing_delay_end\n\n")