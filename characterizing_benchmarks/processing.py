from characterizing_benchmarks.spatialLocality import *
from pre_traffic_trace_categorizing import *
from kernel_traffic_model import *
import gc


def start_processing_portal(input_, chiplet_num):
    base_path = os.path.dirname(os.path.dirname(input_))
    file_size = os.path.getsize(input_)
    file_name = os.path.basename(input_)
    if file_size > 1000000000:
        line_num = os.popen("cat " + input_ + " | wc -l").read()
        chunk_size = round(int(line_num) / 8)
        os.system("split --numeric-suffixes=1 --additional-suffix=.txt -l " + str(chunk_size) + " " + input_ + " data_")
        file_num = int(os.popen("ls -d *data* | wc -l").read())
    else:
        file_num = 1
    request_packet = {}
    for i in range(1, file_num+1, 1):
        if file_size > 1000000000:
            file_name = "data_0" + str(i) + ".txt"
        else:
            file_name = input_
        file2 = open(file_name, "r")
        raw_content = ""
        if file2.mode == "r":
            raw_content = file2.readlines()
        file2.close()
        if file_name != input_:
            os.system("rm " + file_name)
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
    kernel_num = list(file_name.split("_"))[-1].split(".")[0]
    if kernel_num == "trace":
        kernel_num = 1
    else:
        kernel_num = int(kernel_num)
    overall_plot(base_path, request_packet, kernel_num)
    traffic_pattern_examination(request_packet, chiplet_num, input_, kernel_num)
    spatial_locality(input_, request_packet, chiplet_num, kernel_num)
    per_chiplet_model(base_path, request_packet, chiplet_num, kernel_num)
    traffic_model(input_, request_packet, chiplet_num, kernel_num)

    gc.enable()
    gc.collect()
