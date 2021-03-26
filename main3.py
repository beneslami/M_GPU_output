from statistics import mean

import matplotlib.pyplot as plt
import numpy as np

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
        if int(x[1].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[1].split(": ")[1]) in chiplet[i]["LLC_ID"]:
            if int(x[2].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[2].split(": ")[1]) in chiplet[i]["LLC_ID"]:
                return 0
        return 1


if __name__ == '__main__':
    file = open("icnt2.txt", "r")
    raw_content = ""
    if file.mode == "r":
        raw_content = file.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        #if check_local_or_remote(item):
        lined_list.append(item)

    # print(lined_list[0][0]) function
    # print(lined_list[0][1]) type
    # print(lined_list[0][2]) source
    # print(lined_list[0][3]) destination
    # print(lined_list[0][4]) packet_num
    # print(lined_list[0][5]) cycle
    # print(lined_list[0][6]) size
    # print(lined_list[0][7]) explain

    packet = {}
    one_hop = {}
    two_hop = {}
    llc_boundary = {}
    temp = {}
    for i in range(len(lined_list)):
        if int(lined_list[i][4].split(": ")[1]) in packet.keys():
            packet.setdefault(int(lined_list[i][4].split(": ")[1]), []).append(lined_list[i])
        else:
            packet.setdefault(int(lined_list[i][4].split(": ")[1]), []).append(lined_list[i])
    
"""""
    injection_buffer = {}
    forwarding_buffer = {}
    t1 = t2 = t3 = 0
    for i in packet.keys():
        if int(packet[i][0][3].split(": ")[1]) == 192:
            for j in range(len(packet[i])):
                if "3-forward_waiting_pop" in packet[i][j][0] and int(packet[i][j][2].split(": ")[1]) == 193:
                    t1 = int(packet[i][j][5].split(": ")[1])
                if "4-icnt_pop_llc_push" in packet[i][j][0]:
                    t2 = int(packet[i][j][5].split(": ")[1])
                    temp[int(packet[i][j][4].split(": ")[1])] = (t2 - t1)
                    t2 = t1 = 0
                    break

    for i in temp.keys():
        if temp[i] in forwarding_buffer.keys():
            forwarding_buffer[temp[i]] += 1
        else:
            forwarding_buffer[temp[i]] = 1
    for i in forwarding_buffer.keys():
        forwarding_buffer[i] = forwarding_buffer[i]/len(temp)

    plt.bar(list(forwarding_buffer.keys()), list(forwarding_buffer.values()), color="blue", width=20)
    plt.xlabel("Cycle")
    plt.ylabel("Probability")
    plt.title("The latency distribution between forwarding buffer pop and LLC boundary push")
    plt.show()
    """""
"""""
    for i in packet.keys():
        t1 = t3 = 0
        t2 = t4 = 0
        for j in range(len(packet[i])):
            if "8-forward_waiting_pop" in packet[i][j][0]:
                t1 = int(packet[i][j][5].split(": ")[1])
            if "9-inter_icnt_pop_sm_push" in packet[i][j][0]:
                t3 = int(packet[i][j][5].split(": ")[1])
                temp[int(packet[i][j][4].split(": ")[1])] = t3 - t1
                t1 = t3 = 0


    plt.bar(list(temp.keys()), list(temp.values()), width=20)
    plt.xlabel("packet Number")
    plt.ylabel("Latency in Cycle")
    plt.title("Latency between Forward queue and LLC_boundary queue")
    plt.show()

    
    for i in packet.keys():
        if abs(int(packet[i][0][2].split(": ")[1]) - int(packet[i][0][3].split(": ")[1])) == 1 or abs(int(packet[i][0][2].split(": ")[1]) - int(packet[i][0][3].split(": ")[1])) == 3: # one_hop
            t1 = t2 = t3 = t4 = t5 = 0
            for j in range(len(packet[i])):
                if "1-injection buffer" in packet[i][j][0]:
                    t1 = int(packet[i][j][5].split(": ")[1])
                if "2-icnt_pop_llc_push" in packet[i][j][0]:
                    t2 = int(packet[i][j][5].split(": ")[1])
                if "3-inter_icnt_pop_llc_pop" in packet[i][j][0]:
                    t3 = int(packet[i][j][5].split(": ")[1])
                if "4-L2-to-ICNT" in packet[i][j][0]:
                    t4 = int(packet[i][j][5].split(": ")[1])
                if "5-inter_icnt_pop_sm_push" in packet[i][j][0]:
                    t5 = int(packet[i][j][5].split(": ")[1])

            one_hop.setdefault("SM_2_LLC", []).append(t2 - t1)
            one_hop.setdefault("LLC_push_pop", []).append(t3 - t2)
            one_hop.setdefault("ICNT_2_SM", []).append(t5 - t4)
        else:
            t1 = t2 = t3 = t4 = t5 = t6 = t7 = t8 = t9 = 0
            for j in range(len(packet[i])):
                if "1-injection buffer" in packet[i][j][0]:
                    t1 = int(packet[i][j][5].split(": ")[1])
                if "2-forward_waiting_push" in packet[i][j][0]:
                    t2 = int(packet[i][j][5].split(": ")[1])
                if "3-forward_waiting_pop" in packet[i][j][0]:
                    t3 = int(packet[i][j][5].split(": ")[1])
                if "4-icnt_pop_llc_push" in packet[i][j][0]:
                    t4 = int(packet[i][j][5].split(": ")[1])
                if "5-inter_icnt_pop_llc_pop" in packet[i][j][0]:
                    t5 = int(packet[i][j][5].split(": ")[1])
                if "6-L2-to-ICNT" in packet[i][j][0]:
                    t6 = int(packet[i][j][5].split(": ")[1])
                if "7-forward_waiting_push" in packet[i][j][0]:
                    t7 = int(packet[i][j][5].split(": ")[1])
                if "8-forward_waiting_pop" in packet[i][j][0]:
                    t8 = int(packet[i][j][5].split(": ")[1])
                if "9-inter_icnt_pop_sm_push" in packet[i][j][0]:
                    t9 = int(packet[i][j][5].split(": ")[1])

    err = []
    err.append(np.std(one_hop["SM_2_LLC"]))
    err.append(np.std(one_hop["LLC_push_pop"]))
    err.append(np.std(one_hop["ICNT_2_SM"]))
    one_hop["SM_2_LLC"] = mean(one_hop["SM_2_LLC"])
    one_hop["LLC_push_pop"] = mean(one_hop["LLC_push_pop"])
    one_hop["ICNT_2_SM"] = mean(one_hop["ICNT_2_SM"])
    plt.bar(list(one_hop.keys()), list(one_hop.values()), yerr=err, align='center', ecolor='black', capsize=10)
    plt.xlabel("Interconnect steps")
    plt.ylabel("Mean Cycle Time")
    plt.title("The latency of one-hop traffics with respect to the interconnect steps")
    plt.xticks(rotation=90)
    for i, v in enumerate(one_hop.values()):
        plt.text(i-0.1, v + 10, str("{:.1f}".format(v)), color='blue', fontweight='bold')
    plt.show()
    
    
    two_hop.setdefault("SM_2_FWD_push", []).append(t2 - t1)
    two_hop.setdefault("Forwarding_Q", []).append(t3 - t2)
    two_hop.setdefault("FWD_2_LLC", []).append(t4 - t3)
    two_hop.setdefault("LLC_push_pop", []).append(t5 - t4)
    two_hop.setdefault("ICNT_2_FWD_push", []).append(t7 - t6)
    two_hop.setdefault("Forwarding_Q_2", []).append(t8 - t7)
    two_hop.setdefault("FWD_SM", []).append(t9 - t8)
    err.append(np.std(two_hop["SM_2_FWD_push"]))
    err.append(np.std(two_hop["Forwarding_Q"]))
    err.append(np.std(two_hop["FWD_2_LLC"]))
    err.append(np.std(two_hop["LLC_push_pop"]))
    err.append(np.std(two_hop["ICNT_2_FWD_push"]))
    err.append(np.std(two_hop["Forwarding_Q_2"]))
    err.append(np.std(two_hop["FWD_SM"]))
    two_hop["SM_2_FWD_push"] = mean(two_hop["SM_2_FWD_push"])
    two_hop["Forwarding_Q"] = mean(two_hop["Forwarding_Q"])
    two_hop["FWD_2_LLC"] = mean(two_hop["FWD_2_LLC"])
    two_hop["LLC_push_pop"] = mean(two_hop["LLC_push_pop"])
    two_hop["ICNT_2_FWD_push"] = mean(two_hop["ICNT_2_FWD_push"])
    two_hop["Forwarding_Q_2"] = mean(two_hop["Forwarding_Q_2"])
    two_hop["FWD_SM"] = mean(two_hop["FWD_SM"])
    plt.bar(list(two_hop.keys()), list(two_hop.values()), yerr=err, align='center', ecolor='black', capsize=10)
    plt.xlabel("Interconnect steps")
    plt.ylabel("Mean Cycle Time")
    plt.title("The latency of two-hop traffics with respect to the interconnect steps")
    plt.xticks(rotation=90)
    for i, v in enumerate(two_hop.values()):
        plt.text(i-0.1, v + 10, str("{:.1f}".format(v)), color='blue', fontweight='bold')
    plt.show()
    """""
"""""
    p_8 = {}
    p_16 = {}
    p_32 = {}
    for i in packet.keys():
        if 186944 <= int(packet[i][0][3].split(": ")[1]) <= 243604:
            if len(packet[i]) == 8:
                base = int(packet[i][0][5].split(": ")[1])
                for j in range(len(packet[i])):
                    p_8.setdefault(packet[i][j][0], []).append(int(packet[i][j][5].split(": ")[1]) - base)
                    base = int(packet[i][j][5].split(": ")[1])
            if len(packet[i]) == 16:
                base = int(packet[i][0][5].split(": ")[1])
                for j in range(len(packet[i])):
                    if int(packet[i][j][4].split(": ")[1]) == 0:
                        p_16.setdefault(packet[i][j][0] + "_request", []).append(int(packet[i][j][5].split(": ")[1]) - base)
                        base = int(packet[i][j][5].split(": ")[1])
                    elif int(packet[i][j][4].split(": ")[1]) == 2:
                        p_16.setdefault(packet[i][j][0] + "_respond", []).append(int(packet[i][j][5].split(": ")[1]) - base)
                        base = int(packet[i][j][5].split(": ")[1])
            if len(packet[i]) == 32:
                base = int(packet[i][0][5].split(": ")[1])
                for j in range(len(packet[i])):
                    if int(packet[i][j][4].split(": ")[1]) == 0:
                        p_32.setdefault(packet[i][j][0] + "_request", []).append(int(packet[i][j][5].split(": ")[1]) - base)
                        base = int(packet[i][j][5].split(": ")[1])
                    elif int(packet[i][j][4].split(": ")[1]) == 2:
                        p_32.setdefault(packet[i][j][0] + "_respond", []).append(int(packet[i][j][5].split(": ")[1]) - base)
                        base = int(packet[i][j][5].split(": ")[1])

    p_32_plot = {}
    for i in p_32.keys():
        p_32_plot[i] = mean(p_16[i])
    plt.bar(list(p_32_plot.keys()), list(p_32_plot.values()))
    plt.xlabel("Interconnect queue")
    plt.ylabel("Relative Mean Cycle Time")
    plt.title("The latency of two-hop traffics with respect to the interconnect steps")
    plt.xticks(rotation=90)
    for i, v in enumerate(p_32_plot.values()):
        plt.text(i-0.2, v, str("{:.1f}".format(v)), color='blue', fontweight='bold')
    plt.show()
    """""