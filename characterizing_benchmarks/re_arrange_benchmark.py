import gc
import os
import shutil
from colorama import Fore


def rearrange_traces(suits, benchmarks, topology, NVLink, chiplet_num, path):
    for suite in suits:
        suite_path = path + suite + "/"
        benchlists = benchmarks[suite]
        for bench in benchlists:
            bench_sub_path = suite_path + bench + "/"
            for topo in topology:
                topo_sub_path = bench_sub_path + topo + "/"
                for NV in NVLink:
                    NV_sub_path = topo_sub_path + NV + "/"
                    for chipNum in chiplet_num:
                        ch_sub_path = NV_sub_path + chipNum + "/"
                        if len(os.listdir(ch_sub_path)) != 0:
                            nv = ""
                            if NV == "NVLink4":
                                nv = "NV4"
                            elif NV == "NVLink3":
                                nv = "NV3"
                            elif NV == "NVLink2":
                                nv = "NV2"
                            elif NV == "NVLink1":
                                nv = "NV1"
                            ch = ""
                            if chipNum == "4chiplet":
                                ch = "4ch"
                            elif chipNum == "8chiplet":
                                ch = "8ch"
                            elif chipNum == "16chiplet":
                                ch = "16ch"
                            topol = ""
                            if topo == "torus":
                                topol = "2Dtorus"
                            elif topo == "mesh":
                                topol = "2Dmesh"
                            elif topo == "ring":
                                topol = "ring"
                            elif topo == "fly":
                                if chipNum == "4chiplet" or chipNum == "8chiplet":
                                    topol = "1fly"
                                else:
                                    topol = "2fly"
                            if not os.path.exists(ch_sub_path + "kernels/"):
                                print(Fore.YELLOW + "kernel directory does not exist" + Fore.WHITE)
                                old_kernel_trace = ""
                                for file in os.listdir(ch_sub_path):
                                    if file.__contains__("_trace.txt"):
                                        old_kernel_trace = ch_sub_path + file
                                        break
                                assert os.path.exists(old_kernel_trace)
                                new_kernel_trace = ch_sub_path + suite + '-' + bench + "_" + nv + '_1vc_' + ch + '_' + topol + '_trace.txt'
                                os.rename(old_kernel_trace, new_kernel_trace)
                                print(Fore.GREEN + "trace file renaming done successfully" + Fore.WHITE)
                                os.mkdir(ch_sub_path + "kernels")
                                shutil.move(new_kernel_trace, ch_sub_path + "kernels/")
                                print(Fore.GREEN + "moving trace file to kernel directory done successfully" + Fore.WHITE)
                            else:
                                sub_ch_kernel_trace = ch_sub_path + "kernels/"
                                print(Fore.GREEN + "kernel directory exists" + Fore.WHITE)
                                new_kernel_trace = sub_ch_kernel_trace + suite + '-' + bench + "_" + nv + '_1vc_' + ch + '_' + topol + '_trace_'
                                for f in os.listdir(sub_ch_kernel_trace):
                                    num = int(f.split(".")[0])
                                    os.rename(sub_ch_kernel_trace + f, new_kernel_trace + str(num) + ".txt")
                                print(Fore.GREEN + "trace file renaming done successfully" + Fore.WHITE)
                            print(Fore.GREEN + "rearrange " + suite + "_" + bench + "_" + topo + "_" + NV + "_" + chipNum + " [done " + u'\u2713]' + Fore.WHITE)
                        else:
                            print(ch_sub_path + " is empty")
    gc.enable()
    gc.collect()