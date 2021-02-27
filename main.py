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


def check_local_or_remote(x):  # 0 for local, 1 for remote
    for i in range(len(chiplet)):
        if int(x[2].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[2].split(": ")[1]) in chiplet[i]["LLC_ID"] or int(
                x[2].split(": ")[1]) == chiplet[i]["port"]:
            if int(x[3].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[3].split(": ")[1]) in chiplet[i][
                "LLC_ID"] or int(x[3].split(": ")[1]) == chiplet[i]["port"]:
                return 0
            return 1


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
        total[i] = temp_dict[i]/tot

    #plt.plot(total.keys(), total.values(), "g*")
    plt.bar(list(temp_dict.keys()), list(temp_dict.values()))
    plt.ylim(0, 200)
    plt.xlabel("Per Packet RTC")
    plt.ylabel("Number of Packets")
    plt.title("Number of Packets for each RTC")
    plt.show()


def bytes_distribution(x):
    tot = 0
    temp_dict = {}
    for i in x.keys():
        if abs(int(x[i][0][2].split(": ")[1]) - int(x[i][0][3].split(": ")[1])) > 1: # two hop
            continue
        else: # one hop
            continue


def dominant_factor(x):
    out = {}
    for i in x.keys():
        base = int(x[i][0][5].split(": ")[1])
        for j in range(len(x[i])):
            if x[i][j][0] == "IN_ICNT_TO_MEM":
                out.setdefault("injection_buffer", []).append(0)

            elif x[i][j][0] == "icnt_pop_llc_push":
                out.setdefault("LLC_boundary_buffer",[]).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "IN_PARTITION_ROP_DELAY":
                out.setdefault("ROP push",[]).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "IN_PARTITION_ICNT_TO_L2_QUEUE":
                out.setdefault("ICNT_2_L2 push",[]).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "m_icnt_L2_queue-":
                out.setdefault("cache hit/miss",[]).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "IN_PARTITION_L2_TO_DRAM_QUEUE":
                out.setdefault("L2_TO_DRAM (cache miss)",[]).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "L2_dram_queue_top()":
                out.setdefault("push to mem_latency Q",[]).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "m_dram_latency_queue()":
                out.setdefault("DRAM access", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "m_dram_r->r_return_queue_top":
                out.setdefault("DRAM to LLC push", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "fL2_TO_ICNT_QUEUE":
                out.setdefault("L2_TO_ICNT", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "inter_icnt_pop_sm_push":
                out.setdefault("sm_push", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "'forward_waiting_push":
                out.setdefault("forward_waiting_push", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])

            elif x[i][j][0] == "'forward_waiting_pop":
                out.setdefault("forward_waiting_pop", []).append(int(x[i][j][5].split(": ")[1]) - base)
                base = int(x[i][j][5].split(": ")[1])




if __name__ == '__main__':
    file = open("report.txt", "r")
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

    lined_list.sort(key=lambda x: (int(x[4].split(": ")[1]), int(x[5].split(": ")[1])))
    packet = {}
    cycles = {}
    flag = 0
    for i in range(0, len(lined_list)):
        if check_local_or_remote(lined_list[i]):
            if int(lined_list[i][4].split(": ")[1]) in packet.keys():
                packet.setdefault(int(lined_list[i][4].split(": ")[1]), []).append(lined_list[i])
            else:
                packet.setdefault(int(lined_list[i][4].split(": ")[1]), []).append(lined_list[i])
                flag = 0

    # total_distribution(packet)
    # bytes_distribution(packet)
    dominant_factor(packet)
