import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":
    benchMarksNames = ['AsyncAPI', 'BinomialOptions', 'MergeSort', 'Dct8*8', 'ConvolutionTexture', 'BFS_Cuda', 'CP', 'LIB',
                   'LPS', 'MUM']
    RandomForestRegressorAccuracy = 41.300146
    LinearRegressionAccuracy = 96.25013
    XGBRegressorAccuracy = 49.768548
    KernelRidgeAccuracy = 99.161891
    ElasticNetAccuracy = 95.908626
    SVRAccuracy = 18.729927
    MLPRegressorAccuracy = 98.448936
    rangx = 10

    RandomForest = []
    Linear = []
    XGBR = []
    Kernel = []
    Elastic = []
    SVR = []
    MLP = []
    kir = []
    koon = []
    khaye = []
    for x in range(rangx):
        data = {'RandomForestRegressor': RandomForestRegressorAccuracy, 'LinearRegression': LinearRegressionAccuracy,
                'XGBRegressor': XGBRegressorAccuracy, 'KernelRidge': KernelRidgeAccuracy,
                'ElasticNet': ElasticNetAccuracy, 'SVR': SVRAccuracy, 'MLPRegressor': MLPRegressorAccuracy}
        courses = list(data.keys())
        values = list(data.values())
        RandomForest.append(RandomForestRegressorAccuracy - (x * 5))
        Linear.append(LinearRegressionAccuracy)
        XGBR.append(XGBRegressorAccuracy)
        Kernel.append(KernelRidgeAccuracy)
        Elastic.append(ElasticNetAccuracy)
        SVR.append(SVRAccuracy)
        MLP.append(MLPRegressorAccuracy)
        kir.append(2.5*rangx)
        khaye.append(3.5*rangx)
        koon.append(4.5*rangx)

    data = pd.DataFrame.from_dict(
        {
            'RandomForestRegressor': RandomForest,
            'LinearRegression': Linear,
            'XGBRegressor': XGBR,
            'KernelRidge': Kernel,
            'ElasticNet': Elastic,
            'SVR': SVR,
            'MLPRegressor': MLP,
            'kir': kir,
            'koon': koon,
            'khaye': khaye
        }
    )
    benchMarksNames = ['AsyncAPI', 'BinomialOptions', 'MergeSort', 'Dct8*8', 'ConvolutionTexture', 'BFS_Cuda', 'CP',
                       'LIB',
                       'LPS', 'MUM']
    algorithm = ['RandomForestRegressor', 'LinearRegression', 'XGBRegressor', 'KernelRidge', 'ElasticNet', 'SVR', 'MLPRegressor', 'kir', 'koon', 'khaye']
    x_ = np.arange(0, len(benchMarksNames), 1)
    plt.figure(figsize=(35, 5))
    for i in range(rangx):
        plt.bar(x=x_ + (0.06*i - 0.24), height=data[algorithm[i]], width=0.06, label=algorithm[i], linewidth=3)
    plt.xticks(x_, benchMarksNames)
    plt.xticks(rotation=90)
    plt.legend(loc="best")
    plt.show()




