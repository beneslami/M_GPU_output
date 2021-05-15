import math


def RS(lined_list):
    time_byte = {}
    windows = {}
    duration = 200000
    M = math.log(duration, 2)
    for i in range(1, len(lined_list)):
        if int(lined_list[i][0].split(",")[0]) in time_byte.keys():
            time_byte[int(lined_list[i][0].split(",")[0])] += int(lined_list[i][0].split(",")[1])
        else:
            time_byte[int(lined_list[i][0].split(",")[0])] = int(lined_list[i][0].split(",")[1])
    j = 1
    for wnd in range(1, int(M)):
        for key, value in time_byte.items():
            if key < j * int(duration / wnd):
                if wnd in windows.keys():
                    if j in windows[wnd].keys():
                        windows[wnd].setdefault(j, []).append(value)
                else:
                    windows.setdefault(wnd, {}).setdefault(j, []).append(value)
            else:
                j += 1

    for key, v in windows.items():
       for values in v.keys():
           print(values)
       print("-------")


if __name__ == "__main__":
    with open(' nn_ispass.csv', 'r') as file:
        reader = file.readlines()
    lined_list = []
    for line in reader:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)

    RS(lined_list)