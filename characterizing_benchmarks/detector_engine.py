import os
import re
import gc
import numpy as np
from matplotlib import pyplot as plt


def detector_engine(traffic):
    off_cycle = 0
    off_counter = 0
    off_burst_sequence = {}
    off_flag = 0
    on_flag = 0
    for cyc, byte in traffic.items():
        if byte == 0:
            if off_flag == 0:
                off_cycle = cyc
                off_flag = 1
        elif byte != 0:
            if off_flag == 1:
                off_flag = 0
                off_burst_sequence[off_counter] = cyc - off_cycle
                off_counter += 1
            if on_flag == 0:
                on_cycle = cyc
                on_flag = 1
    avg = np.mean(list(off_burst_sequence.values()))
    std = np.std(list(off_burst_sequence.values()))
    maximum = max(list(off_burst_sequence.values()))
    minimum = min(list(off_burst_sequence.values()))
    print(avg)
    print(std)
    print(minimum)
    print(maximum)
    plt.plot(off_burst_sequence.keys(), off_burst_sequence.values())
    plt.show()
    plt.close()


if __name__ == "__main__":
    #emp = "../benchmarks/stencil/torus/NVLink4/4chiplet/parboil-stencil_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/b+tree/torus/NVLink4/4chiplet/b+tree-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/spmv/torus/NVLink4/4chiplet/parboil-spmv_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/hotspot3D/torus/NVLink4/4chiplet/hotspot3D-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/3mm/new/torus/NVLink4/4chiplet/polybench-3mm_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/mri-gridding/torus/NVLink4/4chiplet/parboil-mri-gridding_NV4_1vc_4ch_2Dtorus_trace.txt"
    emp = "../benchmarks/2mm/torus/NVLink4/4chiplet/polybench-2mm_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/lavaMD/torus/NVLink4/4chiplet/lavaMD-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/kmeans/torus/NVLink4/4chiplet/kmeans-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/hybridsort/torus/NVLink4/4chiplet/hybridsort-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/particlefinder/torus/NVLink4/4chiplet/particlefilter_float-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/2DConvolution/torus/NVLink4/4chiplet/polybench-2DConvolution_NV4_1vc_4ch_2Dtorus_trace.txt"
    #emp = "../benchmarks/AlexNet/torus/NVLink4/4chiplet/tango-alexnet_NV4_1vc_4ch_2Dtorus_trace.txt"
    chiplet_num = -1
    request_packet = {}
    sub_str = os.path.basename(emp).split("_")
    for sub_s in sub_str:
        if sub_str.index(sub_s) != 0:
            if sub_s.__contains__("ch"):
                chiplet_num = int(re.split(r'(\d+)', sub_s)[1])
                break
    file = open(emp, "r")
    raw_content = ""
    if file.mode == "r":
        raw_content = file.readlines()
    file.close()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    for i in range(len(lined_list)):
        if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
            if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        else:
            request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
    del (raw_content)
    del (lined_list)
    traffic = {}
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "request injected":
                src = int(request_packet[id][j][1].split(": ")[1])
                dst = int(request_packet[id][j][2].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if cycle not in traffic.keys():
                    traffic[cycle] = byte
                else:
                    traffic[cycle] += byte

    minimum = min(list(traffic.keys()))
    maximum = max(list(traffic.keys()))
    for i in range(minimum, maximum):
        if i not in traffic.keys():
            traffic[i] = 0
    traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
    detector_engine(traffic)
    gc.enable()
    gc.collect()