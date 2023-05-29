import sys
import os
import re
from contention import *
import numpy as np
import plotly.graph_objects as go
import pandas as pd


def bar_distribution_plot(base_path, traffic, chiplet_num, plot_name):
    if base_path.__contains__("fly"):
        injection_per_chiplet_rate = traffic
        _x = np.arange(0, max(injection_per_chiplet_rate.keys()) + 1, 1)
        _y = np.arange(0, max(injection_per_chiplet_rate.keys()) + 1, 1)
        n_row = len(injection_per_chiplet_rate.keys())
        thikness = 0.5
        thikness *= 0.5
        fig = go.Figure()
        for x in injection_per_chiplet_rate.keys():
            x_cnt = x % n_row
            x_min = x_cnt - thikness
            x_max = x_cnt + thikness
            for y in injection_per_chiplet_rate[x].keys():
                y_cnt = y
                y_min = y_cnt - thikness
                y_max = y_cnt + thikness
                Z = injection_per_chiplet_rate[x][y]
                go.Layout(width=1024, height=1024, )
                fig.add_trace(go.Mesh3d(
                    x=[x_min, x_min, x_max, x_max, x_min, x_min, x_max, x_max],
                    y=[y_min, y_max, y_max, y_min, y_min, y_max, y_max, y_min],
                    z=[0, 0, 0, 0, Z, Z, Z, Z], opacity=1, alphahull=0, color="green",
                    intensity=np.linspace(0, 1, 12, endpoint=True), intensitymode='vertex', ))
        z_axis_name = ""
        if plot_name.__contains__("throughput"):
            z_axis_name = "average throughput (Bytes/cycle)"
        elif plot_name.__contains__("channel"):
            z_axis_name = "Average channel BW (normalized)"
        fig.update_layout(scene=dict(
            xaxis=dict(backgroundcolor="rgb(200, 200, 230)", gridcolor="white", showbackground=True,
                       zerolinecolor="white",
                       tickvals=list(range(0, len(injection_per_chiplet_rate.keys()) + 1)), showline=True,
                       titlefont=dict(family='arial, sans-serif', size=18)),
            yaxis=dict(backgroundcolor="rgb(230, 200, 230)", gridcolor="white", showbackground=True,
                       zerolinecolor="white",
                       tickvals=list(range(0, len(injection_per_chiplet_rate.keys()) + 1)), showline=True,
                       titlefont=dict(family='arial, sans-serif', size=18)),
            zaxis=dict(backgroundcolor="rgb(230, 230, 200)", gridcolor="white", showbackground=True,
                       zerolinecolor="white",
                       showline=True, titlefont=dict(family='arial, sans-serif', size=18), )))
        fig.update_layout(
            scene=dict(xaxis_title='source chiplet', yaxis_title='router', zaxis_title=z_axis_name,
                       aspectratio=dict(x=1, y=0.1, z=1)),
            margin=dict(l=65, r=50, b=65, t=90))
        fig.write_html(base_path + "/plots/link_usage/" + plot_name + ".html")
    else:
        injection_per_chiplet_rate = traffic
        for src in range(chiplet_num):
            if src not in injection_per_chiplet_rate.keys():
                injection_per_chiplet_rate.setdefault(src, {})
            for dest in range(chiplet_num):
                if dest not in injection_per_chiplet_rate[src].keys():
                    injection_per_chiplet_rate[src][dest] = 0
        _x = np.arange(0, max(injection_per_chiplet_rate.keys()) + 1, 1)
        _y = np.arange(0, max(injection_per_chiplet_rate.keys()) + 1, 1)
        n_row = len(injection_per_chiplet_rate.keys())

        thikness = 0.5
        thikness *= 0.5
        fig = go.Figure()
        for x in injection_per_chiplet_rate.keys():
            x_cnt = x % n_row
            x_min = x_cnt - thikness
            x_max = x_cnt + thikness
            for y in injection_per_chiplet_rate[x].keys():
                y_cnt = y % n_row
                y_min = y_cnt - thikness
                y_max = y_cnt + thikness
                Z = injection_per_chiplet_rate[x][y]
                go.Layout(width=1024, height=1024,)
                fig.add_trace(go.Mesh3d(
                    x=[x_min, x_min, x_max, x_max, x_min, x_min, x_max, x_max],
                    y=[y_min, y_max, y_max, y_min, y_min, y_max, y_max, y_min],
                    z=[0, 0, 0, 0, Z, Z, Z, Z], opacity=1, alphahull=0, color="green", intensity=np.linspace(0, 1, 12, endpoint=True), intensitymode='vertex',))
        z_axis_name = ""
        if plot_name.__contains__("throughput"):
            z_axis_name = "average throughput (Bytes/cycle)"
        elif plot_name.__contains__("channel"):
            z_axis_name = "Average channel BW (normalized)"
        fig.update_layout(scene=dict(
            xaxis=dict(backgroundcolor="rgb(200, 200, 230)", gridcolor="white", showbackground=True, zerolinecolor="white",
                       tickvals=list(range(0, len(injection_per_chiplet_rate.keys()) + 1)), showline=True,
                       titlefont=dict(family='arial, sans-serif', size=18)),
            yaxis=dict(backgroundcolor="rgb(230, 200, 230)", gridcolor="white", showbackground=True, zerolinecolor="white",
                       tickvals=list(range(0, len(injection_per_chiplet_rate.keys()) + 1)), showline=True,
                       titlefont=dict(family='arial, sans-serif', size=18)),
            zaxis=dict(backgroundcolor="rgb(230, 230, 200)", gridcolor="white", showbackground=True, zerolinecolor="white",
                       showline=True, titlefont=dict(family='arial, sans-serif', size=18),)))
        fig.update_layout(
            scene=dict(xaxis_title='source router', yaxis_title='destination router', zaxis_title=z_axis_name, aspectratio=dict(x=1, y=1, z=1)),
            margin=dict(l=65, r=50, b=65, t=90))
        if os.path.exists(base_path + "/plots/link_usage"):
            pass
        else:
            os.system("mkdir " + base_path + "/plots/link_usage/")
        fig.write_html(base_path + "/plots/link_usage/" + plot_name + ".html")
        #fig.show()


def measure_average_link_usage_between_routers(input_, chiplet_num):
    base_path = os.path.dirname(input_)
    path = base_path + "/link_usage/"
    link = {}
    link_usage = {}
    avg_channel_bw = {}
    max_duration = {}

    if base_path.__contains__("fly"):
        if base_path.__contains__("4chiplet") or base_path.__contains__("8chiplet"):
            for i in range(chiplet_num):
                file_name = path + "side_link_usage_" + str(i) + "0.csv"
                if os.path.exists(file_name):
                    if i not in link.keys():
                        link.setdefault(i, {}).setdefault(0, {})
                        link_usage.setdefault(i, {}).setdefault(0, [])
                        avg_channel_bw.setdefault(i, {}).setdefault(0, [])
                        max_duration.setdefault(i, {}).setdefault(0, [])
                    df = pd.read_csv(file_name)
                    x = df['cycle']
                    y = df['byte']
                    res = {x[i]: y[i] for i in range(len(x))}
                    minimum = min(x)
                    maximum = max(x)
                    max_duration[i][0] = maximum - minimum
                    for c in range(minimum, maximum + 1):
                        if c not in res.keys():
                            res[c] = 0
                    res = dict(sorted(res.items(), key=lambda x: x[0]))
                    for cycle, byte in res.items():
                        link[i][0][cycle] = byte
            for src in link.keys():
                for dest in link[src].keys():
                    cycle_flag = 0
                    aggregate_byte = 0
                    prev_cycle = 0
                    for cycle, byte in link[src][dest].items():
                        if byte != 0:
                            if cycle_flag == 0:
                                prev_cycle = cycle
                                cycle_flag = 1
                            aggregate_byte += byte
                        elif byte == 0:
                            if cycle_flag == 1:
                                duration = cycle - prev_cycle
                                link_usage[src][dest].append(aggregate_byte / duration)
                                avg_channel_bw[src][dest].append(duration)
                                cycle_flag = 0
                                aggregate_byte = 0
            for src in avg_channel_bw.keys():
                avg_channel_bw[src][0] = np.sum(avg_channel_bw[src][0]) / max_duration[src][0]
            bar_distribution_plot(base_path, avg_channel_bw, chiplet_num, "average_channel_use")
        else:
            pass
    else:
        for src in range(chiplet_num):
            for dest in range(chiplet_num):
                if src != dest:
                    file_name = path + "link_usage_" + str(src) + str(dest) + ".csv"
                    if os.path.exists(file_name) and os.path.getsize(file_name) > 500:
                        if src not in link.keys():
                            link.setdefault(src, {})
                            link_usage.setdefault(src, {})
                            avg_channel_bw.setdefault(src, {})
                            max_duration.setdefault(src, {})
                        if dest not in link[src].keys():
                            link[src].setdefault(dest, {})
                            link_usage[src].setdefault(dest, [])
                            avg_channel_bw[src].setdefault(dest, [])
                        df = pd.read_csv(file_name)
                        x = df['cycle']
                        y = df['byte']
                        res = {x[i]: y[i] for i in range(len(x))}
                        minimum = min(x)
                        maximum = max(x)
                        max_duration[src][dest] = maximum - minimum
                        for c in range(minimum, maximum+1):
                            if c not in res.keys():
                                res[c] = 0
                        res = dict(sorted(res.items(), key=lambda x: x[0]))
                        for cycle, byte in res.items():
                            link[src][dest][cycle] = byte
        for src in link.keys():
            for dest in link[src].keys():
                cycle_flag = 0
                aggregate_byte = 0
                prev_cycle = 0
                for cycle, byte in link[src][dest].items():
                    if byte != 0:
                        if cycle_flag == 0:
                            prev_cycle = cycle
                            cycle_flag = 1
                        aggregate_byte += byte
                    elif byte == 0:
                        if cycle_flag == 1:
                            duration = cycle - prev_cycle
                            link_usage[src][dest].append(aggregate_byte / duration)
                            avg_channel_bw[src][dest].append(duration)
                            cycle_flag = 0
                            aggregate_byte = 0
        for src in avg_channel_bw.keys():
            for dest in avg_channel_bw[src].keys():
                avg_channel_bw[src][dest] = np.sum(avg_channel_bw[src][dest]) / max_duration[src][dest]
        bar_distribution_plot(base_path, avg_channel_bw, chiplet_num, "average_channel_use")


def measure_throughput_per_link(input_, chiplet_num):
    base_path = os.path.dirname(input_)
    path = base_path + "/link_usage/"
    link = {}
    throughput = {}
    if base_path.__contains__("fly"):
        if base_path.__contains__("4chiplet") or base_path.__contains__("8chiplet"):
            for i in range(chiplet_num):
                file_name = path + "side_link_usage_" + str(i) + "0.csv"
                if os.path.exists(file_name):
                    if i not in link.keys():
                        link.setdefault(i, {}).setdefault(0, {})
                        throughput.setdefault(i, {})
                    df = pd.read_csv(file_name)
                    x = df['cycle']
                    y = df['byte']
                    res = {x[i]: y[i] for i in range(len(x))}
                    minimum = min(x)
                    maximum = max(x)
                    for c in range(minimum, maximum + 1):
                        if c not in res.keys():
                            res[c] = 0
                    res = dict(sorted(res.items(), key=lambda x: x[0]))
                    for cycle, byte in res.items():
                        link[i][0][cycle] = byte
            for src in link.keys():
                minimum = min(list(link[src][0].keys()))
                maximum = max(list(link[src][0].keys()))
                throughput[src][0] = np.sum(list(link[src][0].values())) / (maximum - minimum)
            bar_distribution_plot(base_path, throughput, chiplet_num, "average_throughput")
        else:
            pass
    else:
        for src in range(chiplet_num):
            for dest in range(chiplet_num):
                if src != dest:
                    file_name = path + "link_usage_" + str(src) + str(dest) + ".csv"
                    if os.path.exists(file_name) and os.path.getsize(file_name) > 500:
                        if src not in link.keys():
                            link.setdefault(src, {})
                            throughput.setdefault(src, {})
                        if dest not in link[src].keys():
                            link[src].setdefault(dest, {})
                        df = pd.read_csv(file_name)
                        x = df['cycle']
                        y = df['byte']
                        res = {x[i]: y[i] for i in range(len(x))}
                        minimum = min(x)
                        maximum = max(x)
                        for c in range(minimum, maximum + 1):
                            if c not in res.keys():
                                res[c] = 0
                        res = dict(sorted(res.items(), key=lambda x: x[0]))
                        for cycle, byte in res.items():
                           link[src][dest][cycle] = byte
        for src in link.keys():
            for dest in link[src].keys():
                minimum = min(list(link[src][dest].keys()))
                maximum = max(list(link[src][dest].keys()))
                throughput[src][dest] = np.sum(list(link[src][dest].values())) / (maximum - minimum)
        bar_distribution_plot(base_path, throughput, chiplet_num, "average_throughput")


def measure_router_inter_arrival_time(input_, chiplet_num):
    router = {}
    base_path = os.path.dirname(input_)
    path = base_path + "/link_usage/"
    for src in range(chiplet_num):
        for dest in range(chiplet_num):
            if src != dest:
                file_name = path + "link_usage_" + str(src) + str(dest) + ".csv"
                if os.path.exists(file_name):
                    if src not in router.keys():
                        router.setdefault(src, {})
                    if dest not in router[src].keys():
                        router[src].setdefault(dest, {})
                    df = pd.read_csv(file_name)
                    x = df['cycle']
                    y = df['byte']
                    res = {x[i]: y[i] for i in range(len(x))}
                    prev_cycle = list(res.keys())[0]
                    for cyc, byte in res.items():
                        if cyc - prev_cycle > 1:
                            if cyc - prev_cycle not in router[src][dest].keys():
                                router[src][dest][cyc - prev_cycle] = 1
                            else:
                                router[src][dest][cyc - prev_cycle] += 1
                            prev_cycle = cyc
                    router[src][dest] = dict(sorted(router[src][dest].items(), key=lambda x: x[0]))

    for src in router.keys():
        for dest in router[src].keys():
            total = sum(router[src][dest].values())
            for cycle in router[src][dest].keys():
                router[src][dest][cycle] = router[src][dest][cycle] / total
    plt.plot(router[2][3].keys(), router[2][3].values(), marker="*")
    plt.show()


def calculate_link_usage_(input_, packet, chiplet_num):
    link_usage = {}
    base_path = os.path.dirname(input_)
    if os.path.exists(base_path + "/link_usage"):
        pass
    else:
        for id in packet.keys():
            for j in range(len(packet[id])):
                if packet[id][j][0] == "request injected":
                    source = int(packet[id][j][1].split(": ")[1])
                    dest = int(packet[id][j][2].split(": ")[1])
                    cycle = int(packet[id][j][5].split(": ")[1])
                    byte = int(packet[id][j][7].split(": ")[1])
                    for k in range(j, len(packet[id])):
                        if packet[id][k][0] == "request received":
                            if source not in link_usage.keys():
                                link_usage.setdefault(source, {}).setdefault(dest, {})[cycle] = byte
                            else:
                                if dest not in link_usage[source].keys():
                                    link_usage[source].setdefault(dest, {})[cycle] = byte
                                else:
                                    if cycle not in link_usage[source][dest].keys():
                                        link_usage[source][dest][cycle] = byte
                                    else:
                                        link_usage[source][dest][cycle] += byte
                            break
                        elif packet[id][k][0] == "FW buffer" and (int(packet[id][k][4].split(": ")[1]) == 0 or int(packet[id][k][4].split(": ")[1]) == 2):
                            temp = int(packet[id][k][6].split(": ")[1])
                            if source not in link_usage.keys():
                                link_usage.setdefault(source, {}).setdefault(temp, {})[cycle] = byte
                            else:
                                if temp not in link_usage[source].keys():
                                    link_usage[source].setdefault(temp, {})[cycle] = byte
                                else:
                                    if cycle not in link_usage[source][temp].keys():
                                        link_usage[source][temp][cycle] = byte
                                    else:
                                        link_usage[source][temp][cycle] += byte
                            break

                elif packet[id][j][0] == "FW buffer" and (int(packet[id][j][4].split(": ")[1]) == 0 or int(packet[id][j][4].split(": ")[1]) == 2):
                    source = int(packet[id][j][6].split(": ")[1])
                    dest = int(packet[id][j][2].split(": ")[1])
                    cycle = int(packet[id][j][5].split(": ")[1])
                    byte = int(packet[id][j][7].split(": ")[1])
                    for k in range(j, len(packet[id])):
                        if packet[id][k][0] == "request received":
                            assert(dest == int(packet[id][k][2].split(": ")[1]))
                            if source not in link_usage.keys():
                                link_usage.setdefault(source, {}).setdefault(dest, {})[cycle] = byte
                            else:
                                if dest not in link_usage[source].keys():
                                    link_usage[source].setdefault(dest, {})[cycle] = byte
                                else:
                                    if cycle not in link_usage[source][dest].keys():
                                        link_usage[source][dest][cycle] = byte
                                    else:
                                        link_usage[source][dest][cycle] += byte
                            break

                elif packet[id][j][0] == "reply injected":
                    source = int(packet[id][j][6].split(": ")[1])
                    dest = int(packet[id][j][1].split(": ")[1])
                    cycle = int(packet[id][j][5].split(": ")[1])
                    byte = int(packet[id][j][7].split(": ")[1])
                    for k in range(j, len(packet[id])):
                        if packet[id][k][0] == "reply received":
                            if source not in link_usage.keys():
                                link_usage.setdefault(source, {}).setdefault(dest, {})[cycle] = byte
                            else:
                                if dest not in link_usage[source].keys():
                                    link_usage[source].setdefault(dest, {})[cycle] = byte
                                else:
                                    if cycle not in link_usage[source][dest].keys():
                                        link_usage[source][dest][cycle] = byte
                                    else:
                                        link_usage[source][dest][cycle] += byte
                            break
                        elif packet[id][k][0] == "FW buffer" and (int(packet[id][k][4].split(": ")[1]) == 1 or int(packet[id][k][4].split(": ")[1]) == 3):
                            temp = int(packet[id][k][6].split(": ")[1])
                            if source not in link_usage.keys():
                                link_usage.setdefault(source, {}).setdefault(temp, {})[cycle] = byte
                            else:
                                if temp not in link_usage[source].keys():
                                    link_usage[source].setdefault(temp, {})[cycle] = byte
                                else:
                                    if cycle not in link_usage[source][temp].keys():
                                        link_usage[source][temp][cycle] = byte
                                    else:
                                        link_usage[source][temp][cycle] += byte
                            break

                elif packet[id][j][0] == "FW buffer" and (int(packet[id][j][4].split(": ")[1]) == 1 or int(packet[id][j][4].split(": ")[1]) == 3):
                    source = int(packet[id][j][6].split(": ")[1])
                    dest = int(packet[id][j][2].split(": ")[1])
                    cycle = int(packet[id][j][5].split(": ")[1])
                    byte = int(packet[id][j][7].split(": ")[1])
                    for k in range(j, len(packet[id])):
                        if packet[id][k][0] == "reply received":
                            if source not in link_usage.keys():
                                link_usage.setdefault(source, {}).setdefault(dest, {})[cycle] = byte
                            else:
                                if dest not in link_usage[source].keys():
                                    link_usage[source].setdefault(dest, {})[cycle] = byte
                                else:
                                    if cycle not in link_usage[source][dest].keys():
                                        link_usage[source][dest][cycle] = byte
                                    else:
                                        link_usage[source][dest][cycle] += byte
                            break

        link_usage = dict(sorted(link_usage.items(), key=lambda x: x[0]))
        for c in link_usage.keys():
            link_usage[c] = dict(sorted(link_usage[c].items(), key=lambda x: x[0]))
        os.system("mkdir " + base_path + "/link_usage")
        for src in link_usage.keys():
            for dest in link_usage[src].keys():
                with open(base_path + "/link_usage/link_usage_" + str(src) + str(dest) + ".csv", "w") as file:
                    for cycle, byte in link_usage[src][dest].items():
                        file.write(str(cycle) + "," + str(byte) + "\n")
    measure_contention(input_, chiplet_num)
    #measure_average_link_usage_between_routers(input_, chiplet_num)
    #measure_throughput_per_link(input_, chiplet_num)
    #measure_router_inter_arrival_time(input_, chiplet_num)