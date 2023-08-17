import os.path

import numpy as np
import matplotlib.pyplot as plt


def return_coefficient(topo, nv, chiplet_num):
    bw_coef = -1
    if topo == "ring":
        if nv == 4:
            bw_coef = 5.625
        elif nv == 3:
            bw_coef = 3.75
        elif nv == 2:
            bw_coef = 1.875
        elif nv == 1:
            bw_coef = 1
    elif topo == "mesh":
        if nv == 4:
            bw_coef = 2.812
        elif nv == 3:
            bw_coef = 1.875
        elif nv == 2:
            bw_coef = 0.937
        elif nv == 1:
            bw_coef = 0.5
    elif topo == "fly":
        if nv == 4:
            if chiplet_num == 4:
                bw_coef = 5.625
            elif chiplet_num == 8:
                bw_coef = 3.75
            elif chiplet_num == 16:
                bw_coef = 2.812
        elif nv == 3:
            if chiplet_num == 4:
                bw_coef = 3.75
            elif chiplet_num == 8:
                bw_coef = 2.5
            elif chiplet_num == 16:
                bw_coef = 1.875
        elif nv == 2:
            if chiplet_num == 4:
                bw_coef = 1.875
            elif chiplet_num == 8:
                bw_coef = 1
            elif chiplet_num == 16:
                bw_coef = 0.75
        elif nv == 1:
            if chiplet_num == 4:
                bw_coef = 1
            elif chiplet_num == 8:
                bw_coef = 0.666
            elif chiplet_num == 16:
                bw_coef = 0.5
    elif topo == "torus":
        if nv == 4:
            bw_coef = 2.812
        elif nv == 3:
            bw_coef = 1.875
        elif nv == 2:
            bw_coef = 0.937
        elif nv == 1:
            bw_coef = 0.5
    return bw_coef


def measure_metrics(request_packet, chiplet_num):
    total_sm = 32 * chiplet_num
    injection_rate = {}
    lat = {}
    throughput = {}
    occs = {}
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
        injection_rate[cyc] = rate / total_sm
    return injection_rate, throughput, occs, lat


def cnf_graph(target_path, input_, topo, nv, ch, kernel_name):
    emp_injection_rate = {}
    syn_injection_rate = {}
    emp_throughput = {}
    syn_throughput = {}
    emp_occs = {}
    syn_occs = {}
    emp_lat = {}
    syn_lat = {}

    for tr_path in target_path:
        file = ""
        if "kernels" in tr_path:
            file = tr_path + input_
        elif "synthetic_trace" in tr_path:
            file = tr_path + str(kernel_name) + "/" + input_
        file = open(file, "r")
        raw_content = ""
        if file.mode == "r":
            raw_content = file.readlines()
        file.close()
        lined_list = []
        for line in raw_content:
            item = [x for x in line.split("\t") if x not in ['', '\t']]
            lined_list.append(item)
        request_packet = {}
        for i in range(len(lined_list)):
            if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
                if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                    request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
            else:
                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        del (raw_content)
        del (lined_list)
        if "kernels" in tr_path:
            emp_injection_rate, emp_throughput, emp_occs, emp_lat = measure_metrics(request_packet, ch)
        elif "synthetic_trace" in tr_path:
            syn_injection_rate, syn_throughput, syn_occs, syn_lat = measure_metrics(request_packet, ch)
    bw_coef = return_coefficient(topo, nv, ch)
    injection_rate_list = {"emp": emp_injection_rate, "syn": syn_injection_rate}
    throughput_list = {"emp": emp_throughput, "syn": syn_throughput}
    occs_list = {"emp": emp_occs, "syn": syn_occs}
    lat_list = {"emp": emp_lat, "syn": syn_lat}
    occup = {}
    latency = {}
    cnf = {}
    throughput = {}
    temp_val = []
    for name, injection_rate in injection_rate_list.items():
        if name not in cnf.keys():
            cnf.setdefault(name, {})
            occup.setdefault(name, {})
            latency.setdefault(name, {})
            throughput.setdefault(name, {})
        for cyc, rate in injection_rate.items():
            if rate not in cnf[name].keys():
                cnf[name].setdefault(rate, [])
            if rate not in occup[name].keys():
                occup[name].setdefault(rate, [])
            if rate not in latency[name].keys():
                latency[name].setdefault(rate, {})
            if cyc in throughput_list[name].keys():
                cnf[rate].append(throughput_list[name][cyc])
            else:
                cnf[name][rate].append(0)
            if cyc in occs_list[name].keys():
                occup[name][rate].append(occs_list[name][cyc])
            if cyc in lat_list[name].keys():
                latency[rate] = np.mean(lat_list[name][cyc])/bw_coef
                temp_val.append(np.mean(lat_list[name][cyc]))

    cnf = dict(sorted(cnf.items(), key=lambda x: x[0]))
    latency = dict(sorted(latency.items(), key=lambda x: x[0]))
    occup = dict(sorted(occup.items(), key=lambda x: x[0]))
    throughput_graph = {}
    for name in cnf.keys():
        if name not in throughput_graph.keys():
            throughput_graph.setdefault(name, {})
        for rate, thr_list in cnf[name].items():
            throughput_graph[name][rate] = np.mean(thr_list)*bw_coef
        for rate, occ_list in occup[name].items():
            occup[name][rate] = np.mean(occ_list)


    #model1 = np.poly1d(np.polyfit(list(throughput_graph.keys()), list(throughput_graph.values()), 3))
    plt.plot(throughput_graph["emp"].keys(), throughput_graph["emp"].values(), marker="o", label="AccelSim")
    plt.plot(throughput_graph["syn"].keys(), throughput_graph["syn"].values(), marker="o", label="synthetic")
    #plt.plot(throughput_graph.keys(), model1(list(throughput_graph.keys())), label="fitted function")
    plt.xlabel("injection rate")
    plt.ylabel("throughput (GB/s)")
    #plt.title(string + " throughput")
    plt.legend()
    plt.savefig(os.path.dirname(target_path[0]) + "/plots/" + str(kernel_name) + "/CNF_throughput_comparison.jpg")
    plt.close()

    #model1 = np.poly1d(np.polyfit(list(occupancy.keys()), list(occupancy.values()), 3))
    plt.plot(occup["emp"].keys(), occup["emp"].values(), marker="o", label="AccelSim")
    plt.plot(occup["syn"].keys(), occup["syn"].values(), marker="o", label="synthetic")
    #plt.plot(occupancy.keys(), model1(list(occupancy.keys())), label="fitted function", color='red')
    plt.xlabel("injection rate")
    plt.ylabel("total occupancy")
    #plt.title(string + " occupancy")
    plt.legend()
    plt.savefig(os.path.dirname(target_path[0]) + "/plots/" + str(kernel_name) + "/CNF_buffer_occupancy_comparison.jpg")
    plt.close()

    #model1 = np.poly1d(np.polyfit(list(latency.keys()), list(latency.values()), 1))
    plt.plot(latency["emp"].keys(), latency["emp"].values(), marker="o", label="AccelSim")
    plt.plot(latency["syn"].keys(), latency["syn"].values(), marker="o", label="synthetic")
    #plt.plot(latency.keys(), model1(list(latency.keys())), label="fitted function", color='red')
    plt.xlabel("injection rate")
    plt.ylabel("latency")
    #plt.title(string + " latency")
    plt.legend()
    plt.savefig(os.path.dirname(os.path.dirname(target_path[0])) + "/plots/" + str(kernel_name) + "/CNF_latency_comparison.jpg")
    plt.close()