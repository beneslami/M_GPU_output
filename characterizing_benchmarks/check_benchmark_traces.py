import glob
import gc
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


def check_kernel_traces(path, suite, bench, topo, nv, ch):
    topol, NV, chipNum = determine_architecture(topo, nv, ch)
    file_name = path + suite + '-' + bench + "_NV" + str(NV) + '_1vc_' + str(chipNum) + 'ch_' + topol + "_trace*"
    if glob.glob(file_name):
        print(Fore.GREEN + suite + "-" + bench + "_" + topo + "_" + str(NV) + "_" + str(chipNum) + " [passed " + u'\u2713]' + Fore.WHITE)
    else:
        print(Fore.RED + suite + "-" + bench + "_" + topo + "_" + str(NV) + "_" + str(chipNum) + " [failed " + u'\u274c]' + Fore.WHITE)
    gc.enable()
    gc.collect()