import matplotlib.pyplot as plt

chiplet = []
chiplet_0 = dict(
    SM_ID=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
           28, 29, 30, 31],
    LLC_ID=[128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143], port=192)
link_01 = 0
chiplet_1 = dict(
    SM_ID=[32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58,
           59, 60, 61, 62, 63],
    LLC_ID=[144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159], port=193)
link_12 = 0
chiplet_2 = dict(
    SM_ID=[64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
           91, 92, 93, 94],
    LLC_ID=[160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174], port=194)
link_23 = 0
chiplet_3 = dict(
    SM_ID=[96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117,
           118, 119, 120, 121, 122, 123, 124, 125, 126, 127],
    LLC_ID=[176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191], port=195)
link_30 = 0
chiplet.append(chiplet_0)
chiplet.append(chiplet_1)
chiplet.append(chiplet_2)
chiplet.append(chiplet_3)


def check_local_or_remote(x):  # 0 for local, 1 for remote
    for i in range(len(chiplet)):
        if int(x[5].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[5].split(": ")[1]) in chiplet[i]["LLC_ID"]:
            if int(x[6].split(": ")[1]) in chiplet[i]["SM_ID"] or int(x[6].split(": ")[1]) in chiplet[i]["LLC_ID"]:
                return 0
        return 1


def chip_select(x):
    if x == 192:
        return 0
    elif x == 193:
        return 1
    elif x == 194:
        return 2
    elif x == 195:
        return 3


if __name__ == '__main__':
    file = open("queue.txt", "r")
    file2 = open("q.csv", "w")
    raw_content = ""
    if file.mode == "r":
        raw_content = file.readlines()
    lined_list = []
    for line in raw_content:
        item = [x for x in line.split("\t") if x not in ['', '\t']]
        lined_list.append(item)
    vc = {}
    # lined_list[0].split(": ")[0] push/pop
    # lined_list[0].split(": ")[1] vc
    # lined_list[1].split(": ")[1] cycle
    # lined_list[2].split(": ")[1] packet_num
    # lined_list[3].split(": ")[1] queue_size
    # lined_list[4].split(": ")[1] type
    # lined_list[5].split(": ")[1] size
    # lined_list[6].split(": ")[1] src
    # lined_list[7].split(": ")[1] dst
    # lined_list[8].split(": ")[1] chiplet

    chip = {
        0: {
            "input_queue": {
                "push": {

                },
                "pop": {

                }
            },
            "ejection_buffer": {
                "push": {
                    1: {

                    },
                    2: {

                    },
                    3: {

                    }
                },
                "pop": {
                    1: {

                    },
                    2: {

                    },
                    3: {

                    }
                }
            },
            "boundary_buffer": {
                "push": {
                    0: {

                    },
                    1: {

                    },
                    2: {

                    },
                    3: {

                    },
                    14: {

                    },
                    15: {

                    }
                },
                "pop": {
                    0: {

                    },
                    1: {

                    },
                    2: {

                    },
                    3: {

                    },
                    14: {

                    },
                    15: {

                    }
                }
            }
        },
        1: {
            "input_queue": {
                "push": {

                },
                "pop": {

                }
            },
            "ejection_buffer": {
                "push": {
                    1: {

                    },
                    2: {

                    },
                    3: {

                    }
                },
                "pop": {
                    1: {

                    },
                    2: {

                    },
                    3: {

                    }
                }
            },
            "boundary_buffer": {
                "push": {
                    0: {

                    },
                    1: {

                    },
                    2: {

                    },
                    3: {

                    },
                    14: {

                    },
                    15: {

                    }
                },
                "pop": {
                    0: {

                    },
                    1: {

                    },
                    2: {

                    },
                    3: {

                    },
                    14: {

                    },
                    15: {

                    }
                }
            }
        },
        2: {
            "input_queue": {
                "push": {

                },
                "pop": {

                }
            },
            "ejection_buffer": {
                "push": {
                    1: {

                    },
                    2: {

                    },
                    3: {

                    }
                },
                "pop": {
                    1: {

                    },
                    2: {

                    },
                    3: {

                    }
                }
            },
            "boundary_buffer": {
                "push": {
                    0: {

                    },
                    1: {

                    },
                    2: {

                    },
                    3: {

                    },
                    14: {

                    },
                    15: {

                    }
                },
                "pop": {
                    0: {

                    },
                    1: {

                    },
                    2: {

                    },
                    3: {

                    },
                    14: {

                    },
                    15: {

                    }
                }
            }
        },
        3: {
            "input_queue": {
                "push": {

                },
                "pop": {

                }
            },
            "ejection_buffer": {
                "push": {
                    0: {

                    },
                    1: {

                    },
                    2: {

                    },
                    3: {

                    },
                    14: {

                    },
                    15: {

                    }
                },
                "pop": {
                    1: {

                    },
                    2: {

                    },
                    3: {

                    },
                    15: {

                    }
                }
            },
            "boundary_buffer": {
                "push": {
                    1: {

                    },
                    2: {

                    },
                    3: {

                    }
                },
                "pop": {
                    0: {

                    },
                    1: {

                    },
                    2: {

                    },
                    3: {

                    },
                    14: {

                    },
                    15: {

                    }
                }
            }
        }
    }
    for i in range(len(lined_list)):
        if check_local_or_remote(lined_list[i]):
            file2.write(str(lined_list[i]))
            file2.write("\n")
            if lined_list[i][0].split(": ")[0] == "push_input_queue":
                chip[int(lined_list[i][8].split(": ")[1])]["input_queue"]["push"].setdefault(int(lined_list[i][2].split(": ")[1]), []).append(int(lined_list[i][1].split(": ")[1]))
            elif lined_list[i][0].split(": ")[0] == "pop_input_queue":
                chip[int(lined_list[i][8].split(": ")[1])]["input_queue"]["pop"].setdefault(int(lined_list[i][2].split(": ")[1]), []).append(int(lined_list[i][1].split(": ")[1]))
            elif lined_list[i][0].split(": ")[0] == "push_ejection_buffer":
                chip[int(lined_list[i][7].split(": ")[1])]["ejection_buffer"]["push"][int(lined_list[i][0].split(": ")[1])].setdefault(int(lined_list[i][2].split(": ")[1]), []).append(int(lined_list[i][1].split(": ")[1]))
            elif lined_list[i][0].split(": ")[0] == "pop_ejection_buffer":
                chip[int(lined_list[i][7].split(": ")[1])]["ejection_buffer"]["pop"][int(lined_list[i][0].split(": ")[1])].setdefault(int(lined_list[i][2].split(": ")[1]), []).append(int(lined_list[i][1].split(": ")[1]))
            elif lined_list[i][0].split(": ")[0] == "push_boundary_buffer":
                chip[int(lined_list[i][7].split(": ")[1])]["boundary_buffer"]["push"][int(lined_list[i][0].split(": ")[1])].setdefault(int(lined_list[i][2].split(": ")[1]), []).append(int(lined_list[i][1].split(": ")[1]))
            elif lined_list[i][0].split(": ")[0] == "pop_boundary_buffer":
                chip[int(lined_list[i][7].split(": ")[1])]["boundary_buffer"]["pop"][int(lined_list[i][0].split(": ")[1])].setdefault(int(lined_list[i][2].split(": ")[1]), []).append(int(lined_list[i][1].split(": ")[1]))

    """""
    waiting_time = {}
    chip_num = 1
    queue_num = "boundary_buffer"
    vc_num = 15
    for i in chip[chip_num][queue_num]["push"][vc_num].keys():
        for j in chip[chip_num][queue_num]["pop"][vc_num].keys():
            if i == j:
                waiting_time[i] = chip[chip_num][queue_num]["pop"][vc_num][j][0] - chip[chip_num][queue_num]["push"][vc_num][i][0]
                break
    
    waiting_time = {}
    x1 = x2 = 0
    push = chip[1]["input_queue"]["push"]
    pop = chip[1]["input_queue"]["pop"]

    for i in push.keys():
        waiting_time[i] = pop[i][0] - push[i][0]

    plt.bar(list(waiting_time.keys()), list(waiting_time.values()), width=20)
    plt.xlabel("packet ID")
    plt.ylabel("Waiting Time")
    plt.title("packet waiting time in ejection_buffer of chiplet 1")
    plt.show()
    """""
