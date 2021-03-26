from statistics import mean
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


def check_local_or_remote(x):  # 0 for local, 1 for remote
    for i in range(len(chiplet)):
        if int(x[1].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[1].split(": ")[1]) in chiplet[i]["LLC_ID"]:
            if int(x[2].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[2].split(": ")[1]) in chiplet[i]["LLC_ID"]:
                return 0
        return 1


if __name__ == '__main__':
    file = open("icnt.txt", "r")
    raw_content = ""
    if file.mode == "r":
        raw_content = file.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        if check_local_or_remote(item):
            lined_list.append(item)

    chip0 = []
    chip1 = []
    chip2 = []
    chip3 = []
    temp = {}
    input_queue = {}
    input = []
    waiting_queue = {}
    output = []
    ejection_buffer = {}
    boundary_buffer = {}
    # packet[i][j][0]                explain
    # packet[i][j][1].split(": ")[1] source
    # packet[i][j][2].split(": ")[1] destination
    # packet[i][j][3].split(": ")[1] packet_ID
    # packet[i][j][4].split(": ")[1] type
    # packet[i][j][5].split(": ")[1] gpu_cycle
    # packet[i][j][6].split(": ")[1] icnt_cycle
    packet = {}
    delay_req = {}
    delay_resp = {}
    flit_req = {}
    flit_resp = {}
    req_num = resp_num = 0
    for i in range(len(lined_list)):
        if check_local_or_remote(lined_list[i]):
            if int(lined_list[i][3].split(": ")[1]) in packet.keys():
                packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
            else:
                packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
    t3 = t2 = t1 = 0
    x1 = x2 = 0
    f1 = f2 = 0

    req_cycle = {}
    resp_cycle = {}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "input_queue_push" and int(packet[i][j][4].split(": ")[1]) == 0:
                if int(packet[i][j][5].split(": ")[1]) in req_cycle.keys():
                    req_cycle.setdefault(int(packet[i][j][5].split(": ")[1]), []).append(int(packet[i][j][6].split(": ")[1]))
                    req_num += 1
                else:
                    req_cycle.setdefault(int(packet[i][j][5].split(": ")[1]), []).append(int(packet[i][j][6].split(": ")[1]))
                    req_num += 1
            elif packet[i][j][0] == "input_queue_push" and int(packet[i][j][4].split(": ")[1]) == 2:
                if int(packet[i][j][5].split(": ")[1]) in resp_cycle.keys():
                    resp_cycle.setdefault(int(packet[i][j][5].split(": ")[1]), []).append(int(packet[i][j][6].split(": ")[1]))
                    resp_num += 1
                else:
                    resp_cycle.setdefault(int(packet[i][j][5].split(": ")[1]), []).append(int(packet[i][j][6].split(": ")[1]))
                    resp_num += 1
    resp_dist = {}
    req_dist = {}
    for i in req_cycle.keys():
        if len(req_cycle[i])*32 in req_dist.keys():
            req_dist[len(req_cycle[i]) * 32] += 1
        else:
            req_dist[len(req_cycle[i]) * 32] = 1
    for i in req_dist.keys():
        req_dist[i] = req_dist[i] / req_num

    for i in resp_cycle.keys():
        if len(resp_cycle[i])*32 in resp_dist.keys():
            resp_dist[len(resp_cycle[i]) * 32] += 1
        else:
            resp_dist[len(resp_cycle[i]) * 32] = 1
    for i in resp_dist.keys():
        resp_dist[i] = resp_dist[i] / resp_num

    plt.bar(req_dist.keys(), req_dist.values(), width=12, label="request")
    #plt.bar(resp_dist.keys(), resp_dist.values(), width=10, label="response")
    plt.xlabel("Bytes Per Cycle")
    plt.ylabel("Probability")
    plt.title("Distribution of Bytes per Cycle")
    plt.legend(loc="best")
    plt.show()

    """""
    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "input_queue_push" and int(packet[i][j][4].split(": ")[1]) == 0:
                x1 = int(packet[i][j][5].split(": ")[1])
                f1 = int(packet[i][j][6].split(": ")[1])
                for k in range(j+1, len(packet[i])):
                    if packet[i][k][0] == "Boundary_Buffer_pop" and int(packet[i][k][4].split(": ")[1]) == 0:
                        x2 = int(packet[i][k][5].split(": ")[1])
                        if x2 - x1 in delay_req.keys():
                            delay_req[x2 - x1] += 1
                        else:
                            delay_req[x2 - x1] = 1
                        req_num += 1
                        break
            elif packet[i][j][0] == "input_queue_push" and int(packet[i][j][4].split(": ")[1]) == 2:
                x1 = int(packet[i][j][5].split(": ")[1])
                f1 = int(packet[i][j][6].split(": ")[1])
                for k in range(j+1, len(packet[i])):
                    if packet[i][k][0] == "Boundary_Buffer_pop" and int(packet[i][k][4].split(": ")[1]) == 2:
                        x2 = int(packet[i][k][5].split(": ")[1])
                        if x2 - x1 in delay_resp.keys():
                            delay_resp[x2 - x1] += 1
                        else:
                            delay_resp[x2 - x1] = 1
                        resp_num += 1
                        break
    for i in delay_req.keys():
        delay_req[i] = delay_req[i]/req_num
    for i in delay_resp.keys():
        delay_resp[i] = delay_resp[i]/resp_num

    plt.bar(list(delay_req.keys()), list(delay_req.values()), width=2, color="red", label="request")
    plt.bar(list(delay_resp.keys()), list(delay_resp.values()), width=1, color="blue", label="response")
    plt.legend(loc="best")
    plt.xlabel("Latency in Cycle")
    plt.ylabel("Probability")
    plt.title("Distribution of the latency of packets")
    plt.show()
    """""
    """""
        for j in range(len(packet[i])):
            if packet[i][j][0] == "input_queue_push":
                t1 = int(packet[i][j][5].split(": ")[1])
                for k in range(j+1, len(packet[i])):
                    if packet[i][k][0] == "input_queue_pop" and int(packet[i][k][1].split(": ")[1]) == int(packet[i][j][1].split(": ")[1]):
                        input_queue.setdefault(int(packet[i][k][1].split(": ")[1]), []).append(int(packet[i][k][5].split(": ")[1]) - t1)
                        x1 = int(packet[i][k][5].split(": ")[1])
                        num = int(packet[i][k][3].split(": ")[1])
                        t1 = 0
                        break
            elif packet[i][j][0] == "Boundary_buffer_push":
                t1 = int(packet[i][j][5].split(": ")[1])
                for k in range(j+1, len(packet[i])):
                    if packet[i][k][0] == "Boundary_Buffer_pop" and int(packet[i][k][2].split(": ")[1]) == int(packet[i][j][2].split(": ")[1]):
                        boundary_buffer.setdefault(int(packet[i][k][2].split(": ")[1]), []).append(int(packet[i][k][5].split(": ")[1]) - t1)
                        t1 = 0
                        break
            elif packet[i][j][0] == "Ejection_buffer_push":
                t1 = int(packet[i][j][5].split(": ")[1])
                if num == int(packet[i][j][3].split(": ")[1]):
                    x2 = int(packet[i][j][5].split(": ")[1])
                    if x2 - x1 >= 200:
                        print(packet[i][j])
                        print("---------\n")
                    temp[num] = x2 - x1
                for k in range(j+1, len(packet[i])):
                    if packet[i][k][0] == "Ejection_buffer_pop" and int(packet[i][k][2].split(": ")[1]) == int(packet[i][j][2].split(": ")[1]):
                        ejection_buffer.setdefault(int(packet[i][k][2].split(": ")[1]), []).append(int(packet[i][k][5].split(": ")[1]) - t1)
                        t1 = 0
                        break
            elif packet[i][j][0] == "waiting_queue_push":
                t1 = int(packet[i][j][5].split(": ")[1])
                for k in range(j + 1, len(packet[i])):
                    if packet[i][k][0] == "waiting_queue_pop" and int(packet[i][k][3].split(": ")[1]) == int(packet[i][j][3].split(": ")[1]):
                        waiting_queue.setdefault(int(packet[i][k][3].split(": ")[1]), []).append(int(packet[i][k][5].split(": ")[1]) - t1)
                        t1 = 0
                        break
            
        for i in range(len(packet[248577])):
            print(packet[248577][i])
        break
        """
