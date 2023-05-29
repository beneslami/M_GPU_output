import sys
import os
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import ks_2samp

if __name__ == '__main__':
    real_injection = sys.argv[1]
    real_path = os.path.dirname(os.path.realpath(real_injection)) + "/injection.csv"
    df_real = pd.read_csv(real_path)['byte'].values
    synthetic_injection = sys.argv[2]
    synthetic_path = os.path.dirname(os.path.realpath(synthetic_injection)) + "/injection.csv"
    df_synthetic = pd.read_csv(synthetic_path)['byte'].values
    stat, p = ks_2samp(df_real, df_synthetic)
    count, bins_count = np.histogram(df_real, bins=len(df_real))
    pdf = count / sum(count)
    cdf = np.cumsum(pdf)
    plt.plot(bins_count[1:], cdf, label="CDF_AccelSim", linestyle="-", marker="o")
    count, bins_count = np.histogram(df_synthetic, bins=len(df_synthetic))
    pdf = count / sum(count)
    cdf = np.cumsum(pdf)
    plt.plot(bins_count[1:], cdf, label="CDF_BookSim", linestyle="-", marker="o")
    plt.title("CDF with respect to request and response")
    plt.text(np.mean(bins_count), np.mean(cdf)/2, "p-value = " + str("{:.5f}".format(p)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    plt.legend()
    plt.show()