from lux.core.

import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/college.csv")
    VisList(["Region=?", "AverageCost"], df)
