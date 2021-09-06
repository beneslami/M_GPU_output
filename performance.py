from hurst import compute_Hc
import matplotlib.pyplot as plt
import seaborn as sns

def hurst(lined_list):
    time_byte = {}
    for i in range(1, len(lined_list)):
        if int(lined_list[i][0].split(",")[0]) in time_byte.keys():
            time_byte[int(lined_list[i][0])] += float(lined_list[i][1])
        else:
            time_byte[int(lined_list[i][0])] = float(lined_list[i][1])
    H, c, data = compute_Hc(list(time_byte.values()), simplified=True)
    f, ax = plt.subplots()
    ax.plot(data[0], c * data[0] ** H, color="deepskyblue")
    ax.scatter(data[0], data[1], color="purple")
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.text(10000, 5, "slope = " + str("{:.3f}".format(H)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax.set_xlabel('Time interval')
    ax.set_ylabel('R/S ratio')
    #ax.grid(True)
    plt.show()
    print("H={:.4f}, c={:.4f}".format(H, c))


if __name__ == "__main__":
    with open("example.txt", "r") as file:
        reader = file.readlines()
    lined_list = []
    pair = {}
    for line in reader:
        item = line.split(",")
        lined_list.append(item)
    hurst(lined_list)
    pair[int(lined_list[0][0])] = float(lined_list[0][1])
    for i in range(1, len(lined_list)):
        if int(lined_list[i][0]) in pair.keys():
            pair[int(lined_list[i][0])] += float(lined_list[i][1])
        else:
            pair[int(lined_list[i][0])] = float(lined_list[i][1])
    sns.distplot(list(pair.values()), kde=True, hist=False)
    plt.show()

    with open("example2.txt", "r") as file:
        reader = file.readlines()
    lined_list = []
    pair = {}
    for line in reader:
        item = line.split(": ")
        lined_list.append(item)
    hurst(lined_list)
    for i in range(1, len(lined_list)):
        if int(lined_list[i][0]) in pair.keys():
            pair[int(lined_list[i][0])] += float(lined_list[i][1])
        else:
            pair[int(lined_list[i][0])] = float(lined_list[i][1])
    sns.distplot(list(pair.values()), kde=True, hist=False)
    plt.show()