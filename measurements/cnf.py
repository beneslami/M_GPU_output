import numpy as np
import matplotlib.pyplot as plt


def cnf_graph(request_packet, chiplet_num, string):
    total_sm = 32 * chiplet_num
    injection_rate = {}
    lat = {}
    throughput = {}
    occs = {}
    occupancy = {}
    latency = {}
    cnf = {}
    cycle1 = 0
    flag = 0
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "request injected":
                flag = 1
                src = int(request_packet[id][j][1].split(": ")[1])
                dst = int(request_packet[id][j][2].split(": ")[1])
                cycle1 = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                occ = int(request_packet[id][j][8].split(": ")[1])
                if cycle1 not in injection_rate.keys():
                    injection_rate[cycle1] = 1
                else:
                    injection_rate[cycle1] += 1
                if cycle1 not in occs.keys():
                    occs[cycle1] = occ
                else:
                    occs[cycle1] += occ
            elif request_packet[id][j][0] == "request received":
                if flag == 1:
                    flag = 0
                    cycle2 = int(request_packet[id][j][5].split(": ")[1])
                    if cycle1 not in lat.keys():
                        lat.setdefault(cycle1, []).append(cycle2 - cycle1)
                    else:
                        lat[cycle1].append(cycle2 - cycle1)
            elif request_packet[id][j][0] == "reply injected":
                    src = int(request_packet[id][j][1].split(": ")[1])
                    dst = int(request_packet[id][j][2].split(": ")[1])
                    cycle3 = int(request_packet[id][j][5].split(": ")[1])
                    byte = int(request_packet[id][j][7].split(": ")[1])
                    occ = int(request_packet[id][j][8].split(": ")[1])
                    if cycle3 not in occs.keys():
                        occs[cycle3] = occ
                    else:
                        occs[cycle3] += occ

    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "inj rtr":
                src = int(request_packet[id][j][1].split(": ")[1])
                dst = int(request_packet[id][j][2].split(": ")[1])
                chip = int(request_packet[id][j][6].split(": ")[1])
                type = int(request_packet[id][j][4].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if (src == chip and (type == 2 or type == 0)) or (dst == chip and (type == 1 or type == 3)):
                    if cycle not in throughput.keys():
                        throughput[cycle] = byte
                    else:
                        throughput[cycle] += byte

    for cyc, rate in injection_rate.items():
        injection_rate[cyc] = rate/total_sm

    temp_val = []

    for cyc, rate in injection_rate.items():
        if rate not in cnf.keys():
            cnf.setdefault(rate, [])
        if rate not in occupancy.keys():
            occupancy.setdefault(rate, [])
        if rate not in latency.keys():
            latency.setdefault(rate, {})
        if cyc in throughput.keys():
            cnf[rate].append(throughput[cyc])
        else:
            cnf[rate].append(0)
        if cyc in occs.keys():
            occupancy[rate].append(occs[cyc])
        if cyc in lat.keys():
            latency[rate] = np.mean(lat[cyc])/1.132
            temp_val.append(np.mean(lat[cyc]))

    cnf = dict(sorted(cnf.items(), key=lambda x: x[0]))
    latency = dict(sorted(latency.items(), key=lambda x: x[0]))
    occupancy = dict(sorted(occupancy.items(), key=lambda x: x[0]))
    throughput_graph = {}
    for rate, thr_list in cnf.items():
        throughput_graph[rate] = np.mean(thr_list)*1.132
    for rate, occ_list in occupancy.items():
        occupancy[rate] = np.mean(occ_list)

    #model1 = np.poly1d(np.polyfit(list(throughput_graph.keys()), list(throughput_graph.values()), 3))
    plt.plot(throughput_graph.keys(), throughput_graph.values(), marker="*", label="observation")
    #plt.plot(throughput_graph.keys(), model1(list(throughput_graph.keys())), label="fitted function")
    plt.xlabel("injection rate")
    plt.ylabel("throughput (GB/s)")
    plt.title(string + " throughput")
    plt.legend()
    plt.show()
    plt.close()

    #model1 = np.poly1d(np.polyfit(list(occupancy.keys()), list(occupancy.values()), 3))
    plt.plot(occupancy.keys(), occupancy.values(), marker="o", label="observed occupancy")
    #plt.plot(occupancy.keys(), model1(list(occupancy.keys())), label="fitted function", color='red')
    plt.xlabel("injection rate")
    plt.ylabel("total occupancy")
    plt.title(string + " occupancy")
    plt.legend()
    plt.show()
    plt.close()

    #model1 = np.poly1d(np.polyfit(list(latency.keys()), list(latency.values()), 1))
    plt.plot(latency.keys(), latency.values(), marker="*", label="observed latency")
    #plt.plot(latency.keys(), model1(list(latency.keys())), label="fitted function", color='red')
    plt.xlabel("injection rate")
    plt.ylabel("latency")
    plt.title(string + " latency")
    plt.legend()
    plt.show()
    plt.close()