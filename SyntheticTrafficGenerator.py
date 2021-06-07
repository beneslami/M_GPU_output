import csv
from hurst import compute_Hc, random_walk
import matplotlib.pyplot as plt
from stochastic.processes import FractionalBrownianMotion, FractionalGaussianNoise, MultifractionalBrownianMotion


def synthetic_generator(fbm):
    out = {}
    for i in range(1, len(fbm)):
        out[i] = fbm[i]
    with open('synthetic.csv', 'a') as file:
        field = ['cycle', 'byte']
        writer = csv.DictWriter(file, fieldnames=field)
        writer.writeheader()
        for j in range(1, len(fbm)):
            writer.writerow({"cycle": j + 100000, "byte": fbm[j]})


def hurst(lined_list):
    H, c, data = compute_Hc(lined_list, simplified=True)
    f, ax = plt.subplots()
    ax.plot(data[0], c * data[0] ** H, color="deepskyblue")
    ax.scatter(data[0], data[1], color="purple")
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.text(10000, 5, "slope = " + str("{:.3f}".format(H)), bbox={'facecolor': 'blue', 'alpha': 0.1, 'pad': 10})
    ax.set_xlabel('Time interval')
    ax.set_ylabel('R/S ratio')
    #ax.grid(True)
    plt.show()
    print("H={:.4f}, c={:.4f}".format(H, c))


def hurst_func(t):
    return 0.174


if __name__ == "__main__":
    duration = 100000

    """fbm = FractionalBrownianMotion(t=duration, hurst=0.174)
    s1 = fbm.sample(duration)
    times = fbm.times(duration)"""

    """mfbm = MultifractionalBrownianMotion(t=duration, hurst=hurst_func)
    s2 = mfbm.sample(duration)
    time2 = mfbm.times(duration)"""

    """fgn = FractionalGaussianNoise(t=duration, hurst=hurst_func)
    s3 = fgn.sample(duration)
    time3 = fgn.times(duration)"""

    #fig, ax = plt.subplots(1, 1, figsize=(18, 5))
    #ax[0].plot(times, s1)
    #ax.plot(time2, s2)
    #ax[2].plot(time3, s3)
    #plt.show()

    #synthetic_generator(s2)
    #hurst(s2)