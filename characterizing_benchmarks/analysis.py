import gc
import os
import sys
sys.path.append("../")
import benchlist
from pathlib import Path
from colorama import Fore
from check_benchmark_traces import *
from re_arrange_benchmark import *
from processing import *
from prettytable import PrettyTable
from range_dependency import calculate_hurst


topology = benchlist.topology
NVLink = benchlist.NVLink
chiplet_num = benchlist.chiplet_num


def kernel_analysis(path, suite, bench):
    for topo in topology:
        if os.path.exists(path + suite + "/" + bench + "/" + topo):
            for nv in NVLink:
                if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv):
                    for ch in chiplet_num:
                        if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch):
                            sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                            benchTable = PrettyTable()
                            benchTable.field_names = ["kernel_num", "hurst", "IAT CoV", "Vol CoV", "dur CoV", "ratio CoV", "R/W", "req/inst", "CTA", "local", "remote", "gpu_cycle", "instruction", "P latency", "N latency", "throughput", "ipc", "GPU occupancy"]
                            if len(os.listdir(os.path.dirname(os.path.dirname(sub_path)))) != 0:
                                chip_num = int(ch[0])
                                for trace_file in os.listdir(sub_path):
                                    if Path(trace_file).suffix == '.txt':
                                        if kernel_is_valid(sub_path, trace_file):
                                            information = []
                                            start_processing_portal(sub_path + trace_file, chip_num)
                                            information.append(int(trace_file.split(".")[0].split("_")[-1]))
                                            information.append(calculate_hurst(sub_path + trace_file, suite, bench, int(trace_file.split(".")[0].split("_")[-1]))) #calculate Hurst
                                            information.append(burstiness.measure_iat(sub_path + trace_file, suite, bench, int(trace_file.split(".")[0].split("_")[-1]))) # caluclate burstiness
                                            information.append(burstiness.measure_vol(sub_path + trace_file, suite, bench, int(trace_file.split(".")[0].split("_")[-1]))) # caluclate burstiness
                                            information.append(burstiness.measure_duration(sub_path + trace_file, suite, bench, int(trace_file.split(".")[0].split("_")[-1]))) # caluclate burstiness
                                            information.append(burstiness.measure_burst_ratio(sub_path + trace_file, suite, bench, int(trace_file.split(".")[0].split("_")[-1]))) # caluclate burstiness
                                            information.append(measure_packet_distribution(sub_path + trace_file, suite, bench, int(trace_file.split(".")[0].split("_")[-1]))) # calculate read/write intensity
                                            req_inst, remote, local, CTA, cycle, inst, occ, P_latency, N_latency, throughput, ipc = extract_kernel_info(
                                                os.path.dirname(os.path.dirname(sub_path)), suite, bench, topo, nv, ch, int(trace_file.split(".")[0].split("_")[-1]))
                                            information.append(req_inst)
                                            information.append(CTA)
                                            information.append(local)
                                            information.append(remote)
                                            information.append(cycle)
                                            information.append(inst)
                                            information.append(P_latency)
                                            information.append(N_latency)
                                            information.append(throughput)
                                            information.append(ipc)
                                            information.append(occ)
                                            benchTable.add_row(information)
                                        else:
                                            print(Fore.RED + "kernel " + trace_file + " not usable" + Fore.RESET)
                                benchTable.sortby = "kernel_num"
                                with open(os.path.dirname(os.path.dirname(sub_path)) + "/bench_info.csv", "w") as file:
                                    file.write(benchTable.get_csv_string())
                                print(benchTable)
                            else:
                                print(Fore.YELLOW + "directory " + sub_path + " is empty" + Fore.RESET)


def link_analysis(path, suite, bench):
    for topo in topology:
        if os.path.exists(path + suite + "/" + bench + "/" + topo):
            for ch in chiplet_num:
                data = {}
                for nv in NVLink:
                    if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch):
                        if len(os.listdir(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch)) != 0:
                            sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                            for trace_file in os.listdir(sub_path):
                                if Path(trace_file).suffix == '.txt':
                                    kernel_num = (int(trace_file.split(".")[0].split("_")[-1]))
                                    req_inst, _, _, _, cycle, _, _, P_latency, N_latency, throughput, ipc = extract_kernel_info(
                                        os.path.dirname(os.path.dirname(sub_path)), suite, bench, topo, nv, ch, kernel_num)
                                    if nv not in data.keys():
                                        data.setdefault(nv, {}).setdefault(kernel_num, [])
                                    else:
                                        if kernel_num not in data[nv].keys():
                                            data[nv].setdefault(kernel_num, [])
                                    data[nv][kernel_num].append(req_inst)
                                    data[nv][kernel_num].append(cycle)
                                    data[nv][kernel_num].append(P_latency)
                                    data[nv][kernel_num].append(N_latency)
                                    data[nv][kernel_num].append(throughput)
                                    data[nv][kernel_num].append(ipc)
                        else:
                            print(Fore.YELLOW + "directory " + path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + " is empty" + Fore.RESET)
                if len(data) != 0:
                    ipcTable = PrettyTable()
                    throughputTable = PrettyTable()
                    platTable = PrettyTable()
                    nlatTable = PrettyTable()
                    reqinstTable = PrettyTable()
                    cycleTable = PrettyTable()
                    cycleTable.field_names = ["kernel_num", "NVLink4", "NVLink3", "NVLink2", "NVLink1"]
                    reqinstTable.field_names = ["kernel_num", "NVLink4", "NVLink3", "NVLink2", "NVLink1"]
                    nlatTable.field_names = ["kernel_num", "NVLink4", "NVLink3", "NVLink2", "NVLink1"]
                    platTable.field_names = ["kernel_num", "NVLink4", "NVLink3", "NVLink2", "NVLink1"]
                    throughputTable.field_names = ["kernel_num", "NVLink4", "NVLink3", "NVLink2", "NVLink1"]
                    ipcTable.field_names = ["kernel_num", "NVLink4", "NVLink3", "NVLink2", "NVLink1"]
                    v = list(data.keys())
                    n = list(data["NVLink4"].keys())
                    for i in n:
                        ipc_row = [i]
                        throughput_row = [i]
                        plat_row = [i]
                        nlat_row = [i]
                        reqinst_row = [i]
                        cycle_row = [i]
                        for j in v:
                            ipc_row.append(data[j][i][5])
                            throughput_row.append(data[j][i][4])
                            plat_row.append(data[j][i][2])
                            nlat_row.append(data[j][i][3])
                            reqinst_row.append(data[j][i][0])
                            cycle_row.append(data[j][i][1])
                        ipcTable.add_row(ipc_row)
                        throughputTable.add_row(throughput_row)
                        platTable.add_row(plat_row)
                        nlatTable.add_row(nlat_row)
                        reqinstTable.add_row(reqinst_row)
                        cycleTable.add_row(cycle_row)
                    with open(path + suite + "/" + bench + "/" + topo + "/link_analysis_" + ch + ".csv", "w") as file:
                        file.write("ipc\n")
                        file.write(ipcTable.get_csv_string())
                        file.write("throughput\n")
                        file.write(throughputTable.get_csv_string())
                        file.write("packet latency\n")
                        file.write(platTable.get_csv_string())
                        file.write("network latency\n")
                        file.write(nlatTable.get_csv_string())
                        file.write("request per instruction\n")
                        file.write(reqinstTable.get_csv_string())
                        file.write("cycle\n")
                        file.write(cycleTable.get_csv_string()).


def find_the_number_of_fucking_kernels(suite, bench, topo, nv, ch):
    sub_path = benchlist.bench_path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/" 
    items = []
    for trace_file in os.listdir(sub_path):
        if Path(trace_file).suffix == '.txt':
            num = int(trace_file.split('.')[0].split('_')[-1])
            items.append(num)
    return items


def topology_analysis(path, suite, bench):
    sub_path = path + suite + "/" + bench + "/"
    data = {}
    if {"torus", "ring", "mesh", "fly"}.issubset(set(os.listdir(sub_path))):
        for topo in topology:
            if os.path.exists(path + suite + "/" + bench + "/" + topo):
                if topo not in data.keys():
                    data.setdefault(topo, {})
                for nv in NVLink:
                    if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv + "/"):
                        if nv not in data[topo].keys():
                            data[topo].setdefault(nv, {})
                        for ch in chiplet_num:
                            if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch):
                                if ch not in data[topo][nv].keys():
                                    data[topo][nv].setdefault(ch, {})
                                if len(os.listdir(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch)) != 0:
                                    sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                                    for trace_file in os.listdir(sub_path):
                                        if Path(trace_file).suffix == '.txt':
                                            kernel_num = (int(trace_file.split(".")[0].split("_")[-1]))
                                            req_inst, _, _, _, cycle, _, _, P_latency, N_latency, throughput, ipc = extract_kernel_info(
                                                os.path.dirname(os.path.dirname(sub_path)), suite, bench, topo, nv, ch,
                                                kernel_num)
                                            if kernel_num not in data[topo][nv][ch].keys():
                                                data[topo][nv][ch].setdefault(kernel_num, [])
                                            data[topo][nv][ch][kernel_num].append(req_inst)
                                            data[topo][nv][ch][kernel_num].append(cycle)
                                            data[topo][nv][ch][kernel_num].append(P_latency)
                                            data[topo][nv][ch][kernel_num].append(N_latency)
                                            data[topo][nv][ch][kernel_num].append(throughput)
                                            data[topo][nv][ch][kernel_num].append(ipc)
                                else:
                                    print(
                                        Fore.YELLOW + "directory " + path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + " is empty" + Fore.RESET)
        sub_path = path + suite + "/" + bench + "/"
        for ch in chiplet_num:
            if ch == "4chiplet":
                ipc_tableList = {}
                throughput_tableList = {}
                cycle_tableList = {}
                reqinst_tableList = {}
                plat_tableList = {}
                nlat_tableList = {}
                for nv in NVLink:
                    ipcTable = PrettyTable()
                    reqinstTable = PrettyTable()
                    throughputTable = PrettyTable()
                    cycleTable = PrettyTable()
                    platTable = PrettyTable()
                    nlatTable = PrettyTable()
                    ipcTable.field_names = ["kernel_num", "torus", "ring", "mesh", "fly"]
                    reqinstTable.field_names = ["kernel_num", "torus", "ring", "mesh", "fly"]
                    throughputTable.field_names = ["kernel_num", "torus", "ring", "mesh", "fly"]
                    cycleTable.field_names = ["kernel_num", "torus", "ring", "mesh", "fly"]
                    platTable.field_names = ["kernel_num", "torus", "ring", "mesh", "fly"]
                    nlatTable.field_names = ["kernel_num", "torus", "ring", "mesh", "fly"]
                    k = find_the_number_of_fucking_kernels(suite, bench, topo, nv, ch) # so frustrated at this point, tbh
                    for num in k:
                        ipc_items = [num]
                        throughput_items = [num]
                        reqinst_items = [num]
                        cycle_items = [num]
                        plat_items = [num]
                        nlat_items = [num]
                        for topo in topology:
                            reqinst_items.append(data[topo][nv][ch][num][0])
                            cycle_items.append(data[topo][nv][ch][num][1])
                            plat_items.append(data[topo][nv][ch][num][2])
                            nlat_items.append(data[topo][nv][ch][num][3])
                            throughput_items.append(data[topo][nv][ch][num][4])
                            ipc_items.append(data[topo][nv][ch][num][5])
                        ipcTable.add_row(ipc_items)
                        reqinstTable.add_row(reqinst_items)
                        throughputTable.add_row(throughput_items)
                        cycleTable.add_row(cycle_items)
                        platTable.add_row(plat_items)
                        nlatTable.add_row(nlat_items)
                    if nv not in ipc_tableList.keys():
                        ipc_tableList[nv] = ipcTable
                    if nv not in throughput_tableList.keys():
                        throughput_tableList[nv] = throughputTable
                    if nv not in cycle_tableList.keys():
                        cycle_tableList[nv] = cycleTable
                    if nv not in reqinst_tableList.keys():
                        reqinst_tableList[nv] = reqinstTable
                    if nv not in plat_tableList.keys():
                        plat_tableList[nv] = platTable
                    if nv not in nlat_tableList.keys():
                        nlat_tableList[nv] = nlatTable
                if len(ipc_tableList) != 0:
                    with open(sub_path + "topology_sensitivity_" + ch + ".csv", "w") as file:
                        for nv in ipc_tableList.keys():
                            file.write(nv + "\n")
                            file.write("ipc\n")
                            ipc_tableList[nv].sortby = "kernel_num"
                            file.write(ipc_tableList[nv].get_csv_string())
                            file.write("\nthroughput\n")
                            throughput_tableList[nv].sortby = "kernel_num"
                            file.write(throughput_tableList[nv].get_csv_string())
                            file.write("\ngpu cycle\n")
                            cycle_tableList[nv].sortby = "kernel_num"
                            file.write(cycle_tableList[nv].get_csv_string())
                            file.write("\nrequest per k. instruction\n")
                            reqinst_tableList[nv].sortby = "kernel_num"
                            file.write(reqinst_tableList[nv].get_csv_string())
                            file.write("\npacket latency\n")
                            plat_tableList[nv].sortby = "kernel_num"
                            file.write(plat_tableList[nv].get_csv_string())
                            file.write("\nnetwork latency\n")
                            nlat_tableList[nv].sortby = "kernel_num"
                            file.write(nlat_tableList[nv].get_csv_string())
                            file.write("\n\n")
    else:
        print(Fore.RED + "benchmark " + bench + " from suite " + suite + " has no complete report" + Fore.RESET)
