import seaborn as sn
import os
from pathlib import Path
import gc
from measurements.cnf import *
import math
import calculate_link_usage
import benchlist


def determine_architecture(topo, nv, ch):
    topol = ""
    chipNum = -1
    NV = -1
    if topo == "torus":
        topol = "2Dtorus"
    elif topo == "ring":
        topol = "ring"
    elif topo == "mesh":
        topol = "2Dmesh"
    elif topo == "fly":
        if ch == "4chiplet" or ch == "8chiplet":
            topol = "1fly"
        else:
            topol = "2fly"
    if ch == "4chiplet":
        chipNum = 4
    elif ch == "8chiplet":
        chipNum = 8
    elif ch == "16chiplet":
        chipNum = 16
    if nv == "NVLink4":
        NV = 4
    elif nv == "NVLink3":
        NV = 3
    elif nv == "NVLink2":
        NV = 2
    elif nv == "NVLink1":
        NV = 1
    return topol, NV, chipNum


def MAPE(emp, syn):
    summation = 0
    length = 0
    for k, v in syn.items():
        if k in emp.keys() and emp[k] > 0:
            summation += np.abs((emp[k] - v)/emp[k])
            length += 1
    return summation/length


def MAE(emp, syn):
    summation = 0
    length = 0
    for k, v in syn.items():
        if k in emp.keys() and emp[k] > 0:
            summation += np.abs((emp[k] - v))
            length += 1
    return summation / length


def MSE(emp, syn):
    summation = 0
    length = 0
    for k, v in syn.items():
        if k in emp.keys() and emp[k] > 0:
            summation += (emp[k] - v)**2
            length += 1
    return summation / length


def kullback_leibler_divergence(emp, syn):
    sum = 0
    for item in syn.keys():
        if item in emp.keys() and emp[item] > 0:
            p = emp[item]
            q = syn[item]
            sum += p*(np.log(p/q))
    gc.enable()
    gc.collect()
    return sum


def hellinger_distance(emp, syn):
    p = []
    q = []
    for item in syn.keys():
        if item in emp.keys():
            p.append(syn[item])
            q.append(emp[item])
    list_of_squares = []
    for p_i, q_i in zip(p, q):
        s = (math.sqrt(p_i) - math.sqrt(q_i)) ** 2
        list_of_squares.append(s)
    sosq = math.sqrt(sum(list_of_squares)/2)
    print("H(p,q): " + str(sosq))


def generate_request_injected_traffic(request_packet):
    traffic = {}
    temp_item = {}
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "request injected":
                src = int(request_packet[id][j][1].split(": ")[1])
                dst = int(request_packet[id][j][2].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if src not in temp_item.keys():
                    temp_item.setdefault(src, {})[dst] = 0
                else:
                    if dst not in temp_item[src].keys():
                        temp_item[src][dst] = 0
                if cycle not in traffic.keys():
                    traffic.setdefault(cycle, {}).setdefault(src, {})[dst] = byte
                else:
                    if src not in traffic[cycle].keys():
                        traffic[cycle].setdefault(src, {})[dst] = byte
                    else:
                        if dst not in traffic[cycle][src].keys():
                            traffic[cycle][src][dst] = byte
                        else:
                            traffic[cycle][src][dst] += byte
    temp_item = dict(sorted(temp_item.items(), key=lambda x: x[0]))
    for c in temp_item.keys():
        temp_item[c] = dict(sorted(temp_item[c].items(), key=lambda x: x[0]))

    aggregate_traffic = {}
    for cyc in traffic.keys():
        temp = 0
        for src in traffic[cyc].keys():
            temp += sum(list(traffic[cyc][src].values()))
        aggregate_traffic[cyc] = temp

    minimum = min(list(traffic.keys()))
    maximum = max(list(traffic.keys()))
    for i in range(minimum, maximum):
        if i not in traffic.keys():
            traffic[i] = temp_item
    traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
    for c in traffic.keys():
        traffic[c] = dict(sorted(traffic[c].items(), key=lambda x: x[0]))
        for s in traffic[c].keys():
            traffic[c][s] = dict(sorted(traffic[c][s].items(), key=lambda x: x[0]))
    """plt.figure(figsize=(20, 8))
    plt.plot(aggregate_traffic.keys(), aggregate_traffic.values())
    if string == "AccelSim":
        plt.title("AccelSim traffic")
    elif string == "Synthetic":
        plt.title("Synthetic traffic")
    plt.xlabel("cycle")
    plt.ylabel("aggregate request bytes")
    plt.show()
    del(aggregate_traffic)"""
    gc.enable()
    gc.collect()
    return traffic


def generate_reply_injected_traffic(request_packet, string):
    traffic = {}
    temp_item = {}
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "reply injected":
                src = dst = -1
                if string == "AccelSim":
                    src = int(request_packet[id][j][2].split(": ")[1])
                    dst = int(request_packet[id][j][1].split(": ")[1])
                elif string == "Synthetic":
                    src = int(request_packet[id][j][1].split(": ")[1])
                    dst = int(request_packet[id][j][2].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if src not in temp_item.keys():
                    temp_item.setdefault(src, {})[dst] = 0
                else:
                    if dst not in temp_item[src].keys():
                        temp_item[src][dst] = 0
                if cycle not in traffic.keys():
                    traffic.setdefault(cycle, {}).setdefault(src, {})[dst] = byte
                else:
                    if src not in traffic[cycle].keys():
                        traffic[cycle].setdefault(src, {})[dst] = byte
                    else:
                        if dst not in traffic[cycle][src].keys():
                            traffic[cycle][src][dst] = byte
                        else:
                            traffic[cycle][src][dst] += byte
    temp_item = dict(sorted(temp_item.items(), key=lambda x: x[0]))
    for c in temp_item.keys():
        temp_item[c] = dict(sorted(temp_item[c].items(), key=lambda x: x[0]))
    aggregate_traffic = {}
    for cyc in traffic.keys():
        temp = 0
        for src in traffic[cyc].keys():
            temp += sum(list(traffic[cyc][src].values()))
        aggregate_traffic[cyc] = temp

    minimum = min(list(traffic.keys()))
    maximum = max(list(traffic.keys()))
    for i in range(minimum, maximum):
        if i not in traffic.keys():
            traffic[i] = temp_item
    traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
    """aggregate_traffic = dict(sorted(aggregate_traffic.items(), key=lambda x: x[0]))
    plt.figure(figsize=(20, 8))
    plt.plot(aggregate_traffic.keys(), aggregate_traffic.values(), marker="*")
    if string == "AccelSim":
        plt.title("AccelSim traffic")
    elif string == "Synthetic":
        plt.title("Synthetic traffic")
    plt.xlabel("cycle")
    plt.ylabel("aggregate reply bytes")
    plt.show()
    del (aggregate_traffic)"""
    gc.enable()
    gc.collect()
    return traffic


def compare_overall_traffic_cdf(emp_injected_traffic, syn_injected_traffic, string, path, kernel_name):
    emp_cdf = {}
    syn_cdf = {}

    aggregate_traffic = {}
    for cyc in emp_injected_traffic.keys():
        temp = 0
        for src in emp_injected_traffic[cyc].keys():
            temp += sum(list(emp_injected_traffic[cyc][src].values()))
        if temp > 0:
            aggregate_traffic[cyc] = temp

    for cyc, byte in aggregate_traffic.items():
        if byte not in emp_cdf.keys():
            emp_cdf[byte] = 1
        else:
            emp_cdf[byte] += 1

    aggregate_traffic = {}
    for cyc in syn_injected_traffic.keys():
        temp = 0
        for src in syn_injected_traffic[cyc].keys():
            temp += sum(list(syn_injected_traffic[cyc][src].values()))
        if temp > 0:
            aggregate_traffic[cyc] = temp

    for cyc, byte in aggregate_traffic.items():
        if byte not in syn_cdf.keys():
            syn_cdf[byte] = 1
        else:
            syn_cdf[byte] += 1

    emp_cdf = dict(sorted(emp_cdf.items(), key=lambda x: x[0]))
    syn_cdf = dict(sorted(syn_cdf.items(), key=lambda x: x[0]))

    total = sum(list(emp_cdf.values()))
    for byte, freq in emp_cdf.items():
        emp_cdf[byte] = freq / total
    total = sum(list(syn_cdf.values()))
    for byte, freq in syn_cdf.items():
        syn_cdf[byte] = freq / total

    prev = 0
    for byte, pdf in emp_cdf.items():
        emp_cdf[byte] = pdf + prev
        prev += pdf
    prev = 0
    for byte, pdf in syn_cdf.items():
        syn_cdf[byte] = pdf + prev
        prev += pdf
    emp_cdf = dict(sorted(emp_cdf.items(), key=lambda x: x[0]))
    syn_cdf = dict(sorted(syn_cdf.items(), key=lambda x: x[0]))

    if not os.path.exists(os.path.dirname(os.path.dirname(path)) + "/plots"):
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots")
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name))
    elif not os.path.exists(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name)):
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name))

    plt.plot(list(emp_cdf.keys()), list(emp_cdf.values()), color='red', linestyle='--', marker='o', label="AccelSim")
    plt.plot(list(syn_cdf.keys()), list(syn_cdf.values()), color='blue', linestyle='-', marker='*', label="Synthetic")
    plt.legend()
    plt.title("aggregate " + string + " CDF")
    plt.xlabel("aggregate " + string + " byte")
    plt.ylabel("CDF")
    plt.savefig(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name) + "/aggregate_" + string + "_byte_CDF.jpg")
    plt.close()
    print("--------" + string + " comparison: ----------")
    hellinger_distance(emp_cdf, syn_cdf)
    print("KL: " + str(kullback_leibler_divergence(emp_cdf, syn_cdf)))
    print("MSE: " + str(MSE(emp_cdf, syn_cdf)))
    print("MAE: " + str(MAE(emp_cdf, syn_cdf)))
    print("MAPE: " + str(MAPE(emp_cdf, syn_cdf)))
    gc.enable()
    gc.collect()


def compare_traffic_pattern(emp_injected_traffic, syn_injected_traffic, chiplet_num, path, kernel_name):
    data1 = []
    data2 = []
    pattern = {}
    for cyc in emp_injected_traffic.keys():
        for src in emp_injected_traffic[cyc].keys():
            for dest, byte in emp_injected_traffic[cyc][src].items():
                if src not in pattern.keys():
                    pattern.setdefault(src, {})[dest] = 1
                else:
                    if dest not in pattern[src].keys():
                        pattern[src][dest] = 1
                    else:
                        pattern[src][dest] += 1
    for i in range(chiplet_num):
        if i not in pattern.keys():
            for j in range(chiplet_num):
                pattern.setdefault(i, {})[j] = 0
        else:
            for j in range(chiplet_num):
                if j not in pattern[i].keys():
                    pattern[i][j] = 0

    for src in pattern.keys():
        total = sum(list(pattern[src].values()))
        for dest, freq in pattern[src].items():
            if total == 0:
                pattern[src][dest] = 0
            else:
                pattern[src][dest] = freq / total
    pattern = dict(sorted(pattern.items(), key=lambda x: x[0]))
    for s in pattern.keys():
        pattern[s] = dict(sorted(pattern[s].items(), key=lambda x: x[0]))
    for src in pattern.keys():
        temp = []
        for dest, frac in pattern[src].items():
            temp.append(frac)
        data1.append(temp)

    pattern = {}
    for cyc in syn_injected_traffic.keys():
        for src in syn_injected_traffic[cyc].keys():
            for dest, byte in syn_injected_traffic[cyc][src].items():
                if src not in pattern.keys():
                    pattern.setdefault(src, {})[dest] = 1
                else:
                    if dest not in pattern[src].keys():
                        pattern[src][dest] = 1
                    else:
                        pattern[src][dest] += 1
    for i in range(chiplet_num):
        if i not in pattern.keys():
            for j in range(chiplet_num):
                pattern.setdefault(i, {})[j] = 0
        else:
            for j in range(chiplet_num):
                if j not in pattern[i].keys():
                    pattern[i][j] = 0

    for src in pattern.keys():
        total = sum(list(pattern[src].values()))
        for dest, freq in pattern[src].items():
            if total == 0:
                pattern[src][dest] = 0
            else:
                pattern[src][dest] = freq / total
    pattern = dict(sorted(pattern.items(), key=lambda x: x[0]))
    for s in pattern.keys():
        pattern[s] = dict(sorted(pattern[s].items(), key=lambda x: x[0]))
    for src in pattern.keys():
        temp = []
        for dest, frac in pattern[src].items():
            temp.append(frac)
        data2.append(temp)

    if not os.path.exists(os.path.dirname(os.path.dirname(path)) + "/plots"):
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots")
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name))
    elif not os.path.exists(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name)):
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name))

    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(20, 20))
    fig.subplots_adjust(wspace=0.01)
    sn.heatmap(data1, cmap="hot", ax=ax1, cbar=True, linewidth=.3, annot=True)
    sn.heatmap(data2, cmap="hot", ax=ax2, cbar=True, linewidth=.3, annot=True)
    ax1.set_title("AccelSim Traffic Pattern")  # AccelSim link usage (Byte/Cycle)      AccelSim Traffic Pattern
    ax2.set_title("synthetic Traffic Pattern")  # BookSim link usage (Byte/Cycle)       BookSim Traffic Pattern
    ax2.yaxis.tick_right()

    fig.subplots_adjust(wspace=0.1)
    plt.savefig(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name) + "/traffic_pattern_comparison.jpg")
    gc.enable()
    gc.collect()


def compare_burst_variability(emp_injected_traffic, syn_injected_traffic, string, path, kernel_name):
    emp_burst = {}
    syn_burst = {}
    flag = 0
    total_burst = 0
    start_cycle = 0

    for cyc in emp_injected_traffic.keys():
        temp = 0
        for src in emp_injected_traffic[cyc].keys():
            for dest, byte in emp_injected_traffic[cyc][src].items():
                temp += byte
        if temp == 0:
            if flag == 1:
                flag = 0
                if total_burst/(cyc - start_cycle) not in emp_burst.keys():
                    emp_burst[total_burst/(cyc - start_cycle)] = 1
                else:
                    emp_burst[total_burst/(cyc - start_cycle)] += 1
                total_burst = 0
        else:
            total_burst += temp
            if flag == 0:
                start_cycle = cyc
                flag = 1

    flag = 0
    total_burst = 0
    start_cycle = 0
    for cyc in syn_injected_traffic.keys():
        temp = 0
        for src in syn_injected_traffic[cyc].keys():
            for dest, byte in syn_injected_traffic[cyc][src].items():
                temp += byte
        if temp == 0:
            if flag == 1:
                flag = 0
                if total_burst / (cyc - start_cycle) not in syn_burst.keys():
                    syn_burst[total_burst / (cyc - start_cycle)] = 1
                else:
                    syn_burst[total_burst / (cyc - start_cycle)] += 1
                total_burst = 0
        else:
            total_burst += temp
            if flag == 0:
                start_cycle = cyc
                flag = 1
    syn_burst = dict(sorted(syn_burst.items(), key=lambda x: x[0]))
    emp_burst = dict(sorted(emp_burst.items(), key=lambda x: x[0]))

    total = sum(list(emp_burst.values()))
    for burst, freq in emp_burst.items():
        emp_burst[burst] = freq / total
    total = sum(list(syn_burst.values()))
    for burst, freq in syn_burst.items():
        syn_burst[burst] = freq / total

    syn_burst = dict(sorted(syn_burst.items(), key=lambda x: x[0]))
    emp_burst = dict(sorted(emp_burst.items(), key=lambda x: x[0]))

    prev = 0
    for burst, pdf in emp_burst.items():
        emp_burst[burst] = pdf + prev
        prev += pdf
    prev = 0
    for burst, pdf in syn_burst.items():
        syn_burst[burst] = pdf + prev
        prev += pdf

    if not os.path.exists(os.path.dirname(os.path.dirname(path)) + "/plots"):
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots")
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name))
    elif not os.path.exists(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name)):
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name))

    plt.plot(list(emp_burst.keys()), list(emp_burst.values()), color='green', linestyle='--', marker='o', label="AccelSim")
    plt.plot(list(syn_burst.keys()), list(syn_burst.values()), color='black', linestyle='-', marker='*', label="Synthetic")
    plt.legend()
    plt.xlabel("burst per unit time")
    plt.ylabel("CDF")
    plt.title(string + " network burst variation")
    plt.savefig(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name) + "/" + string + "_burst_variability.jpg")
    plt.close()
    print("-------" + string + "burst comparison: -------")
    hellinger_distance(emp_burst, syn_burst)
    print("KL divergence: " + str(kullback_leibler_divergence(emp_burst, syn_burst)))
    print("MSE: " + str(MSE(emp_burst, syn_burst)))
    print("MAE: " + str(MAE(emp_burst, syn_burst)))
    print("MAPE: " + str(MAE(emp_burst, syn_burst)))
    gc.enable()
    gc.collect()


def measure_packet_latency(packet, string):
    packet_latency = {}
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "request injected":
                send_src = int(packet[id][j][1].split(": ")[1])
                send_dst = int(packet[id][j][2].split(": ")[1])
                send_cycle = int(packet[id][j][5].split(": ")[1])
                send_byte = int(packet[id][j][7].split(": ")[1])
                for k in range(j, len(packet[id])):
                    if packet[id][k][0] == "request received":
                        recv_src = int(packet[id][k][1].split(": ")[1])
                        recv_dst = int(packet[id][k][2].split(": ")[1])
                        recv_cycle = int(packet[id][k][5].split(": ")[1])
                        recv_byte = int(packet[id][k][7].split(": ")[1])
                        id = int(packet[id][k][3].split(": ")[1])
                        assert send_src == recv_src
                        assert send_dst == recv_dst
                        assert send_byte == recv_byte
                        if recv_cycle - send_cycle not in packet_latency.keys():
                            packet_latency[recv_cycle - send_cycle] = 1
                        else:
                            packet_latency[recv_cycle - send_cycle] += 1
                        break
    for id in packet.keys():
        for j in range(len(packet[id])):
            send_src = -1
            send_dst = -1
            if packet[id][j][0] == "reply injected":
                if string == "AccelSim":
                    send_src = int(packet[id][j][2].split(": ")[1])
                    send_dst = int(packet[id][j][1].split(": ")[1])
                elif string == "Synthetic":
                    send_src = int(packet[id][j][1].split(": ")[1])
                    send_dst = int(packet[id][j][2].split(": ")[1])
                send_cycle = int(packet[id][j][5].split(": ")[1])
                send_byte = int(packet[id][j][7].split(": ")[1])
                for k in range(j, len(packet[id])):
                    recv_src = 1
                    recv_dst = -1
                    if packet[id][k][0] == "reply received":
                        if string == "AccelSim":
                            recv_src = int(packet[id][k][2].split(": ")[1])
                            recv_dst = int(packet[id][k][1].split(": ")[1])
                        elif string == "Synthetic":
                            recv_src = int(packet[id][k][1].split(": ")[1])
                            recv_dst = int(packet[id][k][2].split(": ")[1])
                        recv_cycle = int(packet[id][k][5].split(": ")[1])
                        recv_byte = int(packet[id][k][7].split(": ")[1])
                        assert send_src == recv_src
                        assert send_dst == recv_dst
                        assert send_byte == recv_byte
                        if recv_cycle - send_cycle not in packet_latency.keys():
                            packet_latency[recv_cycle - send_cycle] = 1
                        else:
                            packet_latency[recv_cycle - send_cycle] += 1
                        break
    packet_latency = dict(sorted(packet_latency.items(), key=lambda x: x[0]))
    total = sum(list(packet_latency.values()))
    for lat, freq in packet_latency.items():
        packet_latency[lat] = freq / total
    gc.enable()
    gc.collect()
    return packet_latency


def compare_packet_latency(emp, syn, path, kernel_name):
    prev = 0
    for lat, pdf in emp.items():
        emp[lat] = pdf + prev
        prev += pdf
    prev = 0
    for lat, pdf in syn.items():
        syn[lat] = pdf + prev
        prev += pdf
    emp = dict(sorted(emp.items(), key=lambda x: x[0]))
    syn = dict(sorted(syn.items(), key=lambda x: x[0]))

    if not os.path.exists(os.path.dirname(os.path.dirname(path)) + "/plots"):
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots")
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name))
    elif not os.path.exists(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name)):
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name))

    plt.plot(emp.keys(), emp.values(), color='red', linestyle='--', marker='o', label="AccelSim")
    plt.plot(syn.keys(), syn.values(), color='black', linestyle='-', marker='*', label="Synthetic")
    plt.title("packet latency")
    plt.xlabel("end-to-end latency (cycle)")
    plt.ylabel("CDF")
    plt.legend()
    plt.savefig(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name) + "/packet_latency_CDF_comparison.jpg")
    plt.close()
    emp = dict(sorted(emp.items(), key=lambda x: x[0]))
    syn = dict(sorted(syn.items(), key=lambda x: x[0]))
    print("-----packet latency comparison: -------")
    hellinger_distance(emp, syn)
    print("KL: " + str(kullback_leibler_divergence(emp, syn)))
    print("MSE: " + str(MSE(emp, syn)))
    print("MAE: " + str(MAE(emp, syn)))
    print("MAPE: " + str(MAPE(emp, syn)))
    gc.enable()
    gc.collect()


def measure_network_latency(packet):
    network_latency = {}
    start = end = src = dst = -1
    for id in packet.keys():
        flag = 0
        if len(packet[id]) > 3:
            for j in range(len(packet[id])):
                if packet[id][j][0] == "request injected":
                    flag = 1
                    index = j + 1
                    assert packet[id][index][0] == "inj rtr"
                    src = int(packet[id][index][1].split(": ")[1])
                    dst = int(packet[id][index][2].split(": ")[1])
                    start = int(packet[id][index][5].split(": ")[1])
                elif packet[id][j][0] == "request received":
                    if flag == 1:
                        flag = 0
                        index = j - 1
                        assert packet[id][index][0] == "ejc rtr"
                        assert dst == int(packet[id][index][6].split(": ")[1])
                        end = int(packet[id][index][5].split(": ")[1])
                        if end - start not in network_latency.keys():
                            network_latency[end - start] = 1
                        else:
                            network_latency[end - start] += 1
                    start = end = src = dst = -1
                    break
    start = end = src = dst = -1
    for id in packet.keys():
        flag = 0
        for j in range(len(packet[id])):
            if packet[id][j][0] == "reply injected":
                flag = 1
                index = j + 1
                if len(packet[id][j:]) > 3:
                    assert packet[id][index][0] == "inj rtr"
                    src = int(packet[id][index][1].split(": ")[1])
                    dst = int(packet[id][index][2].split(": ")[1])
                    start = int(packet[id][index][5].split(": ")[1])
                else:
                    break
            elif packet[id][j][0] == "reply received":
                if flag == 1:
                    flag = 0
                    index = j - 1
                    while packet[id][index][0] != "ejc rtr":
                        index -= 1
                    assert packet[id][index][0] == "ejc rtr"
                    assert dst == int(packet[id][index][6].split(": ")[1])
                    end = int(packet[id][index][5].split(": ")[1])
                    if end - start not in network_latency.keys():
                        network_latency[end - start] = 1
                    else:
                        network_latency[end - start] += 1
                start = end = src = dst = -1
                break
    network_latency = dict(sorted(network_latency.items(), key=lambda x: x[0]))
    total = sum(list(network_latency.values()))
    for lat, freq in network_latency.items():
        network_latency[lat] = freq / total
    gc.enable()
    gc.collect()
    return network_latency


def compare_network_latency(emp, syn, path, kernel_name):
    prev = 0
    for lat, pdf in emp.items():
        emp[lat] = pdf + prev
        prev += pdf
    prev = 0
    for lat, pdf in syn.items():
        syn[lat] = pdf + prev
        prev += pdf
    emp = dict(sorted(emp.items(), key=lambda x: x[0]))
    syn = dict(sorted(syn.items(), key=lambda x: x[0]))

    if not os.path.exists(os.path.dirname(os.path.dirname(path)) + "/plots"):
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots")
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name))
    elif not os.path.exists(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name)):
        os.mkdir(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name))

    plt.plot(emp.keys(), emp.values(), color='red', linestyle='--', marker='o', label="AccelSim")
    plt.plot(syn.keys(), syn.values(), color='black', linestyle='-', marker='*', label="Synthetic")
    plt.title("Network latency")
    plt.xlabel("Network latency (cycle)")
    plt.ylabel("CDF")
    plt.legend()
    plt.savefig(os.path.dirname(os.path.dirname(path)) + "/plots/" + str(kernel_name) + "/network_latency_CDF_comparison.jpg")
    gc.enable()
    gc.collect()


if __name__ == "__main__":
    base_path = benchlist.bench_path
    suite = "parboil"
    benchmark = "spmv"
    topology = "torus-new"
    NVLink = "NVLink4"
    chiplet = "4chiplet"
    base_emp = base_path + suite + "/" + benchmark + "/" + topology + "/" + NVLink + "/" + chiplet + "/kernels/"
    base_syn = base_path + suite + "/" + benchmark + "/" + topology + "/" + NVLink + "/" + chiplet + "/synthetic_trace/"
    chiplet_num = int(chiplet[0])
    target_path = [base_emp, base_syn]
    for input_ in os.listdir(base_syn):
        kernel_num = int(input_)
        for file_trace in os.listdir(base_syn + input_):
            if Path(file_trace).suffix == '.txt':
                assert os.path.exists(base_emp + file_trace)
                emp_request_injected_traffic = {}
                syn_request_injected_traffic = {}
                emp_reply_injected_traffic = {}
                syn_reply_injected_traffic = {}
                emp_packet_latency_dist = {}
                syn_packet_latency_dist = {}
                emp_network_latency_dist = {}
                syn_network_latency_dist = {}
                topo, nv, ch = determine_architecture(topology, NVLink, chiplet)
                request_packet = {}
                for tr_path in target_path:
                    if "kernels" in tr_path:
                        pass
                    elif "synthetic_trace" in tr_path:
                        file_trace = str(kernel_num) + "/" + file_trace
                    file = open(tr_path + file_trace, "r")
                    raw_content = ""
                    if file.mode == "r":
                        raw_content = file.readlines()
                    file.close()
                    lined_list = []
                    for line in raw_content:
                        item = [x for x in line.split("\t") if x not in ['', '\t']]
                        lined_list.append(item)
                    for i in range(len(lined_list)):
                        if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
                            if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
                        else:
                            request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
                    del (raw_content)
                    del (lined_list)

                    if tr_path.__str__() == base_emp:
                        emp_request_injected_traffic = generate_request_injected_traffic(request_packet)
                        emp_reply_injected_traffic = generate_reply_injected_traffic(request_packet, "AccelSim")
                        emp_packet_latency_dist = measure_packet_latency(request_packet, "AccelSim")
                        emp_network_latency_dist = measure_network_latency(request_packet)
                    elif tr_path.__str__() == base_syn:
                        syn_request_injected_traffic = generate_request_injected_traffic(request_packet)
                        syn_reply_injected_traffic = generate_reply_injected_traffic(request_packet, "Synthetic")
                        syn_packet_latency_dist = measure_packet_latency(request_packet, "Synthetic")
                        syn_network_latency_dist = measure_network_latency(request_packet)
                    request_packet = {}

                kernel_name = int(input_.split("_")[-1].split(".")[0])
                compare_overall_traffic_cdf(emp_request_injected_traffic, syn_request_injected_traffic, "request", base_emp, kernel_name)
                compare_overall_traffic_cdf(emp_reply_injected_traffic, syn_reply_injected_traffic, "reply", base_emp, kernel_name)
                compare_burst_variability(emp_request_injected_traffic, syn_request_injected_traffic, "request", base_emp, kernel_name)
                compare_burst_variability(emp_reply_injected_traffic, syn_reply_injected_traffic, "reply", base_emp, kernel_name)
                compare_traffic_pattern(emp_request_injected_traffic, syn_request_injected_traffic, chiplet_num, base_emp, kernel_name)
                compare_packet_latency(emp_packet_latency_dist, syn_packet_latency_dist, base_emp, kernel_name)
                compare_network_latency(emp_network_latency_dist, syn_network_latency_dist, base_emp, kernel_name)
                cnf_graph(target_path, file_trace.split("/")[1], topo, nv, ch, kernel_name)
                #calculate_link_usage.calculate_link_usage_(target_path, kernel_name)
                gc.enable()
                gc.collect()