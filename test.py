import matplotlib.pyplot as plt
from hurst import compute_Hc

chiplet = []
chiplet_0 = dict(
    SM_ID=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
           28, 29, 30, 31],
    LLC_ID=[128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143], port=192)

chiplet_1 = dict(
    SM_ID=[32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
           59, 60, 61, 62, 63],
    LLC_ID=[144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159], port=193)

chiplet_2 = dict(
    SM_ID=[64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
           91, 92, 93, 94, 95],
    LLC_ID=[160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175], port=194)

chiplet_3 = dict(
    SM_ID=[96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117,
           118, 119, 120, 121, 122, 123, 124, 125, 126, 127],
    LLC_ID=[176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191], port=195)

chiplet.append(chiplet_0)
chiplet.append(chiplet_1)
chiplet.append(chiplet_2)
chiplet.append(chiplet_3)


def chip_select(num):
    out = -1
    for i in range(len(chiplet)):
        if num in chiplet[i]["SM_ID"]:
            out = i
            break
        if num in chiplet[i]["LLC_ID"]:
            out = i
            break
        if num == chiplet[i]["port"]:
            out = i
            break
    return out

#      ax.plot(data[0], c * data[0] ** H, color="deepskyblue")
#      ax.scatter(data[0], data[1], color="purple")
def hurst(out):
    H_192, c_192, data_192 = compute_Hc(list(out[192].values()))
    H_193, c_193, data_193 = compute_Hc(list(out[193].values()))
    H_194, c_194, data_194 = compute_Hc(list(out[194].values()))
    H_195, c_195, data_195 = compute_Hc(list(out[195].values()))

    f, ax = plt.subplots(2, 2)
    ax[0, 0].plot(data_192[0], c_192 * data_192[0] ** H_192, color="deepskyblue")
    ax[0, 0].scatter(data_192[0], data_192[1], color="purple")
    ax[0, 0].set_xscale('log')
    ax[0, 0].set_yscale('log')
    ax[0, 0].text(100, 2, "slope = " + str("{:.3f}".format(H_192)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})

    ax[0, 1].plot(data_193[0], c_193 * data_193[0] ** H_193, color="deepskyblue")
    ax[0, 1].scatter(data_193[0], data_193[1], color="purple")
    ax[0, 1].set_xscale('log')
    ax[0, 1].set_yscale('log')
    ax[0, 1].text(100, 10, "slope = " + str("{:.3f}".format(H_193)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})

    ax[1, 0].plot(data_194[0], c_194 * data_194[0] ** H_194, color="deepskyblue")
    ax[1, 0].scatter(data_194[0], data_194[1], color="purple")
    ax[1, 0].set_xscale('log')
    ax[1, 0].set_yscale('log')
    ax[1, 0].text(100, 2, "slope = " + str("{:.3f}".format(H_194)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})

    ax[1, 1].plot(data_195[0], c_195 * data_195[0] ** H_195, color="deepskyblue")
    ax[1, 1].scatter(data_195[0], data_195[1], color="purple")
    ax[1, 1].set_xscale('log')
    ax[1, 1].set_yscale('log')
    ax[1, 1].text(100, 2, "slope = " + str("{:.3f}".format(H_195)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})

    plt.show()


if __name__ == '__main__':
    with open('report_bicg.tx', 'r') as file:
        reader = file.readlines()
    lined_list = []
    out = {
        192: {},
        193: {},
        194: {},
        195: {}
    }
    packet = {}

    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    for i in range(len(lined_list)):  # packet based classification
        if chip_select(int(lined_list[i][1].split(": ")[1])) != chip_select(int(lined_list[i][2].split(": ")[1])):
            if int(lined_list[i][3].split(": ")[1]) in packet.keys():
                if lined_list[i] not in packet[int(lined_list[i][3].split(": ")[1])]:
                    packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
            else:
                packet.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])

    for i in packet.keys():
        for j in range(len(packet[i])):
            if packet[i][j][0] == "injection buffer":
                if int(packet[i][j][5].split(": ")[1]) not in out[int(packet[i][j][1].split(": ")[1])].keys():
                    out[int(packet[i][j][1].split(": ")[1])][int(packet[i][j][5].split(": ")[1])] = int(packet[i][j][7].split(": ")[1])
                else:
                    out[int(packet[i][j][1].split(": ")[1])][int(packet[i][j][5].split(": ")[1])] += int(packet[i][j][7].split(": ")[1])

    fig, ax = plt.subplots(2, 2, figsize=(18, 5))
    ax[0, 0].plot(list(out[192].keys()), list(out[192].values()), label="192", color="red")
    ax[0, 0].title.set_text("chip0")
    ax[0, 1].plot(list(out[193].keys()), list(out[193].values()), label="193", color="blue")
    ax[0, 1].title.set_text("chip1")
    ax[1, 0].plot(list(out[194].keys()), list(out[194].values()), label="194", color="yellow")
    ax[1, 0].title.set_text("chip2")
    ax[1, 1].plot(list(out[195].keys()), list(out[195].values()), label="195", color="green")
    ax[1, 1].title.set_text("chip3")
    plt.show()
    hurst(out)

