import sys
import os

if __name__ == '__main__':
    input_ = sys.argv[1]
    real_path = os.path.dirname(os.path.realpath(input_))
    file2 = open(input_, "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    del (raw_content)
    injection = {}
    for i in range(len(lined_list)):
        if lined_list[i][0] == "request injected" or lined_list[i][0] == "reply injected":
            cycle = int(lined_list[i][5].split(": ")[1])
            byte = int(lined_list[i][7].split(": ")[1])
            chiplet = int(lined_list[i][6].split(": ")[1])
            if cycle not in injection.keys():
                injection.setdefault(cycle, {}).setdefault(chiplet, []).append(byte)
            else:
                if chiplet not in injection[cycle].keys():
                    injection[cycle].setdefault(chiplet, []).append(byte)
                else:
                    injection[cycle][chiplet].append(byte)
    m = min(list(injection.keys()))
    M = max(list(injection.keys()))
    for i in range(m, M, 1):
        if i not in injection.keys():
            injection[i] = 0

    injection = dict(sorted(injection.items(), key=lambda x: x[0]))