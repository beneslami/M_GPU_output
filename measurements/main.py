import gc
import os

import benchlist
import sensitivity_tests
from colorama import Fore

if __name__ == "__main__":
    suits = benchlist.suits
    benchmarks = benchlist.benchmarks
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet_num = benchlist.chiplet_num
    path = benchlist.bench_path

    for suite in suits:
        if suite == "rodinia":
            for bench in benchmarks[suite]:
                if bench == "huffman":
                    sub_path = path + suite + "/" + bench + "/"
                    if {"torus", "ring", "mesh", "fly"}.issubset(set(os.listdir(sub_path))):
                        sensitivity_tests.bandwidth_sensitivity(sub_path, suite, bench)
                    else:
                        print(Fore.RED + "benchmark " + bench + " from suite " + suite + " has no complete report" + Fore.WHITE)

    #sensitivity_tests.latency_sensitivity_test("/home/ben/Desktop/outputs/rodinia-huffman")
    #sensitivity_tests.ipc_sensitivity_test("/home/ben/Desktop/outputs/rodinia-huffman")
    #sensitivity_tests.throughput_sensitivity("/home/ben/Desktop/outputs/rodinia-huffman")

    gc.enable()
    gc.collect()