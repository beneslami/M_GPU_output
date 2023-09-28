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


if __name__ == "__main__":
    suits = benchlist.suits
    benchmarks = benchlist.benchmarks
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet_num = benchlist.chiplet_num
    path = benchlist.bench_path

    for suite in suits:
        if os.path.exists(path + suite) and suite == "shoc":
            for bench in benchmarks[suite]:
                if os.path.exists(path + suite + "/" + bench) and (bench == "Spmv"):
                    for topo in topology:
                        if os.path.exists(path + suite + "/" + bench + "/" + topo) and (topo == "torus"):
                            for nv in NVLink:
                                if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv) and nv == "NVLink3":
                                    for ch in chiplet_num:
                                        if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch):
                                            sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                                            benchTable = PrettyTable()
                                            benchTable.field_names = ["kernel_num", "hurst", "IAT CoV", "Vol CoV", "dur CoV", "ratio CoV", "R/W", "req/inst", "CTA", "local", "remote", "gpu_cycle", "instruction", "P latency", "N latency", "throughput", "ipc", "GPU occupancy"]
                                            if len(os.listdir(os.path.dirname(os.path.dirname(sub_path)))) != 0:
                                                rearrange_traces(sub_path, suite, bench, topo, nv, ch)
                                                check_kernel_traces(sub_path, suite, bench, topo, nv, ch)
                                                chip_num = int(ch[0])
                                                for trace_file in os.listdir(sub_path):
                                                    if Path(trace_file).suffix == '.txt':
                                                        information = []
                                                        start_processing_portal(sub_path + trace_file, chip_num)
                                                        information.append(int(trace_file.split(".")[0][-1]))
                                                        information.append(calculate_hurst(sub_path + trace_file, suite, bench, int(trace_file.split(".")[0][-1]))) #calculate Hurst
                                                        information.append(burstiness.measure_iat(sub_path + trace_file, suite, bench, int(trace_file.split(".")[0][-1]))) # caluclate burstiness
                                                        information.append(burstiness.measure_vol(sub_path + trace_file, suite, bench, int(trace_file.split(".")[0][-1]))) # caluclate burstiness
                                                        information.append(burstiness.measure_duration(sub_path + trace_file, suite, bench, int(trace_file.split(".")[0][-1]))) # caluclate burstiness
                                                        information.append(burstiness.measure_burst_ratio(sub_path + trace_file, suite, bench, int(trace_file.split(".")[0][-1]))) # caluclate burstiness
                                                        information.append(measure_packet_distribution(sub_path + trace_file, suite, bench, int(trace_file.split(".")[0][-1]))) # calculate read/write intensity
                                                        req_inst, remote, local, CTA, cycle, inst, occ, P_latency, N_latency, throughput, ipc = extract_kernel_info(
                                                            os.path.dirname(os.path.dirname(sub_path)), suite, bench, topo, nv, ch, int(trace_file.split(".")[0][-1]))
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
                                                benchTable.sortby = "kernel_num"
                                                with open(os.path.dirname(os.path.dirname(sub_path)) + "/bench_info.csv", "w") as file:
                                                    file.write(benchTable.get_csv_string())
                                                print(benchTable)
                                            else:
                                                print(Fore.YELLOW + "directory " + sub_path + " is empty" + Fore.RESET)

                                            # TODO: ipc_kernel function should be invoked here

    gc.enable()
    gc.collect()
