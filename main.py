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


def link_percentage(src, dst):
    global link_01
    global link_12
    global link_23
    global link_30
    if (src == 192 and dst == 193) or (src == 193 and dst == 192):
        link_01 += 1
    if (src == 193 and dst == 194) or (src == 194 and dst == 193):
        link_12 += 1
    if (src == 194 and dst == 195) or (src == 195 and dst == 194):
        link_23 += 1
    if (src == 195 and dst == 192) or (src == 192 and dst == 195):
        link_30 += 1


def check_local_or_remote(x):  # 0 for local, 1 for remote
    for i in range(len(chiplet)):
        if int(x[2]) in chiplet[i]["SM_ID"] or int(x[2]) in chiplet[i]["LLC_ID"] or int(x[2]) == chiplet[i]["port"]:
            if int(x[3]) in chiplet[i]["SM_ID"] or int(x[3]) in chiplet[i]["LLC_ID"] or int(x[3]) == chiplet[i]["port"]:
                return 0
            return 1


if __name__ == '__main__':
    file = open("test.rtf", "r")
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
    print(lined_list[4][4])
    #sorted_lined_list = sorted(lined_list, key=lambda x: int(x[4].split(":")[1]))
    #packet = {int(lined_list[0][4].split(":")[1]): lined_list[0]}
    #print(sorted_lined_list)
    """""
    for i in range(1, len(lined_list)):
        if int(lined_list[i][4].split(":")[1]) in packet.keys():
            packet[int(lined_list[i][4].split(":")[1])].append(lined_list[i])
        else:
            packet[int(lined_list[i][4].split(":")[1])] = lined_list[i]
    print(packet)
    #
    x = [0, 8000]
    m = [mean2, mean2]
    s_plus = [mean2 + stdv2, mean2 + stdv2]
    s_minus = [mean2 - stdv2, mean2 - stdv2]
    plt.plot(pkt_rtt.keys(), pkt_rtt.values(), label="(request/reply) two hops")
    plt.plot(x, m, "r", label="mean")
    plt.plot(x, s_plus, "r--", label="stdev")
    plt.plot(x, s_minus, "r--")
    plt.title("Round Trip Cycle for each packet")
    plt.xlabel("packet index")
    plt.ylabel("Round Trip Cycle (RTC)")

    x = [0, 16500]
    m = [mean1, mean1]
    s_plus = [mean1 + stdv1, mean1 + stdv1]
    s_minus = [mean1 - stdv1, mean1 - stdv1]
    plt.plot(pkt_rtt_half.keys(), pkt_rtt_half.values(), label="request for two hop packets")
    plt.plot(x, m, "r", label="mean")
    plt.plot(x, s_plus, "r--", label="stdev")
    plt.plot(x, s_minus, "r--")
    plt.title("Single Trip Cycle for each packet")
    plt.xlabel("packet index")
    plt.ylabel("Single Trip Cycle (STC)")

    #plt.plot(pkt_rtt_half_one_hop.keys(), pkt_rtt_half_one_hop.values())


    plt.legend(loc="best")
    plt.show()

    """
