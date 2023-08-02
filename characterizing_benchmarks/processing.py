from measurements.spatialLocality import *
from measurements.calculate_link_usage import *
from characterizing_benchmarks.phaseClustering import *
import gc

if __name__ == '__main__':
    input_ = sys.argv[1]
    base_path = os.path.dirname(input_)
    file_size = os.path.getsize(input_)
    if file_size > 10000:
        line_num = os.popen("cat " + input_ + " | wc -l").read()
        chunk_size = round(int(line_num) / 8)
        os.system("split --numeric-suffixes=1 --additional-suffix=.txt -l " + str(chunk_size) + " " + input_ + " data_")
        file_num = int(os.popen("ls -d *data* | wc -l").read())
    else:
        file_num = 0
    if os.path.exists(base_path + "/models"):
        pass
    else:
        os.system("mkdir " + base_path + "/models")
    if os.path.exists(base_path + "/plots"):
        pass
    else:
        os.system("mkdir " + base_path + "/plots")
    if os.path.exists(base_path + "/data"):
        pass
    else:
        os.system("mkdir " + base_path + "/data")
    request_packet = {}
    reply_packet = {}
    chiplet_num = 4
    topology = ""
    nv = 0
    sub_str = os.path.basename(input_).split("_")
    for sub_s in sub_str:
        if sub_str.index(sub_s) != 0:
            if sub_s.__contains__("ch"):
                chiplet_num = int(re.split(r'(\d+)', sub_s)[1])
                break
    for sub_s in sub_str:
        if sub_s.__contains__("ring") or sub_s.__contains__("torus") or sub_s.__contains__(
                "mesh") or sub_s.__contains__("fly"):
            topology = sub_s
    for sub_s in sub_str:
        if sub_s.__contains__("NV"):
            nv = int(re.split(r'(\d+)', sub_s)[1])
            break

    for i in range(1, file_num+1, 1):
        if file_size > 10000:
            file_name = "data_0" + str(i) + ".txt"
        else:
            file_name = input_
        #file_name = input_
        print(file_name)
        file2 = open(file_name, "r")
        raw_content = ""
        if file2.mode == "r":
            raw_content = file2.readlines()
        file2.close()
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

    destination_locality(request_packet)
    #calculate_link_usage_(input_, chiplet_num)
    #overall_plot(input_, request_packet) # from pre_traffic_categorizing
    #generate_aggregate_byte_distribution(input_, request_packet) #from generate_injection_csv
    #spatial_locality(input_, request_packet, chiplet_num)# from spatialLocality
    #traffic_pattern_examination(request_packet, chiplet_num, input_)
    # per_chiplet_model(input_, request_packet, reply_packet)# from pre_traffic_distribution
    #check_stationary(input_, request_packet, chiplet_num)# from check_random_process
    #measure_throughput(input_, topology, chiplet_num, nv)
    # phase_clustering(input_, request_packet)
    # measure_contention(input_, chiplet_num)
    gc.enable()
    gc.collect()
