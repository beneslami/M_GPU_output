import os.path
import gc
import matplotlib.pyplot as plt

INTERVAL = 10000


def list_prunning(packet, input_):
    base_path = os.path.dirname(input_)
    new_packet = {}
    for id in packet.keys():
        new_packet.setdefault(id, [])
        for j in range(len(packet[id])):
            if packet[id][j][0] == "FW buffer" and (int(packet[id][j][1].split(": ")[1]) > 15 or int(packet[id][j][2].split(": ")[1]) > 15):
                pass
            else:
                new_packet[id].append(packet[id][j])
    del(packet)
    updated_packet = {}
    for id in new_packet.keys():
        count = 0
        for j in range(len(new_packet[id])):
            if new_packet[id][j][0] == "request injected":
                count += 1
            elif new_packet[id][j][0] == "request received":
                count += 1
            elif new_packet[id][j][0] == "reply injected":
                count += 1
            elif new_packet[id][j][0] == "reply received":
                count += 1
        if count == 4:
            updated_packet.setdefault(id, [])
            for j in range(len(new_packet[id])):
                updated_packet[id].append(new_packet[id][j])
    del(new_packet)
    with open(base_path + "/test.txt", "w") as file:
        for id in updated_packet.keys():
            for j in range(len(updated_packet[id])):
                for k in updated_packet[id][j]:
                    file.write(k)
                    if updated_packet[id][j].index(k) == len(updated_packet[id][j])-1:
                        pass
                    else:
                        file.write("\t")
    return updated_packet


def overall_injection_traffic(packet):
    traffic = {}
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "request injected":
                src = int(packet[id][j][1].split(": ")[1])
                dst = int(packet[id][j][2].split(": ")[1])
                cycle = int(packet[id][j][5].split(": ")[1])
                byte = int(packet[id][j][7].split(": ")[1])
                if cycle not in traffic.keys():
                    traffic.setdefault(cycle, {}).setdefault(src, {})[dst] = byte
                else:
                    if src not in traffic[cycle].keys():
                        traffic[cycle].setdefault(src, {})[dst] = byte
                    else:
                        if dst not in traffic[cycle][src].keys():
                            traffic[cycle][src][dst] = byte
                        else:
                            traffic[cycle][src][dst] += byte

    minimum = list(traffic.keys())[0]
    maximum = list(traffic.keys())[len(traffic.keys()) - 1]

    for i in range(minimum, maximum):
        if i not in traffic.keys():
            traffic[i] = 0

    traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
    gc.enable()
    gc.collect()
    return traffic


def generate_statistics_based_on_interval_sttistics_calculation_clustering_markov_chain(traffic):
    markov_chain = {}
    interval = INTERVAL
    interval_index = 0
    i = 0
    temp = []
    for cyc in traffic.keys():
        if i == interval:
            state = temp[0]
            chain = {}
            for j in range(1, len(temp)):
                if state not in chain.keys():
                    chain.setdefault(state, {})[temp[j]] = 1
                else:
                    if temp[j] not in chain[state].keys():
                        chain[state][temp[j]] = 1
                    else:
                        chain[state][temp[j]] += 1
                state = temp[j]
            markov_chain[interval_index] = chain
            temp = []
            i = 0
            interval_index += 1
        else:
            if not isinstance(traffic[cyc], int):
                temp_num = 0
                for src in traffic[cyc].keys():
                    for dest in traffic[cyc][src].keys():
                        temp_num += traffic[cyc][src][dest]
                temp.append(temp_num)
            else:
                temp.append(traffic[cyc])
            i += 1

    markov_chain = dict(sorted(markov_chain.items(), key=lambda x: x[0]))
    for s in markov_chain.keys():
        markov_chain[s] = dict(sorted(markov_chain[s].items(), key=lambda x: x[0]))
        for st in markov_chain[s].keys():
            markov_chain[s][st] = dict(sorted(markov_chain[s][st].items(), key=lambda x: x[0]))
    gc.enable()
    gc.collect()
    return markov_chain


def burst_window_dependency(traffic):
    burst_window_dist = {}
    burst_window_per_interval = {}
    interval = INTERVAL
    i = 0
    interval_index = 0
    for cyc in traffic.keys():
        if i == interval:
            temporary_burst = dict(sorted(burst_window_dist.items(), key=lambda x: x[0]))
            for b in temporary_burst.keys():
                temporary_burst[b] = dict(sorted(temporary_burst[b].items(), key=lambda x: x[0]))
            burst_window_per_interval[interval_index] = temporary_burst
            interval_index += 1
            i = 0
            burst_window_dist = {}
        else:
            if not isinstance(traffic[cyc], int):
                window_size = len(traffic[cyc].keys()) #number of sources
                burst_size = 0
                for src in traffic[cyc].keys():
                    for dst, byte in traffic[cyc][src].items():
                        burst_size += byte
                if burst_size > 0:
                    if burst_size not in burst_window_dist.keys():
                        burst_window_dist.setdefault(burst_size, {})[window_size] = 1
                    else:
                        if window_size not in burst_window_dist[burst_size].keys():
                            burst_window_dist[burst_size][window_size] = 1
                        else:
                            burst_window_dist[burst_size][window_size] += 1
            i += 1

    if i != interval:
        burst_window_dist = dict(sorted(burst_window_dist.items(), key=lambda x: x[0]))
        for b in burst_window_dist.keys():
            burst_window_dist[b] = dict(sorted(burst_window_dist[b].items(), key=lambda x: x[0]))
        burst_window_per_interval[interval_index] = burst_window_dist
    gc.enable()
    gc.collect()
    return burst_window_per_interval


def reuse_distance(traffic):
    destination = {}
    stack_snapshot = {}
    for cyc in traffic.keys():
        if not isinstance(traffic[cyc], int):
            for src in traffic[cyc].keys():
                if src not in destination.keys():
                    destination.setdefault(src, {}).setdefault(cyc, [])
                else:
                    if cyc not in destination[src].keys():
                        destination[src].setdefault(cyc, [])
                for dest, byte in traffic[cyc][src].items():
                    if byte != 0:
                        destination[src][cyc].append(dest)

    reuse_distance = {}
    for src in destination.keys():
        if src not in reuse_distance.keys():
            reuse_distance.setdefault(src, {})
        stack = []
        for cyc, dest_list in destination[src].items():
            for dest in dest_list:
                if dest not in stack:
                    stack.append(dest)
                else:
                    counter = 0
                    temp = []
                    b = stack.pop()
                    while b != dest:
                        if b not in temp:
                            temp.append(b)
                            counter += 1
                        b = stack.pop()
                    temp.append(b)
                    if counter not in reuse_distance[src].keys():
                        reuse_distance[src][counter] = 1
                    else:
                        reuse_distance[src][counter] += 1
                    top = temp.pop()
                    while len(temp) != 0:
                        b = temp.pop()
                        stack.append(b)
                    stack.append(top)
                    temp.clear()
        stack.clear()

    reuse_distance = dict(sorted(reuse_distance.items(), key=lambda x: x[0]))
    for s in reuse_distance.keys():
        reuse_distance[s] = dict(sorted(reuse_distance[s].items(), key=lambda x: x[0]))

    """for src in reuse_distance.keys():
        total = sum(list(reuse_distance[src].values()))
        for dist, freq in reuse_distance[src].items():
            reuse_distance[src][dist] = freq / total
    for src in reuse_distance.keys():
        prev = 0
        for dist, pdf in reuse_distance[src].items():
            reuse_distance[src][dist] = pdf + prev
            prev += pdf"""
    """plt.bar(list(reuse_distance[2].keys()), list(reuse_distance[2].values()), width=0.5)
    plt.xticks([0, 1, 2])
    plt.xlabel("reuse distance")
    plt.ylabel("CDF")
    plt.show()"""
    gc.enable()
    gc.collect()
    return reuse_distance


def packet_distribution(request_packet):
    req_packet = {}
    rep_packet = {}
    request_traffic = {}
    reply_traffic = {}
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "request injected":
                src = int(request_packet[id][j][1].split(": ")[1])
                dst = int(request_packet[id][j][2].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if cycle not in request_traffic.keys():
                    request_traffic.setdefault(cycle, {}).setdefault(src, {}).setdefault(dst, []).append(byte)
                else:
                    if src not in request_traffic[cycle].keys():
                        request_traffic[cycle].setdefault(src, {}).setdefault(dst, []).append(byte)
                    else:
                        if dst not in request_traffic[cycle][src].keys():
                            request_traffic[cycle][src].setdefault(dst, []).append(byte)
                        else:
                            request_traffic[cycle][src][dst].append(byte)
            elif request_packet[id][j][0] == "reply injected":
                src = int(request_packet[id][j][2].split(": ")[1])
                dst = int(request_packet[id][j][1].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if cycle not in reply_traffic.keys():
                    reply_traffic.setdefault(cycle, {}).setdefault(src, {}).setdefault(dst, []).append(byte)
                else:
                    if src not in reply_traffic[cycle].keys():
                        reply_traffic[cycle].setdefault(src, {}).setdefault(dst, []).append(byte)
                    else:
                        if dst not in reply_traffic[cycle][src].keys():
                            reply_traffic[cycle][src].setdefault(dst, []).append(byte)
                        else:
                            reply_traffic[cycle][src][dst].append(byte)
    minimum = min(list(request_traffic.keys()))
    maximum = max(list(request_traffic.keys()))
    for i in range(minimum, maximum+1):
        if i not in request_traffic.keys():
            request_traffic[i] = 0
    minimum = min(list(reply_traffic.keys()))
    maximum = max(list(reply_traffic.keys()))
    for i in range(minimum, maximum + 1):
        if i not in reply_traffic.keys():
            reply_traffic[i] = 0
    request_traffic = dict(sorted(request_traffic.items(), key=lambda x: x[0]))
    reply_traffic = dict(sorted(reply_traffic.items(), key=lambda x: x[0]))

    interval = INTERVAL
    i = 0
    interval_index = 0
    temp = {}
    for cyc in request_traffic.keys():
        if i == interval:
            req_packet[interval_index] = temp
            interval_index += 1
            i = 0
            temp = {}
        else:
            if not isinstance(request_traffic[cyc], int):
                for src in request_traffic[cyc].keys():
                    for dest in request_traffic[cyc][src].keys():
                        if src not in temp.keys():
                            temp.setdefault(src, {}).setdefault(dest, {})
                        else:
                            if dest not in temp[src].keys():
                                temp[src].setdefault(dest, {})
                        for byte in request_traffic[cyc][src][dest]:
                            if byte not in temp[src][dest].keys():
                                temp[src][dest][byte] = 1
                            else:
                                temp[src][dest][byte] += 1
            i += 1
    if i != interval:
        req_packet[interval_index] = temp

    for c in req_packet.keys():
        req_packet[c] = dict(sorted(req_packet[c].items(), key=lambda x: x[0]))
        for d in req_packet[c].keys():
            req_packet[c][d] = dict(sorted(req_packet[c][d].items(), key=lambda x: x[0]))

    interval = INTERVAL
    i = 0
    interval_index = 0
    temp = {}
    for cyc in reply_traffic.keys():
        if i == interval:
            rep_packet[interval_index] = temp
            flag = 0
            """for src in req_packet[interval_index].keys():
                for dest in req_packet[interval_index][src].keys():
                    if dest not in rep_packet[interval_index].keys():
                        flag = 1
                        rep_packet[interval_index].setdefault(dest, {}).setdefault(src, {})
                    else:
                        if src not in rep_packet[interval_index][dest].keys():
                            flag = 1
                            rep_packet[interval_index][dest].setdefault(src, {})
                    if flag == 1:
                        for byte, freq in req_packet[interval_index][src][dest].items():
                            if byte == 8:
                                rep_packet[interval_index][dest][src][40] = freq
                            else:
                                rep_packet[interval_index][dest][src][8] = freq"""
            interval_index += 1
            i = 0
            temp = {}
        else:
            if not isinstance(reply_traffic[cyc], int):
                for src in reply_traffic[cyc].keys():
                    for dest in reply_traffic[cyc][src].keys():
                        if src not in temp.keys():
                            temp.setdefault(src, {}).setdefault(dest, {})
                        else:
                            if dest not in temp[src].keys():
                                temp[src].setdefault(dest, {})
                        for byte in reply_traffic[cyc][src][dest]:
                            if byte not in temp[src][dest].keys():
                                temp[src][dest][byte] = 1
                            else:
                                temp[src][dest][byte] += 1
            i += 1
    if i != interval:
        rep_packet[interval_index] = temp

    for c in rep_packet.keys():
        rep_packet[c] = dict(sorted(rep_packet[c].items(), key=lambda x: x[0]))
        for d in rep_packet[c].keys():
            rep_packet[c][d] = dict(sorted(rep_packet[c][d].items(), key=lambda x: x[0]))
    gc.enable()
    gc.collect()
    return req_packet, rep_packet


def calculate_processing_time(request_packet):
    cache = {}
    processing_time = {}
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "request received":
                chip = int(request_packet[id][j][6].split(": ")[1])
                start_time = int(request_packet[id][j][5].split(": ")[1])
                for k in range(j, len(request_packet[id])):
                    if request_packet[id][k][0] == "reply injected":
                        assert chip == int(request_packet[id][k][6].split(": ")[1])
                        #assert "cache" == request_packet[id][k][8].split(": ")[0]
                        #cache_stat = int(request_packet[id][k][8].split(": ")[1])
                        end_time = int(request_packet[id][k][5].split(": ")[1])
                        """if chip not in cache.keys():
                            cache.setdefault(chip, {})[cache_stat] = 1
                        else:
                            if cache_stat not in cache[chip].keys():
                                cache[chip][cache_stat] = 1
                            else:
                                cache[chip][cache_stat] += 1"""
                        if chip not in processing_time.keys():
                            processing_time.setdefault(chip, {})[end_time - start_time] = 1
                        else:
                            if end_time - start_time not in processing_time[chip].keys():
                                processing_time[chip][end_time - start_time] = 1
                            else:
                                processing_time[chip][end_time - start_time] += 1
    processing_time = dict(sorted(processing_time.items(), key=lambda x: x[0]))
    cache = dict(sorted(cache.items(), key=lambda x: x[0]))
    for c in cache.keys():
        cache[c] = dict(sorted(cache[c].items(), key=lambda x: x[0]))
    for c in processing_time.keys():
        processing_time[c] = dict(sorted(processing_time[c].items(), key=lambda x: x[0]))

    gc.enable()
    gc.collect()
    return cache, processing_time


def calculate_hotspot(request_packet):
    traffic = {}
    hotspot = {}
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "request injected":
                src = int(request_packet[id][j][1].split(": ")[1])
                dst = int(request_packet[id][j][2].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if cycle not in traffic.keys():
                    traffic.setdefault(cycle, {}).setdefault(src, {}).setdefault(dst, []).append(byte)
                else:
                    if src not in traffic[cycle].keys():
                        traffic[cycle].setdefault(src, {}).setdefault(dst, []).append(byte)
                    else:
                        if dst not in traffic[cycle][src].keys():
                            traffic[cycle][src].setdefault(dst, []).append(byte)
                        else:
                            traffic[cycle][src][dst].append(byte)
    minimum = min(list(traffic.keys()))
    maximum = max(list(traffic.keys()))
    for i in range(minimum, maximum + 1):
        if i not in traffic.keys():
            traffic[i] = 0
    traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
    i = 0
    interval_index = 0
    interval = INTERVAL
    temp = {}
    for cycle in traffic.keys():
        if i == interval:
            hotspot[interval_index] = temp
            interval_index += 1
            i = 0
            temp = {}
        else:
            if not isinstance(traffic[cycle], int):
                for src in traffic[cycle].keys():
                    for dst in traffic[cycle][src].keys():
                        if src not in temp.keys():
                            temp.setdefault(src, {})[dst] = sum(traffic[cycle][src][dst])
                        else:
                            if dst not in temp[src].keys():
                                temp[src][dst] = sum(traffic[cycle][src][dst])
                            else:
                                temp[src][dst] += sum(traffic[cycle][src][dst])
            i += 1

    if i != interval:
        hotspot[interval_index] = temp

    for c in hotspot.keys():
        hotspot[c] = dict(sorted(hotspot[c].items(), key=lambda x: x[0]))
        for src in hotspot[c].keys():
            hotspot[c][src] = dict(sorted(hotspot[c][src].items(), key=lambda x: x[0]))

    source_hotspot = {}
    for i in hotspot.keys():
        if i not in source_hotspot.keys():
            source_hotspot.setdefault(i, {})
        for src in hotspot[i].keys():
            for dest, byte_list in hotspot[i][src].items():
                if src not in source_hotspot[i].keys():
                    source_hotspot[i][src] = (byte_list)
                else:
                    source_hotspot[i][src] += (byte_list)

    destination_hotspot = {}
    for i in hotspot.keys():
        if i not in destination_hotspot.keys():
            destination_hotspot.setdefault(i, {})
        for src in hotspot[i].keys():
            for dest, byte_list in hotspot[i][src].items():
                if src not in destination_hotspot[i].keys():
                    destination_hotspot[i].setdefault(src, {})[dest] = (byte_list)
                else:
                    if dest not in destination_hotspot[i][src].keys():
                        destination_hotspot[i][src][dest] = (byte_list)
                    else:
                        destination_hotspot[i][src][dest] += (byte_list)

    gc.enable()
    gc.collect()
    return source_hotspot, destination_hotspot


def reply_network(request_packet):
    traffic = {}
    prev_cycle = {}
    iat_flag = {}
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "reply injected":
                src = int(request_packet[id][j][2].split(": ")[1])
                dst = int(request_packet[id][j][1].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if src not in prev_cycle.keys():
                    prev_cycle[src] = cycle
                    iat_flag[src] = 0
                if cycle not in traffic.keys():
                    traffic.setdefault(cycle, {}).setdefault(src, {}).setdefault(dst, []).append(byte)
                else:
                    if src not in traffic[cycle].keys():
                        traffic[cycle].setdefault(src, {}).setdefault(dst, []).append(byte)
                    else:
                        if dst not in traffic[cycle][src].keys():
                            traffic[cycle][src].setdefault(dst, []).append(byte)
                        else:
                            traffic[cycle][src][dst].append(byte)
    """minimum = min(list(traffic.keys()))
    maximum = max(list(traffic.keys()))
    for i in range(minimum, maximum + 1):
        if i not in traffic.keys():
            traffic[i] = 0"""
    traffic = dict(sorted(traffic.items(), key=lambda x: x[0]))
    reply_iat = {}

    for cyc in traffic.keys():
        for src in traffic[cyc].keys():
            if cyc - prev_cycle[src] >= 1:
                if src not in reply_iat.keys():
                    reply_iat.setdefault(src, {})[cyc - prev_cycle[src]] = 1
                else:
                    if cyc - prev_cycle[src] not in reply_iat[src].keys():
                        reply_iat[src][cyc - prev_cycle[src]] = 1
                    else:
                        reply_iat[src][cyc - prev_cycle[src]] += 1
            prev_cycle[src] = cyc

    reply_iat = dict(sorted(reply_iat.items(), key=lambda x: x[0]))
    for c in reply_iat.keys():
        reply_iat[c] = dict(sorted(reply_iat[c].items(), key=lambda x: x[0]))

    reply_window = {}
    for cycle in traffic.keys():
        if not isinstance(traffic[cycle], int):
            for src in traffic[cycle].keys():
                window = 0
                for dest, byte_list in traffic[cycle][src].items():
                    window += len(byte_list)
                if src not in reply_window.keys():
                    reply_window.setdefault(src, {})[window] = 1
                else:
                    if window not in reply_window[src].keys():
                        reply_window[src][window] = 1
                    else:
                        reply_window[src][window] += 1


    reply_window = dict(sorted(reply_window.items(), key=lambda x: x[0]))
    for c in reply_window.keys():
        reply_window[c] = dict(sorted(reply_window[c].items(), key=lambda x: x[0]))

    gc.enable()
    gc.collect()
    return reply_iat, reply_window


def off_time(packet):
    traffic = {}
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "request injected":
                cycle = int(packet[id][j][5].split(": ")[1])
                byte = int(packet[id][j][7].split(": ")[1])
                if cycle not in traffic.keys():
                    traffic[cycle] = byte
                else:
                    traffic[cycle] += byte

    prev = 0
    flag = 0
    off_dist = {}
    for cycle, byte in traffic.items():
        if flag == 0:
            flag = 1
            prev = cycle
        else:
            if cycle - prev > 1:
                if cycle - prev not in off_dist.keys():
                    off_dist[cycle - prev] = 1
                else:
                    off_dist[cycle - prev] += 1
            prev = cycle
    off_dist = dict(sorted(off_dist.items(), key=lambda x: x[0]))
    total = sum(off_dist.values())
    for length, freq in off_dist.items():
        off_dist[length] = freq / total
    prev = 0
    for length, pdf in off_dist.items():
        off_dist[length] = pdf + prev
        prev += pdf
    gc.enable()
    gc.collect()
    return off_dist


def generate_model(input_):
    file2 = open(input_, "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    file2.close()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    request_packet = {}
    for i in range(len(lined_list)):
        if int(lined_list[i][3].split(": ")[1]) in request_packet.keys():
            if lined_list[i] not in request_packet[int(lined_list[i][3].split(": ")[1])]:
                request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        else:
            request_packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
    del (raw_content)
    del (lined_list)
    request_packet = list_prunning(request_packet, input_)
    """empirical_traffic = overall_injection_traffic(request_packet)
    markov_chain = generate_statistics_based_on_interval_sttistics_calculation_clustering_markov_chain(empirical_traffic)
    burst_win_dep = burst_window_dependency(empirical_traffic)
    reuse = reuse_distance(empirical_traffic)
    req_packet_dist, rep_packet_dist = packet_distribution(request_packet)
    cache_hit_dist, processing_time_dist = calculate_processing_time(request_packet)
    source_hotspot, destination_hotspot = calculate_hotspot(request_packet)
    interval_list = list(markov_chain.keys())
    reply_iat, reply_window = reply_network(request_packet)
    off_dist = off_time(request_packet)
    file_name = os.path.basename(input_).split("_")[0] + "_model.txt"

    with open(file_name, "w") as file:
        file.write("interval_begin\n")
        for interval in interval_list:
            file.write("int\t" + str(interval) + "\n")
            file.write("markov_begin\n")
            for state in markov_chain[interval].keys():
                file.write("b " + str(state) + "\n")
                for next_state, cdf in markov_chain[interval][state].items():
                    file.write(str(next_state) + "\t" + str(cdf) + "\n")
            file.write("markov_end\n")

            file.write("burst_win_begin\n")
            for burst in burst_win_dep[interval].keys():
                file.write("bst\t" + str(burst) + "\n")
                for window, cdf in burst_win_dep[interval][burst].items():
                    file.write(str(window) + "\t" + str(cdf) + "\n")
            file.write("burst_win_end\n")

            file.write("hot_src_begin\n")
            for src, freq in source_hotspot[interval].items():
                file.write(str(src) + "\t" + str(freq) + "\n")
            file.write("hot_src_end\n")

            file.write("dest_begin\n")
            for src in destination_hotspot[interval].keys():
                file.write("src\t" + str(src) + "\n")
                for dest, freq in destination_hotspot[interval][src].items():
                    file.write(str(dest) + "\t" + str(freq) + "\n")
            file.write("dest_end\n")

            file.write("req_packet_dist_begin\n")
            for src in req_packet_dist[interval].keys():
                file.write("src " + str(src) + "\n")
                for dest in req_packet_dist[interval][src].keys():
                    file.write("dest\t" + str(dest) + "\n")
                    for byte, freq in req_packet_dist[interval][src][dest].items():
                        file.write(str(byte) + "\t" + str(freq) + "\n")
            file.write("req_packet_dist_end\n")

            file.write("rep_packet_dist_begin\n")
            for src in rep_packet_dist[interval].keys():
                file.write("src\t" + str(src) + "\n")
                for dest in rep_packet_dist[interval][src].keys():
                    file.write("dest\t" + str(dest) + "\n")
                    for byte, freq in rep_packet_dist[interval][src][dest].items():
                        file.write(str(byte) + "\t" + str(freq) + "\n")
            file.write("rep_packet_dist_end\n")
        file.write("interval_end\n")

        file.write("reply_iat_begin\n")
        for src in reply_iat.keys():
            file.write("src\t" + str(src) + "\n")
            for duration, freq in reply_iat[src].items():
                file.write(str(duration) + "\t" + str(freq) + "\n")
        file.write("reply_iat_end\n")

        file.write("reply_win_begin\n")
        for src in reply_window.keys():
            file.write("src\t" + str(src) + "\n")
            for win, freq in reply_window[src].items():
                file.write(str(win) + "\t" + str(freq) + "\n")
        file.write("reply_win_end\n")

        file.write("processing_time_begin\n")
        for src in processing_time_dist.keys():
            file.write("src\t" + str(src) + "\n")
            for k, v in processing_time_dist[src].items():
                file.write(str(k) + "\t" + str(v) + "\n")
        file.write("processing_time_end\n")"""

    gc.enable()
    gc.collect()