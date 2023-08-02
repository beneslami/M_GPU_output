import os
import sys
import pandas as pd
from matplotlib import pyplot as plt
import statsmodels.api as sm
import scipy.stats as stats

if __name__ == '__main__':
    real_injection = sys.argv[1]
    real_path = os.path.dirname(os.path.realpath(real_injection)) + "/injection.csv"
    df_real = pd.read_csv(real_path)['byte'].values
    synthetic_injection = sys.argv[2]
    synthetic_path = os.path.dirname(os.path.realpath(synthetic_injection)) + "/injection.csv"
    df_synthetic = pd.read_csv(synthetic_path)['byte'].values

    minimum = 0
    if len(df_real) < len(df_synthetic):
        minimum = len(df_real)
        df_synthetic = df_synthetic[0:minimum]
    else:
        minimum = len(df_synthetic)
        df_real = df_real[0: minimum]
    df_real.sort()
    df_synthetic.sort()

    plt.scatter(df_real, df_synthetic)
    plt.plot([min(df_real), max(df_real)], [min(df_real), max(df_real)], color="red")
    plt.title("QQ Plot")
    plt.xlabel("AccelSim quantiles")
    plt.ylabel("BookSim quantiles")
    plt.show()