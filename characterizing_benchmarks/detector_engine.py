import os
import re
import gc
import numpy as np


def kernel_detection(input_):
    file_name = os.path.basename(input_).split("_")[0]
    traffic_type = {
        'homogeneous': ['parboil-spmv', 'parboil-mri-gridding', 'rodinia-b+tree', 'polybench-2DConvolution', 'tango-SqueezeNet',
                        'tango-ResNet', 'tango-AlexNet', 'shoc-gemm'],
        'spiky-sync': ['rodinia-lavaMD', 'polybench-2mm', 'polybench-3mm', 'polybench-bicg', 'polybench-correlation',
                       'polybench-covariance', 'parboil-sgemm'],
        'spiky-async': ['parboil-stencil', 'rodinia-hotspot3D', 'rodinia-kmeans', 'polybench-atax', 'polybench-gesummv',
                        'polybench-gemm']
    }

    for type, bench_list in traffic_type.items():
        if file_name in bench_list:
            return type
