import gc
import os
import sys
sys.path.append("../")
import benchlist
from analysis import *
from measurements.sensitivity_tests import bandwidth_sensitivity, kernel_sensitivity_test, iat_sensitivity_test, burst_length_sensitivity_test, burst_volume_sensitivity_test
from re_arrange_benchmark import *
from collect_data import data_collection_wrapper
from burstiness import burst_feature_extraction


if __name__ == "__main__":
    suits = benchlist.suits
    benchmarks = benchlist.benchmarks
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    chiplet_num = benchlist.chiplet_num
    path = benchlist.bench_path
    ch = "4chiplet"
    for suite in suits:
        if os.path.exists(path + suite) and suite == "pannotia":
            for bench in benchmarks[suite]:
                if os.path.exists(path + suite + "/" + bench) and bench == "fw-block":
                    organizing_benchmark(path, suite, bench, ch)
                    print(Fore.GREEN + "organizing files for benchmark " + bench + " from " + suite + " suite " + " [done " + u'\u2713]' + Fore.RESET)
                    kernel_analysis(path, suite, bench, ch)
                    print(Fore.GREEN + "kernel analysis for benchmark " + bench + " from " + suite + " suite " + " [done " + u'\u2713]' + Fore.RESET)
                    link_analysis(path, suite, bench, ch)
                    print(Fore.GREEN + "NVLink comparison for benchmark " + bench + " from " + suite + " suite " + " [done " + u'\u2713]' + Fore.RESET)
                    topology_analysis(path, suite, bench, ch)
                    print(Fore.GREEN + "bandwodth/topology comparison for benchmark " + bench + " from " + suite + " suite " + " [done " + u'\u2713]' + Fore.RESET)
                    bandwidth_sensitivity(path, suite, bench, ch)
                    print(Fore.GREEN + "bandwodth/topology plot for benchmark " + bench + " from " + suite + " suite " + " [done " + u'\u2713]' + Fore.RESET)
    data_collection_wrapper(ch)
    burst_feature_extraction(ch)
    kernel_sensitivity_test(ch)
    iat_sensitivity_test(ch)
    burst_volume_sensitivity_test(ch)
    burst_length_sensitivity_test(ch)
    gc.enable()
    gc.collect()
