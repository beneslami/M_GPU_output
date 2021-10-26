import csv

import matplotlib.pyplot as plt
import seaborn as sns

throughput = {0: {}, 1: {}, 2: {}, 3: {}}
throughput_update = {0: {}, 1: {}, 2: {}, 3: {}}
sorted_throughput_update = {0: {}, 1: {}, 2: {}, 3: {}}
if __name__ == "__main__":
    for src in range(0, 4):
        lined_list = {}
        for dest in range(0, 4):
            if src != dest:
                subpath = "benchmarks/bfs/pre/"
                path = subpath + "out/pre_" + str(src) + "_" + str(dest) + ".txt"
                file2 = open(path, "r")
                raw_content = ""
                if file2.mode == "r":
                    raw_content = file2.readlines()
                for line in raw_content:
                    item = [x for x in line.split("\t") if x not in ['', '\t']]
                    y = len(item[1].split("\n")[0][1:][:-1].split(", "))
                    for index in range(y):
                        if int(item[0]) not in lined_list.keys():
                            lined_list.setdefault(int(item[0]), []).append(int(item[1].split("\n")[0][1:][:-1].split(", ")[index]))
                        else:
                            lined_list[int(item[0])].append(int(item[1].split("\n")[0][1:][:-1].split(", ")[index]))
        throughput[src] = lined_list

    """out = {0: {}, 1: {}, 2: {}, 3: {}}
    for core in throughput.keys():
        for cycle, byte in throughput[core].items():
            out[core][cycle] = sum(byte)/32

    fig, ax = plt.subplots(4, 1, figsize=(18, 5), dpi=200)
    ax[0].bar(list(out[0].keys()), list(out[0].values()), width=3)
    ax[0].set_ylim(0, 50)
    ax[1].bar(list(out[1].keys()), list(out[1].values()), width=3)
    ax[1].set_ylim(0, 50)
    ax[2].bar(list(out[2].keys()), list(out[2].values()), width=3)
    ax[2].set_ylim(0, 50)
    ax[3].bar(list(out[3].keys()), list(out[3].values()), width=3)
    ax[3].set_ylim(0, 50)
    plt.show()

    dist = {0: [], 1: [], 2: [], 3: []}
    for core in throughput.keys():
        for cycle, byte in throughput[core].items():
            dist[core].append(sum(byte))
    sns.set(style="dark", palette="muted", color_codes=True)
    fig, ax = plt.subplots(2, 2, figsize=(15, 15), sharex=True)
    sns.distplot(list(dist[0]), kde=True, hist=True, ax=ax[0, 0])
    ax[0, 0].set_title("core 0")
    sns.distplot(list(dist[1]), kde=True, hist=True, ax=ax[0, 1])
    ax[0, 1].set_title("core 1")
    sns.distplot(list(dist[2]), kde=True, hist=True, ax=ax[1, 0])
    ax[1, 0].set_title("core 2")
    sns.distplot(list(dist[3]), kde=True, hist=True, ax=ax[1, 1])
    ax[1, 1].set_title("core 3")
    plt.setp(ax, yticks=[])
    plt.tight_layout()
    plt.show()"""

    for core in throughput.keys():
        throughput_update[core] = dict(sorted(throughput[core].items(), key=lambda x: x[0]))
    flag = 0
    start = end = 0
    dist = {0: {}, 1: {}, 2: {}, 3: {}}
    for source in throughput_update.keys():
        for cyc in throughput_update[source].keys():
            if flag == 0:
                start = cyc
                flag = 1
            elif flag == 1:
                if cyc - start not in dist[source].keys():
                    dist[source][cyc - start] = 1
                else:
                    dist[source][cyc - start] += 1
                start = cyc

    fields = ['duration', 'dist']
    dist[0] = dict(sorted(dist[0].items(), key=lambda x: x[0]))
    with open("0.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[0].items():
            writer.writerow([cyc, byte])
    dist[1] = dict(sorted(dist[1].items(), key=lambda x: x[0]))
    with open("1.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[1].items():
            writer.writerow([cyc, byte])
    dist[2] = dict(sorted(dist[2].items(), key=lambda x: x[0]))
    with open("2.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[2].items():
            writer.writerow([cyc, byte])
    dist[3] = dict(sorted(dist[3].items(), key=lambda x: x[0]))
    with open("3.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for cyc, byte in dist[3].items():
            writer.writerow([cyc, byte])

    """fig, ax = plt.subplots(2, 2, figsize=(15, 15))
    ax[0, 0].bar(list(dist[0].keys()), list(dist[0].values()), width=4)
    ax[0, 1].bar(list(dist[1].keys()), list(dist[1].values()), width=4)
    ax[1, 0].bar(list(dist[2].keys()), list(dist[2].values()), width=4)
    ax[1, 1].bar(list(dist[3].keys()), list(dist[3].values()), width=4)
    plt.show()"""
    """sns.set(style="dark", palette="muted", color_codes=True)
    fig, ax = plt.subplots(2, 2, figsize=(15, 15), sharex=True)
    sns.distplot(list(dist[0]), kde=True, hist=True, ax=ax[0, 0])
    ax[0, 0].set_title("core 0")
    ax[0, 0].set_xlim(-20, 300)
    sns.distplot(list(dist[1]), kde=True, hist=True, ax=ax[0, 1])
    ax[0, 1].set_title("core 1")
    ax[0, 1].set_xlim(-20, 300)
    sns.distplot(list(dist[2]), kde=True, hist=True, ax=ax[1, 0])
    ax[1, 0].set_title("core 2")
    ax[1, 0].set_xlim(-20, 300)
    sns.distplot(list(dist[3]), kde=True, hist=True, ax=ax[1, 1])
    ax[1, 1].set_title("core 3")
    ax[1, 1].set_xlim(-20, 300)
    plt.setp(ax, yticks=[])
    plt.tight_layout()
    plt.show()"""