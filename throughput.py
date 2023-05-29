import pandas as pd
import numpy as np
import os
import seaborn as sns
from matplotlib import pyplot as plt


def measure_throughput(path_, topology, chiplet_num, nvlink):
    abs_path = os.path.dirname(path_)
    tr = {}
    traffic = {}
    link_width = 0
    path = abs_path + "/link_usage/"
    if topology == "ring":
        if nvlink == 4:
            link_width = 200
        elif nvlink == 3:
            link_width = 160
        elif nvlink == 2:
            link_width = 80
        elif nvlink == 1:
            link_width = 40
    elif topology == "2Dtorus":
        if nvlink == 4:
            link_width = 120
        elif nvlink == 3:
            link_width = 80
        elif nvlink == 2:
            link_width = 40
        elif nvlink == 1:
            link_width = 40
    elif topology == "2Dmesh":
        if nvlink == 4:
            link_width = 120
        elif nvlink == 3:
            link_width = 80
        elif nvlink == 2:
            link_width = 40
        elif nvlink == 1:
            link_width = 40
    if topology == "ring" or topology == "2Dtorus" or topology == "2Dmesh":
        for i in range(chiplet_num):
            for j in range(chiplet_num):
                path += "link_usage_" + str(i) + str(j) + ".csv"
                try:
                    if os.path.getsize(path) == 0:
                        os.system("rm " + path)
                        path = abs_path + "/link_usage/"
                        continue
                except FileNotFoundError:
                    path = abs_path + "/link_usage/"
                    continue
                content = ""
                df = pd.read_csv(path)
                x = df['cycle']
                y = df['byte']
                residual = 0
                for c, b in zip(x, y):
                    cycle = c
                    byte = b + residual
                    if byte > link_width:
                        tr.setdefault(i, {}).setdefault(j, {})[cycle] = link_width
                        residual = byte - link_width
                    else:
                        tr.setdefault(i, {}).setdefault(j, {})[cycle] = byte
                        residual = 0
                path = abs_path + "/link_usage/"

    average_traffic = {}
    total_avg_traffic = {}
    for x in tr.keys():
        if x not in traffic.keys():
            traffic.setdefault(x, {})
        if x not in total_avg_traffic.keys():
            total_avg_traffic.setdefault(x, {})
        for y in tr[x].keys():
            if y not in traffic[x].keys():
                traffic[x].setdefault(y, {})
            if y not in total_avg_traffic[x].keys():
                total_avg_traffic[x].setdefault(y, {})
            m = min(tr[x][y].keys())
            M = max(tr[x][y].keys())
            for c in range(m, M, 1):
                if c not in tr[x][y].keys():
                    traffic[x][y][c] = 0
                else:
                    traffic[x][y][c] = tr[x][y][c]

            total_avg_traffic[x][y] = np.mean(list(traffic[x][y].values()))
            window = 0
            for c in range(m, M, 50):
                avg = 0
                length = 0
                for i in range(0, 50):
                    try:
                        avg += traffic[x][y][c+i]
                        length += 1
                    except KeyError:
                        break
                avg = avg/length
                if x not in average_traffic.keys():
                    average_traffic.setdefault(x, {}).setdefault(y, {})[window] = (avg/link_width)
                else:
                    if y not in average_traffic[x].keys():
                        average_traffic[x].setdefault(y, {})[window] = (avg/link_width)
                    else:
                        average_traffic[x][y][window] = (avg/link_width)
                window += 1

    fig = plt.figure(figsize=(20, 6))
    plt.plot(average_traffic[0][1].keys(), average_traffic[0][1].values())
    plt.show()
    if os.path.exists(abs_path + "/plots/link_usage"):
        pass
    else:
        os.system("mkdir " + abs_path + "/plots/link_usage")
        for src in average_traffic.keys():
            for dest in average_traffic[src].keys():
                plt.figure(figsize=(20, 5))
                line = []
                for i in range(len(list(average_traffic[src][dest].keys()))):
                    line.append(total_avg_traffic[src][dest]/link_width)
                plt.plot(list(average_traffic[src][dest].keys()), list(average_traffic[src][dest].values()), label="normalized link usage", color="black")
                plt.plot(list(average_traffic[src][dest].keys()), line, label="average", color="red")
                plt.xlabel("intervals of 50 cycles")
                plt.ylabel("link utilization (percentage)")
                plt.title("bus width: " + str(link_width) + "B for NVLink " + str(nvlink) + "in " + topology + " topology")
                #plt.xlim(92600, 92800)
                plt.legend()
                plt.savefig(abs_path + "/plots/link_usage/src" + str(src) + "dest" + str(dest) + ".jpg")
                plt.close()

    m = list(average_traffic)[0]
    M = list(average_traffic[m])[0]
    maximum = list(average_traffic[m][M].keys())
    for x in average_traffic.keys():
        for y in average_traffic[x].keys():
            if len(average_traffic[x][y].keys()) > len(maximum):
                maximum = list(average_traffic[x][y].keys())
    traffic_array = []
    ylabel = []
    for x in average_traffic.keys():
        for y in average_traffic[x].keys():
            label = str(x) + str(y)
            ylabel.append(label)
            temp = []
            for c in maximum:
                if c in average_traffic[x][y].keys():
                    temp.append(average_traffic[x][y][c])
                else:
                    temp.append(0)
            traffic_array.append(temp)
    df = pd.DataFrame(traffic_array)
    ax = sns.heatmap(df, cmap="Blues", yticklabels=ylabel, vmin=0, vmax=1)
    for i in range(df.shape[1] + 1):
        ax.axhline(i, color='white', lw=0.8)
    plt.xlabel("intervals of 50 cycles")
    plt.ylabel("source-destination link")
    plt.title("link utilization")
    plt.savefig(abs_path + "/plots/overall_link_utilization.jpg")
    plt.close()