import numpy as np
import matplotlib.pyplot as plt
from numpy import average, random
import pymc3 as pm
import seaborn as sns
import scipy.stats
from scipy.stats import multinomial
from scipy.stats import norm, uniform
import pandas as pd


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
    plt.bar(list(arr.keys()), list(arr.values()))
    plt.text(20, 10000, str(mean), bbox={'facecolor': 'blue', 'alpha': 0.5, 'pad': 10})
    plt.xlabel("burst time duration")
    plt.ylabel("Occurrence")
    plt.xlim(0, 100)
    plt.show()


def state_non_burst(lined_list):
    start = end = 0
    flag = 1
    with open("state_non_burst.txt", "a") as file:
        for i in range(1, len(lined_list)):
            if 4*8 <= int(lined_list[i][0].split(",")[1]) <= 4*136 or -4*136 <= int(lined_list[i][0].split(",")[1]) <= -4*8:
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
    plt.text(20, 10000, str(mean), bbox={'facecolor': 'blue', 'alpha': 0.5, 'pad': 10})
    plt.xlim(0, 100)
    plt.xlabel("burst time duration")
    plt.ylabel("Occurrence")
    plt.show()


def state_burst(lined_list):
    start = end = 0
    flag = 1
    with open("state_burst.txt", "a") as file:
        for i in range(1, len(lined_list)):
            if int(lined_list[i][0].split(",")[1]) > 4*136 or int(lined_list[i][0].split(",")[1]) < -4*136:
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
    plt.xlabel("burst time duration")
    plt.ylabel("Occurrence")
    plt.text(20, 10000, str(mean), bbox={'facecolor': 'blue', 'alpha': 0.5, 'pad': 10})
    plt.show()


def time_byte(lined_list):
    arr = {int(lined_list[1][0].split(",")[0]): int(lined_list[1][0].split(",")[1])}
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
    zero = {}
    min_threshold = 4*8
    max_threshold = 4*136
    s_0 = s_1 = s_2 = total = 0
    for i in range(1, len(lined_list)):
        if -max_threshold <= int(lined_list[i][0].split(",")[1]) <= -min_threshold:
            if int(lined_list[i][0].split(",")[1]) in constant.keys():
                constant[int(lined_list[i][0].split(",")[1])] += 1
            else:
                constant[int(lined_list[i][0].split(",")[1])] = 1
            s_1 += 1
            total += 1
        elif min_threshold <= int(lined_list[i][0].split(",")[1]) <= max_threshold:
            if int(lined_list[i][0].split(",")[1]) in constant.keys():
                constant[int(lined_list[i][0].split(",")[1])] += 1
            else:
                constant[abs(int(lined_list[i][0].split(",")[1]))] = 1
            s_1 += 1
            total += 1
        elif int(lined_list[i][0].split(",")[1]) > max_threshold or int(lined_list[i][0].split(",")[1]) < -max_threshold:
            if int(lined_list[i][0].split(",")[1]) in burst.keys():
                burst[int(lined_list[i][0].split(",")[1])] += 1
            else:
                burst[int(lined_list[i][0].split(",")[1])] = 1
            s_2 += 1
            total += 1
        elif -min_threshold <= int(lined_list[i][0].split(",")[1]) <= min_threshold:
            if int(lined_list[i][0].split(",")[1]) in zero.keys():
                zero[int(lined_list[i][0].split(",")[1])] += 1
            else:
                zero[int(lined_list[i][0].split(",")[1])] = 1
            s_0 += 1
            total += 1
    print("state 0: " + str(s_0/total) + "\nstate 1: " + str(s_1/total) + "\nstate 2: " + str(s_2/total))
    burst_mean = average(list(burst.keys()), weights=list(burst.values()))
    burst_vars = average((list(burst.keys()) - burst_mean) ** 2, weights=list(burst.values()))
    burst_std = np.sqrt(burst_vars)
    constant_mean = average(list(constant.keys()), weights=list(constant.values()))
    constant_vars = average((list(constant.keys()) - constant_mean) ** 2, weights=list(constant.values()))
    constant_std = np.sqrt(constant_vars)
    zero_mean = average(list(zero.keys()), weights=list(zero.values()))
    zero_vars = average((list(zero.keys()) - zero_mean) ** 2, weights=list(zero.values()))
    zero_std = np.sqrt(zero_vars)

    plt.bar(list(burst.keys()), list(burst.values()), width=4)
    string = "mean: " + str(zero_mean) + "\n" + "variance: " + str(zero_vars) + "\n" + "stdev: " + str(
        zero_std) + "\nmin_threshold: " + str(min_threshold) + "\nmax_threshold: " + str(max_threshold)
    plt.text(3000, 150, string, bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})
    plt.xlabel("byte")
    plt.ylabel("Occurrence")
    plt.title("Byte distribution of zero traffic")
    plt.show()


def equilibrium_distribution(p_transition):
    n_states = p_transition.shape[0]
    A = np.append(arr=p_transition.T - np.eye(n_states), values=np.ones(n_states).reshape(1, -1), axis=0)
    b = np.transpose(np.array([0] * n_states + [1]))
    p_eq = np.linalg.solve(a=np.transpose(A).dot(A), b=np.transpose(A).dot(b))
    return p_eq


def markov_chain():
    p_init = np.array([1, 0., 0.])
    p_transition = np.array(
        [[0.90, 0.05, 0.],
         [0.01, 0.80, 0.19],
         [0., 0.5, 0.5]]
    )
    p_state_t = [p_init]

    for i in range(2000): # calculate the state matrix for each time step
        p_state_t.append(p_state_t[-1] @ p_transition)
    state_distributions = pd.DataFrame(p_state_t)
    state_distributions.plot()

    equilibrium_distribution(p_transition)

    # Generate a Markov sequence based on p_init and p_transition
    initial_state = list(multinomial.rvs(1, p_init)).index(1)
    states = [initial_state]
    for i in range(2000 - 1):
        p_tr = p_transition[states[-1]]
        new_state = list(multinomial.rvs(1, p_tr)).index(1)
        states.append(new_state)

    emissions = []
    mus = [1, 0, -1]
    sigmas = [0.2, 0.5, 0.1]
    for state in states:
        loc = mus[state]
        scale = sigmas[state]
        e = norm.rvs(loc=loc, scale=scale)
        emissions.append(e)

    fig, ax = plt.subplots(2, 1, figsize=(12, 4))
    ax[0].plot(states)
    ax[1].plot(emissions)
    plt.xlabel("time step")
    sns.despine()
    plt.show()


def state_change_example():
    init_state = [1, 0, 0]
    state = {}
    for i in range(1000):
        x = random.uniform()
        if 0. <= x <= 0.015:
            state[i] = 0
        elif 0.0151 <= x <= 0.495:
            state[i] = 1
        elif 0.496 <= x <= 1.:
            state[i] = 2
    plt.plot(list(state.keys()), list(state.values()))
    plt.yticks([0, 1, 2])
    plt.show()


if __name__ == "__main__":
    with open('atax.csv', 'r') as file:
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
    #markov_chain()
    state_change_example()