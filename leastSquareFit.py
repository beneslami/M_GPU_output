import numpy as np
import matplotlib.pyplot as plt
from stochastic.processes import *
from scipy.stats import *
import pandas as pd
from statsmodels.sandbox.distributions.extras import *


if __name__ == "__main__":
    input_ = "../benchmarks/spmv/mesh/NVLink1/4chiplet/data/burst_ratio.csv"
    df = pd.read_csv(input_)
    ratio = df['ratio']
    dist = {}
    for i in ratio:
        if i not in dist.keys():
            dist[i] = 1
        else:
            dist[i] += 1
    dist = dict(sorted(dist.items(), key=lambda x: x[0]))
    total = sum(dist.values())
    for ratio in dist.keys():
        dist[ratio] = dist[ratio] / total
    df = pd.DataFrame(ratio)




    x_peaks, _ = scipy.signal.find_peaks(list(df), height=0)
    print(x_peaks)

    y_peaks = []
    for x in x_peaks[0]:
        y_peaks.append(dist[x])
    plt.plot(dist.keys(), dist.values())
    plt.plot(list(x_peaks[0]), list(y_peaks), "x")
    plt.show()