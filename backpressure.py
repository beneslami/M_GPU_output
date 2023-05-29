import os
from matplotlib import pyplot as plt


def measure_backpressure(input_):
    base_path = os.path.dirname(input_)
    file = open(base_path + "/icnt_stats_0.txt", "r")
    raw_content = ""
    if file.mode == "r":
        raw_content = file.readlines()
    file.close()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    input_node = {}
    input_router = {}
    link = {}
    cycle = 0
    node = -1
    for i in range(len(lined_list)):
        if lined_list[i][0].__contains__("cycle:"):
            cycle = int(lined_list[i][0].split(": ")[1])
        elif lined_list[i][0].__contains__("s: "):
            node = int(lined_list[i][1].split(": ")[1])
            buff = int(lined_list[i][2].split(": ")[1])
            if node not in input_node.keys():
                input_node.setdefault(node, {})[cycle] = buff
            else:
                input_node[node][cycle] = buff
        elif lined_list[i][0].__contains__("r: "):
            router = int(lined_list[i][0].split(": ")[1])
            router_link = int(lined_list[i][1].split(" ")[1])
            occupancy = int(lined_list[i][2].split(": ")[1])
            if router not in input_router.keys():
                input_router.setdefault(router, {}).setdefault(router_link, {})[cycle] = occupancy
            else:
                if router_link not in input_router[router].keys():
                    input_router[router].setdefault(router_link, {})[cycle] = occupancy
                else:
                    input_router[router][router_link][cycle] = occupancy
        elif lined_list[i][0].__contains__("subnet: "):
            src = int(lined_list[i][1].split(": ")[1])
            dest = int(lined_list[i][3].split(": ")[1])
            size = int(lined_list[i][5].split(": ")[1])
            if src not in link.keys():
                link.setdefault(src, {}).setdefault(dest, {})[cycle] = size
            else:
                if dest not in link[src].keys():
                    link[src].setdefault(dest, {})[cycle] = size
                else:
                    if cycle not in link[src][dest].keys():
                        link[src][dest][cycle] = size
                    else:
                        link[src][dest][cycle] += size

    fig = plt.figure(figsize=(20, 6))
    plt.subplot(3, 1, 1)
    plt.plot(list(input_node[1].keys()), list(input_node[1].values()))
    plt.subplot(3, 1, 2)
    plt.plot(list(input_router[1][1].keys()), list(input_router[1][1].values()))
    plt.subplot(3, 1, 3)
    plt.plot(list(link[1][0].keys()), list(link[1][0].values()))
    plt.show()