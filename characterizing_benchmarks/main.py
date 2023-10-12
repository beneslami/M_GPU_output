import gc
import os
import sys
sys.path.append("../")
import benchlist
from analysis import *
from measurements.sensitivity_tests import bandwidth_sensitivity
from re_arrange_benchmark import *


if __name__ == "__main__":
    suits = benchlist.suits
    benchmarks = benchlist.benchmarks
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet_num = benchlist.chiplet_num
    path = benchlist.bench_path

    for suite in suits:
        if os.path.exists(path + suite) and suite == "SDK":
            for bench in benchmarks[suite]:
                if os.path.exists(path + suite + "/" + bench) and bench == "hsoptical" or bench == "nvjpeg":
                    organizing_benchmark(path, suite, bench)
                    print(Fore.GREEN + "organizing files for benchmark " + bench + " from " + suite + " suite " + " [done " + u'\u2713]' + Fore.RESET)
                    kernel_analysis(path, suite, bench)
                    print(Fore.GREEN + "kernel analysis for benchmark " + bench + " from " + suite + " suite " + " [done " + u'\u2713]' + Fore.RESET)
                    link_analysis(path, suite, bench)
                    print(Fore.GREEN + "NVLink comparison for benchmark " + bench + " from " + suite + " suite " + " [done " + u'\u2713]' + Fore.RESET)
                    topology_analysis(path, suite, bench)
                    print(Fore.GREEN + "bandwodth/topology comparison for benchmark " + bench + " from " + suite + " suite " + " [done " + u'\u2713]' + Fore.RESET)
                    bandwidth_sensitivity(path, suite, bench)
                    print(Fore.GREEN + "bandwodth/topology plot for benchmark " + bench + " from " + suite + " suite " + " [done " + u'\u2713]' + Fore.RESET)
    gc.enable()
    gc.collect()
