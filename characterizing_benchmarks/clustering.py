import os
import sys
import csv
import plotly.graph_objs as go
import numpy as np
from kneefinder import KneeFinder
import matplotlib.pyplot as plt
sys.path.append("..")
import benchlist
from sklearn.cluster import KMeans


def collect_data(topo, nv, ch):
    threeD = {}
    twoD = {}
    kernel_counter = 1
    for suite in benchlist.suits:
        for bench in benchlist.benchmarks[suite]:
            if os.path.exists(benchlist.bench_path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/"):
                df = csv.reader(benchlist.bench_path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/bench_info.csv")
                for row in df:
                    kernel_num = row[0]
                    hurst = row[1]
                    iat = row[2]
                    vol = row[3]
                    duration = row[5]
                    ratio = row[4]
                    threeD[kernel_counter] = [iat, vol, duration]
                    twoD[kernel_counter] = [iat, ratio]
                    kernel_counter += 1
    return twoD, threeD


def measure_inertia(twoD, threeD, nv, topo):
    wss = []
    iterator = range(1, 10)
    for k in iterator:
        km = KMeans(n_clusters=k)
        km.fit(list(twoD.values()))
        wss.append(km.inertia_)
    kf = KneeFinder(np.array(iterator), wss)
    twoD_knee_x, _ = kf.find_knee()
    kf.plot("WSS error for 2D clustering (IAT/burst ratio)", benchlist.bench_path + "2D_inertia_" + nv + "_" + topo + ".jpg")
    wss = []
    for k in iterator:
        km = KMeans(n_clusters=k)
        km.fit(list(threeD.values()))
        wss.append(km.inertia_)
    kf = KneeFinder(np.array(iterator), wss)
    threeD_knee_x, _ = kf.find_knee()
    kf.plot("WSS error for 3D clustering (IAT/burst volume/burst duration)", benchlist.bench_path + "3D_inertia.jpg" + nv + "_" + topo + ".jpg")
    return twoD_knee_x, threeD_knee_x


def optimum_clustering(twoD, threeD, twoD_cluster, threeD_cluster):
    km = KMeans(n_clusters=twoD_cluster, init='k-means++')
    fit = km.fit_predict(list(twoD.values()))
    x_val = []
    y_val = []
    for kernel_id, values in twoD.items():
        x_val.append(values[0])
        y_val.append(values[1])
    x_center = []
    y_center = []
    for center_point in km.cluster_centers_:
        x_center.append(center_point[0])
        y_center.append(center_point[1])
    plt.figure(figsize=(8, 8))
    plt.scatter(x_val, y_val, c=fit)
    plt.scatter(x_center, y_center, s=100, c='red')
    plt.title('K-means clustering (k={})'.format(twoD_cluster))
    plt.xlabel('Inter Arrival Time CoV')
    plt.ylabel('Burst ratio CoV')
    plt.tight_layout()
    plt.savefig(benchlist.bench_path + "2D_clustering.jpg")
    plt.close()

    km = KMeans(n_clusters=threeD_cluster, init='k-means++')
    fit = km.fit_predict(list(threeD.values()))
    x_val = []
    y_val = []
    z_val = []
    for kernel_id, values in threeD.items():
        x_val.append(values[0])
        y_val.append(values[1])
        z_val.append(values[2])
    threeD = []
    for i in range(len(x_val)):
        temp = []
        temp.append(x_val[i])
        temp.append(y_val[i])
        temp.append(z_val[i])
        threeD.append(temp)
    km = KMeans(n_clusters=threeD_cluster, init='k-means++')
    km = km.fit(threeD)
    labels = km.predict(threeD)
    x_center = []
    y_center = []
    z_center = []
    for center_point in km.cluster_centers_:
        x_center.append(center_point[0])
        y_center.append(center_point[1])
        z_center.append(center_point[2])

    scatter_colors = ["red", "green", "blue", "black", "yellow"]
    plot_points = {}
    for i in range(3):
        plot_points.setdefault(i, {})

    for i in range(len(labels)):
        if "x" not in plot_points[labels[i]].keys():
            plot_points[labels[i]].setdefault("x", []).append(x_val[i])
        else:
            plot_points[labels[i]]["x"].append(x_val[i])
        if "y" not in plot_points[labels[i]].keys():
            plot_points[labels[i]].setdefault("y", []).append(y_val[i])
        else:
            plot_points[labels[i]]["y"].append(y_val[i])
        if "z" not in plot_points[labels[i]].keys():
            plot_points[labels[i]].setdefault("z", []).append(z_val[i])
        else:
            plot_points[labels[i]]["z"].append(z_val[i])

    data_plot = []
    for cluster_id, points in plot_points.items():
        scatter = go.Scatter3d(x=points["x"], y=points["y"], z=points["z"], mode="markers",
                               marker=dict(size=10, color=scatter_colors[cluster_id]))
        mesh = go.Mesh3d(x=points["x"], y=points["y"], z=points["z"], color=scatter_colors[cluster_id], opacity=0.45)
        data_plot.append(scatter)
        data_plot.append(mesh)
    layout = go.Layout(margin=dict(l=0, r=0, b=0, t=0))
    fig = go.Figure(data=data_plot, layout=layout)
    fig.write_html(benchlist.bench_path + "3D_clustering.html")


if __name__ == "__main__":
    ch = "4chiplet"
    for nv in benchlist.NVLink:
        for topo in benchlist.topology:
            twoD, threeD = collect_data(topo, nv, ch)
            twoD_cluster, threeD_cluster = measure_inertia(twoD, threeD, nv, topo)
            optimum_clustering(twoD, threeD, twoD_cluster, threeD_cluster)