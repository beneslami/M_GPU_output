import os.path
from colorama import Fore
from detector_engine import *
import homogeneous_mode_generator_engine
import spiky_sync_model
import spiky_nonSync_model_generator


def per_chiplet_model(base_path, request_packet, chiplet_num, kernel_num):
    destination = {}
    request_packet_type = {}
    reply_packet_type = {}
    window_cycle = {}
    iat = {}
    iat_over_time = {}
    reply_iat = {}
    reply_window_cycle = {}
    processing_time = {}
    window = {}
    reply_window = {}
    request_sequence = {}
    reply_sequence = {}
    dest_win = {}
    destination_window = {}
    for id in request_packet.keys():
        for j in range(len(request_packet[id])):
            if request_packet[id][j][0] == "request injected":
                chiplet = int(request_packet[id][j][1].split(": ")[1])
                dest = int(request_packet[id][j][2].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if chiplet not in request_sequence.keys():
                    request_sequence.setdefault(chiplet, []).append(cycle)
                else:
                    request_sequence[chiplet].append(cycle)

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
                if chiplet not in request_packet_type.keys():
                    request_packet_type.setdefault(chiplet, {}).setdefault(dest, {})[byte] = 1
                else:
                    if dest not in request_packet_type[chiplet].keys():
                        request_packet_type[chiplet].setdefault(dest, {})[byte] = 1
                    else:
                        if byte not in request_packet_type[chiplet][dest].keys():
                            request_packet_type[chiplet][dest][byte] = 1
                        else:
                            request_packet_type[chiplet][dest][byte] += 1
                if chiplet not in dest_win.keys():
                    dest_win.setdefault(chiplet, {}).setdefault(cycle, {})[dest] = 1
                else:
                    if cycle not in dest_win[chiplet].keys():
                        dest_win[chiplet].setdefault(cycle, {})[dest] = 1
                    else:
                        if dest not in dest_win[chiplet][cycle].keys():
                            dest_win[chiplet][cycle][dest] = 1
                        else:
                            dest_win[chiplet][cycle][dest] += 1

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

            elif request_packet[id][j][0] == "reply injected":
                chiplet = int(request_packet[id][j][6].split(": ")[1])
                dest = int(request_packet[id][j][1].split(": ")[1])
                cycle = int(request_packet[id][j][5].split(": ")[1])
                byte = int(request_packet[id][j][7].split(": ")[1])
                if chiplet not in reply_window_cycle.keys():
                    reply_window_cycle.setdefault(chiplet, {}).setdefault(cycle, []).append(byte)
                else:
                    if cycle not in reply_window_cycle[chiplet].keys():
                        reply_window_cycle[chiplet].setdefault(cycle, []).append(byte)
                    else:
                        reply_window_cycle[chiplet][cycle].append(byte)
                if chiplet not in reply_sequence.keys():
                    reply_sequence.setdefault(chiplet, []).append(cycle)
                else:
                    reply_sequence[chiplet].append(cycle)
                if chiplet not in reply_packet_type.keys():
                    reply_packet_type.setdefault(chiplet, {}).setdefault(dest, {})[byte] = 1
                else:
                    if dest not in reply_packet_type[chiplet].keys():
                        reply_packet_type[chiplet].setdefault(dest, {})[byte] = 1
                    else:
                        if byte not in reply_packet_type[chiplet][dest].keys():
                            reply_packet_type[chiplet][dest][byte] = 1
                        else:
                            reply_packet_type[chiplet][dest][byte] += 1

    for chiplet in dest_win.keys():
        for cyc in dest_win[chiplet].keys():
            for dest, freq in dest_win[chiplet][cyc].items():
                if chiplet not in destination_window.keys():
                    destination_window.setdefault(chiplet, {}).setdefault(dest, {})[freq] = 1
                else:
                    if dest not in destination_window[chiplet].keys():
                        destination_window[chiplet].setdefault(dest, {})[freq] = 1
                    else:
                        if freq not in destination_window[chiplet][dest].keys():
                            destination_window[chiplet][dest][freq] = 1
                        else:
                            destination_window[chiplet][dest][freq] += 1
    for chiplet in request_sequence.keys():
        if len(request_sequence[chiplet]) > 0:
            request_sequence[chiplet].sort()
            if chiplet not in iat.keys():
                iat.setdefault(chiplet, {})
                for i in range(len(request_sequence[chiplet])-1):
                    if request_sequence[chiplet][i+1] - request_sequence[chiplet][i] > 0:
                        if request_sequence[chiplet][i+1] - request_sequence[chiplet][i] not in iat[chiplet].keys():
                            iat[chiplet][request_sequence[chiplet][i+1] - request_sequence[chiplet][i]] = 1
                        else:
                            iat[chiplet][request_sequence[chiplet][i + 1] - request_sequence[chiplet][i]] += 1
    for chiplet in reply_sequence.keys():
        if len(reply_sequence[chiplet]) > 0:
            reply_sequence[chiplet].sort()
            if chiplet not in reply_iat.keys():
                reply_iat.setdefault(chiplet, {})
                for i in range(len(reply_sequence[chiplet])-1):
                    if reply_sequence[chiplet][i+1] - reply_sequence[chiplet][i] > 0:
                        if reply_sequence[chiplet][i+1] - reply_sequence[chiplet][i] not in reply_iat[chiplet].keys():
                            reply_iat[chiplet][reply_sequence[chiplet][i+1] - reply_sequence[chiplet][i]] = 1
                        else:
                            reply_iat[chiplet][reply_sequence[chiplet][i + 1] - reply_sequence[chiplet][i]] += 1
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
        for cycle, win in window_cycle[chiplet].items():
            if len(win) not in window[chiplet].keys():
                window[chiplet].setdefault(len(win), {})[sum(win)] = 1
            else:
                if sum(win) not in window[chiplet][len(win)].keys():
                    window[chiplet][len(win)][sum(win)] = 1
                else:
                    window[chiplet][len(win)][sum(win)] += 1

    destination_window = dict(sorted(destination_window.items(), key=lambda x: x[0]))
    for c in destination_window.keys():
        destination_window[c] = dict(sorted(destination_window[c].items(), key=lambda x: x[0]))
        for d in destination_window[c].keys():
            destination_window[c][d] = dict(sorted(destination_window[c][d].items(), key=lambda x: x[0]))
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
    for chiplet in request_packet_type.keys():
        request_packet_type[chiplet] = dict(sorted(request_packet_type[chiplet].items(), key=lambda x: x[0]))
        for dest in request_packet_type[chiplet].keys():
            request_packet_type[chiplet][dest] = dict(sorted(request_packet_type[chiplet][dest].items(), key=lambda x: x[0]))
    for chiplet in reply_packet_type.keys():
        reply_packet_type[chiplet] = dict(sorted(reply_packet_type[chiplet].items(), key=lambda x: x[0]))
        for dest in reply_packet_type[chiplet].keys():
            reply_packet_type[chiplet][dest] = dict(sorted(reply_packet_type[chiplet][dest].items(), key=lambda x: x[0]))
    request_packet_type = dict(sorted(request_packet_type.items(), key=lambda x: x[0]))
    reply_packet_type = dict(sorted(reply_packet_type.items(), key=lambda x: x[0]))
    window = dict(sorted(window.items(), key=lambda x: x[0]))
    for i in window.keys():
        window[i] = dict(sorted(window[i].items(), key=lambda x: x[0]))
        for burst in window[i].keys():
            window[i][burst] = dict(sorted(window[i][burst].items(), key=lambda x: x[0]))

    if os.path.exists(base_path + "/models/"):
        if os.path.exists(base_path + "/models/" + str(kernel_num)):
            pass
        else:
            os.mkdir(base_path + "/models/" + str(kernel_num))
    else:
        os.mkdir(base_path + "/models/")
        os.mkdir(base_path + "/models/" + str(kernel_num))
    for i in range(chiplet_num):
        with open(base_path + "/models/" + str(kernel_num) + "/chiplet_" + str(i) + ".txt", "w") as file:
            file.write("chiplet " + str(i) + "\n")

            file.write("\nrequest_packet_distribution_begin\n")
            try:
                for dest in request_packet_type[i].keys():
                    file.write("destination " + str(dest) + "\n")
                    for k, v in request_packet_type[i][dest].items():
                        file.write(str(k) + "\t" + str(v) + "\n")
            except KeyError:
                pass
            file.write("request_packet_distribution_end\n")

            file.write("\nreply_packet_distribution_begin\n")
            try:
                for dest in reply_packet_type[i].keys():
                    file.write("destination " + str(dest) + "\n")
                    for k, v in reply_packet_type[i][dest].items():
                        file.write(str(k) + "\t" + str(v) + "\n")
            except KeyError:
                pass
            file.write("reply_packet_distribution_end\n")

            file.write("\ndestination_begin\n")
            try:
                for dest, freq in destination[i].items():
                    file.write(str(dest) + "\t" + str(freq) + "\n")
            except KeyError:
                pass
            file.write("destination_end\n")

            """file.write("\nInter_arrival_time_begin\n")
            try:
                for duration, freq in iat[i].items():
                    file.write(str(duration) + "\t" + str(freq) + "\n")
            except KeyError:
                pass
            file.write("Inter_arrival_time_end\n")"""

            file.write("\ndest_window_begin\n")
            try:
                for dest in destination_window[i].keys():
                    file.write("dest\t" + str(dest) + "\n")
                    for win, freq in destination_window[i][dest].items():
                        file.write(str(win) + "\t" + str(freq) + "\n")
            except KeyError:
                pass
            file.write("dest_window_end\n")

            file.write("\nprocessing_time_begin\n")
            try:
                for duration, frequency in processing_time[i].items():
                    file.write(str(duration) + "\t" + str(frequency) + "\n")
            except KeyError:
                pass
            file.write("processing_time_end\n")

            file.write("\nreply_window_size_begin\n")
            try:
                for win, freq in reply_window[i].items():
                    file.write(str(win) + "\t" + str(freq) + "\n")
            except KeyError:
                pass
            file.write("reply_window_size_end\n")

            """file.write("\nreply_inter_arrival_time_begin\n")
            try:
                for duration, freq in reply_iat[i].items():
                    file.write(str(duration) + "\t" + str(freq) + "\n")
            except KeyError:
                pass
            file.write("reply_inter_arrival_time_end\n")"""
    print(Fore.GREEN + "chiplet models for kernel " + str(kernel_num) + " is generated " + u'\u2713' + Fore.WHITE)


def traffic_model(input_, request_packet, chiplet_num, kernel_num):
    req_off = {}
    req_byte_markov = {}
    req_burst_duration = {}
    req_burst_volume = {}
    req_byte_per_cycle = {}
    rep_off = {}
    rep_byte_markov = {}
    rep_burst_duration = {}
    rep_burst_volume = {}
    rep_byte_per_cycle = {}
    total_window = {}
    source = {}
    traffic_type = kernel_detection(input_)
    if traffic_type == "homogeneous":
        req_off, total_window, req_byte_markov, req_burst_duration, req_burst_volume, req_byte_per_cycle, source, rep_off, rep_byte_markov, rep_burst_duration, rep_burst_volume, rep_byte_per_cycle = homogeneous_mode_generator_engine.generate_traffic_characteristics_wrapper(request_packet)
    elif traffic_type == "spiky-sync":
        req_off, total_window, req_byte_markov, req_burst_duration, req_burst_volume, req_byte_per_cycle, source, rep_off, rep_byte_markov, rep_burst_duration, rep_burst_volume, rep_byte_per_cycle = spiky_sync_model.generate_traffic_characteristics_wrapper(request_packet)
    elif traffic_type == "spiky-async":
        req_off, total_window, req_byte_markov, req_burst_duration, req_burst_volume, req_byte_per_cycle, source, rep_off, rep_byte_markov, rep_burst_duration, rep_burst_volume, rep_byte_per_cycle = spiky_nonSync_model_generator.generate_traffic_characteristics_wrapper(request_packet)
    base_path = os.path.dirname(os.path.dirname(input_))
    if os.path.exists(base_path + "/models/"):
        if os.path.exists(base_path + "/models/" + str(kernel_num)):
            pass
        else:
            os.mkdir(base_path + "/models/" + str(kernel_num))
    else:
        os.mkdir(base_path + "/models/")
        os.mkdir(base_path + "/models/" + str(kernel_num))
    with open(base_path + "/models/" + str(kernel_num) + "/traffic.txt", "w") as file:
        file.write("req_off_time_begin\n")
        for k, v in req_off.items():
            file.write(str(k) + "\t" + str(v) + "\n")
        file.write("req_off_time_end\n\n")

        file.write("req_burst_time_begin\n")
        for prev in req_burst_duration.keys():
            file.write("burst\t" + str(prev) + "\n")
            for k, v in req_burst_duration[prev].items():
                file.write(str(k) + "\t" + str(v) + "\n")
        file.write("req_burst_time_end\n\n")

        file.write("req_burst_vol_begin\n")
        for byte in req_burst_volume.keys():
            file.write("burst\t" + str(byte) + "\n")
            for k, v in req_burst_volume[byte].items():
                file.write(str(k) + "\t" + str(v) + "\n")
        file.write("req_burst_vol_end\n\n")

        file.write("req_window_begin\n")
        for byte in total_window.keys():
            file.write("byte\t" + str(byte) + "\n")
            for k, v in total_window[byte].items():
                file.write(str(k) + "\t" + str(v) + "\n")
        file.write("req_window_end\n\n")

        file.write("req_byte_markov_begin\n")
        for byte in req_byte_markov.keys():
            file.write("b\t" + str(byte) + "\n")
            for k, v in req_byte_markov[byte].items():
                file.write(str(k) + "\t" + str(v) + "\n")
        file.write("req_byte_markov_end\n\n")

        file.write("req_byte_begin\n")
        for byte in req_byte_per_cycle:
            file.write(str(byte) + "\t")
        file.write("\nreq_byte_end\n\n")

        file.write("source_begin\n")
        for k, v in source.items():
            file.write(str(k) + "\t" + str(v) + "\n")
        file.write("source_end\n\n")

        file.write("rep_off_time_begin\n")
        for k, v in rep_off.items():
            file.write(str(k) + "\t" + str(v) + "\n")
        file.write("rep_off_time_end\n\n")

        file.write("rep_burst_time_begin\n")
        for prev in rep_burst_duration.keys():
            file.write("burst\t" + str(prev) + "\n")
            for k, v in rep_burst_duration[prev].items():
                file.write(str(k) + "\t" + str(v) + "\n")
        file.write("rep_burst_time_end\n\n")

        file.write("rep_burst_vol_begin\n")
        for time in rep_burst_volume.keys():
            file.write("burst\t" + str(time) + "\n")
            for k, v in rep_burst_volume[time].items():
                file.write(str(k) + "\t" + str(v) + "\n")
        file.write("rep_burst_vol_end\n\n")

        file.write("rep_byte_markov_begin\n")
        for byte in rep_byte_markov.keys():
            file.write("b\t" + str(byte) + "\n")
            for k, v in rep_byte_markov[byte].items():
                file.write(str(k) + "\t" + str(v) + "\n")
        file.write("rep_byte_markov_end\n\n")

        file.write("rep_byte_begin\n")
        for byte in rep_byte_per_cycle:
            file.write(str(byte) + "\t")
        file.write("\nrep_byte_end\n\n")

    print(Fore.GREEN + "traffic model for kernel " + str(kernel_num) + " is generated " + u'\u2713' + Fore.WHITE)