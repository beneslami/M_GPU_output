import os
import sys
import csv
import matplotlib.pyplot as plt
import pandas as pd
sys.path.append("..")
import benchlist


def mk_groups(data):
    try:
        newdata = data.items()
    except:
        return
    thisgroup = []
    groups = []
    for key, value in newdata:
        newgroups = mk_groups(value)
        if newgroups is None:
            thisgroup.append((key, value))
        else:
            thisgroup.append((key, len(newgroups[-1])))
            if groups:
                groups = [g + n for n, g in zip(newgroups, groups)]
            else:
                groups = newgroups
    return [thisgroup] + groups


def add_line(ax, xpos, ypos):
    line = plt.Line2D([xpos, xpos], [ypos + .1, ypos], transform=ax.transAxes, color='black')
    line.set_clip_on(False)
    ax.add_line(line)


def label_group_bar(ax, data):
    xticklabel = []
    names = []
    for bench in data.keys():
        names.append(bench)
        for index, values in data[bench].items():
            xticklabel.append(index)
    groups = mk_groups(data)
    xy = groups.pop()
    x, y = zip(*xy)
    ly = int(len(y) / 2)

    xticks = range(1, ly + 1)
    r = []
    w = []
    for i in range(len(y)):
        if i % 2 == 0:
            r.append(y[i])
        else:
            w.append(y[i])

    ax.bar(xticks, r, align='center', color="blue")
    ax.bar(xticks, w, bottom=r, align='center', color="red")
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabel)
    ax.set_xlim(.5, ly + .5)
    ax.yaxis.grid(True)

    scale = 1. / ly
    ypos = -0.1
    pos = 0
    line_points = []
    for i in xticklabel:
        if i == 1:
            add_line(ax, pos * scale, ypos)
            line_points.append(pos)
        pos += 1
    line_points.append(pos)
    ypos = -8
    for i in range(len(line_points) - 1):
        first = line_points[i]
        second = line_points[i + 1]
        ax.text(((first + second) / 2) + 0.5, ypos, names[i], ha='center')


def read_data(path):
    packet_ratio = {}
    df = pd.read_csv(path + "bench_info.csv")
    for i in df.index:
        kernel_num = int(df['kernel_num'][i])
        r = int(df["R/W"][i].split("/")[0])
        w = int(df["R/W"][i].split("/")[1]) + 1
        if kernel_num not in packet_ratio.keys():
            packet_ratio.setdefault(kernel_num, {})
        packet_ratio[kernel_num]['r'] = r
        packet_ratio[kernel_num]['w'] = w
    return packet_ratio


if __name__ == "__main__":
    ch = "4chiplet"
    nv = "NVLink4"
    topo = "torus"
    for suite in benchlist.suits:
        data = {}
        if suite == "parboil":
            for bench in benchlist.benchmarks[suite]:
                if os.path.exists(benchlist.bench_path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/bench_info.csv"):
                    path = benchlist.bench_path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/"
                    packet_ratio = read_data(path)
                    data[bench] = packet_ratio
            fig = plt.figure(figsize=(20, 8))
            ax = fig.add_subplot(1, 1, 1)
            label_group_bar(ax, data)
            plt.title("read/write ratio - " + suite + " benchmark suite")
            plt.tight_layout()
            plt.savefig(benchlist.bench_path + suite + "/packet_type.jpg")