import os
import sys
import pandas as pd
sys.path.append("..")
import benchlist
from sensitivity_tests import *


def is_sensitivie(suite, bench, kernel_num):
    info = pd.read_csv(benchlist.bench_path + "4chiplet_NVLink4_characterization.csv")
    ipc = []
    for i in info.index:
        if info["suite"][i] == suite:
            if info["benchmarks"][i] == bench:
                if info["kernels"][i] == kernel_num:
                    if info["hurst"][i] != -1 and info["IAT_CoV"][i] != -1 and info["Vol_CoV"][i] != -1 and info["Dur_CoV"][i] != -1:
                        ipc.append(info["ipc"][i])
    if len(ipc) == 4:
        if max(ipc) - min(ipc) >= 50:
            return True
        else:
            return False
    else:
        return False


if __name__ == "__main__":
    for suite in benchlist.suits:
        for bench in benchlist.benchmarks[suite]:
            chiplet_number_sensitivity(suite, bench)
            for ch in benchlist.chiplet_num:
                bandwidth_sensitivity(suite, bench, ch)