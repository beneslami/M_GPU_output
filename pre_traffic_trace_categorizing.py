import sys

from matplotlib import pyplot as plt

if __name__ == '__main__':
    input_ = sys.argv[1]
    file2 = open(input_, "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]

        lined_list.append(item)
    trace = {}
    Trace = {}
    del(raw_content)

    for i in range(len(lined_list)):
        if int(lined_list[i][1].split(": ")[1]) in trace.keys():
            if lined_list[i] not in trace[int(lined_list[i][1].split(": ")[1])]:
                trace.setdefault(int(lined_list[i][1].split(": ")[1]), []).append(lined_list[i])
        else:
            trace.setdefault(int(lined_list[i][1].split(": ")[1]), []).append(lined_list[i])

    traffic = {}
    overall = {}
    for chiplet in trace.keys():
        for i in range(len(trace[chiplet])):
            if trace[chiplet][i][0] == "request injected":
                byte = int(trace[chiplet][i][7].split(": ")[1])
                cycle = int(trace[chiplet][i][5].split(": ")[1])
                if chiplet not in traffic.keys():
                    traffic.setdefault(chiplet, {})[cycle] = byte
                else:
                    if cycle not in traffic[chiplet].keys():
                        traffic[chiplet][cycle] = byte
                    else:
                        traffic[chiplet][cycle] += byte
                if cycle not in overall.keys():
                    overall[cycle] = byte
                else:
                    overall[cycle] += byte

            if trace[chiplet][i][0] == "request received":
                byte = int(trace[chiplet][i][7].split(": ")[1])
                cycle = int(trace[chiplet][i][5].split(": ")[1])
                if cycle not in overall.keys():
                    overall[cycle] = -byte
                else:
                    overall[cycle] -= byte

            if trace[chiplet][i][0] == "reply injected":
                byte = int(trace[chiplet][i][7].split(": ")[1])
                cycle = int(trace[chiplet][i][5].split(": ")[1])
                if cycle not in overall.keys():
                    overall[cycle] = byte
                else:
                    overall[cycle] += byte

            if trace[chiplet][i][0] == "reply received":
                byte = int(trace[chiplet][i][7].split(": ")[1])
                cycle = int(trace[chiplet][i][5].split(": ")[1])
                if cycle not in overall.keys():
                    overall[cycle] = -byte
                else:
                    overall[cycle] -= byte

    chiplet_num = len(traffic)
    traffic_ = {}
    for i in range(chiplet_num):
        m = min(traffic[i].keys())
        M = max(traffic[i].keys())
        for j in range(m, M, 1):
            if j not in traffic[i].keys():
                if i not in traffic_.keys():
                    traffic_.setdefault(i, {})[j] = 0
                else:
                    traffic_[i][j] = 0
            else:
                if i not in traffic_.keys():
                    traffic_.setdefault(i, {})[j] = traffic[i][j]
                else:
                    traffic_[i][j] = traffic[i][j]

    overall_ = {}
    m = min(overall.keys())
    M = max(overall.keys())
    for i in range(m, M, 1):
        if i not in overall.keys():
            overall_[i] = 0
        else:
            overall_[i] = overall[i]

    fig = plt.figure(figsize=(20, 20))
    plt.subplots_adjust(wspace=0.868, hspace=0.798, top=0.962, right=0.958, bottom=0.03, left=0.04)
    fig.tight_layout()
    ax = fig.subplots(chiplet_num+1, 1)
    for i in range(chiplet_num):
        ax[i].plot(list(traffic_[i].keys()), list(traffic_[i].values()))
        #ax[i].set_title("chiplet" + str(i))
        ax[i].set_ylim(0, 20)
    ax[chiplet_num].plot(list(overall_.keys()), list(overall_.values()))
    #ax[chiplet_num].set_title("overall aggregate traffic")
    plt.savefig("traffic.jpg")
    plt.show()