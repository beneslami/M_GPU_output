from statistics import mean, stdev
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

injection_q = {}
icnt_to_mem_q = {}
forward_waiting_q = {}
icnt_pop_llc_q = {}
rop_q = {}
icnt_to_l2_q = {}
l2_to_icnt_q = {}
inter_icnt_pop_sm_q = {}
response_q = {}
total = {}


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
    for i in x.keys():
        for j in range(len(x[i])):
            if x[i][j][7].find("(injection port buffer)"):
                start = int(x[i][j][5].split(": ")[1])
                for k in range(j+1, len(x[i])):
                    if x[i][k][7].find("reply is pushed to SM boundary Q in chiplet"):
                        end = int(x[i][k][5].split(": ")[1])
                        if (end - start) in total.keys():
                            total[end - start] += 1
                        else:
                            total[end - start] = 1
                        start = end = 0
                        break
                    else:
                        continue
            else:
                continue
    plt.plot(total.keys(), total.values(), "g*")
    plt.xlabel("per packet RTC")
    plt.ylabel("number of packets")
    plt.xlim(0, 400)
    plt.ylim(-500, 6000)
    plt.show()


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
    for i in range(0, len(lined_list)):
        if check_local_or_remote(lined_list[i]):
            if int(lined_list[i][4].split(": ")[1]) in packet.keys():
                packet.setdefault(int(lined_list[i][4].split(": ")[1]), []).append(lined_list[i])
            else:
                packet.setdefault(int(lined_list[i][4].split(": ")[1]), []).append(lined_list[i])

    total_distribution(packet)