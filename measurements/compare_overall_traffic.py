import seaborn as sn
import os
import re
import gc
from measurements.cnf import *


def Hellinger_distance(emp, syn):
    local_emp = emp
    local_syn = syn
    for item, pdf in local_emp.items():
        if item not in local_syn.keys():
            local_syn[item] = 0
    for item, pdf in local_syn.items():
        if item not in local_emp.keys():
            emp[item] = 0
    local_emp = dict(sorted(local_emp.items(), key=lambda x: x[0]))
    local_syn = dict(sorted(local_syn.items(), key=lambda x: x[0]))
    sum = 0
    for item in local_syn.keys():
        p = local_emp[item]
        q = local_syn[item]
        sum += (np.sqrt(p) - np.sqrt(q))**2
    total = np.sqrt(sum)/np.sqrt(2)
    gc.enable()
    gc.collect()
    return total


def MSE(emp, syn):
    local_emp = emp
    local_syn = syn
    for item, pdf in local_emp.items():
        if item not in local_syn.keys():
            local_syn[item] = 0
    for item, pdf in local_syn.items():
        if item not in local_emp.keys():
            emp[item] = 0
    local_emp = dict(sorted(local_emp.items(), key=lambda x: x[0]))
    local_syn = dict(sorted(local_syn.items(), key=lambda x: x[0]))
    sum = 0
    for item in local_syn.keys():
        p = local_emp[item]
        q = local_syn[item]
        sum += (p - q)**2
    total = sum/len(syn.keys())
    gc.enable()
    gc.collect()
    return total


def kullback_leibler_divergence(emp, syn):
    local_emp = emp
    local_syn = syn
    for item, pdf in local_emp.items():
        if item not in local_syn.keys():
            local_syn[item] = 0
    for item, pdf in local_syn.items():
        if item not in local_emp.keys():
            emp[item] = 0
    local_emp = dict(sorted(local_emp.items(), key=lambda x: x[0]))
    local_syn = dict(sorted(local_syn.items(), key=lambda x: x[0]))
    sum = 0
    for item in local_syn.keys():
        p = local_emp[item]
        q = local_syn[item]
        try:
            sum += p*(np.log(p/q))
        except ZeroDivisionError:
            continue
    gc.enable()
    gc.collect()
    return sum


def generate_request_injected_traffic(request_packet, string):
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
    plt.figure(figsize=(20, 8))
    plt.plot(aggregate_traffic.keys(), aggregate_traffic.values())
    if string == "AccelSim":
        plt.title("AccelSim traffic")
    elif string == "Synthetic":
        plt.title("Synthetic traffic")
    plt.xlabel("cycle")
    plt.ylabel("aggregate request bytes")
    plt.show()
    del(aggregate_traffic)
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
    aggregate_traffic = dict(sorted(aggregate_traffic.items(), key=lambda x: x[0]))
    plt.figure(figsize=(20, 8))
    plt.plot(aggregate_traffic.keys(), aggregate_traffic.values(), marker="*")
    if string == "AccelSim":
        plt.title("AccelSim traffic")
    elif string == "Synthetic":
        plt.title("Synthetic traffic")
    plt.xlabel("cycle")
    plt.ylabel("aggregate reply bytes")
    plt.show()
    del (aggregate_traffic)
    gc.enable()
    gc.collect()
    return traffic


def compare_overall_traffic_cdf(emp_injected_traffic, syn_injected_traffic, string):
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

    plt.plot(list(emp_cdf.keys()), list(emp_cdf.values()), color='red', linestyle='--', marker='o', label="AccelSim")
    plt.plot(list(syn_cdf.keys()), list(syn_cdf.values()), color='blue', linestyle='-', marker='*', label="Synthetic")
    plt.legend()
    plt.title("aggregate " + string + " CDF")
    plt.xlabel("aggregate " + string + " byte")
    plt.ylabel("CDF")
    plt.show()
    plt.close()
    H = Hellinger_distance(emp_cdf, syn_cdf)
    KL = kullback_leibler_divergence(emp_cdf, syn_cdf)
    print(string + " comparison: ")
    mse = MSE(emp_cdf, syn_cdf)
    print("hellinger: " + str(H))
    print("KL divergence: " + str(KL))
    print("MSE: " + str(mse))
    gc.enable()
    gc.collect()


def compare_traffic_pattern(emp_injected_traffic, syn_injected_traffic, chiplet_num):
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

    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(20, 20))
    fig.subplots_adjust(wspace=0.01)
    sn.heatmap(data1, cmap="hot", ax=ax1, cbar=True, linewidth=.3, annot=True)
    sn.heatmap(data2, cmap="hot", ax=ax2, cbar=True, linewidth=.3, annot=True)
    ax1.set_title("AccelSim Traffic Pattern")  # AccelSim link usage (Byte/Cycle)      AccelSim Traffic Pattern
    ax2.set_title("synthetic Traffic Pattern")  # BookSim link usage (Byte/Cycle)       BookSim Traffic Pattern
    ax2.yaxis.tick_right()

    fig.subplots_adjust(wspace=0.1)
    plt.show()
    gc.enable()
    gc.collect()


def compare_burst_variability(emp_injected_traffic, syn_injected_traffic, string):
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
    plt.plot(list(emp_burst.keys()), list(emp_burst.values()), color='green', linestyle='--', marker='o', label="AccelSim")
    plt.plot(list(syn_burst.keys()), list(syn_burst.values()), color='black', linestyle='-', marker='*', label="Synthetic")
    plt.legend()
    plt.xlabel("burst per unit time")
    plt.ylabel("CDF")
    plt.title(string + " network burst variation")
    plt.show()
    plt.close()
    H = Hellinger_distance(emp_burst, syn_burst)
    KL = kullback_leibler_divergence(emp_burst, syn_burst)
    mse = MSE(emp_burst, syn_burst)
    print("burst comparison: ")
    print("hellinger: " + str(H))
    print("KL divergence: " + str(KL))
    print("MSE: " + str(mse))
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


def compare_packet_latency(emp, syn):
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
    plt.plot(emp.keys(), emp.values(), color='red', linestyle='--', marker='o', label="AccelSim")
    plt.plot(syn.keys(), syn.values(), color='black', linestyle='-', marker='*', label="Synthetic")
    plt.title("packet latency")
    plt.xlabel("end-to-end latency (cycle)")
    plt.ylabel("CDF")
    plt.legend()
    plt.show()
    plt.close()
    emp = dict(sorted(emp.items(), key=lambda x: x[0]))
    syn = dict(sorted(syn.items(), key=lambda x: x[0]))
    H = Hellinger_distance(emp, syn)
    KL = kullback_leibler_divergence(emp, syn)
    mse = MSE(emp, syn)
    print("packet latency comparison: ")
    print("hellinger: " + str(H))
    print("KL divergence: " + str(KL))
    print("MSE: " + str(mse))
    gc.enable()
    gc.collect()


def measure_network_latency(packet, string):
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


def compare_network_latency(emp, syn):
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
    plt.plot(emp.keys(), emp.values(), color='red', linestyle='--', marker='o', label="AccelSim")
    plt.plot(syn.keys(), syn.values(), color='black', linestyle='-', marker='*', label="Synthetic")
    plt.title("Network latency")
    plt.xlabel("Network latency (cycle)")
    plt.ylabel("CDF")
    plt.legend()
    plt.show()
    gc.enable()
    gc.collect()


if __name__ == "__main__":
    #emp = "../benchmarks/stencil/torus/NVLink4/4chiplet/parboil-stencil_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/b+tree/torus/NVLink4/4chiplet/b+tree-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/spmv/torus/NVLink4/4chiplet/parboil-spmv_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/hotspot3D/torus/NVLink4/4chiplet/hotspot3D-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/3mm/new/torus/NVLink4/4chiplet/polybench-3mm_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/2mm/torus/NVLink4/4chiplet/polybench-2mm_NV4_1vc_4ch_2Dtorus_trace.txt"
    emp = "../benchmarks/2DConvolution/torus/NVLink4/4chiplet/polybench-2DConvolution_NV4_1vc_4ch_2Dtorus_trace.txt"
    #syn = "../b_ooksim2/src/examples/out.txt"
    syn = "/home/ben/Downloads/booksim2.0-2014.03.08/src/examples/out.txt"
    chiplet_num = -1
    sub_str = os.path.basename(emp).split("_")
    for sub_s in sub_str:
        if sub_str.index(sub_s) != 0:
            if sub_s.__contains__("ch"):
                chiplet_num = int(re.split(r'(\d+)', sub_s)[1])
                break

    request_packet = {}
    emp_request_injected_traffic = {}
    syn_request_injected_traffic = {}
    emp_reply_injected_traffic = {}
    syn_reply_injected_traffic = {}
    emp_packet_latency_dist = {}
    syn_packet_latency_dist = {}
    emp_network_latency_dist = {}
    syn_network_latency_dist = {}
    input_list = [emp, syn]
    for input_ in input_list:
        file = open(input_, "r")
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

        if input_.__str__() == emp:
            pass
            emp_request_injected_traffic = generate_request_injected_traffic(request_packet, "AccelSim")
            emp_reply_injected_traffic = generate_reply_injected_traffic(request_packet, "AccelSim")
            emp_packet_latency_dist = measure_packet_latency(request_packet, "AccelSim")
            #emp_network_latency_dist = measure_network_latency(request_packet, "AccelSim")
            #cnf_graph(request_packet, chiplet_num, "AccelSim")
        elif input_.__str__() == syn:
            pass
            syn_request_injected_traffic = generate_request_injected_traffic(request_packet, "Synthetic")
            syn_reply_injected_traffic = generate_reply_injected_traffic(request_packet, "Synthetic")
            syn_packet_latency_dist = measure_packet_latency(request_packet, "Synthetic")
            #syn_network_latency_dist = measure_network_latency(request_packet, "Synthetic")
            #cnf_graph(request_packet, chiplet_num, "Synthetic")
        request_packet = {}
    del(request_packet)

    compare_overall_traffic_cdf(emp_request_injected_traffic, syn_request_injected_traffic, "request")
    compare_overall_traffic_cdf(emp_reply_injected_traffic, syn_reply_injected_traffic, "reply")
    compare_burst_variability(emp_request_injected_traffic, syn_request_injected_traffic, "request")
    compare_burst_variability(emp_reply_injected_traffic, syn_reply_injected_traffic, "reply")
    #compare_traffic_pattern(emp_request_injected_traffic, syn_request_injected_traffic, chiplet_num=chiplet_num)
    compare_packet_latency(emp_packet_latency_dist, syn_packet_latency_dist)
    #compare_network_latency(emp_network_latency_dist, syn_network_latency_dist)
    gc.enable()
    gc.collect()