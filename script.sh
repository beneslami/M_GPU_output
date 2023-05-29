#!/bin/bash
BENCHMARK="b+tree-rodinia-3.1"
BENCH_NAME="b+tree"
TOPO="torus"
NVLINK="3"
CHIPLET="4"
if [ $TOPO = "torus" ]; then
  TOPOLOGY="2Dtorus"
elif [ $TOPO = "mesh" ]; then
  TOPOLOGY="2Dmesh"
elif [ $TOPO = "fly" ]; then
  if [ $CHIPLET = "4" ]; then
    TOPOLOGY="1fly"
  elif [ $CHIPLET = "8" ]; then
    TOPOLOGY="1fly"
  elif [ $CHIPLET = "16" ]; then
    TOPOLOGY="2fly"
  fi
else
    TOPOLOGY=$TOPO
fi

#real_traffic="../benchmarks/output.txt"
real_traffic="../benchmarks/${BENCH_NAME}/${TOPO}/NVLink${NVLINK}/${CHIPLET}chiplet/${BENCHMARK}_NV${NVLINK}_1vc_${CHIPLET}ch_${TOPOLOGY}_trace.txt"
synthetic_traffic=../accelsim-chiplet/test/output.txt #../b_ooksim2/src/examples/out.txt
echo $real_traffic

#python3 modeling.py "$real_traffic"

python3 processing.py "$real_traffic"
#python3 pre_traffic_distribution.py "$real_traffic"
#python3 pre_traffic_distribution.py "$synthetic_traffic"

#python3 pre_traffic_trace_categorizing.py "$real_traffic"
#python3 pre_traffic_trace_categorizing.py "$synthetic_traffic"

#python3 check_random_process.py "$real_traffic"
#python3 spatialLocality.py "$real_traffic"
#python3 generate_injection_csv.py "$real_traffic"
#python3 generate_injection_csv.py "$synthetic_traffic"
#python3 kolmogorov_smirnov.py "$real_traffic" "$synthetic_traffic"

#python3 QQplot.py "$real_traffic" "$synthetic_traffic"
