import gc
import sys
import os

import matplotlib.pyplot as plt
import pandas as pd


def generate_aggregate_byte_distribution(input_, packet):
    base_path = os.path.dirname(input_)
    aggregate_injection = {}
    aggregate_req_injection = {}
    aggregate_rep_injection = {}
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "request injected":
                chiplet = int(packet[id][j][1].split(": ")[1])
                cycle = int(packet[id][j][5].split(": ")[1])
                byte = int(packet[id][j][7].split(": ")[1])
                #if chiplet == 3:
                if cycle not in aggregate_injection.keys():
                    aggregate_injection[cycle] = byte
                else:
                    aggregate_injection[cycle] += byte
                if cycle not in aggregate_req_injection.keys():
                    aggregate_req_injection[cycle] = byte
                else:
                    aggregate_req_injection[cycle] += byte
            if packet[id][j][0] == "reply injected":
                chiplet = int(packet[id][j][6].split(": ")[1])
                cycle = int(packet[id][j][5].split(": ")[1])
                byte = int(packet[id][j][7].split(": ")[1])
                #if chiplet == 12:
                if cycle not in aggregate_injection.keys():
                    aggregate_injection[cycle] = byte
                else:
                    aggregate_injection[cycle] += byte
                if cycle not in aggregate_rep_injection.keys():
                    aggregate_rep_injection[cycle] = byte
                else:
                    aggregate_rep_injection[cycle] += byte

    aggregate_injection = dict(sorted(aggregate_injection.items(), key=lambda x: x[0]))
    with open(base_path + "/data/total_injection.csv", "w") as file:
        file.write("cycle,byte\n")
        for cycle, byte in aggregate_injection.items():
            file.write(str(cycle) + "," + str(byte) + "\n")
    
    aggregate_req_injection = dict(sorted(aggregate_req_injection.items(), key=lambda x: x[0]))
    with open(base_path + "/data/total_req_injection.csv", "w") as file:
        file.write("cycle,byte\n")
        for cycle, byte in aggregate_req_injection.items():
            file.write(str(cycle) + "," + str(byte) + "\n")
    
    aggregate_rep_injection = dict(sorted(aggregate_rep_injection.items(), key=lambda x: x[0]))
    with open(base_path + "/data/total_rep_injection.csv", "w") as file:
        file.write("cycle,byte\n")
        for cycle, byte in aggregate_rep_injection.items():
            file.write(str(cycle) + "," + str(byte) + "\n")
            
    aggregate_dist = {}
    for cycle, byte in aggregate_injection.items():
        if byte not in aggregate_dist.keys():
            aggregate_dist[byte] = 1
        else:
            aggregate_dist[byte] += 1
    aggregate_dist = dict(sorted(aggregate_dist.items(), key=lambda x: x[0]))
    aggregate_pdf = {}
    for k, v in aggregate_dist.items():
        aggregate_pdf[k] = v / sum(aggregate_dist.values())
    aggregate_pdf = dict(sorted(aggregate_pdf.items(), key=lambda x: x[0]))
    
    aggregate_req_dist = {}
    for cycle, byte in aggregate_req_injection.items():
        if byte not in aggregate_req_dist.keys():
            aggregate_req_dist[byte] = 1
        else:
            aggregate_req_dist[byte] += 1
    aggregate_req_dist = dict(sorted(aggregate_req_dist.items(), key=lambda x: x[0]))
    aggregate_req_pdf = {}
    for k, v in aggregate_req_dist.items():
        aggregate_req_pdf[k] = v / sum(aggregate_req_dist.values())
    aggregate_req_pdf = dict(sorted(aggregate_req_pdf.items(), key=lambda x: x[0]))
    
    aggregate_rep_dist = {}
    for cycle, byte in aggregate_rep_injection.items():
        if byte not in aggregate_rep_dist.keys():
            aggregate_rep_dist[byte] = 1
        else:
            aggregate_rep_dist[byte] += 1
    aggregate_rep_dist = dict(sorted(aggregate_rep_dist.items(), key=lambda x: x[0]))
    aggregate_rep_pdf = {}
    for k, v in aggregate_rep_dist.items():
        aggregate_rep_pdf[k] = v / sum(aggregate_rep_dist.values())
    aggregate_rep_pdf = dict(sorted(aggregate_rep_pdf.items(), key=lambda x: x[0]))
    
    with open(base_path + "/data/aggregate_injection_distribution.csv", "w") as file:
        file.write("byte,cycle\n")
        for k, v in aggregate_pdf.items():
            file.write(str(k) + "," + str(v) + "\n")
    plt.bar(list(aggregate_pdf.keys()), list(aggregate_pdf.values()), width=5)
    plt.title("aggregate byte injection with respect to request and response packets")
    plt.xlabel("packets per cycle")
    plt.ylabel("PDF")
    plt.savefig(base_path + "/plots/aggregate_request_response.jpg")
    plt.close()
    
    with open(base_path + "/data/aggregate_request_injection_distribution.csv", "w") as file:
        file.write("byte,cycle\n")
        for k, v in aggregate_req_pdf.items():
            file.write(str(k) + "," + str(v) + "\n")
    plt.bar(list(aggregate_req_pdf.keys()), list(aggregate_req_pdf.values()), width=5)
    plt.title("aggregate byte injection with respect to request packets")
    plt.xlabel("packets per cycle")
    plt.ylabel("PDF")
    plt.savefig(base_path + "/plots/aggregate_request.jpg")
    plt.close()
    
    with open(base_path + "/data/aggregate_response_injection_distribution.csv", "w") as file:
        file.write("byte,cycle\n")
        for k, v in aggregate_rep_pdf.items():
            file.write(str(k) + "," + str(v) + "\n")
    plt.bar(list(aggregate_rep_pdf.keys()), list(aggregate_rep_pdf.values()), width=5)
    plt.title("aggregate byte injection with respect to response packets")
    plt.xlabel("packets per cycle")
    plt.ylabel("PDF")
    plt.savefig(base_path + "/plots/aggregate_response.jpg")
    plt.close()
    gc.enable()
    gc.collect()