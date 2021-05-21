import numpy as np
import matplotlib.pyplot as plt
from numpy import average


def state_zero(lined_list):
    start = end = 0
    flag = 1
    with open("state_zero.txt", "a") as file:
        for i in range(1, len(lined_list)):
            if int(lined_list[i][0].split(",")[1]) < 8:
                if flag == 1:
                    continue
                else:
                    start = int(lined_list[i][0].split(",")[0])
                    flag = 1
            else:
                if flag == 1:
                    end = int(lined_list[i][0].split(",")[0])
                    file.write(str(end - start) + "\n")
                    flag = 0


def state_zero_distribution():
    arr = {}
    with open('state_zero.txt', 'r') as file:
        reader = file.readlines()
    for num in reader:
        if int(num) in arr.keys():
            arr[int(num)] += 1
        else:
            arr[int(num)] = 1
    mean = average(list(arr.keys()), weights=list(arr.values()))
    print(mean)    #3.2839665665322895
    #actual = np.random.exponential(mean)
    #print((1/mean)*np.exp(-(1/mean)*actual))
    """plt.bar(list(arr.keys()), list(arr.values()))
    plt.xlim(0, 100)
    plt.show()"""


def state_non_burst(lined_list):
    start = end = 0
    flag = 1
    with open("state_non_burst.txt", "a") as file:
        for i in range(1, len(lined_list)):
            if 8 <= int(lined_list[i][0].split(",")[1]) <= 800 or -800 <= int(lined_list[i][0].split(",")[1]) <= -8:
                if flag == 1:
                    continue
                else:
                    start = int(lined_list[i][0].split(",")[0])
                    flag = 1
            else:
                if flag == 1:
                    end = int(lined_list[i][0].split(",")[0])
                    file.write(str(end - start) + "\n")
                    flag = 0


def state_non_burst_distribution():
    arr = {}
    with open('state_non_burst.txt', 'r') as file:
        reader = file.readlines()
    for num in reader:
        if int(num) in arr.keys():
            arr[int(num)] += 1
        else:
            arr[int(num)] = 1
    mean = average(list(arr.keys()), weights=list(arr.values()))
    print(mean)  # 8.751150415177769
    plt.bar(list(arr.keys()), list(arr.values()))
    #plt.xlim(0, 100)
    plt.show()


def state_burst(lined_list):
    start = end = 0
    flag = 1
    with open("state_burst.txt", "a") as file:
        for i in range(1, len(lined_list)):
            if int(lined_list[i][0].split(",")[1]) > 800 or int(lined_list[i][0].split(",")[1]) < -800:
                if flag == 1:
                    continue
                else:
                    start = int(lined_list[i][0].split(",")[0])
                    flag = 1
            else:
                if flag == 1:
                    end = int(lined_list[i][0].split(",")[0])
                    file.write(str(end - start) + "\n")
                    flag = 0


def state_burst_distribution():
    arr = {}
    with open('state_burst.txt', 'r') as file:
        reader = file.readlines()
    for num in reader:
        if int(num) in arr.keys():
            arr[int(num)] += 1
        else:
            arr[int(num)] = 1
    mean = average(list(arr.keys()), weights=list(arr.values()))
    print(mean)  #1.5290773500986523
    plt.bar(list(arr.keys()), list(arr.values()))
    plt.xlim(0, 100)
    plt.show()


def time_byte(lined_list):
    arr= {int(lined_list[1][0].split(",")[0]): int(lined_list[1][0].split(",")[1])}
    prev_time_slot = int(lined_list[1][0].split(",")[0])
    for i in range(2, len(lined_list)):
        if int(lined_list[i][0].split(",")[0]) == prev_time_slot + 1:
            arr[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])
            prev_time_slot = int(lined_list[i][0].split(",")[0])
        else:
            for j in range(prev_time_slot + 1, int(lined_list[i][0].split(",")[0]) + 1):
                arr[j] = 0
            arr[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])
            prev_time_slot = int(lined_list[i][0].split(",")[0])

    plt.plot(list(arr.keys()), list(arr.values()))
    plt.xlim(52000, 54000)
    plt.show()


def state_stay(lined_list):
    constant = {}
    constant_byte = {}
    burst = {}
    burst_byte = {}
    alternation = 0
    threshold = 2000
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
    plt.show()"""


def state_transition(lined_list):
    bernuli = {0: 0, 1: 0}
    threshold = 400

    for i in range(1, len(lined_list)):
        if int(lined_list[i][0].split(",")[1]) > threshold or int(lined_list[i][0].split(",")[1]) < -threshold:
            bernuli[1] += 1

        elif -threshold <= int(lined_list[i][0].split(",")[1]) <= threshold:
            bernuli[0] += 1

    plt.bar(list(bernuli.keys()), list(bernuli.values()), width=0.3)
    plt.text(-0.05, bernuli[0]+380, str(bernuli[0]))
    plt.text(1-0.05, bernuli[1] + 380, str(bernuli[1]))
    plt.xticks([0, 1], [0, 1])
    plt.xlabel("outcome")
    plt.ylabel("Occurrence")
    #plt.ylim(0, 8000)
    plt.text(0.35, 8110, "threshold:" + str(threshold) + "B", bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
    plt.title("Distribution of the number of bursty and non-bursty traffic")
    plt.show()


def byte_state_distribution(lined_list):
    constant = {}
    burst = {}
    threshold = 3000
    for i in range(1, len(lined_list)):
        if -threshold <= int(lined_list[i][0].split(",")[1]) <= threshold:
            if abs(int(lined_list[i][0].split(",")[1])) in constant.keys():
                constant[abs(int(lined_list[i][0].split(",")[1]))] += 1
            else:
                constant[abs(int(lined_list[i][0].split(",")[1]))] = 1
        elif int(lined_list[i][0].split(",")[1]) > threshold or int(lined_list[i][0].split(",")[1]) < -threshold:
            if abs(int(lined_list[i][0].split(",")[1])) in burst.keys():
                burst[abs(int(lined_list[i][0].split(",")[1]))] += 1
            else:
                burst[abs(int(lined_list[i][0].split(",")[1]))] = 1
    burst_mean = average(list(burst.keys()), weights=list(burst.values()))
    burst_vars = average((list(burst.keys()) - burst_mean) ** 2, weights=list(burst.values()))
    burst_std = np.sqrt(burst_vars)
    constant_mean = average(list(constant.keys()), weights=list(constant.values()))
    constant_vars = average((list(constant.keys()) - constant_mean) ** 2, weights=list(constant.values()))
    constant_std = np.sqrt(constant_vars)

    plt.bar(list(constant.keys()), list(constant.values()), width=4)
    string = "mean: " + str(constant_mean) + "\n" + "variance: " + str(constant_vars) + "\n" + "stdev: " + str(
        constant_std) + "\nthreshold: " + str(threshold)
    plt.text(400, 15000, string, bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
    plt.xlabel("byte")
    plt.ylabel("Occurrence")
    plt.title("Byte distribution of non-bursty traffic")
    plt.show()


def markov_chain():
    states = ["zero", "n_burst", "burst"]
    transitions = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    state_probability = [
        [(1/3.2839665665322895)*np.exp(-(1/3.2839665665322895)*np.random.exponential(3.2839665665322895))],
        [(1 / 8.751150415177769) * np.exp(-(1 / 8.751150415177769) * np.random.exponential(8.751150415177769))],
        [(1 / 1.5290773500986523) * np.exp(-(1 / 1.5290773500986523) * np.random.exponential(1.5290773500986523))]
    ]
    transitions[0][1] = state_probability[0][1] / state_probability[0][2] - state_probability[0][1]
    transitions[0][0] = -transitions[0][1]

    transitions[2][1] = state_probability[0][3] / state_probability[0][2] - state_probability[0][3]
    transitions[2][2] = -transitions[2][1]


if __name__ == "__main__":
    with open(' nn_ispass.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    #state_stay(lined_list)
    #state_transition(lined_list)
    #byte_state_distribution(lined_list)
    #time_byte(lined_list)
    #state_zero(lined_list)
    #state_zero_distribution()
    #state_non_burst(lined_list)
    #state_non_burst_distribution()
    #state_burst(lined_list)
    #state_burst_distribution()