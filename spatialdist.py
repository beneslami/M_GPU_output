from _csv import writer

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from mpl_toolkits import mplot3d

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


def injeciton_flow(packet):
    arr = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "injection buffer" and int(packet[i][j][4].split(": ")[1]) == 0:
                src = chip_select(int(packet[i][j][1].split(": ")[1]))
                dst = chip_select(int(packet[i][j][2].split(": ")[1]))
                arr[3 - src][dst] += 1
                continue
            elif packet[i][j][0] == "L2_icnt_pop" and int(packet[i][j][4].split(": ")[1]) == 2:
                src = chip_select(int(packet[i][j][1].split(": ")[1]))
                dst = chip_select(int(packet[i][j][2].split(": ")[1]))
                arr[3 - src][dst] += 1
                break

    Index = [0, 1, 2, 3]
    Cols = [3, 2, 1, 0]
    plt.xticks(ticks=np.arange(len(Index)), labels=Index)
    plt.yticks(ticks=np.arange(len(Cols)), labels=Cols)
    hm = plt.imshow(arr, cmap='gray_r', interpolation="nearest")
    plt.colorbar(hm)
    plt.xlabel("Source")
    plt.ylabel("Destination")
    plt.title("spatial Distribution of Injection Flows")
    plt.show()


def injection_rate(packet):
    arr = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    dst = -1
    src = -1
    for i in packet.keys():
        if chip_select(int(packet[i][0][1].split(": ")[1])) != chip_select(int(packet[i][0][2].split(": ")[1])):
            for j in range(len(packet[i])):
                if packet[i][j][0] == "injection buffer" and int(packet[i][j][4].split(": ")[1]) == 0:
                    src = chip_select(int(packet[i][j][1].split(": ")[1]))
                    for k in range(j, len(packet[i])):
                        if packet[i][k][0] == "inter_icnt_pop_llc_push" and int(packet[i][k][4].split(": ")[1]) == 0:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            arr[3 - src][dst] += 1
                            break
                        elif packet[i][k][0] == "forward_waiting_push" and int(packet[i][k][4].split(": ")[1]) == 0:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            arr[3 - src][dst] += 1
                            break

                if packet[i][j][0] == "forward_waiting_push" and int(packet[i][j][4].split(": ")[1]) == 0:
                    src = chip_select(int(packet[i][j][6].split(": ")[1]))
                    for k in range(j, len(packet[i])):
                        if packet[i][k][0] == "inter_icnt_pop_llc_push" and int(packet[i][k][4].split(": ")[1]) == 0:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            arr[3 - src][dst] += 1
                            break

                if packet[i][j][0] == "L2_icnt_pop" and int(packet[i][j][4].split(": ")[1]) == 2:
                    src = chip_select(int(packet[i][j][1].split(": ")[1]))
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "forward_waiting_push" and int(packet[i][k][4].split(": ")[1]) == 2:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            arr[3 - src][dst] += 1
                            break
                        elif packet[i][k][0] == "SM boundary buffer push" and int(packet[i][k][4].split(": ")[1]) == 2:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            arr[3 - src][dst] += 1
                            break

                if packet[i][j][0] == "forward_waiting_push" and int(packet[i][j][4].split(": ")[1]) == 2:
                    src = chip_select(int(packet[i][j][6].split(": ")[1]))
                    for k in range(j + 1, len(packet[i])):
                        if packet[i][k][0] == "SM boundary buffer push" and int(packet[i][k][4].split(": ")[1]) == 2:
                            dst = chip_select(int(packet[i][k][6].split(": ")[1]))
                            arr[3 - src][dst] += 1
                            break
    print(arr)
# {6: 56226, 8: 31585, 7: 72748, 4: 49984, 9: 38302, 5: 8, 3: 36, 2: 18}
    Index = [0, 1, 2, 3]
    Cols = [3, 2, 1, 0]
    plt.xticks(ticks=np.arange(len(Index)), labels=Index)
    plt.yticks(ticks=np.arange(len(Cols)), labels=Cols)
    hm = plt.imshow(arr, cmap='gray_r', interpolation="nearest")
    plt.colorbar(hm)
    plt.xlabel("Source")
    plt.ylabel("Destination")
    plt.title("spatial Distribution of traffics among links")
    plt.show()


def hop_fraction(packet):
    one_hop = 0
    two_hop = 0
    sum = 0
    for i in packet.keys():
        if chip_select(int(packet[i][0][1].split(": ")[1])) != chip_select(int(packet[i][0][2].split(": ")[1])):
            if abs(int(packet[i][0][1].split(": ")[1]) - int(packet[i][0][2].split(": ")[1])) == 1 or abs(int(packet[i][0][1].split(": ")[1]) - int(packet[i][0][2].split(": ")[1])) == len(chiplet) - 1:
                one_hop += 1
            else:
                two_hop += 1
            sum += 1
    print("one hop: " + str(one_hop / sum))
    print("two hop: " + str(two_hop / sum))


def byte_flow(packet):

    read_req_chip_flow = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]
    read_rep_chip_flow = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]
    write_req_chip_flow = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]
    write_rep_chip_flow = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]
    arr = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]
    dst = -1
    src = -1
    for i in packet.keys():
        if chip_select(int(packet[i][0][1].split(": ")[1])) != chip_select(int(packet[i][0][2].split(": ")[1])):
            for j in range(len(packet[i])):
                if packet[i][j][0] == "injection buffer":
                    src = chip_select(int(packet[i][j][1].split(": ")[1]))
                    dst = chip_select(int(packet[i][j][2].split(": ")[1]))
                    arr[3 - src][dst].append(int(packet[i][j][7].split(": ")[1]))
                    if int(packet[i][j][4].split(": ")[1]) == 0:
                        read_req_chip_flow[3-src][dst].append(int(packet[i][j][7].split(": ")[1]))
                    elif int(packet[i][j][4].split(": ")[1]) == 1:
                        write_req_chip_flow[3-src][dst].append(int(packet[i][j][7].split(": ")[1]))
                    elif int(packet[i][j][4].split(": ")[1]) == 2:
                        read_rep_chip_flow[3-src][dst].append(int(packet[i][j][7].split(": ")[1]))
                    elif int(packet[i][j][4].split(": ")[1]) == 3:
                        write_rep_chip_flow[3-src][dst].append(int(packet[i][j][7].split(": ")[1]))
                    continue
                elif packet[i][j][0] == "L2_icnt_pop":
                    src = chip_select(int(packet[i][j][1].split(": ")[1]))
                    dst = chip_select(int(packet[i][j][2].split(": ")[1]))
                    arr[3 - src][dst].append(int(packet[i][j][7].split(":")[1]))
                    if int(packet[i][j][4].split(": ")[1]) == 0:
                        read_req_chip_flow[3-src][dst].append(int(packet[i][j][7].split(":")[1]))
                    elif int(packet[i][j][4].split(": ")[1]) == 1:
                        write_req_chip_flow[3-src][dst].append(int(packet[i][j][7].split(":")[1]))
                    elif int(packet[i][j][4].split(": ")[1]) == 2:
                        read_rep_chip_flow[3-src][dst].append(int(packet[i][j][7].split(":")[1]))
                    elif int(packet[i][j][4].split(": ")[1]) == 3:
                        write_rep_chip_flow[3-src][dst].append(int(packet[i][j][7].split(":")[1]))
                    continue
    D_arr2 = [[[], [], [], []], [[], [], [], []], [[], [], [], []], [[], [], [], []]]

    D_arr = [[], [], [], []]
    for i in range(len(read_rep_chip_flow)):
        for j in range(len(read_rep_chip_flow[i])):
            if len(read_rep_chip_flow[i][j]) != 0:
                D_arr[i].append(np.mean(read_rep_chip_flow[i][j]))
            else:
                D_arr[i].append(0)
    
    # 3D 
    ax = plt.axes(projection='3d')
    data_array = np.array(D_arr)
    x_data, y_data = np.meshgrid(np.arange(data_array.shape[1]), np.arange(data_array.shape[0]))
    for i in range(len(x_data)):
        x_data[i] = x_data[i][::-1]
    x_data = x_data.flatten()
    y_data = y_data.flatten()
    z_data = data_array.flatten()
    ax.bar3d(x_data, y_data, np.zeros(len(z_data)), 0.7, 0.7, z_data, alpha=0.9)
    ax.set_xlabel('Source')
    ax.set_ylabel('Destination')
    ax.set_zlabel('Mean read_req Flow')
    plt.show()



if __name__ == "__main__":
    file = open("report.txt", "r")
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
            if lined_list[i] not in packet[int(lined_list[i][3].split(": ")[1])]:
                packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        else:
            packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])

    #injeciton_flow(packet)
    #injection_rate(packet)
    #hop_fraction(packet)
    byte_flow(packet)