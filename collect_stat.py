import os.path
import matplotlib.pyplot as plt
import pandas as pd

if __name__ == "__main__":
    benchmark = "gemm"
    suite = "shoc"
    base_path = "../benchmarks/" + benchmark + "/"
    #base_path = "../benchmarks/" + "shoc-gemm" + "/"
    topolist = ['fly', 'mesh', 'ring', 'torus']
    chiplet_num = [4, 8, 16]
    ipc_over_nvlink = {}
    throughput_over_nvlink = {}
    for topo in topolist:
        second_path = base_path + topo + "/"
        if topo == "mesh" or topo == "torus":
            topoName = "2D" + topo
        elif topo == "ring":
            topoName = topo
        for i in range(1, 5):
            third_path = second_path + "NVLink" + str(i) + "/"
            for c in chiplet_num:
                if topo == "fly":
                    if c == 4 or c == 8:
                        topoName = "1fly"
                    else:
                        topoName = "2fly"
                forth_path = third_path + str(c) + "chiplet/"
                file_name = forth_path + suite + "-" + benchmark + "_NV" + str(i) + "_1vc_" + str(c) +"ch_" + topoName + ".txt"
                #file_name = forth_path + "shoc-GEMM" + "_NV" + str(i) + "_1vc_" + str(c) + "ch_" + topoName + ".txt"
                print(file_name)
                if os.path.exists(file_name):
                    with open(file_name, "r") as file:
                        for lines in file.readlines():
                            if lines.__contains__("gpu_tot_ipc"):
                                ipc = float(lines.split("=")[1].split("\n")[0])
                                link_type = "NVLink" + str(i)
                                if link_type not in ipc_over_nvlink.keys():
                                    ipc_over_nvlink.setdefault(link_type, {})[topo] = ipc
                                else:
                                    ipc_over_nvlink[link_type][topo] = ipc
                            elif lines.__contains__("gpu_tot_throughput"):
                                throughput = float(lines.split("=")[1].split("\n")[0])
                                link_type = "NVLink" + str(i)
                                freq = 1.132
                                if link_type not in throughput_over_nvlink.keys():
                                    throughput_over_nvlink.setdefault(link_type, {})[topo] = throughput*freq
                                else:
                                    throughput_over_nvlink[link_type][topo] = throughput*freq
                else:
                    file_name = forth_path + benchmark + "-" + suite + "_NV" + str(i) + "_1vc_" + str(
                        c) + "ch_" + topoName + ".txt"
                    if os.path.exists(file_name):
                        with open(file_name, "r") as file:
                            for lines in file.readlines():
                                if lines.__contains__("gpu_tot_ipc"):
                                    ipc = float(lines.split("=")[1].split("\n")[0])
                                    link_type = "NVLink" + str(i)
                                    if link_type not in ipc_over_nvlink.keys():
                                        ipc_over_nvlink.setdefault(link_type, {})[topo] = ipc
                                    else:
                                        ipc_over_nvlink[link_type][topo] = ipc
                                elif lines.__contains__("gpu_tot_throughput"):
                                    throughput = float(lines.split("=")[1].split("\n")[0])
                                    link_type = "NVLink" + str(i)
                                    freq = 1.132
                                    if link_type not in throughput_over_nvlink.keys():
                                        throughput_over_nvlink.setdefault(link_type, {})[topo] = throughput*freq
                                    else:
                                        throughput_over_nvlink[link_type][topo] = throughput*freq

    x_axis = list(ipc_over_nvlink.keys())
    for tp in topolist:
        temp = []
        for link in x_axis:
            temp.append(ipc_over_nvlink[link][tp])
        plt.plot(x_axis, temp, label=tp, marker="*")
    plt.xlabel("Link technology")
    plt.ylabel("average IPC")
    plt.legend()
    plt.savefig(base_path + "/4ch_ipc.jpg")
    plt.close()
    df = pd.DataFrame(ipc_over_nvlink)
    df.to_csv(base_path + "/4ch_ipc.csv", index=True)

    x_axis = list(throughput_over_nvlink.keys())
    for tp in topolist:
        temp = []
        for link in x_axis:
            temp.append(throughput_over_nvlink[link][tp])
        plt.plot(x_axis, temp, label=tp, marker="*")
    plt.xlabel("Link technology")
    plt.ylabel("average throughput (GB/s/chiplet)")
    plt.legend()
    plt.savefig(base_path + "/4ch_throughput.jpg")
    plt.close()
    df = pd.DataFrame(throughput_over_nvlink)
    df.to_csv(base_path + "/4ch_throughput.csv", index=True)