import os.path
import gc
import plotly.express as px
import matplotlib.pyplot as plt


def overall_plot(base_path, trace, kernel_num):
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

            elif trace[id][i][0] == "reply received":
                chiplet = int(trace[id][i][6].split(": ")[1])
                byte = int(trace[id][i][7].split(": ")[1])
                cycle = int(trace[id][i][5].split(": ")[1])
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

    if os.path.exists(base_path + "/plots/"):
        pass
    else:
        os.mkdir(base_path + "/plots/")
    if os.path.exists(base_path + "/plots/" + str(kernel_num) + "/"):
        pass
    else:
        os.mkdir(base_path + "/plots/" + str(kernel_num) + "/")

    for i in range(chiplet_num):
        fig = px.line(x=list(traffic_[i].keys()), y=list(traffic_[i].values()))
        fig.write_html(base_path + "/plots/" + str(kernel_num) + "/request_reply_injected_chiplet_" + str(i) + ".html")
    fig = px.line(x=list(overall_.keys()), y=list(overall_.values()))
    fig.write_html(base_path + "/plots/" + str(kernel_num) + "/overall_traffic.html")
    fig = px.line(x=list(positive_overall_.keys()), y=list(positive_overall_.values()))
    fig.write_html(base_path + "/plots/" + str(kernel_num) + "/overall_request_reply_injected_traffic.html")
    plt.figure(figsize=(20, 8))
    plt.plot(overall_.keys(), overall_.values())
    plt.savefig(base_path + "/plots/" + str(kernel_num) + "/overall_request_reply_injected_traffic.jpg")
    gc.enable()
    gc.collect()