import os.path

from matplotlib import pyplot as plt
from RescaledRangeAnalysis import *

def overall_plot(input_, trace):
    base_path = os.path.dirname(input_)
    traffic = {}
    overall = {}
    positive_overall = {}
    for id in trace.keys():
        for i in range(len(trace[id])):
            if trace[id][i][0] == "request injected":
                chiplet = int(trace[id][i][1].split(": ")[1])
                byte = int(trace[id][i][7].split(": ")[1])
                cycle = int(trace[id][i][5].split(": ")[1])
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
                if cycle not in positive_overall.keys():
                    positive_overall[cycle] = byte
                else:
                    positive_overall[cycle] += byte

            elif trace[id][i][0] == "request received":
                chiplet = int(trace[id][i][2].split(": ")[1])
                byte = int(trace[id][i][7].split(": ")[1])
                cycle = int(trace[id][i][5].split(": ")[1])
                """if chiplet not in traffic.keys():
                    traffic.setdefault(chiplet, {})[cycle] = -byte
                else:
                    if cycle not in traffic[chiplet].keys():
                        traffic[chiplet][cycle] = -byte
                    else:
                        traffic[chiplet][cycle] -= byte"""
                if cycle not in overall.keys():
                    overall[cycle] = -byte
                else:
                    overall[cycle] -= byte

            elif trace[id][i][0] == "reply injected":
                chiplet = int(trace[id][i][6].split(": ")[1])
                byte = int(trace[id][i][7].split(": ")[1])
                cycle = int(trace[id][i][5].split(": ")[1])
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
                """if cycle not in positive_overall.keys():
                    positive_overall[cycle] = byte
                else:
                    positive_overall[cycle] += byte"""

            elif trace[id][i][0] == "reply received":
                chiplet = int(trace[id][i][6].split(": ")[1])
                byte = int(trace[id][i][7].split(": ")[1])
                cycle = int(trace[id][i][5].split(": ")[1])
                """if chiplet not in traffic.keys():
                    traffic.setdefault(chiplet, {})[cycle] = -byte
                else:
                    if cycle not in traffic[chiplet].keys():
                        traffic[chiplet][cycle] = -byte
                    else:
                        traffic[chiplet][cycle] -= byte"""
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
            
    positive_overall_ = {}
    m = min(positive_overall.keys())
    M = max(positive_overall.keys())
    for i in range(m, M, 1):
        if i not in positive_overall.keys():
            positive_overall_[i] = 0
        else:
            positive_overall_[i] = positive_overall[i]
    #hurst_compute(overall_, "overall traffic") # from Rescaled Range analysis
    hurst_compute(base_path, positive_overall_, "injected traffic") # from Rescaled Range analysis
    """fig = plt.figure(figsize=(20, 20))
    plt.subplots_adjust(wspace=0.868, hspace=0.798, top=0.962, right=0.958, bottom=0.03, left=0.04)
    fig.tight_layout()
    ax = fig.subplots(chiplet_num+1, 1)
    for i in range(chiplet_num):
        ax[i].plot(list(traffic_[i].keys()), list(traffic_[i].values()))
        #ax[i].set_title("chiplet" + str(i))
        #ax[i].set_ylim(0, 20)
        #ax[i].set_xlim(45000, 47000)
    ax[chiplet_num].plot(list(overall_.keys()), list(overall_.values()))
    #ax[chiplet_num].set_xlim(45000, 47000)
    #ax[chiplet_num].set_title("overall aggregate traffic")
    #plt.savefig(base_path + "/plots/traffic.jpg")
    #plt.close()
    #plt.show()"""
