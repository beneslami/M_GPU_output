import glob
import gc
from colorama import Fore


def check_kernel_traces(suits, benchmarks, topology, NVLink, chiplet_num, path):
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
                        nv = ""
                        if NV =="NVLink4":
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
                        file_name = ch_sub_path + "kernels/" + suite + '-' + bench + "_" + nv + '_1vc_' + ch + '_' + topol + '_trace*'
                        if glob.glob(file_name):
                            print(Fore.GREEN + suite + "_" + bench + "_" + topo + "_" + NV + "_" + chipNum + " [passed " + u'\u2713]' + Fore.WHITE)
                        else:
                            print(Fore.RED + suite + "_" + bench + "_" + topo + "_" + NV + "_" + chipNum + " [failed " + u'\u274c]' + Fore.WHITE)
    gc.enable()
    gc.collect()