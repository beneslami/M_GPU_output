import glob
import os
import shutil


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
                            print("passed")
                        else:
                            print(file_name)


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
                                old_kernel_trace = ""
                                for file in os.listdir(ch_sub_path):
                                    if file.__contains__("_trace.txt"):
                                        old_kernel_trace = ch_sub_path + file
                                        break
                                assert os.path.exists(old_kernel_trace)
                                new_kernel_trace = ch_sub_path + suite + '-' + bench + "_" + nv + '_1vc_' + ch + '_' + topol + '_trace.txt'
                                os.rename(old_kernel_trace, new_kernel_trace)
                                os.mkdir(ch_sub_path + "kernels")
                                shutil.move(new_kernel_trace, ch_sub_path + "kernels/")
                            else:
                                sub_ch_kernel_trace = ch_sub_path + "kernels/"
                                new_kernel_trace = sub_ch_kernel_trace + suite + '-' + bench + "_" + nv + '_1vc_' + ch + '_' + topol + '_trace_'
                                for f in os.listdir(sub_ch_kernel_trace):
                                    num = int(f.split(".")[0])
                                    os.rename(sub_ch_kernel_trace + f, new_kernel_trace + str(num) + ".txt")
                        else:
                            print(ch_sub_path + " is empty")


if __name__ == "__main__":
    suits = ['ispass-2009', 'pannotia', 'parboil', 'polybench', 'rodinia', 'shoc', 'tango']
    benchmarks = {
        'ispass-2009': ['NQU', 'STO', 'bfs'],
        'pannotia': ['color-max', 'fw'],
        'parboil': ['bfs', 'cutcp', 'histo', 'mri-gridding', 'sgemm', 'spmv', 'stencil'],
        'polybench': ['2DConvolution', '2mm', '3mm', 'atax', 'bicg', 'correlation', 'covariance', 'fdtd2d', 'gemm',
                      'gesummv', 'mvt', 'syr2k', 'syrk'],
        'rodinia': ['backprop', 'bfs', 'b+tree', 'cfd', 'gaussian', 'heartwall', 'hotspot', 'hotspot3D',
                     'hybridsort', 'kmeans', 'lavaMD', 'lud', 'nn', 'particlefilter-float', 'pathfinder', 'srad',
                    'streamcluster'],
        'shoc': ['gemm'],
        'tango': ['AlexNet', 'ResNet', 'SqueezeNet']
    }
    topology = ['torus', 'ring', 'mesh', 'fly']
    NVLink = ['NVLink1', 'NVLink2', 'NVLink3', 'NVLink4']
    chiplet_num = ['4chiplet']#, '8chiplet', '16chiplet']

    path = "/media/ben/BEN/benchmarks/"

    check_kernel_traces(suits, benchmarks, topology, NVLink, chiplet_num, path)
    #rearrange_traces(suits, benchmarks, topology, NVLink, chiplet_num, path)