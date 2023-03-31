import sys

if __name__ == '__main__':
    input_ = sys.argv[1]
    file2 = open(input_, "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]

        lined_list.append(item)
    packet = {}
    Packet = {}
    Trace = {}
    del(raw_content)

    for i in range(len(lined_list)):
        if int(lined_list[i][3].split(": ")[1]) in packet.keys():
            if lined_list[i] not in packet[int(lined_list[i][3].split(": ")[1])]:
                packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
        else:
            packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])

    window_cycle = {}
    iat = {}
    prev_time = {}
    processing_time = {}
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "request injected":
                chiplet = int(packet[id][j][1].split(": ")[1])
                cycle = int(packet[id][j][5].split(": ")[1])
                if chiplet not in prev_time.keys():
                    prev_time[chiplet] = 0
                if chiplet not in iat.keys():
                    iat.setdefault(chiplet, {})[cycle - prev_time[chiplet]] = 1
                    prev_time[chiplet] = cycle
                else:
                    if (cycle - prev_time[chiplet]) not in iat[chiplet].keys():
                        iat[chiplet][cycle - prev_time[chiplet]] = 1
                    else:
                        iat[chiplet][cycle - prev_time[chiplet]] += 1
                    prev_time[chiplet] = cycle

                if chiplet not in window_cycle.keys():
                    window_cycle.setdefault(chiplet, {})[cycle] = 1
                else:
                    if cycle not in window_cycle[chiplet].keys():
                        window_cycle[chiplet][cycle] = 1
                    else:
                        window_cycle[chiplet][cycle] += 1
            if packet[id][j][0] == "request received":
                chiplet = int(packet[id][j][6].split(": ")[1])
                in_time = int(packet[id][j][5].split(": ")[1])
                for k in range(j, len(packet[id])):
                    if packet[id][k][0] == "reply injected":
                        assert int(packet[id][k][6].split(": ")[1]) == chiplet
                        out_time = int(packet[id][k][5].split(": ")[1])
                        if chiplet not in processing_time.keys():
                            processing_time.setdefault(chiplet, {})[out_time - in_time] = 1
                        else:
                            if (out_time - in_time) not in processing_time[chiplet].keys():
                                processing_time[chiplet][out_time - in_time] = 1
                            else:
                                processing_time[chiplet][out_time - in_time] += 1
                        break
    window = {}
    for chiplet in window_cycle.keys():
        for cycle, win in window_cycle[chiplet].items():
            if chiplet not in window.keys():
                window.setdefault(chiplet, {})[win] = 1
            else:
                if win not in window[chiplet].keys():
                    window[chiplet][win] = 1
                else:
                    window[chiplet][win] += 1

    chiplet_num = len(window)
    for i in range(chiplet_num):
        iat[i] = dict(sorted(iat[i].items(), key=lambda x: x[0]))
        window[i] = dict(sorted(window[i].items(), key=lambda x: x[0]))

    chiplet = 14
    for k, v in iat[chiplet].items():
        print(str(k) + ", " + str(v))
    print("-------------------------")
    for k, v in window[chiplet].items():
        print(str(k) + ", " + str(v))
    print("-------------------------")
    for k, v in processing_time[chiplet].items():
        print(str(k) + ", " + str(v))