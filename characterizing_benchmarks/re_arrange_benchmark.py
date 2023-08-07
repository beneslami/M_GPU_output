import gc
import os
import shutil
from colorama import Fore


def determine_architecture(topo, nv, ch):
    topol = ""
    chipNum = -1
    NV = -1
    if topo == "torus":
        topol = "2Dtorus"
    elif topo == "ring":
        topol = "ring"
    elif topo == "mesh":
        topol = "2Dmesh"
    elif topo == "fly":
        if ch == "4chiplet" or ch == "8chiplet":
            topol = "1fly"
        else:
            topol = "2fly"
    if ch == "4chiplet":
        chipNum = 4
    elif ch == "8chiplet":
        chipNum = 8
    elif ch == "16chiplet":
        chipNum = 16
    if nv == "NVLink4":
        NV = 4
    elif nv == "NVLink3":
        NV = 3
    elif nv == "NVLink2":
        NV = 2
    elif nv == "NVLink1":
        NV = 1
    return topol, NV, chipNum


def rearrange_traces(path, suite, bench, topo, NV, ch):
    topol, nv, chipNum = determine_architecture(topo, NV, ch)
    if not os.path.exists(path):
        print(Fore.YELLOW + "kernel directory does not exist" + Fore.WHITE)
        old_kernel_trace = ""
        ch_sub_path = os.path.dirname(path)
        for file in os.listdir(ch_sub_path):
            if file.__contains__("_trace.txt"):
                old_kernel_trace = ch_sub_path + file
                break
        assert os.path.exists(old_kernel_trace)
        new_kernel_trace = ch_sub_path + suite + '-' + bench + "_NV" + str(nv) + '_1vc_' + str(chipNum) + 'ch_' + topol + '_trace.txt'
        os.rename(old_kernel_trace, new_kernel_trace)
        print(Fore.GREEN + "trace file renaming done successfully" + Fore.WHITE)
        os.mkdir(ch_sub_path + "kernels")
        shutil.move(new_kernel_trace, ch_sub_path + "kernels/")
        print(Fore.GREEN + "moving trace file to kernel directory done successfully" + Fore.WHITE)
    else:
        print(Fore.GREEN + "kernel directory exists" + Fore.WHITE)
        new_kernel_trace = path + suite + "-" + bench + "_NV" + str(nv) + "_1vc_" + str(chipNum) + "ch_" + topol + "_trace_"
        for f in os.listdir(path):
            num = int(f.split(".")[0])
            os.rename(path + f, new_kernel_trace + str(num) + ".txt")
        print(Fore.GREEN + "trace file renaming done successfully" + Fore.WHITE)
    print(Fore.GREEN + "rearrange " + suite + "_" + bench + "_" + topo + "_" + NV + "_" + str(chipNum) + " [done " + u'\u2713]' + Fore.WHITE)

    gc.enable()
    gc.collect()