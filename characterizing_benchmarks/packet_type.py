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


def add_line(data, df, col_count):
    xpos = 0
    scale = 1. / col_count
    ypos = -8
    for bench in data.keys():
        k_num = len(data[bench])
        #plt.Line2D([xpos, xpos], [ypos + .1, ypos], transform=ax.transAxes, color='black')
        df[list(struct.keys())].axvline(x = 85, color = 'green', linestyle='-.');
        df[list(struct.keys())].text(x=70, y=0, s= 'Productivity target', color= 'green');
        xpos += k_num
    line.set_clip_on(False)
    ax.add_line(line)


def label_group_bar(suite, data):
    names = []
    gropus = []
    final_items = []
    for bench in data.keys():
        names.append(bench)
        kernel_temp = []
        for k in data[bench].keys():
            temp = []
            for key, value in data[bench][k].items():
                temp.append(value)
            kernel_temp.append(temp)
        gropus.append(kernel_temp)

    for i in range(len(names)):
        bench_name = names[i]
        kernel_num = len(gropus[i])
        indexs = range(1, kernel_num+1)
        read_list = []
        write_list = []
        for items in gropus[i]:
            read_list.append(items[0])
            write_list.append(items[1])
        df = pd.DataFrame({"read": read_list, "write": write_list}, index=indexs)
        final_items.append(df)
    final_df = pd.concat(final_items)
    final_df.plot.bar(stacked=True, color=["blue", "red"])
    plt.title(suite + " packet_type")
    plt.tight_layout()
    plt.savefig(benchlist.bench_path + suite + "/packet_type.jpg")
    plt.close()


def read_data(path):
    packet_ratio = {}
    df = pd.read_csv(path + "bench_info.csv")
    for i in df.index:
        kernel_num = int(df['kernel_num'][i])
        r = int(df["R/W"][i].split("/")[0])
        w = int(df["R/W"][i].split("/")[1])
        if r > w:
            w += 1
        elif w > r:
            r += 1
        if r == 100:
            w = 0
        elif w == 100:
            r = 0
        assert(r+w == 100)
        if kernel_num not in packet_ratio.keys():
            packet_ratio.setdefault(kernel_num, {})
        packet_ratio[kernel_num]['read'] = r
        packet_ratio[kernel_num]['write'] = w
    return packet_ratio


if __name__ == "__main__":
    ch = "4chiplet"
    nv = "NVLink4"
    topo = "torus"
    for suite in benchlist.suits:
        data = {}
        if suite == "SDK":
            for bench in benchlist.benchmarks[suite]:
                if os.path.exists(benchlist.bench_path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/bench_info.csv"):
                    path = benchlist.bench_path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/"
                    packet_ratio = read_data(path)
                    data[bench] = packet_ratio
            label_group_bar(suite, data)
