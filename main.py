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

total = {}
byte = {}


def hop_rate(x):
    one_hop = 0
    two_hop = 0
    for i in packet.keys():
        for j in range(len(packet[i])):
            if int(packet[i][j][1].split(": ")[1]) == 0:
                if int(packet[i][j][2].split(": ")[1]) != 0 and int(packet[i][j][3].split(": ")[1]) != 0:
                    if abs(int(packet[i][j][2].split(": ")[1]) - int(packet[i][j][3].split(": ")[1])) > 1:
                        two_hop += 1
                        break
                    elif abs(int(packet[i][j][2].split(": ")[1]) - int(packet[i][j][3].split(": ")[1])) == 1:
                        one_hop += 1
                        break
                else:
                    continue
    # print(one_hop)
    # print(two_hop)


def check_local_or_remote(x):  # 0 for local, 1 for remote
    for i in range(len(chiplet)):
        if int(x[2].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[2].split(": ")[1]) in chiplet[i]["LLC_ID"] or int(
                x[2].split(": ")[1]) == chiplet[i]["port"]:
            if int(x[3].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[3].split(": ")[1]) in chiplet[i]["LLC_ID"] or int(x[3].split(": ")[1]) == chiplet[i]["port"]:
                return 0
            return 1


def total_distribution(x):
    start = end = 0
    temp_dict = {}
    tot = 0
    for i in x.keys():
        for j in range(len(x[i])):
            if "(injection port buffer)" in x[i][j][7]:
                start = int(x[i][j][5].split(": ")[1])
                continue
            elif "reply is pushed to SM boundary Q in chiplet" in x[i][j][7]:
                end = int(x[i][j][5].split(": ")[1])
                if (end - start) in temp_dict.keys():
                    temp_dict[end - start] += 1
                else:
                    temp_dict[end - start] = 1
                    break
            else:
                continue
        tot += 1

    for i in temp_dict.keys():
        total[i] = temp_dict[i] / tot

    # plt.plot(total.keys(), total.values(), "g*")
    plt.bar(list(temp_dict.keys()), list(temp_dict.values()))
    plt.ylim(0, 200)
    plt.xlabel("Per Packet RTC")
    plt.ylabel("Number of Packets")
    plt.title("Number of Packets for each RTC")
    plt.show()


def bytes_distribution(x):
    cycle_byte = {}
    cycle_req = {}
    cycle_resp = {}
    prob = {}
    total = 0
    for i in range(len(x)):
        if x[i][0] == "IN_ICNT_TO_MEM" or x[i][0] == "icnt_pop_llc_push" or x[i][0] == "inter_icnt_pop_llc_pop" or x[i][
            0] == "inter_icnt_pop_sm_push" or x[i][0] == "forward_waiting_push" or x[i][0] == "forward_waiting_pop":
            if int(lined_list[i][5].split(": ")[1]) in cycle_byte.keys():
                cycle_byte[int(lined_list[i][5].split(":")[1])] += int(lined_list[i][6].split(":")[1])
            else:
                cycle_byte[int(lined_list[i][5].split(":")[1])] = int(lined_list[i][6].split(":")[1])

            if int(lined_list[i][1].split(": ")[1]) == 0:
                if int(lined_list[i][5].split(": ")[1]) in cycle_req.keys():
                    cycle_req[int(lined_list[i][5].split(":")[1])] += int(lined_list[i][6].split(":")[1])
                else:
                    cycle_req[int(lined_list[i][5].split(":")[1])] = int(lined_list[i][6].split(":")[1])
            elif int(lined_list[i][1].split(": ")[1]) == 2:
                if int(lined_list[i][5].split(": ")[1]) in cycle_resp.keys():
                    cycle_resp[int(lined_list[i][5].split(":")[1])] += int(lined_list[i][6].split(":")[1])
                else:
                    cycle_resp[int(lined_list[i][5].split(":")[1])] = int(lined_list[i][6].split(":")[1])

            if int(lined_list[i][5].split(": ")[1]) in prob.keys():
                prob[int(lined_list[i][5].split(": ")[1])] += 1
            else:
                prob[int(lined_list[i][5].split(": ")[1])] = 1
            total += 1

    sum = 0
    for i in prob.keys():
        prob[i] = prob[i] / total
        sum += prob[i]
    print(sum)
    plt.plot(prob.keys(), prob.values(), "r*")
    plt.xlabel("cycle")
    plt.ylabel("Probability")
    plt.title("The distribution of the number of packets")
    # plt.bar(list(cycle_byte.keys()), list(cycle_byte.values()), label="total")
    # plt.bar(list(cycle_req.keys()), list(cycle_req.values()), label="request")
    # plt.bar(list(cycle_resp.keys()), list(cycle_resp.values()), label="response")
    # plt.xlabel("cycle")
    # plt.ylabel("total bytes")
    # plt.title("Bytes Per Cycle in the interconnect")
    # plt.legend(loc="best")
    plt.show()


def dominant_factor(x):
    out = {}
    temp = {}
    temp2 = 0
    for i in x.keys():
        base = int(x[i][0][5].split(": ")[1])
        if int(x[i][0][4].split(": ")[1]) == 249324:
            temp2 = int(x[i][0][5].split(": ")[1])

        for j in range(len(x[i])):
            if x[i][j][0] == "IN_ICNT_TO_MEM":
                out.setdefault("injection_buffer", []).append(0)
                if int(x[i][0][4].split(": ")[1]) == 258983:
                    temp["injection_buffer"] = 0

            elif x[i][j][0] == "icnt_pop_llc_push":
                out.setdefault("LLC_boundary_buffer", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])
                if int(x[i][0][4].split(": ")[1]) == 258983:
                    temp["LLC_boundary_buffer"] = int(x[i][j][5].split(": ")[1]) - temp2
                    temp2 = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "IN_PARTITION_ROP_DELAY":
                out.setdefault("ROP push", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])
                if int(x[i][0][4].split(": ")[1]) == 258983:
                    temp["ROP push"] = int(x[i][j][5].split(": ")[1]) - temp2
                    temp2 = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "IN_PARTITION_ICNT_TO_L2_QUEUE":
                out.setdefault("ICNT_2_L2 push", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])
                if int(x[i][0][4].split(": ")[1]) == 258983:
                    temp["ICNT_2_L2 push"] = int(x[i][j][5].split(": ")[1]) - temp2
                    temp2 = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "m_icnt_L2_queue-":
                out.setdefault("cache hit/miss", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])
                if int(x[i][0][4].split(": ")[1]) == 258983:
                    temp["cache hit/miss"] = int(x[i][j][5].split(": ")[1]) - temp2
                    temp2 = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "IN_PARTITION_L2_TO_DRAM_QUEUE":
                out.setdefault("L2_TO_DRAM (cache miss)", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])
                if int(x[i][0][4].split(": ")[1]) == 258983:
                    temp["L2_TO_DRAM (cache miss)"] = int(x[i][j][5].split(": ")[1]) - temp2
                    temp2 = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "L2_dram_queue_top()":
                out.setdefault("push to mem_latency Q", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])
                if int(x[i][0][4].split(": ")[1]) == 258983:
                    temp["push to mem_latency Q"] = int(x[i][j][5].split(": ")[1]) - temp2
                    temp2 = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "m_dram_latency_queue()":
                out.setdefault("DRAM_access", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])
                if int(x[i][0][4].split(": ")[1]) == 258983:
                    temp["DRAM_access"] = int(x[i][j][5].split(": ")[1]) - temp2
                    temp2 = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "m_dram_r->r_return_queue_top":
                out.setdefault("DRAM to LLC push", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])
                if int(x[i][0][4].split(": ")[1]) == 258983:
                    temp["DRAM to LLC push"] = int(x[i][j][5].split(": ")[1]) - temp2
                    temp2 = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "fL2_TO_ICNT_QUEUE":
                out.setdefault("L2_TO_ICNT", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])
                if int(x[i][0][4].split(": ")[1]) == 258983:
                    temp["L2_TO_ICNT"] = int(x[i][j][5].split(": ")[1]) - temp2
                    temp2 = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "inter_icnt_pop_sm_push":
                out.setdefault("sm_push", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])
                if int(x[i][0][4].split(": ")[1]) == 258983:
                    temp["sm_push"] = int(x[i][j][5].split(": ")[1]) - temp2
                    temp2 = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "forward_waiting_push":
                out.setdefault("forward_waiting_push", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])
                if int(x[i][0][4].split(": ")[1]) == 258983:
                    temp["forward_waiting_push"] = int(x[i][j][5].split(": ")[1]) - temp2
                    temp2 = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "forward_waiting_pop":
                out.setdefault("forward_waiting_pop", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])
                if int(x[i][0][4].split(": ")[1]) == 258983:
                    temp["forward_waiting_pop"] = int(x[i][j][5].split(": ")[1]) - temp2
                    temp2 = int(x[i][j][5].split(": ")[1])

    items = ["injection_buffer", "ROP push", "ICNT_2_L2 push", "cache hit/miss", "L2_TO_DRAM (cache miss)",
             "push to mem_latency Q", "DRAM to LLC push", "L2_TO_ICNT", "sm_push", "forward_waiting_push",
             "forward_waiting_pop"]

    # z = []
    # for i in range(len(items)):
    #   z.append(mean(out[items[i]]))
    #    print(z)
    # plt.bar(list(items), list(z))
    plt.plot(list(temp.keys()), list(temp.values()), "rs-")
    plt.title("Dominant Factor")
    plt.ylabel("Cycles")
    plt.xticks(rotation=90)
    plt.show()


def interconnect_latency(x):
    latency_packets = {}
    chiplet3 = chiplet2 = chiplet1 = 0
    chiplet33 = chiplet22 = chiplet11 = 0
    chiplet3_latency = {}
    chiplet2_latency = {}
    chiplet1_latency = {}
    chiplet33_latency = {}
    chiplet22_latency = {}
    chiplet11_latency = {}
    for i in x.keys():
        src = dst = 0
        if 186944 < i < 243604:
            if int(x[i][0][2].split(": ")[1]) == 195 and int(x[i][0][3].split(": ")[1]) == 192:
                chiplet3 += 1
                for j in range(len(x[i])):
                    if x[i][j][0] == "IN_ICNT_TO_MEM":
                        src = int(x[i][j][5].split(": ")[1])
                        continue
                    if x[i][j][0] == "icnt_pop_llc_push":
                        dst = int(x[i][j][5].split(": ")[1])
                        break
                if (dst-src) in chiplet3_latency.keys():
                    chiplet3_latency[dst-src] += 1
                else:
                    chiplet3_latency[dst-src] = 1
            elif int(x[i][0][2].split(": ")[1]) == 194 and int(x[i][0][3].split(": ")[1]) == 192:
                chiplet2 += 1
                for j in range(len(x[i])):
                    if x[i][j][0] == "forward_waiting_pop":
                        src = int(x[i][j][5].split(": ")[1])
                        continue
                    if x[i][j][0] == "icnt_pop_llc_push":
                        dst = int(x[i][j][5].split(": ")[1])
                        break
                if (dst-src) in chiplet2_latency.keys():
                    chiplet2_latency[dst-src] += 1
                else:
                    chiplet2_latency[dst-src] = 1
            elif int(x[i][0][2].split(": ")[1]) == 193 and int(x[i][0][3].split(": ")[1]) == 192:
                chiplet1 += 1
                for j in range(len(x[i])):
                    if x[i][j][0] == "IN_ICNT_TO_MEM":
                        src = int(x[i][j][5].split(": ")[1])
                        continue
                    if x[i][j][0] == "icnt_pop_llc_push":
                        dst = int(x[i][j][5].split(": ")[1])
                        break
                if (dst - src) in chiplet1_latency.keys():
                    chiplet1_latency[dst - src] += 1
                else:
                    chiplet1_latency[dst - src] = 1
        else:
            if int(x[i][0][2].split(": ")[1]) == 195 and int(x[i][0][3].split(": ")[1]) == 192:
                chiplet33 += 1
                for j in range(len(x[i])):
                    if x[i][j][0] == "IN_ICNT_TO_MEM":
                        src = int(x[i][j][5].split(": ")[1])
                        continue
                    if x[i][j][0] == "icnt_pop_llc_push":
                        dst = int(x[i][j][5].split(": ")[1])
                        break
                if (dst-src) in chiplet33_latency.keys():
                    chiplet33_latency[dst-src] += 1
                else:
                    chiplet33_latency[dst-src] = 1
            elif int(x[i][0][2].split(": ")[1]) == 194 and int(x[i][0][3].split(": ")[1]) == 192:
                chiplet22 += 1
                for j in range(len(x[i])):
                    if x[i][j][0] == "forward_waiting_pop":
                        src = int(x[i][j][5].split(": ")[1])
                        continue
                    if x[i][j][0] == "icnt_pop_llc_push":
                        dst = int(x[i][j][5].split(": ")[1])
                        break
                if (dst-src) in chiplet22_latency.keys():
                    chiplet22_latency[dst-src] += 1
                else:
                    chiplet22_latency[dst-src] = 1
            elif int(x[i][0][2].split(": ")[1]) == 193 and int(x[i][0][3].split(": ")[1]) == 192:
                chiplet11 += 1
                for j in range(len(x[i])):
                    if x[i][j][0] == "IN_ICNT_TO_MEM":
                        src = int(x[i][j][5].split(": ")[1])
                        continue
                    if x[i][j][0] == "icnt_pop_llc_push":
                        dst = int(x[i][j][5].split(": ")[1])
                        break
                if (dst - src) in chiplet11_latency.keys():
                    chiplet11_latency[dst - src] += 1
                else:
                    chiplet11_latency[dst - src] = 1
    print(chiplet3) #6649
    print(chiplet2) #25
    print(chiplet1) #6488
    print("------")
    print(chiplet33) #1442
    print(chiplet22) #7824
    print(chiplet11) #1592
    print("------")
    print(chiplet3 + chiplet2 + chiplet1 + chiplet11 + chiplet33 + chiplet22)# 24020

    plt.plot(chiplet33_latency.keys(), chiplet33_latency.values(), "rs-", label="chiplet3_to_0")
    plt.plot(chiplet22_latency.keys(), chiplet22_latency.values(), "g*-", label="chiplet2_to_0")
    plt.plot(chiplet11_latency.keys(), chiplet11_latency.values(), "b^-", label="chiplet1_to_0")
    plt.legend(loc="best")
    plt.xlabel("Packet RTC Latency")
    plt.ylabel("Frequency")
    plt.title("")
    plt.show()


if __name__ == '__main__':
    file = open("report_syrk.txt", "r")
    raw_content = ""
    if file.mode == "r":
        raw_content = file.readlines()
    lined_content = []
    lined_list = []
    for line in raw_content:
        lined_content.append(line)
    for i in lined_content:
        item = [x for x in i.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    # print(lined_list[0][0])                 # command
    # print(lined_list[0][1].split(":")[1])   # packet type
    # print(lined_list[0][2].split(":")[1])   # source
    # print(lined_list[0][3].split(":")[1])   # destination
    # print(lined_list[0][4].split(":")[1])   # packet number
    # print(lined_list[0][5].split(":")[1])   # cycle
    # print(lined_list[0][6].split(":")[1])   # size
    # print(lined_list[0][7].split(":")[1])   # explain

    packet = {}
    cycles = {}
    for i in range(len(lined_list)):
        if check_local_or_remote(lined_list[i]):
            if int(lined_list[i][4].split(": ")[1]) in packet.keys():
                packet.setdefault(int(lined_list[i][4].split(": ")[1]), []).append(lined_list[i])
            else:
                packet.setdefault(int(lined_list[i][4].split(": ")[1]), []).append(lined_list[i])

    for i in range(len(packet[248577])):
        print(packet[248577][i])
        print("\n")
    # total_distribution(packet)
    # bytes_distribution(lined_list)
    # dominant_factor(packet)
    # interconnect_latency(packet)