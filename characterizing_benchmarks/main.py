import gc
import os
import sys
sys.path.append("../")
import benchlist
from pathlib import Path
from check_benchmark_traces import *
from re_arrange_benchmark import *
from processing import *
from trace_generator import *


if __name__ == "__main__":
    suits = benchlist.suits
    benchmarks = benchlist.benchmarks
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet_num = benchlist.chiplet_num
    path = benchlist.bench_path

    for suite in suits:
        if os.path.exists(path + suite) and suite == "deepbench":
            for bench in benchmarks[suite]:
                if os.path.exists(path + suite + "/" + bench) and (bench == "gemm"):
                    for topo in topology:
                        if os.path.exists(path + suite + "/" + bench + "/" + topo): #and topo != "torus":
                            for nv in NVLink:
                                if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv): #and nv == "NVLink4":
                                    for ch in chiplet_num:
                                        if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch):
                                            sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                                            if len(os.listdir(os.path.dirname(os.path.dirname(sub_path)))) != 0:
                                                rearrange_traces(sub_path, suite, bench, topo, nv, ch)
                                                check_kernel_traces(sub_path, suite, bench, topo, nv, ch)
                                                chip_num = int(ch[0])
                                                for trace_file in os.listdir(sub_path):
                                                    if Path(trace_file).suffix == '.txt':
                                                        if os.path.getsize(sub_path + trace_file) > 10000:
                                                            start_processing_portal(sub_path + trace_file, chip_num)
                                                            #trace_generator(sub_path + trace_file)
                                            else:
                                                print(Fore.YELLOW + "directory " + sub_path + " is empty" + Fore.RESET)
                                            # TODO: ipc_kernel function should be invoked here
    gc.enable()
    gc.collect()
