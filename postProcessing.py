import csv
import matplotlib.pyplot as plt
from hurst import compute_Hc
import warnings
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

chiplet_2 = dict(
    SM_ID=[64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
           91, 92, 93, 94, 95],
    LLC_ID=[160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175], port=194)

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
injection = {0: {}, 1: {}, 2: {}, 3: {}}
dest_injection = {0: {}, 1: {}, 2: {}, 3: {}}
throughput_byte_update = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
                  3: {0: {}, 1: {}, 2: {}}}
throughput_byte = {0: {}, 1: {}, 2: {}, 3: {}}
packet_type_ratio = {0: {0: 0, 1: 0, 2: 0, 3: 0}, 1: {0: 0, 1: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 2: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0, 3: 0}}
packet_type_ratio_ = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
per_chiplet_heat_map = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}},
                  3: {0: {}, 1: {}, 2: {}}}
src_window = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
inter_injection_rate = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
traffic_pattern = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
offered_throughput_flit = {}
total_throughput = {}
offered_throughput = {0: {}, 1: {}, 2: {}, 3: {}}
total_throughput_flit = {}
response = {0: {}, 1: {}, 2: {}, 3: {}}


def check_local_or_remote(x):  # 0 for local, 1 for remote
    for i in range(len(chiplet)):
        if (int(x[1].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[1].split(": ")[1]) in chiplet[i]["LLC_ID"]):
            if (int(x[2].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[2].split(": ")[1]) in chiplet[i]["LLC_ID"]):
                return 0
        return 1


def chip_select(x):
    if x == 192:
        return 0
    elif x == 193:
        return 1
    elif x == 194:
        return 2
    elif x == 195:
        return 3


def hurst(packet):
    out = {0: {}, 1: {}, 2: {}, 3: {}}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if len(packet[i][j]) > 7:
                continue
            else:
                if int(packet[i][j][5].split(": ")[1]) == 0 or int(packet[i][j][5].split(": ")[1]) == 2:
                    source = int(packet[i][j][0].split(": ")[1])
                    time = int(packet[i][j][6].split(": ")[1])
                    byte = int(packet[i][j][4].split(": ")[1])
                    if time not in out[source].keys():
                        out[source][time] = byte
                    else:
                        out[source][time] += byte

    H_192, c_192, data_192 = compute_Hc(list(out[0].values()))
    H_193, c_193, data_193 = compute_Hc(list(out[1].values()))
    H_194, c_194, data_194 = compute_Hc(list(out[2].values()))
    H_195, c_195, data_195 = compute_Hc(list(out[3].values()))

    f, ax = plt.subplots(2, 2, figsize=(12, 12))
    ax[0, 0].plot(data_192[0], c_192 * data_192[0] ** H_192, color="deepskyblue")
    ax[0, 0].scatter(data_192[0], data_192[1], color="purple")
    ax[0, 0].set_xscale('log')
    ax[0, 0].set_yscale('log')
    ax[0, 0].text(100, 2, "slope = " + str("{:.3f}".format(H_192)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax[0, 0].set_title("core 0")

    ax[0, 1].plot(data_193[0], c_193 * data_193[0] ** H_193, color="deepskyblue")
    ax[0, 1].scatter(data_193[0], data_193[1], color="purple")
    ax[0, 1].set_xscale('log')
    ax[0, 1].set_yscale('log')
    ax[0, 1].text(200, 2, "slope = " + str("{:.3f}".format(H_193)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax[0, 1].set_title("core 1")

    ax[1, 0].plot(data_194[0], c_194 * data_194[0] ** H_194, color="deepskyblue")
    ax[1, 0].scatter(data_194[0], data_194[1], color="purple")
    ax[1, 0].set_xscale('log')
    ax[1, 0].set_yscale('log')
    ax[1, 0].text(100, 2, "slope = " + str("{:.3f}".format(H_194)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax[1, 0].set_title("core 2")

    ax[1, 1].plot(data_195[0], c_195 * data_195[0] ** H_195, color="deepskyblue")
    ax[1, 1].scatter(data_195[0], data_195[1], color="purple")
    ax[1, 1].set_xscale('log')
    ax[1, 1].set_yscale('log')
    ax[1, 1].text(100, 2, "slope = " + str("{:.3f}".format(H_195)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax[1, 1].set_title("core 3")

    plt.show()


def find_next_hop(src, dest):
    if src == 0:
        if dest == 1:
            return 1
        elif dest == 2 or dest == 3:
            return 3
    elif src == 1:
        if dest == 2:
            return 2
        elif dest == 0 or dest == 3:
            return 0
    elif src == 2:
        if dest == 3:
            return 3
        elif dest == 1 or dest == 0:
            return 1
    elif src == 3:
        if dest == 0:
            return 0
        elif dest == 2 or dest == 1:
            return 2


def byte_per_cycle(packet):
    global throughput_byte
    for i in packet.keys():
        for j in range(len(packet[i])):
            source = int(packet[i][j][0].split(": ")[1])
            dest = int(packet[i][j][1].split(": ")[1])
            router_id = int(packet[i][j][3].split(": ")[1])
            byte = int(packet[i][j][4].split(": ")[1])
            time = int(packet[i][j][6].split(": ")[1])
            explain = str(packet[i][j][8])
            if explain.find("packet injected") != -1:
                if time not in throughput_byte[source].keys():
                    throughput_byte[source].setdefault(time, {})
                    if dest not in throughput_byte[source][time].keys():
                        throughput_byte[source][time].setdefault(dest, []).append(byte)
                    else:
                        throughput_byte[source][time].setdefault(dest, []).append(byte)
                else:
                    if dest not in throughput_byte[source][time].keys():
                        throughput_byte[source][time].setdefault(dest, []).append(byte)
                    else:
                        throughput_byte[source][time].setdefault(dest, []).append(byte)


def byte_per_cycle_update():
    for src in throughput_byte.keys():
        for cyc in throughput_byte[src].keys():
            list_ = [0, 1, 2, 3]
            list_.remove(src)
            for dest in throughput_byte[src][cyc].keys():
                list_.remove(dest)
            if len(list_) != 0:
                for i in list_:
                    throughput_byte[src][cyc].setdefault(i, [])

    for src in throughput_byte.keys():
        throughput_byte[src] = dict(sorted(throughput_byte[src].items(), key= lambda x: x[0]))


def byte_per_cycle_dist(dir):
    global throughput_byte
    byte_dist = {0: {}, 1: {}, 2: {}, 3: {}}
    dist_ = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    for source in throughput_byte.keys():
        for cycle in throughput_byte[source].keys():
            temp = 0
            for dest in throughput_byte[source][cycle].keys():
                temp += sum(throughput_byte[source][cycle][dest])
                if len(throughput_byte[source][cycle][dest]) == 0:
                    if 0 not in dist_[source][dest].keys():
                        dist_[source][dest][0] = 1
                    else:
                        dist_[source][dest][0] += 1
                else:
                    if sum(throughput_byte[source][cycle][dest]) not in dist_[source][dest].keys():
                        dist_[source][dest][sum(throughput_byte[source][cycle][dest])] = 1
                    else:
                        dist_[source][dest][sum(throughput_byte[source][cycle][dest])] += 1
            if temp not in byte_dist[source].keys():
                byte_dist[source][temp] = 1
            else:
                byte_dist[source][temp] += 1

    for src in dist_.keys():
        for dest in dist_[src].keys():
            dist_[src][dest] = dict(sorted(dist_[src][dest].items(), key=lambda x: x[0]))

    fields = ['byte', 'dist']
    byte_dist[0] = dict(sorted(byte_dist[0].items(), key=lambda x: x[0]))
    with open(dir + "byte_0.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in byte_dist[0].items():
            writer.writerow([cyc, byte])
    byte_dist[1] = dict(sorted(byte_dist[1].items(), key=lambda x: x[0]))
    with open(dir + "byte_1.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in byte_dist[1].items():
            writer.writerow([cyc, byte])
    byte_dist[2] = dict(sorted(byte_dist[2].items(), key=lambda x: x[0]))
    with open(dir + "byte_2.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in byte_dist[2].items():
            writer.writerow([cyc, byte])
    byte_dist[3] = dict(sorted(byte_dist[3].items(), key=lambda x: x[0]))
    with open(dir + "byte_3.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in byte_dist[3].items():
            writer.writerow([cyc, byte])


def outser(dir):
    for src in throughput_byte.keys():
        for cyc in throughput_byte[src].keys():
            for dest in throughput_byte[src][cyc].keys():
                with open(dir + "post_" + str(src) + "_" + str(dest) + ".txt", "a") as file:
                    file.write(str(cyc) + "\t" + str(throughput_byte[src][cyc][dest]) + "\n")


def generate_packet_type_ratio(dir):
    dist = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    dist_total = {0: {}, 1: {}, 2: {}, 3: {}}
    for src in throughput_byte.keys():
        for cyc in throughput_byte[src].keys():
            for dest, byte in throughput_byte[src][cyc].items():
                if len(byte) == 0:
                    if 0 not in dist[src][dest].keys():
                        dist[src][dest][0] = 1
                    else:
                        dist[src][dest][0] += 1
                    if 0 not in dist_total[src].keys():
                        dist_total[src][0] = 1
                    else:
                        dist_total[src][0] += 1
                else:
                    for b in byte:
                        if b not in dist[src][dest].keys():
                            dist[src][dest][b] = 1
                        else:
                            dist[src][dest][b] += 1
                        if b not in dist_total[src].keys():
                            dist_total[src][b] = 1
                        else:
                            dist_total[src][b] += 1
    with open(dir + "packet_ratio.csv", "w") as file:
        for src in dist_total.keys():
            file.write(str(src) + "\n")
            for packet, freq in dist_total[src].items():
                file.write(str(packet) + "," + str(freq) + "\n")


def check_injection_rate(dir):
    global throughput_byte
    global injection_rate
    on = {}
    total = 0
    for source in throughput_byte.keys():
        for cyc in throughput_byte[source].keys():
            for dest in throughput_byte[source][cyc].keys():
                if dest not in on.keys():
                    on[dest] = 1
                else:
                    on[dest] += 1
            total += 1
        for dst in on.keys():
            injection_rate[source][dst] = on[dst] / total
        total = 0
        on.clear()
    with open(dir + "injection_rate.csv", "w") as file:
        for src in injection_rate.keys():
            file.write(str(src) + "\n")
            for dest, rate in injection_rate[src].items():
                file.write(str(dest)+ "," + str(rate) + "\n")


def generate_traffic_flow(dir):
    traffic_flow = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
    for src in throughput_byte.keys():
        for cycle in throughput_byte[src].keys():
            for dest in throughput_byte[src][cycle].keys():
                traffic_flow[src][dest] += sum(throughput_byte[src][cycle][dest])

    fields = ['dest', 'byte']
    with open(dir + "traffic_flow.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for src in traffic_flow.keys():
            writer.writerow([str(src)])
            for dest, byte in traffic_flow[src].items():
                writer.writerow([dest, byte])


def inter_departure_dist(dir):
    dist = {0: {}, 1: {}, 2: {}, 3: {}}
    flag = 0
    start = -1
    global throughput_byte
    for source in throughput_byte.keys():
        for cycle in throughput_byte[source].keys():
            if flag == 0:
                start = cycle
                flag = 1
            elif flag == 1:
                if (cycle - start) not in dist[source].keys():
                    dist[source][cycle - start] = 1
                else:
                    dist[source][cycle - start] += 1
                start = cycle
        flag = 0
        start = -1

    fields = ['IAT', 'dist']
    dist[0] = dict(sorted(dist[0].items(), key=lambda x: x[0]))
    with open(dir + "iat_0.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[0].items():
            writer.writerow([cyc, byte])
    dist[1] = dict(sorted(dist[1].items(), key=lambda x: x[0]))
    with open(dir + "iat_1.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[1].items():
            writer.writerow([cyc, byte])
    dist[2] = dict(sorted(dist[2].items(), key=lambda x: x[0]))
    with open(dir + "iat_2.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[2].items():
            writer.writerow([cyc, byte])
    dist[3] = dict(sorted(dist[3].items(), key=lambda x: x[0]))
    with open(dir + "iat_3.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[3].items():
            writer.writerow([cyc, byte])

# ------------------------------------------------------


def response_byte_per_core(packet, dir):
    global response
    byte_dist = {0: {}, 1: {}, 2: {}, 3: {}}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][8].find("pending reply") != -1:
                src  = int(packet[i][j][0].split(": ")[1])
                time = int(packet[i][j][6].split(": ")[1])
                byte = int(packet[i][j][4].split(": ")[1])
                if time not in response[src].keys():
                    response[src].setdefault(time, []).append(byte)
                else:
                    response[src][time].append(byte)
    for src in response.keys():
        for time, byte in response[src].items():
            if sum(byte) not in byte_dist[src].keys():
                byte_dist[src][sum(byte)] = 1
            else:
                byte_dist[src][sum(byte)] += 1

    for src in byte_dist.keys():
        byte_dist[src] = dict(sorted(byte_dist[src].items(), key=lambda x: x[0]))
    for src in byte_dist.keys():
        with open(dir + "byte_dest_" + str(src) + ".csv", "w") as file:
            for b, freq in byte_dist[src].items():
                file.write(str(b) + "," + str(freq) + "\n")


def response_iat(dir):
    resp_iat = {0: {}, 1: {}, 2: {}, 3: {}}
    for src in response.keys():
        response[src] = dict(sorted(response[src].items(), key=lambda x: x[0]))
    for src in response.keys():
        flag = 0
        start = -1
        for time, byte in response[src].items():
            if flag == 0:
                flag = 1
                start = time
            elif flag == 1:
                if(time - start) not in resp_iat[src].keys():
                    resp_iat[src][time - start] = 1
                else:
                    resp_iat[src][time - start] += 1
                start = time

    for src in resp_iat.keys():
        resp_iat[src] = dict(sorted(resp_iat[src].items(), key=lambda x: x[0]))

    for src in resp_iat.keys():
        with open(dir + "dest_iat_" + str(src) + ".csv", "w") as file:
            for duration, freq in resp_iat[src].items():
                file.write(str(duration) + "," + str(freq) + "\n")


def response_window_size(dir):
    global response
    resp_window_size = {0: {}, 1: {}, 2: {}, 3: {}}
    for src in response.keys():
        for cyc, byte in response[src].items():
            length = len(byte)
            if length not in resp_window_size[src].keys():
                resp_window_size[src][length] = 1
            else:
                resp_window_size[src][length] += 1

    for src in resp_window_size.keys():
        resp_window_size[src] = dict(sorted(resp_window_size[src].items(), key=lambda x: x[0]))

    with open(dir + "dest_window_size.csv", "w") as file:
        for src in resp_window_size.keys():
            file.write(str(src) + "\n")
            for length, freq in resp_window_size[src].items():
                file.write(str(length) + "," + str(freq) + "\n")
# ------------------------------------------------------


def generate_link_utilization(packet, dir):
    link_req = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    link_resp = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    link = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
    for i in packet.keys():
        for j in range(len(packet[i])):
            explain = str(packet[i][j][8])
            type_ = int(packet[i][j][5].split(": ")[1])

            if explain.find("packet injected") != -1:
                source = int(packet[i][j][0].split(": ")[1])
                byte = int(packet[i][j][4].split(": ")[1])
                time = int(packet[i][j][6].split(": ")[1])  # gpu cycle = 6, icnt_cycle = 7
                for k in range(j+1, len(packet[i])):
                    _type = int(packet[i][k][5].split(": ")[1])
                    if str(packet[i][k][8]).find("FW push") != -1 and (_type == 0 or _type == 2):
                        router_id = int(packet[i][k][3].split(": ")[1])
                        if time not in link_req[source][router_id].keys():
                            link_req[source][router_id][time] = byte
                        else:
                            link_req[source][router_id][time] += byte
                        if time not in link[source][router_id].keys():
                            link[source][router_id][time] = byte
                        else:
                            link[source][router_id][time] += byte
                    elif str(packet[i][k][8]).find("Request Received\n") != -1 and (_type == 0 or _type == 2):
                        dest = int(packet[i][k][1].split(": ")[1])
                        if time not in link_req[source][dest].keys():
                            link_req[source][dest][time] = byte
                        else:
                            link_req[source][dest][time] += byte
                        if time not in link[source][dest].keys():
                            link[source][dest][time] = byte
                        else:
                            link[source][dest][time] += byte
                    break

            elif explain.find("FW pop") != -1:
                router_id = int(packet[i][j][3].split(": ")[1])
                byte = int(packet[i][j][4].split(": ")[1])
                time = int(packet[i][j][6].split(": ")[1])  # gpu cycle = 6, icnt_cycle = 7
                for k in range(j + 1, len(packet[i])):
                    _type = int(packet[i][k][5].split(": ")[1])
                    if str(packet[i][k][8]).find("Request Received") != -1 and (_type == 0 or _type == 2):
                        dest = int(packet[i][k][1].split(": ")[1])
                        if time not in link_req[router_id][dest].keys():
                            link_req[router_id][dest][time] = byte
                        else:
                            link_req[router_id][dest][time] += byte
                        if time not in link[router_id][dest].keys():
                            link[router_id][dest][time] = byte
                        else:
                            link[router_id][dest][time] += byte
                    elif str(packet[i][k][8]).find("Reply Received") != -1 and (_type == 1 or _type == 3):
                        dest = int(packet[i][k][1].split(": ")[1])
                        if time not in link_resp[router_id][dest].keys():
                            link_resp[router_id][dest][time] = byte
                        else:
                            link_resp[router_id][dest][time] += byte
                        if time not in link[router_id][dest].keys():
                            link[router_id][dest][time] = byte
                        else:
                            link[router_id][dest][time] += byte
                    break

            elif explain.find("pending reply") != -1:
                source = int(packet[i][j][0].split(": ")[1])
                byte = int(packet[i][j][4].split(": ")[1])
                time = int(packet[i][j][6].split(": ")[1])  # gpu cycle = 6, icnt_cycle = 7
                for k in range(j+1, len(packet[i])):
                    _type = int(packet[i][k][5].split(": ")[1])
                    if str(packet[i][k][8]).find("Reply Received") != -1 and (_type == 1 or _type == 3):
                        dest = int(packet[i][k][1].split(": ")[1])
                        if time not in link_resp[source][dest].keys():
                            link_resp[source][dest][time] = byte
                        else:
                            link_resp[source][dest][time] += byte
                        if time not in link[source][dest].keys():
                            link[source][dest][time] = byte
                        else:
                            link[source][dest][time] += byte
                    elif str(packet[i][k][8]).find("FW push") != -1 and (_type == 1 or _type == 3):
                        router_id = int(packet[i][k][3].split(": ")[1])
                        if time not in link_resp[source][router_id].keys():
                            link_resp[source][router_id][time] = byte
                        else:
                            link_resp[source][router_id][time] += byte
                        if time not in link[source][router_id].keys():
                            link[source][router_id][time] = byte
                        else:
                            link[source][router_id][time] += byte
                    break

    for src in link_req.keys():
        for dest in link_req[src].keys():
            link_req[src][dest] = dict(sorted(link_req[src][dest].items(), key=lambda x: x[0]))
    for src in link_resp.keys():
        for dest in link_resp[src].keys():
            link_resp[src][dest] = dict(sorted(link_resp[src][dest].items(), key=lambda x: x[0]))
    for src in link.keys():
        for dest in link[src].keys():
            link[src][dest] = dict(sorted(link[src][dest].items(), key=lambda x: x[0]))

    with open(dir + "req_link_usage.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(['link', 'mean'])
        for i in link_req.keys():
            writer.writerow([i])
            for j in link_req[i].keys():
                with warnings.catch_warnings():
                    m = np.nanmean(list(link_req[i][j].values()))
                    writer.writerow([j, m])
    with open(dir + "resp_link_usage.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(['link', 'mean'])
        for i in link_resp.keys():
            writer.writerow([i])
            for j in link_resp[i].keys():
                with warnings.catch_warnings():
                    m = np.nanmean(list(link_resp[i][j].values()))
                    writer.writerow([j, m])
    with open(dir + "link_usage.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(['link', 'mean'])
        for i in link.keys():
            writer.writerow([i])
            for j in link[i].keys():
                with warnings.catch_warnings():
                    m = np.nanmean(list(link[i][j].values()))
                    writer.writerow([j, m])


def calculate_throughput(packet, dir):
    global offered_throughput
    global total_throughput
    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][8].find("packet injected") != -1 or packet[i][j][8].find("pending reply") != -1:
                src = int(packet[i][j][0].split(": ")[1])
                time = int(packet[i][j][6].split(": ")[1])
                byte = int(packet[i][j][4].split(": ")[1])
                if time not in total_throughput.keys():
                    total_throughput[time] = byte
                else:
                    total_throughput[time] += byte
                if time not in offered_throughput[src].keys():
                    offered_throughput[src][time] = byte
                else:
                    offered_throughput[src][time] += byte

            elif packet[i][j][8].find("Request Received") != -1 or packet[i][j][8].find("Reply Received") != -1:
                time = int(packet[i][j][6].split(": ")[1])
                byte = int(packet[i][j][4].split(": ")[1])
                if time not in total_throughput.keys():
                    total_throughput[time] = -byte
                else:
                    total_throughput[time] -= byte

    total_throughput = dict(sorted(list(total_throughput.items()), key=lambda x: x[0]))
    for i in offered_throughput.keys():
        offered_throughput[i] = dict(sorted(list(offered_throughput[i].items()), key=lambda x: x[0]))
    with open(dir + "total_throughput.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        for cyc, byte in total_throughput.items():
            writer.writerow([cyc, byte])


def calculate_throughput_param(dir):
    data = {0: {}, 1: {}, 2: {}, 3: {}}
    for src in offered_throughput.keys():
        for time, byte in offered_throughput[src].items():
            if byte not in data[src].keys():
                data[src][byte] = 1
            else:
                data[src][byte] += 1

    for src in data.keys():
        data[src] = dict(sorted(data[src].items(), key=lambda x: x[0]))
    with open(dir + "throughput_params.csv", "w") as file:
        writer = csv.writer(file)
        for src in data.keys():
            writer.writerow([src])
            for byte, freq in data[src].items():
                writer.writerow([byte, freq])


def calculate_source_window(dir):
    global throughput_byte
    global src_window
    for src in throughput_byte.keys():
        for cyc in throughput_byte[src].keys():
            for dest in throughput_byte[src][cyc].keys():
                if len(throughput_byte[src][cyc][dest]) not in src_window[src][dest].keys():
                    src_window[src][dest][len(throughput_byte[src][cyc][dest])] = 1
                else:
                    src_window[src][dest][len(throughput_byte[src][cyc][dest])] += 1
    for src in src_window.keys():
        for dst in src_window[src].keys():
            src_window[src][dst] = dict(sorted(src_window[src][dst].items(), key=lambda x: x[0]))

    with open(dir + "source_window.csv", "w") as file:
        writer = csv.writer(file)
        for src in src_window.keys():
            writer.writerow(["src", src])
            for dest in src_window[src].keys():
                writer.writerow(["dst", dest])
                for byte, freq in src_window[src][dest].items():
                    writer.writerow([byte, freq])


def generate_traffic_pattern(dir):
    global traffic_pattern
    global throughput_byte
    destination_spread = {0: {}, 1: {}, 2: {}, 3: {}}
    for src in throughput_byte.keys():
        for cycle in throughput_byte[src].keys():
            for dest in throughput_byte[src][cycle].keys():
                byte = sum(throughput_byte[src][cycle][dest])
                traffic_pattern[src][dest] = traffic_pattern[src][dest] + byte

    with open(dir + "traffic_pattern.csv", "w") as file:
        for src in traffic_pattern.keys():
            file.write(str(src) + "\n")
            for dest, byte in traffic_pattern[src].items():
                file.write(str(dest) + "," + str(byte) + "\n")

    for src in throughput_byte.keys():
        for cycle in throughput_byte[src].keys():
            for dest in throughput_byte[src][cycle].keys():
                if len(throughput_byte[src][cycle][dest]) != 0:
                    if dest not in destination_spread[src].keys():
                        destination_spread[src][dest] = 1
                    else:
                        destination_spread[src][dest] += 1

    with open(dir + "destination_spread.csv", "w") as file:
        for src in destination_spread.keys():
            file.write(str(src) + "\n")
            for dest, freq in destination_spread[src].items():
                file.write(str(dest) + "," + str(freq) + "\n")


def cache_latency(packet, path):
    l2 = {0: {}, 1: {}, 2: {}, 3: {}}
    dram = {0: {}, 1: {}, 2: {}, 3: {}}
    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][8].find("Request Received") == 0:
                start = int(packet[i][j][6].split(": ")[1])
                for k in range(j+1, len(packet[i])):
                    if packet[i][k][8].find("reply injected") == 0:
                        src = int(packet[i][k][3].split(": ")[1])
                        time = int(packet[i][k][6].split(": ")[1])
                        if packet[i][k][9].find("DRAM") == 0:
                            if (time - start) not in dram[src].keys():
                                dram[src][time - start] = 1
                            else:
                                dram[src][time - start] += 1
                        elif packet[i][k][9].find("L2") == 0:
                            if (time - start) not in l2[src].keys():
                                l2[src][time - start] = 1
                            else:
                                l2[src][time - start] += 1
                        break
    for src in l2.keys():
        l2[src] = dict(sorted(l2[src].items(), key=lambda x: x[0]))
    for src in dram.keys():
        dram[src] = dict(sorted(dram[src].items(), key=lambda x: x[0]))
    for src in l2.keys():
        with open(path + "l2_" + str(src) + ".csv", "w") as file:
            for duration, freq in l2[src].items():
                file.write(str(duration) + "," + str(freq) + "\n")
    for src in dram.keys():
        with open(path + "dram_" + str(src) + ".csv", "w") as file:
            for duration, freq in dram[src].items():
                file.write(str(duration) + "," + str(freq) + "\n")


if __name__ == "__main__":
    model_name = "2MM"
    path = "post/" + model_name + "/"
    with open(path + 'out.txt', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    packet_ = {}
    packet = {}
    for i in range(len(lined_list)):
        if int(lined_list[i][2].split(": ")[1]) in packet_.keys():
            packet_.setdefault(int(lined_list[i][2].split(": ")[1]), []).append(lined_list[i])
        else:
            packet_.setdefault(int(lined_list[i][2].split(": ")[1]), []).append(lined_list[i])
    packet = dict(sorted(packet_.items(), key=lambda x: x[0]))
    del packet_
    byte_per_cycle(packet)
    byte_per_cycle_update()
    byte_per_cycle_dist(path)
    inter_departure_dist(path)
    generate_traffic_pattern(path)
    generate_link_utilization(packet, path)
    calculate_throughput(packet, path)
    calculate_throughput_param(path)
    cache_latency(packet, path)
    response_byte_per_core(packet, path)
    response_iat(path)
    response_window_size(path)
