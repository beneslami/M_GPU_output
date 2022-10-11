import csv
import threading
import os

chiplet = []
chiplet_0 = dict(
    SM_ID=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
           28, 29, 30, 31],
    LLC_ID=[128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143], port=192)

chiplet_1 = dict(
    SM_ID=[32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
           59, 60, 61, 62, 63],
    LLC_ID=[144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159], port=193)

chiplet_2 = dict(
    SM_ID=[64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
           91, 92, 93, 94, 95],
    LLC_ID=[160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175], port=194)

chiplet_3 = dict(
    SM_ID=[96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117,
           118, 119, 120, 121, 122, 123, 124, 125, 126, 127],
    LLC_ID=[176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191], port=195)

chiplet.append(chiplet_0)
chiplet.append(chiplet_1)
chiplet.append(chiplet_2)
chiplet.append(chiplet_3)
traffic = {0: {}, 1: {}, 2: {}, 3: {}}
window_size = {0: {}, 1: {}, 2: {}, 3: {}}
destination = {0: {1: 0, 2: 0, 3: 0}, 1: {0: 0, 2: 0, 3: 0}, 2: {0: 0, 1: 0, 3: 0}, 3: {0: 0, 1: 0, 2: 0}}
packet_freq = {0: {1: {}, 2: {}, 3: {}}, 1: {0: {}, 2: {}, 3: {}}, 2: {0: {}, 1: {}, 3: {}}, 3: {0: {}, 1: {}, 2: {}}}
iat = {0: {}, 1: {}, 2: {}, 3: {}}
cache_hit = {0: {}, 1: {}, 2: {}, 3: {}}
cache_miss = {0: {}, 1: {}, 2: {}, 3: {}}
cache_hit_ratio = {0: 0, 1: 0, 2: 0, 3: 0}
llc_boundary_buffer_delay = {0: {}, 1: {}, 2: {}, 3: {}}
destination_window_dist = {0: {}, 1: {}, 2: {}, 3: {}}
destination_iat_dist = {0: {}, 1: {}, 2: {}, 3: {}}


def chip_select(num):
    out = -1
    if num < 4:
        return num
    for i in range(len(chiplet)):
        if num in chiplet[i]["SM_ID"]:
            out = i
            break
        if num in chiplet[i]["LLC_ID"]:
            out = i
            break
        if num == chiplet[i]["port"]:
            out = i
            break
    return out


def check_local_or_remote(x):  # 0 for local, 1 for remote
    for i in range(len(chiplet)):
        if (int(x[1].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[1].split(": ")[1]) in chiplet[i]["LLC_ID"]):
            if (int(x[2].split(": ")[1]) in chiplet[i]["SM_ID"]) or (int(x[2].split(": ")[1]) in chiplet[i]["LLC_ID"]):
                return 0
        return 1


def update_traffic():
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            list_ = [0, 1, 2, 3]
            list_.remove(src)
            for dest in traffic[src][cyc].keys():
                list_.remove(dest)
            if len(list_) != 0:
                for i in list_:
                    traffic[src][cyc].setdefault(i, [])
    for src in traffic.keys():
        traffic[src] = dict(sorted(traffic[src].items(), key=lambda x: x[0]))
    for src in traffic.keys():
        for cyc in traffic[src].keys():
            traffic[src][cyc] = dict(sorted(traffic[src][cyc].items(), key=lambda x: x[0]))


def generate_real_traffic_per_core(source, dest, packet):
    global traffic
    for cycle, byte in packet.items():
        if cycle not in traffic[source].keys():
            traffic[source].setdefault(cycle, {})
            if dest not in traffic[source][cycle].keys():
                traffic[source][cycle][dest] = byte
            else:
                for b in byte:
                    traffic[source][cycle][dest].append(b)
        else:
            if dest not in traffic[source][cycle].keys():
                traffic[source][cycle][dest] = byte
            else:
                for b in byte:
                    traffic[source][cycle][dest].append(b)


def packet_type_frequency():
    global traffic
    global packet_freq
    for source in traffic.keys():
        for cycle in traffic[source].keys():
            for dest, bytes in traffic[source][cycle].items():
                if len(bytes) != 0:
                    for i in bytes:
                        if i not in packet_freq[source][dest].keys():
                            packet_freq[source][dest][i] = 1
                        else:
                            packet_freq[source][dest][i] += 1
    for src in packet_freq.keys():
        for dest in packet_freq[src].keys():
            packet_freq[src][dest] = dict(sorted(packet_freq[src][dest].items(), key=lambda x: x[0]))


def destination_choose():
    global traffic
    global destination
    for core in traffic.keys():
        for cyc in traffic[core].keys():
            for dest, byte in traffic[core][cyc].items():
                if len(traffic[core][cyc][dest]) != 0:
                    if dest not in destination[core].keys():
                        destination[core][dest] = 1
                    else:
                        destination[core][dest] += 1
    for src in destination.keys():
        destination[src] = dict(sorted(destination[src].items(), key=lambda x: x[0]))


def inter_arrival_time():
    global iat
    flag = 0
    start = -1
    for source in traffic.keys():
        for cycle in traffic[source].keys():
            if flag == 0:
                start = cycle
                flag = 1
            elif flag == 1:
                if (cycle - start) not in iat[source].keys():
                    iat[source][cycle - start] = 1
                else:
                    iat[source][cycle - start] += 1
                start = cycle
    for source in iat.keys():
        iat[source] = dict(sorted(iat[source].items(), key=lambda x: x[0]))


def generate_source_window():
    global traffic
    global window_size
    for source in traffic.keys():
        for cycle in traffic[source].keys():
            window = 0
            for dest in traffic[source][cycle].keys():
                window += len(traffic[source][cycle][dest])
            if window not in window_size[source].keys():
                window_size[source][window] = 1
            else:
                window_size[source][window] += 1

    for source in window_size.keys():
        window_size[source] = dict(sorted(window_size[source].items(), key=lambda x: x[0]))


def cache_hit_dist(model_name):
    for src in range(0, 4):
        lines = ""
        with open(model_name + "/cache_access/cache_access_hit" + str(src) + ".csv", "r") as file:
            lines = file.readlines()

        if len(lines) == 0:
            cache_hit[src][0] = 0
        else:
            for line in lines:
                items = line.split(",")
                cache_hit[src][int(items[0])] = int(items[1])
        cache_hit[src] = dict(sorted(cache_hit[src].items(), key=lambda x: x[0]))


def cache_miss_dist(model_name):
    for src in range(0, 4):
        lines = ""
        with open(model_name + "/cache_access/cache_access_miss" + str(src) + ".csv", "r") as file:
            lines = file.readlines()
        if len(lines) == 0:
            cache_miss[src][0] = 0
        else:
            for line in lines:
                items = line.split(",")
                cache_miss[src][int(items[0])] = int(items[1])
        cache_miss[src] = dict(sorted(cache_miss[src].items(), key=lambda x: x[0]))


def cache_access_ratio(model_name):
    with open(model_name + "/cache_access/cache_access.csv", "r") as file:
        lines = file.readlines()
    for line in lines:
        chip = int(line.split("-")[0])
        items = line.split("-")[1].split(",")
        hit_val = int(items[0].split(":")[1])
        miss_val = int(items[1].split(":")[1])
        cache_hit_ratio[chip] = float(hit_val / (hit_val+miss_val))


def llc_boundary_buffer_delay_dist(model_name):
    for i in range(0, 4):
        lines = ""
        with open(model_name + "/rop_delay" + str(i) + ".csv", "r") as file:
            lines = file.readlines()
        for line in lines:
            items = line.split(",")
            llc_boundary_buffer_delay[i][int(items[0])] = int(items[1])


def destination_widnow(model_name):
    for i in range(0, 4):
        lines = ""
        with open(model_name + "/response_injection/window_size.csv", "r") as file:
            lines = file.readlines()
        chip = -1
        for line in lines:
            item = line.split(",")
            if len(item) == 1:
                chip = int(item[0])
            else:
                win = int(item[0])
                freq = int(item[1])
                destination_window_dist[chip][win] = freq
    for src in destination_window_dist.keys():
        destination_window_dist[src] = dict(sorted(destination_window_dist[src].items(), key=lambda x: x[0]))


def destination_iat(model_name):
    for i in range(0, 4):
        lines = ""
        with open(model_name + "/response_injection/dest_iat" + str(i) + ".csv", "r") as file:
            lines = file.readlines()
        for line in lines:
            items = line.split(",")
            duration = int(items[0])
            freq = int(items[1])
            destination_iat_dist[i][duration] = freq


if __name__ == "__main__":
    model_name = "2MM"
    frequency = "6144"
    subpath = "pre/" + model_name + "/" + frequency
    for src in range(0, 4):
        for dest in range(0, 4):
            if src != dest:
                path = subpath + "/request_injection/pre_" + str(src) + "_" + str(dest) + ".txt"
                file2 = open(path, "r")
                raw_content = ""
                if file2.mode == "r":
                    raw_content = file2.readlines()
                file2.close()
                lined_list = {}
                for line in raw_content:
                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                    y = len(item[1].split("\n")[0][1:][:-1].split(","))
                    for index in range(y):
                        if int(item[0]) not in lined_list.keys():
                            lined_list.setdefault(int(item[0]), []).append(int(item[1].split("\n")[0][1:][:-1].split(",")[index]))
                        else:
                            lined_list[int(item[0])].append(int(item[1].split("\n")[0][1:][:-1].split(",")[index]))
                del (raw_content)
                generate_real_traffic_per_core(src, dest, lined_list)
                del(lined_list)
    update_traffic()
    t0 = threading.Thread(target=packet_type_frequency, args=())
    t1 = threading.Thread(target=destination_choose, args=())
    t2 = threading.Thread(target=inter_arrival_time, args=())
    t3 = threading.Thread(target=generate_source_window, args=())
    t4 = threading.Thread(target=cache_hit_dist, args=(subpath,))
    t5 = threading.Thread(target=cache_miss_dist, args=(subpath,))
    t6 = threading.Thread(target=cache_access_ratio, args=(subpath,))
    t7 = threading.Thread(target=llc_boundary_buffer_delay_dist, args=(subpath,))
    t8 = threading.Thread(target=destination_widnow, args=(subpath,))
    t9 = threading.Thread(target=destination_iat, args=(subpath,))
    t0.start()
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t7.start()
    t8.start()
    t9.start()

    t0.join()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
    t7.join()
    t8.join()
    t9.join()

    for i in range(0, 4):
        filename = subpath + "/" + model_name + "_core_" + str(i) + str(".model")
        with open(filename, "w") as file:
            file.write("core " + str(i) + "\n\n")

            file.write("packet_distribution_begin\n")
            for dest, data in packet_freq[i].items():
                file.write("destination " + str(dest) + "\n")
                for pack, freq in data.items():
                    file.write(str(pack) + "\t" + str(freq) + "\n")
            file.write("packet_distribution_end\n\n")

            file.write("destination_begin\n")
            for dest, freq in destination[i].items():
                file.write(str(dest) + "\t" + str(freq) + "\n")
            file.write("destination_end\n\n")

            file.write("Inter_arrival_time_begin\n")
            for duration, freq in iat[i].items():
                file.write(str(duration) + "\t" + str(freq) + "\n")
            file.write("Inter_arrival_time_end\n\n")

            file.write("total_window_size_begin\n")
            for win, freq in window_size[i].items():
                file.write(str(win) + "\t" + str(freq) + "\n")
            file.write("total_window_size_end\n\n")

            file.write("cache_hit_begin\n")
            for duration, freq in cache_hit[i].items():
                file.write(str(duration) + "\t" + str(freq) + "\n")
            file.write("cache_hit_end\n\n")

            file.write("cache_miss_begin\n")
            for duration, freq in cache_miss[i].items():
                file.write(str(duration) + "\t" + str(freq) + "\n")
            file.write("cache_miss_end\n\n")

            file.write("cache_hit_probability_begin\n")
            file.write(str(cache_hit_ratio[i]) + "\n")
            file.write("cache_hit_probability_end\n\n")

            file.write("llc_boundary_delay_begin\n")
            for duration, freq in llc_boundary_buffer_delay[i].items():
                file.write(str(duration) + "\t" + str(freq) + "\n")
            file.write("llc_boundary_delay_end\n\n")

            file.write("pending_buffer_begin\n")
            for win, freq in destination_window_dist[i].items():
                file.write(str(win) + "\t" + str(freq) + "\n")
            file.write("pending_buffer_end\n\n")

            file.write("dest_iat_begin\n")
            for win, freq in destination_iat_dist[i].items():
                file.write(str(win) + "\t" + str(freq) + "\n")
            file.write("dest_iat_end\n\n")