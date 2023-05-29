import matplotlib.pyplot as plt


def temporal_locality(packet):
    locality = {}
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "request injected":
                source = int(packet[id][j][1].split(": ")[1])
                dest = int(packet[id][j][2].split(": ")[1])
                cycle = int(packet[id][j][5].split(": ")[1])
                byte = int(packet[id][j][7].split(": ")[1])
                if source not in locality.keys():
                    locality.setdefault(source, {}).setdefault(dest, {})[cycle] = byte
                else:
                    if dest not in locality[source].keys():
                        locality[source].setdefault(dest, {})[cycle] = byte
                    else:
                        if cycle not in locality[source][dest].keys():
                            locality[source][dest][cycle] = byte
                        else:
                            locality[source][dest][cycle] += byte
    locality = dict(sorted(locality.items(), key=lambda x: x[0]))
    for src in locality.keys():
        locality[src] = dict(sorted(locality[src].items(), key=lambda x: x[0]))
        for dest in locality[src].keys():
            locality[src][dest] = dict(sorted(locality[src][dest].items(), key=lambda x: x[0]))

    for src in locality.keys():
        for dest in locality[src].keys():
            flag = 0
            prev_cycle = 0
            distribution = {}
            for cycle, byte in locality[src][dest].items():
                if flag == 0:
                    flag = 1
                    prev_cycle = cycle
                if cycle - prev_cycle > 0:
                    if cycle - prev_cycle not in distribution.keys():
                        distribution.setdefault(cycle - prev_cycle, []).append(byte)
                    else:
                        distribution[cycle - prev_cycle].append(byte)
                    prev_cycle = cycle
            distribution = dict(sorted(distribution.items(), key=lambda x: x[0]))
            x = list(distribution.keys())
            y = []
            for c, l in distribution.items():
                y.append(len(l))
            plt.plot(x, y, marker='*', label=str(src) + "->" + str(dest))
    plt.legend()
    plt.show()