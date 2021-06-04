import csv
import multiprocessing
from fbm import MBM
import matplotlib.pyplot as plt
import threading
from threading import Lock

plt.style.use('ggplot')
fig, ax = plt.subplots(nrows=1, ncols=1)
#fig2, ax2 = plt.subplots(nrows=1, ncols=1)
#fig3, ax3 = plt.subplots(nrows=1, ncols=1)
mutex = Lock()


def h_90(t):
    return 0.9


def h_75(t):
    return 0.001


def h_5(t):
    return 0.5


def thread_fgn_9():
    x_vec = []
    y_vec = []
    sample_arr = {}
    i = 1
    while True:
        """mutex.acquire()
        f = MBM(n=1, hurst=h_5, length=1, method='riemannliouville')
        fgn_sample = f.mgn()
        x_vec.append(i)
        y_vec.append(fgn_sample[0])
        i += 1
        ax.plot(x_vec, y_vec, "r-")
        plt.pause(0.0001)
        mutex.release()"""
        f = MBM(n=1, hurst=h_75, length=1)
        fgn_sample = f.mgn()
        sample_arr[i] = fgn_sample[0]
        i += 1
        if i == 1000001:
            break
    fig, ax = plt.subplots(1, 1, figsize=(18, 5), dpi=100)
    ax.plot(list(sample_arr.keys()), list(sample_arr.values()))
    plt.xlim(100, 200)
    plt.show()
    """with open('synthetic.csv', 'w') as file:
        field = ['cycle', 'byte']
        writer = csv.DictWriter(file, fieldnames=field)
        writer.writeheader()
        for i in sample_arr.keys():
            writer.writerow({"cycle": i, "byte": sample_arr[i]})"""


if __name__ == "__main__":
    x1 = multiprocessing.Process(target=thread_fgn_9, name="H_90").start()
