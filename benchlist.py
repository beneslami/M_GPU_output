suits = ['SDK', 'deepbench', 'ispass-2009', 'pannotia', 'parboil', 'polybench', 'rodinia', 'shoc', 'tango']

benchmarks = {
    'SDK': ['conjugate-gradient', 'dct8x8', 'fdtd3d', 'hsoptical', 'matrixmul', 'nvjpeg'],
    'deepbench': ['gemm'],
    'ispass-2009': ['bfs', 'NQU', 'STO'],
    'pannotia': ['bc', 'color-max', 'color-maxmin', 'fw', 'fw-block', 'mis', 'pagerank', 'pagerank-spmv'],
    'parboil': ['bfs', 'cutcp', 'histo', 'mri-gridding', 'sgemm', 'spmv', 'stencil'],
    'polybench': ['2DConvolution', '2mm', '3mm', 'atax', 'bicg', 'correlation', 'covariance', 'fdtd2d', 'gemm', 'gesummv', 'mvt', 'syr2k', 'syrk'],
    'rodinia': ['b+tree', 'backprop', 'bfs', 'bt', 'cfd', 'gaussian', 'heartwall', 'hotspot', 'hotspot3D', 'huffman', 'hybridsort', 'kmeans', 'lavaMD', 'lud', 'nn', 'particlefilter-float', 'pathfinder', 'srad', 'streamcluster'],
    'shoc': ['FFT', 'Spmv', 'gemm', 'scan'],
    'tango': ['AlexNet', 'ResNet', 'SqueezeNet']
}

single_kernels = {
    'ispass-2009': ['STO'],
    'pannotia': ['color-max', 'color-maxmin', 'fw'],
    'parboil': ['cutcp', 'mri-gridding', 'sgemm', 'spmv'],
    'polybench': ['2DConvolution', '2mm', '3mm', 'gemm', 'syr2k', 'syrk'],
    'rodinia': ['b+tree', 'heartwall', 'hotspot', 'lavaMD', 'pathfinder', 'srad'],
    'SDK': ['fdtd3d', 'matrixmul'],
    'shoc': ['gemm'],
    'tango': ['AlexNet', 'ResNet', 'SqueezeNet']
}

multi_kernels = {
    'ispass-2009': ['bfs'],
    'pannotia': ['bc', 'fw-block', 'pagerank', 'pagerank-spmv'],
    'parboil': ['histo'],
    'polybench': [],
    'rodinia': ['backprop', 'bfs', 'cfd', 'gaussian', 'huffman', 'lud'],
    'SDK': ['conjugate-gradient', 'dct8x8', 'hspotical', 'nvjpeg'],
    'shoc': ['scan', 'Spmv'],
    'tango': []
}

nominated_benchmarks = {
    'SDK': ['conjugate-gradient', 'dct8x8', 'nvjpeg', 'hsoptical', 'matrixmul', 'fdtd3d'],
    'ispass-2009': ['bfs', 'STO'],
    'pannotia': ['bc', 'color-maxmin', 'fw', 'fw-block', 'pagerank', 'pagerank-spmv'],
    'parboil': ['cutcp', 'histo', 'mri-gridding', 'sgemm', 'spmv'],
    'polybench': ['2mm', '3mm', 'gemm', 'syr2k', 'syrk'],
    'rodinia': ['b+tree', 'backprop', 'bfs', 'bt', 'cfd', 'gaussian', 'heartwall', 'hotspot', 'huffman', 'lavaMD', 'lud', 'nn', 'pathfinder', 'srad'],
    'shoc': ['gemm'],
    'tango': ['AlexNet', 'ResNet', 'SqueezeNet']
}

topology = ['torus', 'ring', 'mesh', 'fly']
NVLink = ['NVLink4', 'NVLink3', 'NVLink2', 'NVLink1']
chiplet_num = ['4chiplet', '8chiplet', '16chiplet']



traffic_type = {
        'homogeneous': ['parboil-spmv', 'parboil-mri-gridding', 'rodinia-b+tree', 'polybench-2DConvolution', 'tango-SqueezeNet', 'tango-ResNet', 'tango-AlexNet', 'shoc-gemm', 'polybench-syr2k', 'polybench-syrk'],
        'spiky-sync': ['rodinia-lavaMD', 'polybench-2mm', 'polybench-3mm', 'polybench-bicg', 'parboil-sgemm', 'polybench-gemm', 'pannotia-fw'],
        'spiky-async': ['parboil-stencil', 'rodinia-hotspot3D', 'rodinia-kmeans', 'polybench-atax', 'polybench-gesummv', 'polybench-gemm']
}

bench_path = "/home/ben/Desktop/benchmarks/"



