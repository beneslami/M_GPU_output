import os.path
import sys
from scipy.optimize import curve_fit
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
import plotly.graph_objects as go


def surface_distribution_plot(base_path, injection_per_chiplet_rate):
    _x = np.arange(0, max(injection_per_chiplet_rate.keys()) + 1, 1)
    _y = np.arange(0, max(injection_per_chiplet_rate.keys()) + 1, 1)
    X, Y = np.meshgrid(_x, _y)
    Z = []
    source = max(injection_per_chiplet_rate.keys()) + 1
    dest = max(injection_per_chiplet_rate.keys()) + 1
    for dst in range(0, dest, 1):
        temp = []
        for src in range(0, source, 1):
            temp.append(injection_per_chiplet_rate[src][dst])
        Z.append(temp)

    fig = go.Figure()
    fig.add_surface(x=X, y=Y, z=Z)
    fig.update_layout(scene=dict(
        xaxis=dict(backgroundcolor="rgb(200, 200, 230)", gridcolor="white", showbackground=True, zerolinecolor="white",
                   tickvals=list(range(0, max(injection_per_chiplet_rate.keys()) + 1)), showline=True,
                   titlefont=dict(family='Arial, sans-serif', size=18)),
        yaxis=dict(backgroundcolor="rgb(230, 200,230)", gridcolor="white", showbackground=True, zerolinecolor="white",
                   tickvals=list(range(0, max(injection_per_chiplet_rate.keys()) + 1)), showline=True,
                   titlefont=dict(family='Arial, sans-serif', size=18)),
        zaxis=dict(backgroundcolor="rgb(230, 230,200)", gridcolor="white", showbackground=True, zerolinecolor="white",
                   showline=True, titlefont=dict(family='Arial, sans-serif', size=18))))
    fig.update_layout(
        scene=dict(xaxis_title='Source chiplet', yaxis_title='Destination chiplet', zaxis_title='injection percentage'),
        margin=dict(l=65, r=50, b=65, t=90))
    fig.update_traces(contours_z=dict(show=True, usecolormap=True, highlightcolor="limegreen", project_z=True))
    fig.write_html(base_path + "/plots/source_destination_distribution.html")


def bar_distribution_plot(base_path, traffic, chiplet_num):
    total = 0
    for x in traffic.keys():
        for y in traffic[x].keys():
            for byte, freq in traffic[x][y].items():
                total += freq*byte

    injection_per_chiplet_rate = {}
    for x in traffic.keys():
        if len(traffic[x]) == 0:
            for i in range(chiplet_num):
                injection_per_chiplet_rate.setdefault(x, {}).setdefault(i, {})[0] = 0
        else:
            for y in traffic[x].keys():
                for byte, freq in traffic[x][y].items():
                    injection_per_chiplet_rate.setdefault(x, {}).setdefault(y, {})[byte] = (byte*freq) / total
    injection_per_chiplet_rate = dict(sorted(injection_per_chiplet_rate.items(), key=lambda x: x[0]))
    for src in injection_per_chiplet_rate.keys():
        injection_per_chiplet_rate[src] = dict(sorted(injection_per_chiplet_rate[src].items(), key=lambda x: x[0]))

    for i in range(chiplet_num):
        if i not in injection_per_chiplet_rate.keys():
            injection_per_chiplet_rate.setdefault(i, {})
        else:
            if i not in injection_per_chiplet_rate[i].keys():
                injection_per_chiplet_rate[i].setdefault(i, {})[0] = 0

    _x = np.arange(0, max(injection_per_chiplet_rate.keys()) + 1, 1)
    _y = np.arange(0, max(injection_per_chiplet_rate.keys()) + 1, 1)
    n_row = len(injection_per_chiplet_rate.keys())
    ann = []
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
            stack = 0
            for byte in injection_per_chiplet_rate[x][y].keys():
                if byte == 8:
                    color = 'blue'
                elif byte == 40:
                    color = 'red'
                elif byte == 72:
                    color = 'green'
                else:
                    color = 'black'
                if byte not in ann:
                    ann.append(byte)
                    fig.add_trace(go.Scatter3d(x=[None], y=[None], z=[None], opacity=0, name=f'{byte} byte', showlegend=True))
                Z = injection_per_chiplet_rate[x][y][byte]
                fig.add_trace(go.Mesh3d(
                    x=[x_min, x_min, x_max, x_max, x_min, x_min, x_max, x_max],
                    y=[y_min, y_max, y_max, y_min, y_min, y_max, y_max, y_min],
                    z=[stack, stack, stack, stack, Z + stack, Z + stack, Z + stack, Z + stack], color=color,
                    opacity=0.70, alphahull=0, ))
                stack += Z

    fig.update_layout(scene=dict(
        xaxis=dict(backgroundcolor="rgb(200, 200, 230)", gridcolor="white", showbackground=True, zerolinecolor="white",
                   tickvals=list(range(0, len(injection_per_chiplet_rate.keys()) + 1)), showline=True,
                   titlefont=dict(family='arial, sans-serif', size=18)),
        yaxis=dict(backgroundcolor="rgb(230, 200, 230)", gridcolor="white", showbackground=True, zerolinecolor="white",
                   tickvals=list(range(0, len(injection_per_chiplet_rate.keys()) + 1)), showline=True,
                   titlefont=dict(family='arial, sans-serif', size=18)),
        zaxis=dict(backgroundcolor="rgb(230, 230, 200)", gridcolor="white", showbackground=True, zerolinecolor="white",
                   showline=True, titlefont=dict(family='arial, sans-serif', size=18))))
    fig.update_layout(
        scene=dict(xaxis_title='source chiplet', yaxis_title='destination chiplet', zaxis_title='injection percentage'),
        margin=dict(l=65, r=50, b=65, t=90))
    fig.write_html(base_path + "/plots/packet_source_destination_distribution.html")


def spatial_locality(input_, packet, chiplet_num):
    base_path = os.path.dirname(input_)
    aggreagate_injection = {}
    injection_per_chiplet = {}
    packet_dist_per_chiplet = {}
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "request injected":
                source = int(packet[id][j][1].split(": ")[1])
                dest = int(packet[id][j][2].split(": ")[1])
                cycle = int(packet[id][j][5].split(": ")[1])
                byte = int(packet[id][j][7].split(": ")[1])
                if cycle not in aggreagate_injection.keys():
                    aggreagate_injection[cycle] = byte
                else:
                    aggreagate_injection[cycle] += byte
                if source not in injection_per_chiplet.keys():
                    injection_per_chiplet.setdefault(source, {}).setdefault(source, {})[cycle] = 0
                    injection_per_chiplet.setdefault(dest, {}).setdefault(dest, {})[cycle] = 0
                    injection_per_chiplet.setdefault(source, {}).setdefault(dest, {})[cycle] = byte
                else:
                    if dest not in injection_per_chiplet[source].keys():
                        injection_per_chiplet[source].setdefault(dest, {})[cycle] = byte
                    else:
                        if cycle not in injection_per_chiplet[source][dest].keys():
                            injection_per_chiplet[source][dest][cycle] = byte
                        else:
                            injection_per_chiplet[source][dest][cycle] += byte

                if source not in packet_dist_per_chiplet.keys():
                    packet_dist_per_chiplet.setdefault(source, {}).setdefault(dest, {})[byte] = 1
                else:
                    if dest not in packet_dist_per_chiplet[source].keys():
                        packet_dist_per_chiplet[source].setdefault(dest, {})[byte] = 1
                    else:
                        if byte not in packet_dist_per_chiplet[source][dest].keys():
                            packet_dist_per_chiplet[source][dest][byte] = 1
                        else:
                            packet_dist_per_chiplet[source][dest][byte] += 1
    for i in range(chiplet_num):
        if i not in packet_dist_per_chiplet.keys():
            packet_dist_per_chiplet.setdefault(i, {})

    injection_per_chiplet = dict(sorted(injection_per_chiplet.items(), key=lambda x: x[0]))
    for ch in injection_per_chiplet.keys():
        injection_per_chiplet[ch] = dict(sorted(injection_per_chiplet[ch].items(), key=lambda x: x[0]))

    Summation = sum(aggreagate_injection.values())
    injection_per_chiplet_rate = {}
    for src in injection_per_chiplet.keys():
        if src not in injection_per_chiplet_rate.keys():
            injection_per_chiplet_rate.setdefault(src, {})
        for dest in injection_per_chiplet[src].keys():
            injection_per_chiplet_rate[src][dest] = sum(injection_per_chiplet[src][dest].values())/Summation

    spatial_distribution = {}
    for src in injection_per_chiplet.keys():
        if src not in spatial_distribution.keys():
            spatial_distribution.setdefault(src, {})
            temp = 0
        for dest in injection_per_chiplet[src].keys():
            temp += sum(injection_per_chiplet[src][dest].values())/Summation
        spatial_distribution[src] = temp
    spatial_distribution = dict(sorted(spatial_distribution.items(), key=lambda x: x[0]))
    interp_func = interp1d(list(spatial_distribution.keys()), list(spatial_distribution.values()))
    newArr = interp_func(np.arange(min(spatial_distribution.keys()), max(spatial_distribution.keys())+1, 1))

    for src in injection_per_chiplet_rate.keys():
        for src2 in injection_per_chiplet_rate.keys():
            if src2 not in injection_per_chiplet_rate[src].keys():
                injection_per_chiplet_rate[src][src2] = 0
    injection_per_chiplet_rate = dict(sorted(injection_per_chiplet_rate.items(), key=lambda x: x[0]))
    for src in injection_per_chiplet_rate.keys():
        injection_per_chiplet_rate[src] = dict(sorted(injection_per_chiplet_rate[src].items(), key=lambda x: x[0]))

    #surface_distribution_plot(base_path, injection_per_chiplet_rate)
    bar_distribution_plot(base_path, packet_dist_per_chiplet, chiplet_num)

    """fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    surf = ax.plot_surface(X, Y, np.array(Z), cmap='viridis', edgecolor='orange', lw=1, alpha=0.9)
    ax.set_xlabel('source chiplet')
    ax.set_ylabel('destination chiplet')
    ax.set_zlabel('injection rate (%)')
    ax.set_title("Spatial injection distribution (per source-destination)")
    plt.xticks(np.arange(0, max(injection_per_chiplet_rate.keys())+1, 1))
    plt.yticks(np.arange(0, max(injection_per_chiplet_rate.keys())+1, 1))
    ax.xaxis._axinfo["grid"].update({"linewidth": 1, 'color': 'red'})
    ax.yaxis._axinfo["grid"].update({"linewidth": 1, 'color': 'red'})
    plt.savefig("3D-spatialLocality.jpg")
    plt.close()"""
    """fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(list(spatial_distribution.keys()), list(spatial_distribution.values()), marker="*", label='actual')
    ax.plot(list(spatial_distribution.keys()), newArr, 'r', label='curve fitting')
    ax.set_xlabel("source chiplet")
    ax.set_ylabel("injection rate (%)")
    ax.set_title("Spatial injection distribution (per source)")
    plt.xticks(np.arange(0, max(injection_per_chiplet_rate.keys()) + 1, 1))
    plt.legend(loc='best', fancybox=True, shadow=True)
    fig.tight_layout(pad=5.0)
    plt.savefig(base_path + "/plots/spatial_injection_distribution.jpg")
    plt.close()"""
