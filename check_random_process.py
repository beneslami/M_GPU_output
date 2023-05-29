import os.path
import sys
from statistics import mean, variance
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from statsmodels.tsa.stattools import adfuller


def plot_aggregate_traffic_injection_distribution(base_path, aggreagate_injection):
    aggreagate_traffic_distribution = {}
    for cycle, byte in aggreagate_injection.items():
        if byte not in aggreagate_traffic_distribution.keys():
            aggreagate_traffic_distribution[byte] = 1
        else:
            aggreagate_traffic_distribution[byte] += 1
    for byte, freq in aggreagate_traffic_distribution.items():
        aggreagate_traffic_distribution[byte] = freq / sum(aggreagate_traffic_distribution.values())
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.bar(list(aggreagate_traffic_distribution.keys()), list(aggreagate_traffic_distribution.values()), width=2,
            edgecolor='black')
    plt.title("PDF of aggregate traffic injection")
    plt.savefig(base_path + "/plots/aggregate_traffic_distribution.png")
    #plt.show()


def check_stationary_distribution(base_path, aggreagate_injection_, M):
    avg = {}
    var = {}
    total_average = {}
    total_var = {}
    delta = 0
    total_avg = mean(aggreagate_injection_.values())
    total_v = variance(aggreagate_injection_.values())
    for cycle in aggreagate_injection_.keys():
        temp = {}
        for i in range(1500):
            if cycle + i < M:
                temp[cycle + i] = aggreagate_injection_[cycle + i]
        avg[delta] = mean(temp.values())
        if len(temp) > 1:
            var[delta] = variance(temp.values())
            total_var[delta] = total_v
        total_average[delta] = total_avg
        delta = delta + 1
        cycle = cycle + 1500
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.plot(list(avg.keys()), list(avg.values()), linewidth=1, label="average per Δt")
    ax.plot(list(total_average.keys()), list(total_average.values()), linewidth=1.5, color="red", label="total average")
    ax.legend()
    plt.title("total average vs average per Δt")
    plt.savefig(base_path + "/plots/first order examination (mean).jpg")
    plt.close()
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.plot(list(var.keys()), list(var.values()), linewidth=1, label="variance per Δt")
    ax.plot(list(total_var.keys()), list(total_var.values()), linewidth=1.5, color="red", label="total variance")
    ax.legend()
    plt.title("total variance vs average per Δt")
    plt.savefig(base_path + "/plots/second order examination (variance).jpg")
    plt.close()
    #plt.show()


def check_autocorrelation(base_path, aggregate_injection_):
    start_flag = 0
    prev_cycle = 0
    aggregate_burst = 0
    burst_variability = []
    for cycle, byte in aggregate_injection_.items():
        if byte != 0:
            if start_flag == 0:
                start_flag = 1
                prev_cycle = cycle
            aggregate_burst += byte
        elif byte == 0:
            if start_flag == 1:
                burst_variability.append(aggregate_burst/(cycle - prev_cycle))
            start_flag = 0
            aggregate_burst = 0

    values = pd.DataFrame(burst_variability)
    #smt.stattools.acovf(values)
    #smt.graphics.plot_acf(values, lags=50, alpha=0.1)
    #plt.ylim(0, 1.1)
    pd.plotting.autocorrelation_plot(values)
    #plt.xlim(0, 100)
    #plt.ylim(0, 1)
    plt.title("Autocorrelation")
    plt.xlabel("Lag")
    plt.savefig(base_path + "/plots/autocorrelation.png")
    plt.close()
    #plt.show()


def dicky_fuller(aggregate_injection_):
    X = list(aggregate_injection_.values())
    result = adfuller(X)
    print('ADF Statistic: %f' % result[0])
    print('p-value: %f' % result[1])
    print('Critical Values:')
    for key, value in result[4].items():
        print('\t%s: %.3f' % (key, value))

    if result[0] < result[4]["5%"]:
        print("Reject Ho - Time Series is Stationary")
    else:
        print("Failed to Reject Ho - Time Series is Non-Stationary")


def check_source_correlation(base_path, request, chiplet_num):
    correlation = {}
    for source1 in request.keys():
        for source2 in request.keys():
            if source1 < source2:
                x = list(request[source1].values())
                y = list(request[source2].values())
                try:
                    mean_x = sum(x) / float(len(x))
                except ZeroDivisionError:
                    mean_x = 0
                try:
                    mean_y = sum(y) / float(len(y))
                except ZeroDivisionError:
                    mean_y = 0
                # Subtracting mean from the individual elements
                sub_x = [i - mean_x for i in x]
                sub_y = [i - mean_y for i in y]
                numerator = sum([sub_x[i] * sub_y[i] for i in range(min(len(sub_y), len(sub_x)))]) #covariance
                # Standard Deviation of x and y
                std_deviation_x = sum([sub_x[i] ** 2.0 for i in range(len(sub_x))])
                std_deviation_y = sum([sub_y[i] ** 2.0 for i in range(len(sub_y))])
                #denominator = len(x) - 1
                #cov = numerator / denominator
                denominator = (std_deviation_x * std_deviation_y) ** 0.5  # short but equivalent to (std_deviation_x**0.5) * (std_deviation_y**0.5)
                try:
                    cor = numerator / denominator
                except ZeroDivisionError:
                    cor = 0
                if source1 not in correlation.keys():
                    correlation.setdefault(source1, {})[source2] = abs(cor)
                else:
                    if source2 not in correlation[source1].keys():
                        correlation[source1][source2] = abs(cor)

    percentage = {}
    total_combination = 0
    for s1 in correlation.keys():
        total_combination += len(correlation[s1])
        for s2 in correlation[s1].keys():
            if correlation[s1][s2] not in percentage.keys():
                percentage[correlation[s1][s2]] = 1
            else:
                percentage[correlation[s1][s2]] += 1

    for sourecs in percentage.keys():
        percentage[sourecs] = percentage[sourecs]/total_combination
    percentage = dict(sorted(percentage.items(), key=lambda x: x[0]))

    cdf = {}
    prev_rate = 0
    for src in percentage.keys():
        cdf[src] = (percentage[src] + prev_rate)*100
        prev_rate += percentage[src]

    plt.plot(cdf.keys(), cdf.values(), marker="*")
    plt.xlabel("absolute value of correlation")
    plt.ylabel("percentage of correlated source chiplets")
    plt.savefig(base_path + "/plots/source correlation analysis.jpg")
    plt.close()


def check_flow_correlation(base_path, request, chiplet_num):
    correlation = {}
    random_variables = {}
    for src in request.keys():
        for dest in request[src].keys():
            if src not in random_variables.keys():
                random_variables.setdefault(src, {})[dest] = list(request[src][dest].values())
            else:
                if dest not in random_variables[src].keys():
                    random_variables[src][dest] = list(request[src][dest].values())

    random_list = {}
    for src in random_variables.keys():
        for dest in random_variables[src].keys():
            label = str(src) + str(dest)
            random_list[label] = list(random_variables[src][dest])

    for label in random_list.keys():
        if len(random_list[label]) > 0:
            for label2 in random_list.keys():
                if len(random_list[label2]) > 0:
                    if label < label2:
                        x = random_list[label]
                        y = random_list[label2]
                        try:
                            mean_x = sum(x) / len(x)
                        except ZeroDivisionError:
                            mean_x = 0
                        try:
                            mean_y = sum(y) / len(y)
                        except ZeroDivisionError:
                            mean_y = 0
                        # Subtracting mean from the individual elements
                        sub_x = [i - mean_x for i in x]
                        sub_y = [i - mean_y for i in y]
                        numerator = sum([sub_x[i] * sub_y[i] for i in range(min(len(sub_y), len(sub_x)))])  # covariance
                        # Standard Deviation of x and y
                        std_deviation_x = sum([sub_x[i] ** 2.0 for i in range(len(sub_x))])
                        std_deviation_y = sum([sub_y[i] ** 2.0 for i in range(len(sub_y))])
                        # denominator = len(x) - 1
                        # cov = numerator / denominator
                        denominator = (std_deviation_x * std_deviation_y) ** 0.5  # short but equivalent to (std_deviation_x**0.5) * (std_deviation_y**0.5)
                        try:
                            cor = numerator / denominator
                        except ZeroDivisionError:
                            cor = 0
                        if label not in correlation.keys():
                            correlation.setdefault(label, {})[label2] = abs(cor)
                        else:
                            correlation[label][label2] = abs(cor)
    correlation = dict(sorted(correlation.items(), key=lambda x: x[0]))

    percentage = {}
    total_combination = 0
    for src in correlation.keys():
        total_combination += len(correlation[src])
        for label in correlation[src].keys():
            if correlation[src][label] not in percentage.keys():
                percentage[correlation[src][label]] = 1
            else:
                percentage[correlation[src][label]] += 1

    for src in percentage.keys():
        percentage[src] = percentage[src] / total_combination
    percentage = dict(sorted(percentage.items(), key=lambda x: x[0]))

    cdf = {}
    prev_rate = 0
    for src in percentage.keys():
        cdf[src] = (percentage[src] + prev_rate)*100
        prev_rate += percentage[src]
    plt.plot(cdf.keys(), cdf.values(), marker="*")
    plt.title("percentage of correlated flows")
    plt.xlabel("absolute value of correlation")
    plt.ylabel("percentage of correlated flows")
    plt.savefig(base_path + "/plots/flow correlation analysis.jpg")
    plt.close()


def check_stationary(input_, packet, chiplet_num):
    base_path = os.path.dirname(input_)
    aggreagate_injection = {}
    aggregate_request_injection = {}
    per_flow_request = {}
    for id in packet.keys():
        for j in range(len(packet[id])):
            if packet[id][j][0] == "request injected":
                chiplet = int(packet[id][j][1].split(": ")[1])
                dest = int(packet[id][j][2].split(": ")[1])
                cycle = int(packet[id][j][5].split(": ")[1])
                byte = int(packet[id][j][7].split(": ")[1])
                if cycle not in aggreagate_injection.keys():
                    aggreagate_injection[cycle] = byte
                else:
                    aggreagate_injection[cycle] += byte
                if chiplet not in aggregate_request_injection.keys():
                    aggregate_request_injection.setdefault(chiplet, {})[cycle] = byte
                else:
                    if cycle not in aggregate_request_injection[chiplet].keys():
                        aggregate_request_injection[chiplet][cycle] = byte
                    else:
                        aggregate_request_injection[chiplet][cycle] += byte
                if chiplet not in per_flow_request.keys():
                    per_flow_request.setdefault(chiplet, {}).setdefault(dest, {})[cycle] = byte
                else:
                    if dest not in per_flow_request[chiplet].keys():
                        per_flow_request[chiplet].setdefault(dest, {})[cycle] = byte
                    else:
                        if cycle not in per_flow_request[chiplet][dest].keys():
                            per_flow_request[chiplet][dest][cycle] = byte
                        else:
                            per_flow_request[chiplet][dest][cycle] += byte
            if packet[id][j][0] == "reply injected":
                cycle = int(packet[id][j][5].split(": ")[1])
                byte = int(packet[id][j][7].split(": ")[1])
                if cycle not in aggreagate_injection.keys():
                    aggreagate_injection[cycle] = byte
                else:
                    aggreagate_injection[cycle] += byte

    aggreagate_injection_ = {}
    m = min(aggreagate_injection.keys())
    M = max(aggreagate_injection.keys())
    for i in range(m, M, 1):
        if i not in aggreagate_injection.keys():
            aggreagate_injection_[i] = 0
        else:
            aggreagate_injection_[i] = aggreagate_injection[i]
    aggregate_request_injection_ = {}

    for i in range(0, chiplet_num, 1):
        if i not in aggregate_request_injection.keys():
            aggregate_request_injection.setdefault(i, {})[0] = 0
    for chiplet in aggregate_request_injection.keys():
        if chiplet not in aggregate_request_injection_.keys():
            aggregate_request_injection_.setdefault(chiplet, {})
        minimum = min(aggregate_request_injection[chiplet].keys())
        maximum = max(aggregate_request_injection[chiplet].keys())
        for i in range(minimum, maximum, 1):
            if i not in aggregate_request_injection[chiplet].keys():
                aggregate_request_injection_[chiplet][i] = 0
            else:
                aggregate_request_injection_[chiplet][i] = aggregate_request_injection[chiplet][i]
    aggregate_request_injection_ = dict(sorted(aggregate_request_injection_.items(), key=lambda x: x[0]))

    for i in range(0, chiplet_num, 1):
        if i not in per_flow_request.keys():
            per_flow_request.setdefault(i, {})
            for j in range(0, chiplet_num, 1):
                if i != j:
                    per_flow_request[i].setdefault(j, {})[0] = 0

    per_chiplet_flow_ = {}
    for src in per_flow_request.keys():
        if src not in per_chiplet_flow_.keys():
            per_chiplet_flow_.setdefault(src, {})
        for dest in per_flow_request[src].keys():
            if dest not in per_chiplet_flow_[src].keys():
                per_chiplet_flow_[src].setdefault(dest, {})
            minimum = min(per_flow_request[src][dest].keys())
            maximum = max(per_flow_request[src][dest].keys())
            for i in range(minimum, maximum, 1):
                if i not in per_flow_request[src][dest].keys():
                    per_chiplet_flow_[src][dest][i] = 0
                else:
                    per_chiplet_flow_[src][dest][i] = per_flow_request[src][dest][i]

    #plot_aggregate_traffic_injection_distribution(base_path, aggreagate_injection)
    #check_stationary_distribution(base_path, aggreagate_injection_, M)
    check_autocorrelation(base_path, aggreagate_injection_)
    #dicky_fuller(aggreagate_injection_)
    #check_source_correlation(base_path, aggregate_request_injection_, chiplet_num)
    #check_flow_correlation(base_path, per_chiplet_flow_, chiplet_num)