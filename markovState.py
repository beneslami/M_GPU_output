import csv
import math
import numpy as np
import matplotlib.pyplot as plt
from numpy import average, random, floor
import seaborn as sns
import pandas as pd
import scipy.stats

N = 4
duration = 200000
threshold_positive = N * 136 # 1040
threshold_negative = N * 136
arr = {0: 0, 1: 0} # Pi_0 -> arr[0]   Pi_1-> arr[1]
state_non_burst_time_dist = {}
state_non_burst_byte_dist = {}
state_burst_time_dist = {}
state_burst_byte_dist = {1: {}, -1: {}}

non_burst_array = []
non_burst_synthetic = []
burst_array = []


def temp():
    with open('atax.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    atax = {}
    for i in range(1, len(lined_list)):
        atax[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])

    with open('bicg.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    bicg = {}
    for i in range(1, len(lined_list)):
        bicg[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])

    with open(' nn_ispass.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    nn_ispass = {}
    for i in range(1, len(lined_list)):
        nn_ispass[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])

    with open('syrk.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    syrk = {}
    for i in range(1, len(lined_list)):
        syrk[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])

    with open('rodinia.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    rodinia = {}
    for i in range(1, len(lined_list)):
        rodinia[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])

    with open('random.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    random = {}
    for i in range(1, len(lined_list)):
        random[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])

    s = sns.kdeplot(list(atax.values()), shade=True, label="atax")
    s = sns.kdeplot(list(bicg.values()), shade=True, label="bicg")
    s = sns.kdeplot(list(nn_ispass.values()), shade=True, label="nn_ispass")
    s = sns.kdeplot(list(random.values()), shade=True, label="random")
    s = sns.kdeplot(list(rodinia.values()), shade=True, label="rodinia")
    s = sns.kdeplot(list(syrk.values()), shade=True, label="syrk")
    plt.legend(loc="best")
    plt.show()


def window(lined_list):
    index = 5
    real_e = {}
    real_v = {}
    real_r = {}
    for i in range(1, len(lined_list)):
        arr = []
        if i+index <= len(lined_list):
            for j in range(index):
                arr.append(float(lined_list[i+j][0].split(",")[1]))
            i += index
        else:
            for j in range(len(lined_list)-i):
                arr.append(float(lined_list[i+j][0].split(",")[1]))
        real_e[i] = np.mean(arr)
        real_v[i] = np.var(arr)
        real_r[i] = (max(arr) - min(arr))

    with open("input.csv", "w", newline='') as file_csv:
        field = ['window', 'mean', 'std']
        writer = csv.DictWriter(file_csv, fieldnames=field)
        writer.writeheader()
        for i in real_e.keys():
            writer.writerow({"window": i, "mean": real_e[i], "std": np.sqrt(real_v[i])})

    out = {}
    i = 1
    synthetic_e = {}
    synthetic_v = {}
    synthetic_r = {}
    with open("synthetic.csv", "w", newline='') as file_csv:
        field = ['cycle', 'byte']
        writer = csv.DictWriter(file_csv, fieldnames=field)
        writer.writeheader()
        for i in real_e.keys():
            temp = []
            for j in range(index):
                try:
                    out[i+j] = np.random.normal(real_e[i], math.sqrt(real_v[i]), 1)[0]
                    writer.writerow({"cycle": i+j, "byte": floor(out[i+j])})
                    temp.append(out[i+j])
                except KeyError:
                    pass
                synthetic_e[i] = np.mean(temp)
                synthetic_v[i] = np.var(temp)
                synthetic_r[i] = (max(temp) - min(temp))
            i += index
    actual = {}
    for i in range(1, len(lined_list)):
        actual[int(lined_list[i][0].split(",")[0])] = float(lined_list[i][0].split(",")[1])

    fig, ax = plt.subplots(2, 1, figsize=(18, 4))
    ax[0].plot(list(out.keys()), list(out.values()))
    ax[0].set_ylabel("synthetic")
    #ax[0].set_xlim(25000, 45000)
    #ax[0].set_ylim(-2500, 2500)

    """ax[1].plot(list(actual.keys()), list(actual.values()))
    ax[1].set_ylabel("atax")
    #ax[1].set_xlim(10000, 20000)
    #ax[1].set_ylim(-600, 25000)
    plt.xlabel("time step")
    sns.despine()
    plt.show()
    #s = sns.kdeplot(list(actual.values()), shade=True, color="r")"""
    plt.show()


def time_byte(lined_list):
    for i in range(1, len(lined_list)):
        if -threshold_negative < int(lined_list[i][0].split(",")[1]) < threshold_positive:
            arr[0] += 1
        else:
            arr[1] += 1

    arr[0], arr[1] = arr[0]/(arr[0] + arr[1]), arr[1]/(arr[0] + arr[1])


def state_non_burst(lined_list):
    prev = int(lined_list[1][0].split(",")[1])
    non_burst_array.append(int(lined_list[1][0].split(",")[1]))
    current = 0
    next = 0
    start = end = 0
    flag = 0
    for i in range(2, len(lined_list)):
        current = int(lined_list[i][0].split(",")[1])
        if i+1 < len(lined_list) and int(lined_list[i+1][0].split(",")[0]) < duration:
            next = int(lined_list[i+1][0].split(",")[1])

        if -threshold_negative <= current <= threshold_positive:
            non_burst_array.append(int(lined_list[i][0].split(",")[1]))
            if int(lined_list[i][0].split(",")[1]) in state_non_burst_byte_dist.keys():
                state_non_burst_byte_dist[int(lined_list[i][0].split(",")[1])] += 1
            else:
                state_non_burst_byte_dist[int(lined_list[i][0].split(",")[1])] = 1

            if prev <= -threshold_negative or prev >= threshold_positive:
                if -threshold_negative <= next <= threshold_positive:
                    start = int(lined_list[i][0].split(",")[0])
                    prev = current
                    continue
        if current <= -threshold_negative or current >= threshold_positive:
            if -threshold_negative <= prev <= threshold_positive:
                end = int(lined_list[i][0].split(",")[0])
                prev = current
                if (end - start) in state_non_burst_time_dist.keys():

                    state_non_burst_time_dist[end - start] += 1
                else:
                    state_non_burst_time_dist[end - start] = 1
                continue

    """mean = average(list(state_non_burst_time_dist.keys()), weights=list(state_non_burst_time_dist.values()))
    plt.bar(list(state_non_burst_time_dist.keys()), list(state_non_burst_time_dist.values()), width=10)
    #plt.text(20, 2, str(mean), bbox={'facecolor': 'blue', 'alpha': 0.5, 'pad': 10})
    plt.xlabel("non-burst time duration")
    plt.ylabel("Frequency")
    plt.show()"""


def state_burst(lined_list):
    prev = int(lined_list[1][0].split(",")[1])
    burst_array.append(int(lined_list[1][0].split(",")[1]))
    current = 0
    next = 0
    start = end = 0
    flag = 0
    for i in range(2, len(lined_list)):
        current = int(lined_list[i][0].split(",")[1])
        if i + 1 < len(lined_list) and int(lined_list[i + 1][0].split(",")[0]) < duration:
            next = int(lined_list[i + 1][0].split(",")[1])

        if not(-threshold_negative <= current <= threshold_positive):
            burst_array.append(int(lined_list[i][0].split(",")[1]))
            if current > 0:
                if int(lined_list[i][0].split(",")[1]) in state_burst_byte_dist[1].keys():
                    state_burst_byte_dist[1][int(lined_list[i][0].split(",")[1])] += 1
                else:
                    state_burst_byte_dist[1][int(lined_list[i][0].split(",")[1])] = 1
            else:
                if int(lined_list[i][0].split(",")[1]) in state_burst_byte_dist[1].keys():
                    state_burst_byte_dist[-1][int(lined_list[i][0].split(",")[1])] += 1
                else:
                    state_burst_byte_dist[-1][int(lined_list[i][0].split(",")[1])] = 1
            if -threshold_negative <= prev <= threshold_positive:
                if not(-threshold_negative <= next <= threshold_positive):
                    start = int(lined_list[i][0].split(",")[0])
                    prev = current
            pass
        else:
            if not(-threshold_negative <= prev <= threshold_positive):
                end = int(lined_list[i][0].split(",")[0])
                prev = current
                if (end - start) in state_burst_time_dist.keys():
                    state_burst_time_dist[end - start] += 1
                else:
                    state_burst_time_dist[end - start] = 1
            pass

    """mean = average(list(state_burst_byte_dist.keys()), weights=list(state_burst_byte_dist.values()))
    plt.bar(list(state_burst_byte_dist[1].keys()), list(state_burst_byte_dist[1].values()), width=5)
    plt.text(2500, 6000, str(mean), bbox={'facecolor': 'blue', 'alpha': 0.5, 'pad': 10})
    plt.xlabel("burst time duration")
    plt.ylabel("Frequency")
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


def equilibrium_distribution(p_transition):
    n_states = p_transition.shape[0]
    A = np.append(arr=p_transition.T - np.eye(n_states), values=np.ones(n_states).reshape(1, -1), axis=0)
    b = np.transpose(np.array([0] * n_states + [1]))
    p_eq = np.linalg.solve(a=np.transpose(A).dot(A), b=np.transpose(A).dot(b))
    return p_eq


def markov_chain(lined_list):
    """p_init = np.array([1, 0.])
    p_transition = np.array(
        [[0.90, 0.05],
         [0.01, 0.80]]
    )
    p_state_t = [p_init]

    for i in range(duration): # calculate the state matrix for each time step
        p_state_t.append(p_state_t[-1] @ p_transition)
    state_distributions = pd.DataFrame(p_state_t)
    state_distributions.plot()

    equilibrium_distribution(p_transition)

    # Generate a Markov sequence based on p_init and p_transition
    initial_state = list(multinomial.rvs(1, p_init)).index(1)
    states = [initial_state]
    for i in range(duration - 1):
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
        emissions.append(e)"""
    state_change = []
    injection = {}
    state_non_burst_duration_mean = average(list(state_non_burst_time_dist.keys()), weights=list(state_non_burst_time_dist.values()))
    state_burst_duration_mean = average(list(state_burst_time_dist.keys()), weights=list(state_burst_time_dist.values()))

    non_burst_mean_mu = average(list(state_non_burst_byte_dist.keys()), weights=list(state_non_burst_byte_dist.values()))
    non_burst_mean_sigma = math.sqrt(average((list(state_non_burst_byte_dist.keys()) - non_burst_mean_mu) ** 2, weights=list(state_non_burst_byte_dist.values())))

    burst_positive_mean_mu = average(list(state_burst_byte_dist[1].keys()), weights=list(state_burst_byte_dist[1].values()))
    burst_negative_mean_mu = average(list(state_burst_byte_dist[-1].keys()),weights=list(state_burst_byte_dist[-1].values()))
    burst_mean_sigma = math.sqrt(average((list(state_burst_byte_dist[1].keys()) - burst_positive_mean_mu)**2, weights=list(state_burst_byte_dist[1].values())))

    i = 0
    while i < duration:
        state_change.append(0)
        window = 11000#int(floor(np.random.exponential(state_non_burst_duration_mean)))
        for j in range(1, window + 1):
            injection[i + j] = np.random.normal(non_burst_mean_mu, non_burst_mean_sigma, 1)[0]
            non_burst_synthetic.append(injection[i + j])
        i += window

        state_change.append(1)
        window = 3000#int(floor(np.random.exponential(state_burst_duration_mean)))
        for j in range(window + 1):
            coin = np.random.binomial(1, 0.5, 1)[0]
            if coin == 0:
                injection[i + j] = -np.random.exponential(abs(burst_positive_mean_mu), 1)[0]
            elif coin == 1:
                injection[i + j] = np.random.exponential(burst_positive_mean_mu, 1)[0]
        i += window

    actual = {}
    for i in range(1, len(lined_list)):
        actual[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])

    x = list(injection.keys())
    for i in x:
        if i not in actual.keys():
            injection.pop(i)

    sort_orders = sorted(injection.items(), key=lambda x: x[0])
    with open("synthetic.csv", "w", newline='') as file_csv:
        field = ['cycle', 'byte']
        writer = csv.DictWriter(file_csv, fieldnames=field)
        writer.writeheader()
        for i in range(len(sort_orders)):
            writer.writerow({"cycle": sort_orders[i][0], "byte": sort_orders[i][1]})
    t1 = []
    t2 = []
    for i in injection.keys():
        t1.append(threshold_positive)
        t2.append(-threshold_negative)
    fig, ax = plt.subplots(2, 1, figsize=(18, 4))
    ax[0].plot(list(injection.keys()), list(injection.values()))
    ax[0].plot(list(injection.keys()), t1, color="red")
    ax[0].plot(list(injection.keys()), t2, color="red")
    ax[0].set_ylabel("synthetic")
    #ax[0].set_xlim(20000, 25000)
    #ax[0].set_ylim(-1000, 1000)
    t1 = []
    t2 = []
    for i in actual.keys():
        t1.append(threshold_positive)
        t2.append(-threshold_negative)
    ax[1].plot(list(actual.keys()), list(actual.values()))
    ax[1].plot(list(actual.keys()), t1, color="red")
    ax[1].plot(list(actual.keys()), t2, color="red")
    ax[1].set_ylabel("bicg")
    #ax[1].set_xlim(20000, 25000)
    #ax[1].set_ylim(-1000, 1000)
    plt.xlabel("time step")
    sns.despine()
    plt.show()


if __name__ == "__main__":
    with open('atax_core.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    """time_byte(lined_list)
    state_non_burst(lined_list)
    state_burst(lined_list)
    markov_chain(lined_list)"""
    window(lined_list)