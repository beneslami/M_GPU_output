import gc
import os
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

    path = "/home/ben/Desktop/benchmarks/"
    for suite in suits:
        if suite == "rodinia":
            for bench in benchmarks[suite]:
                if bench == "huffman":
                    for topo in topology:
                        for nv in NVLink:
                            for ch in chiplet_num:
                                sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                                if len(os.listdir(os.path.dirname(os.path.dirname(sub_path)))) != 0:
                                    rearrange_traces(sub_path, suite, bench, topo, nv, ch)
                                    check_kernel_traces(sub_path, suite, bench, topo, nv, ch)
                                    chip_num = int(ch[0])
                                    for trace_file in os.listdir(sub_path):
                                        if Path(trace_file).suffix == '.txt':
                                            if os.path.getsize(sub_path + trace_file) > 100000:
                                                start_processing_portal(sub_path + trace_file, chip_num)
                                                trace_generator(sub_path + trace_file)
                                else:
                                    print(Fore.YELLOW + "directory " + sub_path + " is empty" + Fore.WHITE)

    gc.enable()
    gc.collect()