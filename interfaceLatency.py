import matplotlib.pyplot as plt

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


if __name__ == '__main__':
    file2 = open("report_syrk.txt", "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    packet = {}
    for i in range(len(lined_list)):
        if lined_list[i][0] == "Instruction cache miss":
            if int(lined_list[i][1].split(": ")[1]) in packet.keys():
                packet.setdefault(int(lined_list[i][1].split(": ")[1]), []).append(lined_list[i])
            else:
                packet.setdefault(int(lined_list[i][1].split(": ")[1]), []).append(lined_list[i])
        else:
            if int(lined_list[i][3].split(": ")[1]) in packet.keys():
                packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
            else:
                packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])

    core = {0: {}, 1: {}, 2: {}, 3: {}}
    injection_buffer = {0: {}, 1: {}, 2: {}, 3: {}}
    l2_icnt_buffer = {0: {}, 1: {}, 2: {}, 3: {}}
    inter_icnt_buffer = {0: {}, 1: {}, 2: {}, 3: {}}
    inter_icnt_buffer_len = {0: {}, 1: {}, 2: {}, 3: {}}
    forward_waiting_buffer = {0: {}, 1: {}, 2: {}, 3: {}}
    start_inter_icnt = start_forward_waiting = 0
    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "injection buffer":
                if int(packet[i][j][5].split(": ")[1]) not in core[chip_select(int(packet[i][j][1].split(": ")[1]))].keys():
                    core[chip_select(int(packet[i][j][1].split(": ")[1]))][int(packet[i][j][5].split(": ")[1])] = int(packet[i][j][7].split(": ")[1])
                else:
                    core[chip_select(int(packet[i][j][1].split(": ")[1]))][int(packet[i][j][5].split(": ")[1])] += int(packet[i][j][7].split(": ")[1])
            elif packet[i][j][0] == "L2_icnt_pop":
                if int(packet[i][j][5].split(": ")[1]) not in core[chip_select(int(packet[i][j][1].split(": ")[1]))].keys():
                    core[chip_select(int(packet[i][j][1].split(": ")[1]))][int(packet[i][j][5].split(": ")[1])] = int(packet[i][j][7].split(":")[1])
                else:
                    core[chip_select(int(packet[i][j][1].split(": ")[1]))][int(packet[i][j][5].split(": ")[1])] += int(packet[i][j][7].split(":")[1])

            if packet[i][j][0] == "inter_icnt_pop_llc_push":
                start_inter_icnt = int(packet[i][j][5].split(": ")[1])
                if start_inter_icnt not in inter_icnt_buffer_len[int(packet[i][j][6].split(": ")[1])].keys():
                    inter_icnt_buffer_len[int(packet[i][j][6].split(": ")[1])][start_inter_icnt] = 1
                else:
                    inter_icnt_buffer_len[int(packet[i][j][6].split(": ")[1])][start_inter_icnt] += 1
            elif packet[i][j][0] == "rop push":
                latency = int(packet[i][j][5].split(": ")[1]) - start_inter_icnt
                start_inter_icnt = 0
                if latency not in inter_icnt_buffer[chip_select(int(packet[i][j][1].split(": ")[1]))].keys():
                    inter_icnt_buffer[chip_select(int(packet[i][j][1].split(": ")[1]))][latency] = 1
                else:
                    inter_icnt_buffer[chip_select(int(packet[i][j][1].split(": ")[1]))][latency] += 1
                if int(packet[i][j][5].split(": ")[1]) not in inter_icnt_buffer_len[int(packet[i][j][6].split(": ")[1])].keys():
                    inter_icnt_buffer_len[int(packet[i][j][6].split(": ")[1])][int(packet[i][j][5].split(": ")[1])] = -1
                else:
                    inter_icnt_buffer_len[int(packet[i][j][6].split(": ")[1])][int(packet[i][j][5].split(": ")[1])] -= 1

            if packet[i][j][0] == "forward_waiting_push":
                start_forward_waiting = int(packet[i][j][5].split(": ")[1])
            elif packet[i][j][0] == "forward waiting pop":
                latency = int(packet[i][j][5].split(": ")[1]) - start_forward_waiting
                start_forward_waiting = 0
                if latency not in forward_waiting_buffer[chip_select(int(packet[i][j][1].split(": ")[1]))].keys():
                    forward_waiting_buffer[chip_select(int(packet[i][j][1].split(": ")[1]))][latency] = 1
                else:
                    forward_waiting_buffer[chip_select(int(packet[i][j][1].split(": ")[1]))][latency] += 1

    plt.bar(list(core[3].keys()), list(core[3].values()), width=4)
    plt.show()
    plt.bar(list(inter_icnt_buffer[3].keys()), list(inter_icnt_buffer[3].values()))
    plt.show()
    plt.bar(list(inter_icnt_buffer_len[3].keys()), list(inter_icnt_buffer_len[3].values()))
    plt.show()