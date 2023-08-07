import gc
import os
from pathlib import Path
from check_benchmark_traces import *
from re_arrange_benchmark import *
from processing import *
from trace_generator import *


if __name__ == "__main__":
    suits = ['ispass-2009', 'pannotia', 'parboil', 'polybench', 'rodinia', 'shoc', 'tango']
    benchmarks = {
        'ispass-2009': ['bfs', 'NQU', 'STO'],
        'pannotia': ['color-max', 'fw'],
        'parboil': ['bfs', 'cutcp', 'histo', 'mri-gridding', 'sgemm', 'spmv', 'stencil'],
        'polybench': ['2DConvolution', '2mm', '3mm', 'atax', 'bicg', 'correlation', 'covariance', 'fdtd2d', 'gemm',
                      'gesummv', 'mvt', 'syr2k', 'syrk'],
        'rodinia': ['backprop', 'bfs', 'b+tree', 'cfd', 'gaussian', 'heartwall', 'hotspot', 'hotspot3D', 'huffman',
                     'hybridsort', 'kmeans', 'lavaMD', 'lud', 'nn', 'particlefilter-float', 'pathfinder', 'srad',
                    'streamcluster'],
        'shoc': ['fft', 'gemm', 'scan', 'Spmv'],
        'tango': ['AlexNet', 'ResNet', 'SqueezeNet']
    }
    topology = ['torus', 'ring', 'mesh', 'fly']
    NVLink = ['NVLink4', 'NVLink3', 'NVLink2', 'NVLink1']
    chiplet_num = ['4chiplet', '8chiplet', '16chiplet']

    path = "/home/ben/Desktop/benchmarks/"
    for suite in suits:
        if suite == "rodinia":
            for bench in benchmarks[suite]:
                if bench == "huffman":
                    for topo in topology:
                        for nv in NVLink:
                            for ch in chiplet_num:
                                sub_path = path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/kernels/"
                                if len(os.listdir(os.path.dirname(os.path.dirname(sub_path)))) != 0:
                                    rearrange_traces(sub_path, suite, bench, topo, nv, ch)
                                    check_kernel_traces(sub_path, suite, bench, topo, nv, ch)
                                    chip_num = int(ch[0])
                                    for trace_file in os.listdir(sub_path):
                                        if Path(trace_file).suffix == '.txt':
                                            if os.path.getsize(sub_path + trace_file) > 100000:
                                                start_processing_portal(sub_path + trace_file, chip_num)
                                                trace_generator(sub_path + trace_file)
                                else:
                                    print(Fore.YELLOW + "directory " + sub_path + " is empty" + Fore.WHITE)

    gc.enable()
    gc.collect()