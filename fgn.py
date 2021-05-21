from fbm import MBM
import numpy as np
import matplotlib.pyplot as plt

def h(t):
    return 0.75

N = 10000

f = MBM(n=N, hurst=h, length=1, method='riemannliouville')
fgn_sample = f.mgn()
x_axis = np.arange(1, N+1)

fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(50, 3))
axes.plot(x_axis, list(fgn_sample))
plt.tight_layout()
plt.show()