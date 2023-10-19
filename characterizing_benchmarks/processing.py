from characterizing_benchmarks.spatialLocality import *
from pre_traffic_trace_categorizing import *
import burstiness
import gc


def determine_architecture(topo, nv, ch):
    topol = ""
    chipNum = -1
    NV = -1
    if topo == "torus":
        topol = "2Dtorus"
    elif topo == "ring":
        topol = "ring"
    elif topo == "mesh":
        topol = "2Dmesh"
    elif topo == "fly":
        if ch == "4chiplet" or ch == "8chiplet":
            topol = "1fly"
        else:
            topol = "2fly"
    if ch == "4chiplet":
        chipNum = 4
    elif ch == "8chiplet":
        chipNum = 8
    elif ch == "16chiplet":
        chipNum = 16
    if nv == "NVLink4":
        NV = 4
    elif nv == "NVLink3":
        NV = 3
    elif nv == "NVLink2":
        NV = 2
    elif nv == "NVLink1":
        NV = 1
    return topol, NV, chipNum


def start_processing_portal(input_, chiplet_num):
    base_path = os.path.dirname(os.path.dirname(input_))
    file_size = os.path.getsize(input_)
    file_name = os.path.basename(input_)
    #if file_size > 1000000000:
        #line_num = os.popen("cat " + input_ + " | wc -l").read()
        #chunk_size = round(int(line_num) / 8)
        #os.system("split --numeric-suffixes=1 --additional-suffix=.txt -l " + str(chunk_size) + " " + input_ + " data_")
        #file_num = int(os.popen("ls -d *data* | wc -l").read())
    #else:
        #file_num = 1
    request_packet = {}
    for i in range(1): #, file_num+1, 1):
        #if file_size > 1000000000:
            #file_name = "data_0" + str(i) + ".txt"
        #else:
        file_name = input_
        file2 = open(file_name, "r")
        raw_content = ""
        if file2.mode == "r":
            raw_content = file2.readlines()
        file2.close()
        #if file_name != input_:
            #os.system("rm " + file_name)
        del(file2)
        lined_list = []
        for line in raw_content:
            item = [x for x in line.split("\t") if x not in ['', '\t']]
            lined_list.append(item)
        del (raw_content)
        for i in range(len(lined_list)):
            if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
                if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                    request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
            else:
                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        del (lined_list)
        gc.enable()
        gc.collect()
    try:
        kernel_num = file_name.split(".")[0].split("_")[-1]
    except:
        kernel_num = 1
    else:
        kernel_num = int(kernel_num)
    overall_plot(base_path, request_packet, kernel_num)
    #traffic_pattern_examination(request_packet, chiplet_num, input_, kernel_num)
    spatial_locality(input_, request_packet, chiplet_num, kernel_num)
    burstiness.measure_traffic_fraction(input_, request_packet)
    gc.enable()
    gc.collect()


def extract_kernel_info(path, suite, bench, topo, nv, ch, kernel_num):
    req_inst = -1
    remote = -1
    local = -1
    CTA = -1
    cycle = -1
    inst = -1
    occ = -1
    P_latency = -1
    N_latency = -1
    throughput = -1
    ipc = -1
    topol, NV, CH = determine_architecture(topo, nv, ch)
    file_name = suite + "-" + bench + "_NV" + str(NV) + "_1vc_" + str(CH) + "ch_" + topol + ".txt"
    file2 = open(path + "/" + file_name, "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    file2.close()
    rem = 0
    flag = 0
    flag2 = 0
    for line in raw_content:
        if "-kernel id" in line:
            id = int(line.split(" = ")[1])
            if id == kernel_num:
                flag = 1
        if "total CTA number" in line and flag == 1:
            CTA = (int(line.split(" ")[-1]))
        if "Number of Local Requests" in line and flag == 1:
            local = (int(line.split(": ")[-1]))
        if "Number of Remote Requests" in line and flag == 1:
            remote = (int(line.split(": ")[-1]))
            rem = int(line.split(": ")[-1])
        if "gpu_sim_cycle" in line and flag == 1:
            cycle = (int(line.split(" = ")[-1]))
        if "gpu_sim_insn" in line and flag == 1:
            inst = (int(line.split(" = ")[-1]))
            req_inst = ("{:.4}".format(float(rem/int(line.split(" = ")[-1]))*100))
            rem = 0
        if "gpu_ipc" in line and flag == 1:
            ipc = ("{:.2f}".format(float(line.split(" = ")[-1])))
        if "gpu_occupancy" in line and "%" in line and flag == 1:
            occ = ("{:.3f}".format(float(line.split(" = ")[-1][0:len(line.split(" = ")[-1])-4])))
        if "gpu_throughput" in line and flag == 1:
            throughput = ("{:.2f}".format(float(line.split(" = ")[-1])))
        if "chLet-DETAILS" in line and flag == 1:
            flag2 = 1
        if flag2 == 1:
            if "Packet latency average" in line and flag == 1:
                P_latency = ("{:.2f}".format(float(line.split(" = ")[-1])))
            if "Network latency average" in line and flag == 1:
                N_latency = ("{:.2f}".format(float(line.split(" = ")[-1])))
                flag2 = 0
                flag = 0
                break
    return req_inst, remote, local, CTA, cycle, inst, occ, P_latency, N_latency, throughput, ipc
