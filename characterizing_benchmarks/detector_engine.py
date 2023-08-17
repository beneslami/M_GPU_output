import os
import re
import gc
import numpy as np
import benchlist


def kernel_detection(input_):
    file_name = os.path.basename(input_).split("_")[0]
    traffic_type = benchlist.traffic_type

    for type, bench_list in traffic_type.items():
        if file_name in bench_list:
            return type
