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
    return 0.75


def h_5(t):
    return 0.5


def thread_fgn_9():
    print(threading.current_thread().getName())
    x_vec = []
    y_vec = []
    i = 1
    while True:
        mutex.acquire()
        f = MBM(n=1, hurst=h_5, length=1, method='riemannliouville')
        fgn_sample = f.mgn()
        x_vec.append(i)
        y_vec.append(fgn_sample[0])
        i += 1
        ax.plot(x_vec, y_vec, "r-")
        plt.pause(0.0001)
        mutex.release()

"""
def thread_fgn_75():
    print(threading.current_thread().getName())
    x_vec_ = []
    y_vec_ = []
    i = 1
    while True:
        mutex.acquire()
        f = MBM(n=1, hurst=h_75, length=1, method='riemannliouville')
        fgn_sample = f.mgn()
        x_vec_.append(i)
        y_vec_.append(fgn_sample[0])
        i += 1
        ax2.plot(x_vec_, y_vec_, "y-o")
        plt.pause(0.0001)
        mutex.release()


def thread_fgn_5():
    print(threading.current_thread().getName())
    x_vec_ = []
    y_vec_ = []
    i = 1
    while True:
        mutex.acquire()
        f = MBM(n=1, hurst=h_5, length=1, method='riemannliouville')
        fgn_sample = f.mgn()
        x_vec_.append(i)
        y_vec_.append(fgn_sample[0])
        i += 1
        ax3.plot(x_vec_, y_vec_, "r-")
        plt.pause(0.0001)
        mutex.release()"""


if __name__ == "__main__":
    x1 = multiprocessing.Process(target=thread_fgn_9, name="H_90").start()
