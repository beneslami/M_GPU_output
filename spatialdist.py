import numpy as np
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


def chip_select(num):
    for i in range(len(chiplet)):
        if num in chiplet[i]["SM_ID"] or num in chiplet[i]["LLC_ID"] or num == chiplet[i]["port"]:
            return i


def check_local_or_remote(x):  # 0 for local, 1 for remote
    for i in range(len(chiplet)):
        if int(x[5].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[5].split(": ")[1]) in chiplet[i]["LLC_ID"]:
            if int(x[6].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[6].split(": ")[1]) in chiplet[i]["LLC_ID"]:
                return 0
        return 1


if __name__ == "__main__":
    file = open("icnt.txt", "r")
    raw_content = ""
    if file.mode == "r":
        raw_content = file.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    packet = {}

    for i in range(len(lined_list)):
        if int(lined_list[i][3].split(": ")[1]) in packet.keys():
            packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        else:
            packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])

    arr = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for i in packet.keys():
        src = int(packet[i][0][1].split(": ")[1])
        dst = int(packet[i][0][2].split(": ")[1])
        arr[3 - chip_select(src)][chip_select(dst)] += 1

    Index = [0, 1, 2, 3]
    Cols = [3, 2, 1, 0]
    plt.xticks(ticks=np.arange(len(Index)), labels=Index)
    plt.yticks(ticks=np.arange(len(Cols)), labels=Cols)
    hm = plt.imshow(arr, cmap='gray_r', interpolation="nearest")
    plt.colorbar(hm)
    plt.show()
