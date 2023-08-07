import gc
import os
import numpy as np


def trace_generator(input_):
    request_packet = {}
    kernel_num = os.path.basename(input_).split("_")[-1].split(".")[0]
    if kernel_num == "trace":
        kernel_num = 1
    else:
        kernel_num = int(kernel_num)
    base_path = os.path.dirname(input_)
    file2 = open(input_, "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    file2.close()
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

    trace = {}
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "request injected":
                src = int(request_packet[id][j][1].split(": ")[1])
                dst = int(request_packet[id][j][2].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                type = int(request_packet[id][j][4].split(": ")[1])
                if cycle not in trace.keys():
                    trace.setdefault(cycle, [])
                temp = []
                temp.append(src)
                temp.append(dst)
                num_flit = int(np.floor(byte / 40))
                if byte % 40 != 0:
                    num_flit += 1
                temp.append(num_flit)
                temp.append(type)
                trace[cycle].append(temp)
            if request_packet[id][j][0] == "reply injected":
                src = int(request_packet[id][j][2].split(": ")[1])
                dst = int(request_packet[id][j][1].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                type = int(request_packet[id][j][4].split(": ")[1])
                if cycle not in trace.keys():
                    trace.setdefault(cycle, [])
                temp = []
                temp.append(src)
                temp.append(dst)
                num_flit = int(np.floor(byte / 40))
                if byte % 40 != 0:
                    num_flit += 1
                temp.append(num_flit)
                temp.append(type)
                trace[cycle].append(temp)
    trace = dict(sorted(trace.items(), key=lambda x: x[0]))
    if os.path.exists(base_path + "/trace"):
        pass
    else:
        os.mkdir(base_path + "/trace/")
    with open(base_path + "/trace/trace" + str(kernel_num) + ".txt", "w") as file:
        start = list(trace.keys())[0]
        for cyc in trace.keys():
            for item_list in trace[cyc]:
                file.write(str((cyc - start) * 3) + "\t")
                for item in item_list:
                    file.write(str(item) + "\t")
                file.write("\n")
    gc.enable()
    gc.collect()


if __name__ == "__main__":
    request_packet = {}
    # homogeneous
    #input_ = "../benchmarks/mri-gridding/torus/NVLink4/4chiplet/parboil-mri-gridding_NV4_1vc_4ch_2Dtorus_trace.txt"
    # input_ = "../benchmarks/b+tree/torus/NVLink4/4chiplet/b+tree-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    # input_ = "../benchmarks/spmv/torus/NVLink4/4chiplet/parboil-spmv_NV4_1vc_4ch_2Dtorus_trace.txt"
    # input_ = "../benchmarks/2DConvolution/torus/NVLink4/4chiplet/polybench-2DConvolution_NV4_1vc_4ch_2Dtorus_trace.txt"
    # input_ =  "../benchmarks/AlexNet/torus/NVLink4/4chiplet/tango-alexnet_NV4_1vc_4ch_2Dtorus_trace.txt"

    #spkiky sync
    #input_ = "../benchmarks/lavaMD/torus/NVLink4/4chiplet/lavaMD-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    #input_ = "../benchmarks/2mm/torus/NVLink4/4chiplet/polybench-2mm_NV4_1vc_4ch_2Dtorus_trace.txt"
    #input_ = "../benchmarks/3mm/new/torus/NVLink4/4chiplet/polybench-3mm_NV4_1vc_4ch_2Dtorus_trace.txt"

    # spiky async
    #input_ = "../benchmarks/stencil/torus/NVLink4/4chiplet/parboil-stencil_NV4_1vc_4ch_2Dtorus_trace.txt"
    #input_ = "../benchmarks/hotspot3D/torus/NVLink4/4chiplet/hotspot3D-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    input_ = "../benchmarks/kmeans/torus/NVLink4/4chiplet/kmeans-rodinia-3.1_NV4_1vc_4ch_2Dtorus_trace.txt"
    #input_ = "../benchmarks/atax/torus/NVLink4/4chiplet/polybench-atax_NV4_1vc_4ch_2Dtorus_trace.txt"
    trace_generator(input_)
    gc.enable()
    gc.collect()