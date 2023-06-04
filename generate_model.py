

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
    return traffic


def generate_statistics_based_on_interval_sttistics_calculation_clustering_markov_chain(traffic):
    counter = 0
    markov_chain = {}
    chain = {}
    window = 1000
    i = 0
    temp = []
    for cyc in traffic.keys():
        for src in traffic[cyc].keys():
            byte = sum(list(traffic[cyc][src].values()))
            temp.append(byte)
            if i < window:
                i += 1
            else:
                i = 0
                state = temp[0]
                for j in range(1, len(temp)):
                    if state not in chain.keys():
                        chain.setdefault(state, {})[temp[j]] = 1
                    else:
                        if temp[j] not in chain[state].keys():
                            chain[state][temp[j]] = 1
                        else:
                            chain[state][temp[j]] += 1
                    state = temp[j]
                temp.clear()
                markov_chain[counter] = chain
                counter += 1

    markov_chain = dict(sorted(markov_chain.items(), key=lambda x: x[0]))
    for s in markov_chain.keys():
        markov_chain[s] = dict(sorted(markov_chain[s].items(), key=lambda x: x[0]))
        for st in markov_chain[s].keys():
            markov_chain[s][st] = dict(sorted(markov_chain[s][st].items(), key=lambda x: x[0]))

    for counter in markov_chain.keys():
        for cur in markov_chain[counter].keys():
            tot = sum(list(markov_chain[counter][cur].values()))
            for next, freq in markov_chain[counter][cur].items():
                markov_chain[counter][cur][next] = freq / tot
    for counter in markov_chain.keys():
        for cur in markov_chain[counter].keys():
            prev = 0
            for next, pdf in markov_chain[counter][cur].items():
                markov_chain[counter][cur][next] = pdf + prev
                prev += pdf

    return markov_chain


def burst_window_dependency(traffic):
    burst_window_dist = {}
    for cyc in traffic.keys():
        window_size = len(traffic[cyc].keys())
        burst_size = 0
        for src in traffic[cyc].keys():
            for dst, byte in traffic[cyc][src].items():
                burst_size += byte
        if burst_size not in burst_window_dist.keys():
            burst_window_dist.setdefault(burst_size, {})[window_size] = 1
        else:
            if window_size not in burst_window_dist[burst_size].keys():
                burst_window_dist[burst_size][window_size] = 1
            else:
                burst_window_dist[burst_size][window_size] += 1
    burst_window_dist = dict(sorted(burst_window_dist.items(), key=lambda x: x[0]))
    for b in burst_window_dist.keys():
        burst_window_dist[b] = dict(sorted(burst_window_dist[b].items(), key=lambda x: x[0]))
    for b in burst_window_dist.keys():
        tot = sum(list(burst_window_dist[b].values()))
        for win, freq in burst_window_dist[b].items():
            burst_window_dist[b][win] = freq / tot
    for b in burst_window_dist.keys():
        prev = 0
        for win, pdf in burst_window_dist[b].items():
            burst_window_dist[b][win] = pdf + prev
            prev += pdf
    """for b in burst_window_dist.keys():
        print("burst: " + str(b))
        for win, freq in burst_window_dist[b].items():
            print("\t" + str(win) + ": " + str(freq))"""
    return burst_window_dist


def reuse_distance(traffic):
    destination = {}
    for cyc in traffic.keys():
        for src in traffic[cyc].keys():
            if src not in destination.keys():
                destination.setdefault(src, {}).setdefault(cyc, [])
            else:
                if cyc not in destination[src].keys():
                    destination[src].setdefault(cyc, [])
            for dest, byte in traffic[cyc][src].items():
                if dest not in destination[src][cyc]:
                    destination[src][cyc].append(dest)

    reuse_distance = {}
    for src in destination.keys():
        if src not in reuse_distance.keys():
            reuse_distance.setdefault(src, {})
        stack = [destination[src][list(destination[src].keys())[0]][0]]
        for cyc, dest_list in destination[src].items():
            for dest in dest_list:
                if dest not in stack:
                    stack.append(dest)
                else:
                    counter = 0
                    temp = []
                    b = stack.pop()
                    while b != dest:
                        temp.append(b)
                        counter += 1
                        b = stack.pop()
                    temp.append(b)
                    if counter not in reuse_distance[src].keys():
                        reuse_distance[src][counter] = 1
                    else:
                        reuse_distance[src][counter] += 1
                    for b in temp:
                        stack.append(b)
        stack.clear()

    reuse_distance = dict(sorted(reuse_distance.items(), key=lambda x: x[0]))
    for s in reuse_distance.keys():
        reuse_distance[s] = dict(sorted(reuse_distance[s].items(), key=lambda x: x[0]))

    for src in reuse_distance.keys():
        total = sum(list(reuse_distance[src].values()))
        for dist, freq in reuse_distance[src].items():
            reuse_distance[src][dist] = freq / total
    for src in reuse_distance.keys():
        prev = 0
        for dist, pdf in reuse_distance[src].items():
            reuse_distance[src][dist] = pdf + prev
            prev += pdf
    """plt.bar(list(reuse_distance[2].keys()), list(reuse_distance[2].values()), width=0.5)
    plt.xticks([0, 1, 2])
    plt.xlabel("reuse distance")
    plt.ylabel("CDF")
    plt.show()"""
    return reuse_distance


def packet_distribution(request_packet):
    packet = {}
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "request injected":
                src = int(request_packet[id][j][1].split(": ")[1])
                dst = int(request_packet[id][j][2].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if src not in packet.keys():
                    packet.setdefault(src, {}).setdefault(dst, {})[byte] = 1
                else:
                    if dst not in packet[src].keys():
                        packet[src].setdefault(dst, {})[byte] = 1
                    else:
                        if byte not in packet[src][dst].keys():
                            packet[src][dst][byte] = 1
                        else:
                            packet[src][dst][byte] += 1

    packet = dict(sorted(packet.items(), key=lambda x: x[0]))
    for src in packet.keys():
        packet[src] = dict(sorted(packet[src].items(), key=lambda x: x[0]))
    for src in packet.keys():
        for dest in packet[src].keys():
            tot = sum(list(packet[src][dest].values()))
            for byte, freq in packet[src][dest].items():
                packet[src][dest][byte] = freq / tot
    for src in packet.keys():
        for dest in packet[src].keys():
            prev = 0
            for byte, pdf in packet[src][dest].items():
                packet[src][dest][byte] = pdf + prev
                prev += pdf
    return packet


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

    empirical_traffic = overall_injection_traffic(request_packet)
    markov_chain = generate_statistics_based_on_interval_sttistics_calculation_clustering_markov_chain(empirical_traffic)
    burst_win_dep = burst_window_dependency(empirical_traffic)
    reuse = reuse_distance(empirical_traffic)
    packet_dist = packet_distribution(request_packet)

    with open("model.txt", "w") as file:
        file.write("int_begin\n")
        for id in markov_chain.keys():
            file.write("st " + str(id) + "\n")
            for state in markov_chain[id].keys():
                file.write("b " + str(state) + "\n")
                for next_state, cdf in markov_chain[id][state].items():
                    file.write(str(next_state) + "\t" + str(cdf) + "\n")
        file.write("int_end\n\n")

        file.write("burst_win_begin\n")
        for burst in burst_win_dep.keys():
            file.write("bst " + str(burst) + "\n")
            for window, cdf in burst_win_dep[burst].items():
                file.write(str(window) + "\t" + str(cdf) + "\n")
        file.write("burst_win_end\n\n")

        file.write("reuse_begin\n")
        for src in reuse.keys():
            file.write("src " + str(src) + "\n")
            for dist, cdf in reuse[src].items():
                file.write(str(dist) + "\t" + str(cdf) + "\n")
        file.write("reuse_end\n\n")

        file.write("packet_dist_begin\n")
        for src in packet_dist.keys():
            file.write("src " + str(src) + "\n")
            for dest in packet_dist[src].keys():
                file.write("dest " + str(dest) + "\n")
                for byte, cdf in packet_dist[src][dest].items():
                    file.write(str(byte) + "\t" + str(cdf) + "\n")
        file.write("packet_dist_end\n")