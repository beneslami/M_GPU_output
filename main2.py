from statistics import mean

import matplotlib.pyplot as plt
import numpy as np

items = ["inter_icnt_pop_llc_push", "forward_waiting_push", "inter_icnt_pop_sm_push", "L2-to-ICNT",
         "forward_waiting_pop"]

chiplet0 = {}
chiplet1 = {}
chiplet2 = {}
chiplet3 = {}


def component_plot(lined_list):
    for i in range(len(lined_list)):
        if int(lined_list[i][3].split(": ")[1]) == 0:
            if lined_list[i][0] in chiplet0.keys():
                chiplet0[lined_list[i][0]] += 1
            else:
                chiplet0[lined_list[i][0]] = 1
        elif int(lined_list[i][3].split(": ")[1]) == 1:
            if lined_list[i][0] in chiplet1.keys():
                chiplet1[lined_list[i][0]] += 1
            else:
                chiplet1[lined_list[i][0]] = 1

        elif int(lined_list[i][3].split(": ")[1]) == 2:
            if lined_list[i][0] in chiplet2.keys():
                chiplet2[lined_list[i][0]] += 1
            else:
                chiplet2[lined_list[i][0]] = 1

        elif int(lined_list[i][3].split(": ")[1]) == 3:
            if lined_list[i][0] in chiplet3.keys():
                chiplet3[lined_list[i][0]] += 1
            else:
                chiplet3[lined_list[i][0]] = 1
    """""
    {'inter_icnt_pop_llc_push': 24016, 'L2-to-ICNT': 23950}
    {'forward_waiting_push': 7849, 'forward_waiting_pop': 7845, 'inter_icnt_pop_sm_push': 8065}
    {'inter_icnt_pop_sm_push': 7802}
    {'inter_icnt_pop_sm_push': 8081, 'forward_waiting_push': 7804, 'forward_waiting_pop': 7802}
    """""
    data0 = [24016, 0, 0, 23950, 0]
    data1 = [0, 7849, 8065, 0, 7804]
    data2 = [0, 0, 7802, 0, 0]
    data3 = [0, 7804, 8081, 0, 7802]
    barWidth = 0.25
    plt.bar(items, data0, color='r', width=barWidth, label="chiplet 0", edgecolor='white')
    plt.bar(items, data1, color='g', width=barWidth, label="chiplet 1", bottom=data0, edgecolor='white')
    plt.bar(items, data2, color='b', width=barWidth, label="chiplet 2", bottom=[i+j for i, j in zip(data0, data1)], edgecolor='white')
    plt.bar(items, data3, color="y", width=barWidth, label="chiplet 3", bottom=[i+j+k for i, j, k in zip(data0, data1, data2)], edgecolor='white')
    plt.ylabel("Number of Access per Cycle")
    plt.xticks(rotation=90)
    plt.legend(loc='best')
    plt.show()


def llc_boundary(lined_list):
    input = output = 0
    input_list = []
    output_list = []
    pop_time = {}
    push_time = {}
    waiting_time = {}
    for i in range(len(lined_list)):
        if lined_list[i][0] == "forward_waiting_pop":
            if int(lined_list[i][3].split(": ")[1]) == 1:
                pop_time[int(lined_list[i][1].split(": ")[1])] = int(lined_list[i][2].split(": ")[1])
        if lined_list[i][0] == "inter_icnt_pop_llc_push":
            if int(lined_list[i][3].split(": ")[1]) == 0:
                push_time[int(lined_list[i][1].split(": ")[1])] = int(lined_list[i][2].split(": ")[1])

    for i in push_time.keys():
        if i in pop_time.keys():
            waiting_time[i] = push_time[i] - pop_time[i]

    xpoints = np.array(list(waiting_time.keys()))
    ypoints = np.array(list(waiting_time.values()))
    flag = 0
    for k, v in waiting_time.items():
        if v == 35:   #186944
            #plt.annotate("32 cycles", (k, 35), xytext=(20, 100), arrowprops=dict(arrowstyle="->", facecolor='black'))
            plt.text(367960, 100, "latency longer than 32 cycles starts from packet 186944")
            #print(k)
            flag = 1
            continue
        if v == 144:  #214568
            #plt.annotate("144 cycles", (k, 144), xytext=(5, 150), arrowprops=dict(arrowstyle="->", facecolor='black'))
            #print(k)
            continue
        if v == 258:  #243415
            #plt.annotate("258 cycles", (k, 258), xytext=(5, 250), arrowprops=dict(arrowstyle="->", facecolor='black'))
            plt.text(299420, 250, "peak latency in packet 243415")
            #print(k)
            continue
        if v == 143:
            #plt.annotate("143 cycles", (k, 143), xytext=(60, 150), arrowprops=dict(arrowstyle="->", facecolor='black'))
            #print(k)
            continue
        if v == 33 and flag:
            #plt.annotate("32 cycles", (k, 33), xytext=(20, 100), arrowprops=dict(arrowstyle="->", facecolor='black'))
            #print(k)
            plt.text(367960, 80, "latency longer than 32 cycles finishes at packet 243604")
            break

    plt.xlabel("Packet number")
    plt.ylabel("Interconnect Latency")
    plt.title("Interconnect Latency between chiplet 1 and 0")

    plt.plot(xpoints, ypoints, "bo-")
    plt.show()
"""""
    for i in range(len(lined_list)):
        if int(lined_list[i][3].split(": ")[1]) == 0:
            if lined_list[i][0] == "inter_icnt_pop_llc_push":
                input_list.append(lined_list[i])
                input += 1
                push_time[int(lined_list[i][1].split(": ")[1])] = int(lined_list[i][2].split(": ")[1])
            elif lined_list[i][0] == "inter_icnt_pop_llc_pop":
                output_list.append(lined_list[i])
                output += 1
                pop_time[int(lined_list[i][1].split(": ")[1])] = int(lined_list[i][2].split(": ")[1])

    for i in pop_time.keys():
        if i in push_time.keys():
            waiting_time[i] = pop_time[i] - push_time[i]
    xpoints = np.array(list(waiting_time.keys()))
    ypoints = np.array(list(waiting_time.values()))
    plt.ylim(-100, 3500)
    plt.bar(xpoints, ypoints)
    plt.xlabel("packet number")
    plt.ylabel("waiting time in cycle")
    plt.title("Incoming packet waiting time in LLC boundary buffer in chiplet 0")
    plt.show()
"""""
"""
    input_rate = {}
    output_rate = {}
    for i in range(len(input_list)):
        if int(input_list[i][2].split(": ")[1]) in input_rate.keys():
            input_rate[int(input_list[i][2].split(": ")[1])] += 1
        else:
            input_rate[int(input_list[i][2].split(": ")[1])] = 1
    for i in input_rate.keys():
        input_rate[i] = input_rate[i] / len(input_list)

    for i in range(len(output_list)):
        if int(output_list[i][2].split(": ")[1]) in output_rate.keys():
            output_rate[int(output_list[i][2].split(": ")[1])] += 1
        else:
            output_rate[int(output_list[i][2].split(": ")[1])] = 1
    for i in output_rate.keys():
        output_rate[i] = output_rate[i] / len(output_list)
    mean_input = mean(input_rate.values())
    mean_output = mean(output_rate.values())
    x = [0, 10000]
    y = [mean_input, mean_input]
    y2 = [mean_output, mean_output]
    #plt.plot(x, y, label="input_rate_mean")
    #plt.plot(x, y2, label="output_rate_mean")
    plt.bar(list(input_rate.keys()), list(input_rate.values()), label="input")
    plt.bar(list(list(output_rate.keys())), list(output_rate.values()), label="output")
    plt.title("LLC boundary Queue input and output distribution")
    plt.xlabel("Cycle")
    plt.ylabel("Probability")
    plt.legend(loc="best")
    plt.show()
    """

if __name__ == '__main__':
    file = open("boundary.txt", "r")
    raw_content = ""
    if file.mode == "r":
        raw_content = file.readlines()
    lined_content = []
    lined_list = []
    for line in raw_content:
        lined_content.append(line)
    for i in lined_content:
        item = [x for x in i.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    # print(lined_list[0])                  function
    # print(lined_list[1].split(": ")[1])   packet_num
    # print(lined_list[2].split(": ")[1])   cycle
    # print(lined_list[3].split(": ")[1])   chiplet

    #component_plot(lined_list)
    llc_boundary(lined_list)