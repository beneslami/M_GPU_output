import matplotlib.pyplot as plt


def buffer_stats(packets):
    router = {}
    for id in packets.keys():
        for j in range(len(packets[id])):
            if packets[id][j][0] == "inj rtr":
                rtr = int(packets[id][j][6].split(": ")[1])
                cycle = int(packets[id][j][5].split(": ")[1])
                port = int(packets[id][j][8].split(": ")[1])
                occ = int(packets[id][j][9].split(": ")[1])
                if rtr not in router.keys():
                    router.setdefault(rtr, {}).setdefault(port, {}).setdefault("in", {})[cycle] = occ
                else:
                    if port not in router[rtr].keys():
                        router[rtr].setdefault(port, {}).setdefault("in", {})[cycle] = occ
                    else:
                        if "in" not in router[rtr][port].keys():
                            router[rtr][port].setdefault("in", {})[cycle] = occ
                        else:
                            if cycle not in router[rtr][port]["in"].keys():
                                router[rtr][port]["in"][cycle] = occ
                            else:
                                if occ > router[rtr][port]["in"][cycle]:
                                    router[rtr][port]["in"][cycle] = occ
            elif packets[id][j][0] == "ejc rtr":
                rtr = int(packets[id][j][6].split(": ")[1])
                cycle = int(packets[id][j][5].split(": ")[1])
                port = int(packets[id][j][8].split(": ")[1])
                occ = int(packets[id][j][9].split(": ")[1])
                if rtr not in router.keys():
                    router.setdefault(rtr, {}).setdefault(port, {}).setdefault("in", {})[cycle] = occ
                else:
                    if port not in router[rtr].keys():
                        router[rtr].setdefault(port, {}).setdefault("out", {})[cycle] = occ
                    else:
                        if "out" not in router[rtr][port].keys():
                            router[rtr][port].setdefault("out", {})[cycle] = occ
                        else:
                            if cycle not in router[rtr][port]["out"].keys():
                                router[rtr][port]["out"][cycle] = occ
                            else:
                                if occ > router[rtr][port]["out"][cycle]:
                                    router[rtr][port]["out"][cycle] = occ
    router = dict(sorted(router.items(), key=lambda x: x[0]))
    for rtr in router.keys():
        router[rtr] = dict(sorted(router[rtr].items(), key=lambda x: x[0]))
        for port in router[rtr].keys():
            router[rtr][port] = dict(sorted(router[rtr][port].items(), key=lambda x: x[0]))

    for rtr in router.keys():
        plot_num = len(router[rtr].keys())
        fig = plt.figure(figsize=(20, 10))
        ax = fig.subplots(plot_num*2, 1)
        plt.subplots_adjust(wspace=0.868, hspace=0.798, top=0.962, right=0.958, bottom=0.03, left=0.04)
        fig.tight_layout()
        counter = 0
        for port in router[rtr].keys():
            ax[counter].set_title("input port " + str(port))
            ax[counter].step(list(router[rtr][port]["in"].keys()), list(router[rtr][port]["in"].values()), color='black', marker='o', markersize=2, linestyle='--', linewidth=0.01)
            counter += 1
            ax[counter].set_title("output port " + str(port))
            ax[counter].step(list(router[rtr][port]["out"].keys()), list(router[rtr][port]["out"].values()), color='black', marker='o', markersize=2, linestyle='--', linewidth=0.01)
            counter += 1
        plt.xlabel("cycle")
        plt.ylabel("buffer occupancy")
        plt.savefig("router" + str(rtr) + ".jpg")
        plt.close()
