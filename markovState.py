import numpy as np
import matplotlib.pyplot as plt
from numpy import average


def state_stay(lined_list):
    constant = {}
    constant_byte = {}
    burst = {}
    burst_byte = {}
    alternation = 0
    threshold = 800
    constant_start = constant_end = 0
    burst_start = burst_end = 0
    if int(lined_list[1][0].split(",")[1]) > threshold or int(lined_list[1][0].split(",")[1]) < threshold:
        alternation = 1
        burst_start = int(lined_list[1][0].split(",")[0])
    elif -threshold <= int(lined_list[1][0].split(",")[1]) <= threshold:
        constant_start = int(lined_list[1][0].split(",")[0])
        alternation = 0

    for i in range(1, len(lined_list)):
        if int(lined_list[i][0].split(",")[1]) > threshold or int(lined_list[i][0].split(",")[1]) < -threshold:
            if alternation == 0:
                burst_start = int(lined_list[i][0].split(",")[0])
                constant_end = int(lined_list[i][0].split(",")[0])
                alternation = 1
                if (constant_end - constant_start) in constant.keys():
                    constant[constant_end - constant_start] += 1
                else:
                    constant[constant_end - constant_start] = 1
            else:
                continue
            burst_byte[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])

        elif -threshold <= int(lined_list[i][0].split(",")[1]) <= threshold:
            if alternation == 1:
                constant_start = int(lined_list[i][0].split(",")[0])
                burst_end = int(lined_list[i][0].split(",")[0])
                alternation = 0
                if (burst_end - burst_start) in burst.keys():
                    burst[burst_end - burst_start] += 1
                else:
                    burst[burst_end - burst_start] = 1
            else:
                continue
            constant_byte[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])

    burst_mean = average(list(burst.keys()), weights=list(burst.values()))
    burst_vars = average((list(burst.keys()) - burst_mean) ** 2, weights=list(burst.values()))
    burst_std = np.sqrt(burst_vars)
    constant_mean = average(list(constant.keys()), weights=list(constant.values()))
    constant_vars = average((list(constant.keys()) - constant_mean) ** 2, weights=list(constant.values()))
    constant_std = np.sqrt(constant_vars)

    string = "mean: " + str(constant_mean) + "\n" + "variance: " + str(constant_vars) + "\n" + "stdev: " + str(
        constant_std) + "\nthreshold: " + str(threshold)
    plt.bar(list(constant.keys()), list(constant.values()), width=1)
    plt.title("non-Burst state duration distribution")
    plt.ylabel("Occurence")
    plt.xlabel("period in cycle")
    plt.text(85, 1000, string, bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
    plt.xlim(-10, 200)
    plt.show()

    """string = "mean: " + str(burst_mean) + "\n" + "variance: " + str(burst_vars) + "\n" + "stdev: " + str(burst_std) + "\nthreshold: " + str(threshold)
    plt.bar(list(burst.keys()), list(burst.values()), width=1)
    plt.ylabel("Occurence")
    plt.xlabel("period in cycle")
    plt.title("Burst state duration distribution")
    plt.text(40, 2500, string, bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
    plt.xlim(-10, 100)
    plt.show()
    """

def state_transition(lined_list):
    threshold = 800
    bernuli = {}
    for i in range(1, len(lined_list)):
        if int(lined_list[i][0].split(",")[1]) > threshold or int(lined_list[i][0].split(",")[1]) < -threshold:
            if 0 in bernuli.keys():
                bernuli[0] += 1
            else:
                bernuli[0] = 1
        else:
            if 1 in bernuli.keys():
                bernuli[1] += 1
            else:
                bernuli[1] = 1
    plt.bar(list(bernuli.keys()), list(bernuli.values()))
    plt.show()


if __name__ == "__main__":
    with open(' nn_ispass.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    #state_stay(lined_list)
    state_transition(lined_list)
