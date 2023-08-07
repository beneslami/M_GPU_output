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
        'rodinia': ['backprop', 'bfs', 'b+tree', 'cfd', 'gaussian', 'heartwall', 'hotspot', 'hotspot3D',
                     'hybridsort', 'kmeans', 'lavaMD', 'lud', 'nn', 'particlefilter-float', 'pathfinder', 'srad',
                    'streamcluster'],
        'shoc': ['gemm'],
        'tango': ['AlexNet', 'ResNet', 'SqueezeNet']
    }
    topology = ['torus']#, 'ring', 'mesh', 'fly']
    NVLink = ['NVLink4']#, 'NVLink3', 'NVLink2', 'NVLink1']
    chiplet_num = ['4chiplet']#, '8chiplet', '16chiplet']

    path = "../benchmarks/"
    path += suits[2] + "/" + benchmarks[suits[2]][6] + "/" + topology[0] + "/" + NVLink[0] + "/" + chiplet_num[0] + "/kernels/"
    chip_num = int(chiplet_num[0][0])

    #rearrange_traces(suits, benchmarks, topology, NVLink, chiplet_num, path)
    #check_kernel_traces(suits, benchmarks, topology, NVLink, chiplet_num, path)

    for trace_file in os.listdir(path):
        if Path(trace_file).suffix == '.txt':
            print(trace_file)
            if os.path.getsize(path + trace_file) > 100000:
                start_processing_portal(path + trace_file, chip_num)
                #trace_generator(path + trace_file)

    gc.enable()
    gc.collect()