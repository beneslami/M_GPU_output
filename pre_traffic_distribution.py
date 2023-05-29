import os.path
import sys

destination = {}
window_cycle = {}
iat = {}
iat_over_time = {}
reply_iat = {}
reply_window_cycle = {}
prev_time = {}
prev_reply_time = {}
processing_time = {}
window = {}
burst_cycle = {}
burst = {}
req_iat_burst_joint_distribution = {}
rep_iat_burst_joint_distribution = {}
prev = {}
flag = {}
reply_window = {}

def IAT_burst_size_dependency(window_cycle):       ############################section for request IAT and burst size dependency##################################

    for chiplet in window_cycle.keys():
        if chiplet not in req_iat_burst_joint_distribution.keys():
            req_iat_burst_joint_distribution.setdefault(chiplet, {})
        if chiplet not in flag.keys():
            flag[chiplet] = 1
        for cycle, byte in window_cycle[chiplet].items():
            if flag[chiplet] == 1:
                flag[chiplet] = 0
                if cycle not in req_iat_burst_joint_distribution[chiplet].keys():
                    req_iat_burst_joint_distribution[chiplet].setdefault(cycle, {})[sum(byte)] = 1
                    prev[chiplet] = cycle
            else:
                if cycle - prev[chiplet] not in req_iat_burst_joint_distribution[chiplet].keys():
                    req_iat_burst_joint_distribution[chiplet].setdefault(cycle - prev[chiplet], {})[sum(byte)] = 1
                else:
                    if sum(byte) not in req_iat_burst_joint_distribution[chiplet][cycle - prev[chiplet]].keys():
                        req_iat_burst_joint_distribution[chiplet][cycle - prev[chiplet]][sum(byte)] = 1
                    else:
                        req_iat_burst_joint_distribution[chiplet][cycle - prev[chiplet]][sum(byte)] += 1
                prev[chiplet] = cycle
    req_iat_burst_joint_distribution = dict(sorted(req_iat_burst_joint_distribution.items(), key=lambda x: x[0]))
    for chiplet in req_iat_burst_joint_distribution.keys():
        req_iat_burst_joint_distribution[chiplet] = dict(sorted(req_iat_burst_joint_distribution[chiplet].items(), key=lambda x: x[0]))
        for t in req_iat_burst_joint_distribution[chiplet].keys():
            req_iat_burst_joint_distribution[chiplet][t] = dict(sorted(req_iat_burst_joint_distribution[chiplet][t].items(), key=lambda x: x[0]))

def reply_IAT_burst_size_dependency(reply_window_cycle): ############################section for reply IAT and burst size dependency##################################

    prev.clear()
    flag.clear()
    for chiplet in reply_window_cycle.keys():
            if chiplet not in rep_iat_burst_joint_distribution.keys():
                rep_iat_burst_joint_distribution.setdefault(chiplet, {})
            if chiplet not in flag.keys():
                flag[chiplet] = 1
            for cycle, byte in reply_window_cycle[chiplet].items():
                if flag[chiplet] == 1:
                    flag[chiplet] = 0
                    if cycle not in rep_iat_burst_joint_distribution[chiplet].keys():
                        rep_iat_burst_joint_distribution[chiplet].setdefault(cycle, {})[sum(byte)] = 1
                        prev[chiplet] = cycle
                else:
                    if cycle - prev[chiplet] not in rep_iat_burst_joint_distribution[chiplet].keys():
                        rep_iat_burst_joint_distribution[chiplet].setdefault(cycle - prev[chiplet], {})[sum(byte)] = 1
                    else:
                        if sum(byte) not in rep_iat_burst_joint_distribution[chiplet][cycle - prev[chiplet]].keys():
                            rep_iat_burst_joint_distribution[chiplet][cycle - prev[chiplet]][sum(byte)] = 1
                        else:
                            rep_iat_burst_joint_distribution[chiplet][cycle - prev[chiplet]][sum(byte)] += 1
                    prev[chiplet] = cycle
    rep_iat_burst_joint_distribution = dict(sorted(rep_iat_burst_joint_distribution.items(), key=lambda x: x[0]))
    for chiplet in rep_iat_burst_joint_distribution.keys():
        rep_iat_burst_joint_distribution[chiplet] = dict(sorted(rep_iat_burst_joint_distribution[chiplet].items(), key=lambda x: x[0]))
        for t in rep_iat_burst_joint_distribution[chiplet].keys():
            rep_iat_burst_joint_distribution[chiplet][t] = dict(sorted(rep_iat_burst_joint_distribution[chiplet][t].items(), key=lambda x: x[0]))
                
def window_size_burst_dpendency(window_cycle):    ############################section for request window size and request burst size##################################
    for chiplet in window_cycle.keys():
        if chiplet not in window.keys():
            window.setdefault(chiplet, {})
        #if chiplet not in burst_cycle.keys():
            #burst_cycle.setdefault(chiplet, {})
        for cycle, win in window_cycle[chiplet].items():
            if len(win) not in window[chiplet].keys():
                window[chiplet].setdefault(len(win), {})[sum(win)] = 1
            else:
                if sum(win) not in window[chiplet][len(win)].keys():
                    window[chiplet][len(win)][sum(win)] = 1
                else:
                    window[chiplet][len(win)][sum(win)] += 1
            """if cycle not in burst_cycle[chiplet].keys():
                burst_cycle[chiplet][cycle] = sum(win)
            else:
                burst_cycle[chiplet][cycle] += sum(win)
    burst_cycle = dict(sorted(burst_cycle.items(), key=lambda x: x[0]))
    for chiplet in burst_cycle.keys():
        burst_cycle[chiplet] = dict(sorted(burst_cycle[chiplet].items(), key=lambda x: x[0]))
        if chiplet not in burst.keys():
            burst.setdefault(chiplet, {})
        for cycle, byte in burst_cycle[chiplet].items():
            if byte not in burst[chiplet].keys():
                burst[chiplet][byte] = 1
            else:
                burst[chiplet][byte] += 1"""
    for i in window.keys():
        window[i] = dict(sorted(window[i].items(), key=lambda x: x[0]))
    #for chiplet in burst.keys():
        #burst[chiplet] = dict(sorted(burst[chiplet].items(), key=lambda x: x[0]))

def per_chiplet_model(input_, request_packet, reply_packet):
    base_path = os.path.dirname(input_)
    global iat_over_time 
    global prev_time 
    global iat 
    global window_cycle
    global window
    global destination 
    global processing_time 
    global reply_window_cycle 
    global prev_reply_time 
    global reply_iat 
    global reply_window 
    
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "request injected":
                chiplet = int(request_packet[id][j][1].split(": ")[1])
                dest = int(request_packet[id][j][2].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if chiplet not in prev_time.keys():
                    prev_time[chiplet] = cycle
                    iat_over_time.setdefault(chiplet, {})[cycle] = cycle
                if cycle - prev_time[chiplet] > 0:
                    if chiplet not in iat.keys():
                        iat.setdefault(chiplet, {})[cycle - prev_time[chiplet]] = 1
                        iat_over_time.setdefault(chiplet, {})[cycle] = cycle - prev_time[chiplet]
                        prev_time[chiplet] = cycle
                    else:
                        if (cycle - prev_time[chiplet]) not in iat[chiplet].keys():
                            iat[chiplet][cycle - prev_time[chiplet]] = 1
                        else:
                            iat[chiplet][cycle - prev_time[chiplet]] += 1
                        iat_over_time.setdefault(chiplet, {})[cycle] = cycle - prev_time[chiplet]
                        prev_time[chiplet] = cycle

                if chiplet not in window_cycle.keys():
                    window_cycle.setdefault(chiplet, {}).setdefault(cycle, []).append(byte)
                else:
                    if cycle not in window_cycle[chiplet].keys():
                        window_cycle[chiplet].setdefault(cycle, []).append(byte)
                    else:
                        window_cycle[chiplet][cycle].append(byte)

                if chiplet not in destination.keys():
                    destination.setdefault(chiplet, {})[dest] = 1
                else:
                    if dest not in destination[chiplet].keys():
                        destination[chiplet][dest] = 1
                    else:
                        destination[chiplet][dest] += 1

            elif request_packet[id][j][0] == "request received":
                chiplet = int(request_packet[id][j][6].split(": ")[1])
                in_time = int(request_packet[id][j][5].split(": ")[1])
                for k in range(j, len(request_packet[id])):
                    if request_packet[id][k][0] == "reply injected":
                        assert int(request_packet[id][k][6].split(": ")[1]) == chiplet
                        out_time = int(request_packet[id][k][5].split(": ")[1])
                        if chiplet not in processing_time.keys():
                            processing_time.setdefault(chiplet, {})[out_time - in_time] = 1
                        else:
                            if (out_time - in_time) not in processing_time[chiplet].keys():
                                processing_time[chiplet][out_time - in_time] = 1
                            else:
                                processing_time[chiplet][out_time - in_time] += 1
                        break

    for id in reply_packet.keys():
        for j in range(len(reply_packet[id])):
            if reply_packet[id][j][0] == "reply injected":
                chiplet = int(reply_packet[id][j][6].split(": ")[1])
                cycle = int(reply_packet[id][j][5].split(": ")[1])
                byte = int(reply_packet[id][j][7].split(": ")[1])
                if chiplet not in reply_window_cycle.keys():
                    reply_window_cycle.setdefault(chiplet, {}).setdefault(cycle, []).append(byte)
                else:
                    if cycle not in reply_window_cycle[chiplet].keys():
                        reply_window_cycle[chiplet].setdefault(cycle, []).append(byte)
                    else:
                        reply_window_cycle[chiplet][cycle].append(byte)

                if chiplet not in prev_reply_time.keys():
                    prev_reply_time[chiplet] = cycle
                if chiplet not in reply_iat.keys():
                    reply_iat.setdefault(chiplet, {})[cycle - prev_reply_time[chiplet]] = 1
                    prev_reply_time[chiplet] = cycle
                else:
                    if (cycle - prev_reply_time[chiplet]) not in reply_iat[chiplet].keys():
                        reply_iat[chiplet][cycle - prev_reply_time[chiplet]] = 1
                    else:
                        reply_iat[chiplet][cycle - prev_reply_time[chiplet]] += 1
                    prev_reply_time[chiplet] = cycle

    for chiplet in reply_window_cycle.keys():
        for cycle, win in reply_window_cycle[chiplet].items():
            if chiplet not in reply_window.keys():
                reply_window.setdefault(chiplet, {})[len(win)] = 1
            else:
                if len(win) not in reply_window[chiplet].keys():
                    reply_window[chiplet][len(win)] = 1
                else:
                    reply_window[chiplet][len(win)] += 1

    for chiplet in window_cycle.keys():
        if chiplet not in window.keys():
            window.setdefault(chiplet, {})
        # if chiplet not in burst_cycle.keys():
        # burst_cycle.setdefault(chiplet, {})
        for cycle, win in window_cycle[chiplet].items():
            if len(win) not in window[chiplet].keys():
                window[chiplet].setdefault(len(win), {})[sum(win)] = 1
            else:
                if sum(win) not in window[chiplet][len(win)].keys():
                    window[chiplet][len(win)][sum(win)] = 1
                else:
                    window[chiplet][len(win)][sum(win)] += 1
            """if cycle not in burst_cycle[chiplet].keys():
                burst_cycle[chiplet][cycle] = sum(win)
            else:
                burst_cycle[chiplet][cycle] += sum(win)
    burst_cycle = dict(sorted(burst_cycle.items(), key=lambda x: x[0]))
    for chiplet in burst_cycle.keys():
        burst_cycle[chiplet] = dict(sorted(burst_cycle[chiplet].items(), key=lambda x: x[0]))
        if chiplet not in burst.keys():
            burst.setdefault(chiplet, {})
        for cycle, byte in burst_cycle[chiplet].items():
            if byte not in burst[chiplet].keys():
                burst[chiplet][byte] = 1
            else:
                burst[chiplet][byte] += 1"""

    iat_over_time = dict(sorted(iat_over_time.items(), key=lambda x: x[0]))
    for chiplet in iat_over_time.keys():
        iat_over_time[chiplet] = dict(sorted(iat_over_time[chiplet].items(), key=lambda x: x[0]))   
    for i in reply_window.keys():
        reply_window[i] = dict(sorted(reply_window[i].items(), key=lambda x: x[0]))
    for i in iat.keys():
        iat[i] = dict(sorted(iat[i].items(), key=lambda x: x[0]))
    for i in processing_time.keys():
        processing_time[i] = dict(sorted(processing_time[i].items(), key=lambda x: x[0]))
    for chiplet in reply_iat.keys():
        reply_iat[chiplet] = dict(sorted(reply_iat[chiplet].items(), key=lambda x: x[0]))
    for chiplet in destination.keys():
        destination[chiplet] = dict(sorted(destination[chiplet].items(), key=lambda x: x[0]))
    window = dict(sorted(window.items(), key=lambda x: x[0]))
    for i in window.keys():
        window[i] = dict(sorted(window[i].items(), key=lambda x: x[0]))
        for burst in window[i].keys():
            window[i][burst] = dict(sorted(window[i][burst].items(), key=lambda x: x[0]))

    chiplet_num = list(window_cycle.keys())
    for chiplet in chiplet_num:
        with open("models/chiplet_" + str(chiplet) + ".txt", "w") as file:
            file.write("chiplet " + str(chiplet) + "\n")
        
            file.write("\nrequest_packet_distribution_begin\n")
            file.write("request_packet_distribution_end\n")
        
            file.write("\nreply_packet_distribution_begin\n")
            file.write("reply_packet_distribution_end\n")        
        
            file.write("\ndestination_begin\n")
            try:
                for dest, freq in destination[chiplet].items():
                    file.write(str(dest) + "\t" + str(freq) + "\n")
            except KeyError:
                pass
            file.write("destination_end\n")
        
            file.write("\nInter_arrival_time_begin\n")
            try:
                for duration, freq in iat[chiplet].items():
                    file.write(str(duration) + "\t" + str(freq) + "\n")
            except KeyError:
                pass
            file.write("Inter_arrival_time_end\n")
            
            file.write("\ntotal_window_size_begin\n")
            try:
                for win, val in window[chiplet].items():
                    tot_freq = 0
                    for burst, freq in val.items():
                        tot_freq += freq
                    file.write(str(win) + "\t" + str(tot_freq) + "\tbegin\t")
                    for burst, freq in val.items():
                        file.write(str(burst) + "\t" + str(freq) + "\t")
                    file.write("end\n")
            except KeyError:
                pass
            file.write("total_window_size_end\n")
        
            file.write("\nprocessing_time_begin\n")
            try:
                for duration, frequency in processing_time[chiplet].items():
                    file.write(str(duration) + "\t" + str(frequency) + "\n")
            except KeyError:
                pass
            file.write("processing_time_end\n")
        
            file.write("\nreply_window_size_begin\n")
            try:
                for win, freq in reply_window[chiplet].items():
                    file.write(str(win) + "\t" + str(freq) + "\n")
            except KeyError:
                pass
            file.write("\nreply_window_size_end\n")
        
            file.write("\nreply_inter_arrival_time_begin\n")
            try:
                for duration, freq in reply_iat[chiplet].items():
                    file.write(str(duration) + "\t" + str(freq) + "\n")
            except KeyError:
                pass
            file.write("reply_inter_arrival_time_end\n")
        
        
