import csv
import math
from random import expovariate
import numpy as np
import matplotlib.pyplot as plt
from numpy import average, random, floor
import seaborn as sns
import scipy

N = 4
duration = 200000
threshold_positive = N * 260
threshold_negative = N * 240
arr = {0: 0, 1: 0} # Pi_0 -> arr[0]   Pi_1-> arr[1]
state_non_burst_time_dist = {}
state_non_burst_byte_dist = {-1: {}, 1: {}}
state_burst_time_dist = {}
state_burst_byte_dist = {-1: {}, 1: {}}

non_burst_array = []
non_burst_synthetic = []
burst_array = []


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
            if current >= 0:
                if int(lined_list[i][0].split(",")[1]) in state_non_burst_byte_dist[1].keys():
                    state_non_burst_byte_dist[1][int(lined_list[i][0].split(",")[1])] += 1
                else:
                    state_non_burst_byte_dist[1][int(lined_list[i][0].split(",")[1])] = 1
            else:
                if int(lined_list[i][0].split(",")[1]) in state_non_burst_byte_dist[-1].keys():
                    state_non_burst_byte_dist[-1][int(lined_list[i][0].split(",")[1])] += 1
                else:
                    state_non_burst_byte_dist[-1][int(lined_list[i][0].split(",")[1])] = 1
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
                if int(lined_list[i][0].split(",")[1]) in state_burst_byte_dist[-1].keys():
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

    mean = average(list(state_burst_byte_dist[1].keys()), weights=list(state_burst_byte_dist[1].values()))
    plt.bar(list(state_burst_byte_dist[1].keys()), list(state_burst_byte_dist[1].values()), width=5)
    plt.text(2500, 6000, str(mean), bbox={'facecolor': 'blue', 'alpha': 0.5, 'pad': 10})
    plt.xlabel("burst time duration")
    plt.ylabel("Frequency")
    plt.show()


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
    non_burst_positive_mean_mu = average(list(state_non_burst_byte_dist[1].keys()), weights=list(state_non_burst_byte_dist[1].values()))
    non_burst_positive_mean_sigma = math.sqrt(average((list(state_non_burst_byte_dist[1].keys()) - non_burst_positive_mean_mu) ** 2,weights=list(state_non_burst_byte_dist[1].values())))
    non_burst_negative_mean_mu = average(list(state_non_burst_byte_dist[-1].keys()), weights=list(state_non_burst_byte_dist[-1].values()))
    non_burst_negative_mean_sigma = math.sqrt(average((list(state_non_burst_byte_dist[-1].keys()) - non_burst_negative_mean_mu) ** 2,weights=list(state_non_burst_byte_dist[-1].values())))

    burst_negative_mean_mu = abs(average(list(state_burst_byte_dist[-1].keys()), weights=list(state_burst_byte_dist[-1].values())))
    burst_negative_mean_sigma = math.sqrt(average((list(state_burst_byte_dist[-1].keys()) - burst_negative_mean_mu) ** 2,weights=list(state_burst_byte_dist[-1].values())))
    burst_positive_mean_mu = average(list(state_burst_byte_dist[1].keys()), weights=list(state_burst_byte_dist[1].values()))
    burst_positive_mean_sigma = math.sqrt(average((list(state_burst_byte_dist[1].keys()) - burst_positive_mean_mu)**2, weights=list(state_burst_byte_dist[1].values())))
    print("positive burst mean: " + str(burst_positive_mean_mu))
    print("positive burst vari: " + str(burst_positive_mean_sigma))
    print("negative burst mean: " + str(burst_negative_mean_mu))
    print("negative burst vari: " + str(burst_negative_mean_sigma))

    state_burst_duration_mean = average(list(state_burst_time_dist.keys()), weights=list(state_burst_time_dist.values()))
    i = 0
    while i < duration:
        s = np.random.uniform(0, 1)
        if 0 < s < arr[0]:
            state_change.append(0)
            window = int(floor(expovariate(1 / state_non_burst_duration_mean)))
            for j in range(1, window + 1):
                coin = np.random.binomial(1, 0.5, 1)[0]
                if coin == 0:
                    injection[i + j] = np.random.normal(non_burst_positive_mean_mu, non_burst_positive_mean_sigma, 1)[0]
                elif coin == 1:
                    injection[i + j] = np.random.normal(non_burst_negative_mean_mu, non_burst_negative_mean_sigma, 1)[0]
                non_burst_synthetic.append(injection[i + j])
            i += window
        else:
            state_change.append(1)
            window = int(floor(expovariate(1 / state_burst_duration_mean)))
            for j in range(window + 1):
                coin = np.random.binomial(1, 0.5, 1)[0]
                if coin == 0:
                    injection[i + j] = -np.random.normal(burst_negative_mean_mu, burst_negative_mean_sigma, 1)[0]
                elif coin == 1:
                    injection[i + j] = np.random.normal(burst_positive_mean_mu, burst_positive_mean_sigma, 1)[0]
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
    #ax[0].set_xlim(5000, 10000)
    ax[0].set_ylim(-2500, 2500)
    t1 = []
    t2 = []
    for i in actual.keys():
        t1.append(threshold_positive)
        t2.append(-threshold_negative)
    ax[1].plot(list(actual.keys()), list(actual.values()))
    ax[1].plot(list(actual.keys()), t1, color="red")
    ax[1].plot(list(actual.keys()), t2, color="red")
    ax[1].set_ylabel("bicg")
    #ax[1].set_xlim(5000, 10000)
    #ax[1].set_ylim(-600, 25000)
    plt.xlabel("time step")
    sns.despine()
    plt.show()


def shapiro_wilk_test():
    _, p1 = scipy.stats.shapiro(non_burst_array[0:5000])
    _, p2 = scipy.stats.normaltest(non_burst_array[0:5000])

    sum = 0
    non_burst_synthetic.pop()
    for i in range(len(non_burst_array)):
        sum += (np.sqrt(abs(non_burst_synthetic[i])) - np.sqrt(abs(non_burst_array[i])))**2
    result = (1 / np.sqrt(2)) * np.sqrt(sum)
    print("hellinger: ", str(result))


if __name__ == "__main__":
    with open('bicg.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    time_byte(lined_list)
    state_non_burst(lined_list)
    state_burst(lined_list)
    markov_chain(lined_list)
    #shapiro_wilk_test()