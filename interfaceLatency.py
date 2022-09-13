if __name__ == '__main__':
    input_ = sys.argv[1]
    file2 = open(input_, "r")
    raw_content = ""
    if file2.mode == "r":
        raw_content = file2.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]

        lined_list.append(item)
    del (raw_content)
    packet = {}
    packet_ = {}
    flag = 0
    for i in range(len(lined_list)):
        if check_local_or_remote(lined_list[i]):
            if int(lined_list[i][3].split(": ")[1]) in packet_.keys():
                for j in range(len(packet_[int(lined_list[i][3].split(": ")[1])])):
                    if lined_list[i][0] == packet_[int(lined_list[i][3].split(": ")[1])][j][0] and lined_list[i][0] != "FW push" and lined_list[i][0] != "FW pop":
                        flag = 1
                        break
                if flag == 0:
                    packet_.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])
                else:
                    flag = 0
            else:
                packet_.setdefault(int(lined_list[i][3].split(": ")[1]), []).append(lined_list[i])

    for i in packet_.keys():
        length = len(packet_[i])
        if packet_[i][0][0] == "injection buffer" and packet_[i][length - 1][0] == "SM pop":
            packet[i] = packet_[i]
        else:
            pass

    arr = {}
    text = ""
    delay_file = open("inj_icnt.txt", "r")
    text = delay_file.readlines()
    for line in text:
        items = line.split("\t")
        arr[int(items[0])] = int(items[1])
    for i in packet.keys():
        flag = 0
        t0 = t1 = 0
        for j in range(len(packet[i])):
            if packet[i][j][0] == "injection buffer" and flag == 0:
                flag = 1
                t0 = int(packet[i][j][8].split(": ")[1])
            if packet[i][j][0] == "icnt_llc_push" and flag == 1:
                flag = 0
                t1 = int(packet[i][j][8].split(": ")[1])
                if (t1 - t0) not in arr.keys():
                    arr[t1 - t0] = 1
                else:
                    arr[t1 - t0] += 1
                break
    arr = dict(sorted(arr.items(), key=lambda x: x[0]))
    with open("inj_icnt.txt", "w") as file:
        for key, value in arr.items():
            file.write(str(key) + "\t" + str(value) + "\n")
    #########################################################
    arr.clear()
    text = ""
    delay_file = open("inj_fw.txt", "r")
    text = delay_file.readlines()
    for line in text:
        items = line.split("\t")
        arr[int(items[0])] = int(items[1])
    for i in packet.keys():
        flag = 0
        t0 = t1 = 0
        for j in range(len(packet[i])):
            if packet[i][j][0] == "injection buffer" and flag == 0:
                flag = 1
                t0 = int(packet[i][j][8].split(": ")[1])
            if packet[i][j][0] == "FW push" and flag == 1:
                flag = 0
                t1 = int(packet[i][j][8].split(": ")[1])
                if (t1 - t0) not in arr.keys():
                    arr[t1 - t0] = 1
                else:
                    arr[t1 - t0] += 1
                break
    arr = dict(sorted(arr.items(), key=lambda x: x[0]))
    with open("inj_fw.txt", "w") as file:
        for key, value in arr.items():
            file.write(str(key) + "\t" + str(value) + "\n")
    #########################################################
    arr.clear()
    text = ""
    delay_file = open("fw_icnt_llc.txt", "r")
    text = delay_file.readlines()
    for line in text:
        items = line.split("\t")
        arr[int(items[0])] = int(items[1])
    for i in packet.keys():
        flag = 0
        t0 = t1 = 0
        for j in range(len(packet[i])):
            if packet[i][j][0] == "FW pop" and flag == 0:
                flag = 1
                t0 = int(packet[i][j][8].split(": ")[1])
            if packet[i][j][0] == "icnt_llc_push" and flag == 1:
                flag = 0
                t1 = int(packet[i][j][8].split(": ")[1])
                if (t1 - t0) not in arr.keys():
                    arr[t1 - t0] = 1
                else:
                    arr[t1 - t0] += 1
                break
    arr = dict(sorted(arr.items(), key=lambda x: x[0]))
    with open("fw_icnt_llc.txt", "w") as file:
        for key, value in arr.items():
            file.write(str(key) + "\t" + str(value) + "\n")
    #########################################################
    arr.clear()
    text = ""
    delay_file = open("icnt_llc_rop.txt", "r")
    text = delay_file.readlines()
    for line in text:
        items = line.split("\t")
        arr[int(items[0])] = int(items[1])
    for i in packet.keys():
        flag = 0
        t0 = t1 = 0
        for j in range(len(packet[i])):
            if packet[i][j][0] == "icnt_llc_push" and flag == 0:
                flag = 1
                t0 = int(packet[i][j][8].split(": ")[1])
            if packet[i][j][0] == "rop push" and flag == 1:
                flag = 0
                t1 = int(packet[i][j][8].split(": ")[1])
                if (t1 - t0) not in arr.keys():
                    arr[t1 - t0] = 1
                else:
                    arr[t1 - t0] += 1
                break
    arr = dict(sorted(arr.items(), key=lambda x: x[0]))
    with open("icnt_llc_rop.txt", "w") as file:
        for key, value in arr.items():
            file.write(str(key) + "\t" + str(value) + "\n")
    #########################################################
    arr.clear()
    text = ""
    delay_file = open("l2_icnt.txt", "r")
    text = delay_file.readlines()
    for line in text:
        items = line.split("\t")
        arr[int(items[0])] = int(items[1])
    for i in packet.keys():
        flag = 0
        t0 = t1 = 0
        for j in range(len(packet[i])):
            if packet[i][j][0] == "L2_icnt_push" and flag == 0:
                flag = 1
                t0 = int(packet[i][j][8].split(": ")[1])
            if packet[i][j][0] == "L2_icnt_pop" and flag == 1:
                flag = 0
                t1 = int(packet[i][j][8].split(": ")[1])
                if (t1 - t0) not in arr.keys():
                    arr[t1 - t0] = 1
                else:
                    arr[t1 - t0] += 1
                break
    arr = dict(sorted(arr.items(), key=lambda x: x[0]))
    with open("l2_icnt.txt", "w") as file:
        for key, value in arr.items():
            file.write(str(key) + "\t" + str(value) + "\n")
    #########################################################
    arr.clear()
    text = ""
    delay_file = open("l2_icnt_sm.txt", "r")
    text = delay_file.readlines()
    for line in text:
        items = line.split("\t")
        arr[int(items[0])] = int(items[1])
    for i in packet.keys():
        flag = 0
        t0 = t1 = 0
        for j in range(len(packet[i])):
            if packet[i][j][0] == "L2_icnt_pop" and flag == 0:
                flag = 1
                t0 = int(packet[i][j][8].split(": ")[1])
            if packet[i][j][0] == "SM push" and flag == 1:
                flag = 0
                t1 = int(packet[i][j][8].split(": ")[1])
                if (t1 - t0) not in arr.keys():
                    arr[t1 - t0] = 1
                else:
                    arr[t1 - t0] += 1
                break
    arr = dict(sorted(arr.items(), key=lambda x: x[0]))
    with open("l2_icnt_sm.txt", "w") as file:
        for key, value in arr.items():
            file.write(str(key) + "\t" + str(value) + "\n")
    #########################################################
    arr.clear()
    text = ""
    delay_file = open("l2_icnt_fw.txt", "r")
    text = delay_file.readlines()
    for line in text:
        items = line.split("\t")
        arr[int(items[0])] = int(items[1])
    for i in packet.keys():
        flag = 0
        t0 = t1 = 0
        for j in range(len(packet[i])):
            if packet[i][j][0] == "L2_icnt_pop" and flag == 0:
                flag = 1
                t0 = int(packet[i][j][8].split(": ")[1])
            if packet[i][j][0] == "FW push" and flag == 1:
                flag = 0
                t1 = int(packet[i][j][8].split(": ")[1])
                if (t1 - t0) not in arr.keys():
                    arr[t1 - t0] = 1
                else:
                    arr[t1 - t0] += 1
                break
    arr = dict(sorted(arr.items(), key=lambda x: x[0]))
    with open("l2_icnt_fw.txt", "w") as file:
        for key, value in arr.items():
            file.write(str(key) + "\t" + str(value) + "\n")
    #########################################################
    arr.clear()
    text = ""
    delay_file = open("fw_sm.txt", "r")
    text = delay_file.readlines()
    for line in text:
        items = line.split("\t")
        arr[int(items[0])] = int(items[1])
    for i in packet.keys():
        flag = 0
        t0 = t1 = 0
        for j in range(len(packet[i])):
            if packet[i][j][0] == "FW pop" and flag == 0 and (int(packet[i][j][4].split(": ")[1]) == 2 or int(packet[i][j][4].split(": ")[1]) == 3):
                flag = 1
                t0 = int(packet[i][j][8].split(": ")[1])
            if packet[i][j][0] == "SM push" and flag == 1:
                flag = 0
                t1 = int(packet[i][j][8].split(": ")[1])
                if (t1 - t0) not in arr.keys():
                    arr[t1 - t0] = 1
                else:
                    arr[t1 - t0] += 1
                break
    arr = dict(sorted(arr.items(), key=lambda x: x[0]))
    with open("fw_sm.txt", "w") as file:
        for key, value in arr.items():
            file.write(str(key) + "\t" + str(value) + "\n")
    #########################################################
    arr.clear()
    text = ""
    delay_file = open("sm.txt", "r")
    text = delay_file.readlines()
    for line in text:
        items = line.split("\t")
        arr[int(items[0])] = int(items[1])
    for i in packet.keys():
        flag = 0
        t0 = t1 = 0
        for j in range(len(packet[i])):
            if packet[i][j][0] == "SM push" and flag == 0:
                flag = 1
                t0 = int(packet[i][j][8].split(": ")[1])
            if packet[i][j][0] == "SM pop" and flag == 1:
                flag = 0
                t1 = int(packet[i][j][8].split(": ")[1])
                if (t1 - t0) not in arr.keys():
                    arr[t1 - t0] = 1
                else:
                    arr[t1 - t0] += 1
                break
    arr = dict(sorted(arr.items(), key=lambda x: x[0]))
    with open("sm.txt", "w") as file:
        for key, value in arr.items():
            file.write(str(key) + "\t" + str(value) + "\n")
    #########################################################