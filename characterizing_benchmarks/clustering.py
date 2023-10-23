import os
import sys
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from kneefinder import KneeFinder
import matplotlib.pyplot as plt
sys.path.append("..")
import benchlist
from sklearn.cluster import KMeans


def collect_data(topo, nv, ch):
    oneD = {}
    threeD = {}
    twoD = {}
    benchmark_category = {}
    kernel_counter = 1
    for suite in benchlist.suits:
        for bench in benchlist.benchmarks[suite]:
            if os.path.exists(benchlist.bench_path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/"):
                df = pd.read_csv(benchlist.bench_path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/bench_info.csv")
                for row in df.index:
                    kernel_num = df["kernel_num"][row]
                    hurst = df["hurst"][row]
                    iat = df["IAT_CoV"][row]
                    vol = df["Vol_CoV"][row]
                    duration = df["Dur_CoV"][row]
                    ratio = df["ratio_CoV"][row]
                    threeD[kernel_counter] = [iat, vol, duration]
                    twoD[kernel_counter] = [iat, ratio]
                    oneD[kernel_counter] = iat
                    if suite not in benchmark_category.keys():
                        benchmark_category.setdefault(suite, {}).setdefault(bench, {}).setdefault(kernel_num, [])
                    else:
                        if bench not in benchmark_category[suite].keys():
                            benchmark_category[suite].setdefault(bench, {}).setdefault(kernel_num, [])
                        else:
                            if kernel_num not in benchmark_category[suite][bench].keys():
                                benchmark_category[suite][bench].setdefault(kernel_num, [])
                    benchmark_category[suite][bench][kernel_num].append(hurst)
                    benchmark_category[suite][bench][kernel_num].append(iat)
                    benchmark_category[suite][bench][kernel_num].append(vol)
                    benchmark_category[suite][bench][kernel_num].append(duration)
                    benchmark_category[suite][bench][kernel_num].append(ratio)
                    benchmark_category[suite][bench][kernel_num].append(kernel_counter)
                    kernel_counter += 1
    return oneD, twoD, threeD, benchmark_category


def measure_inertia(oneD, twoD, threeD, nv, topo):
    if not os.path.exists(benchlist.bench_path + "/characterization_output/"):
        os.mkdir(benchlist.bench_path + "/characterization_output/")
    wss = []
    iterator = range(1, 10)
    for k in iterator:
        km = KMeans(n_clusters=k)
        km.fit(list(twoD.values()))
        wss.append(km.inertia_)
    kf = KneeFinder(np.array(iterator), wss)
    twoD_knee_x, _ = kf.find_knee()
    kf.plot("WSS error for 2D clustering (IAT/burst ratio)", benchlist.bench_path + "/characterization_output/2D_inertia_" + nv + "_" + topo + ".jpg")
    wss = []
    for k in iterator:
        km = KMeans(n_clusters=k)
        km.fit(list(threeD.values()))
        wss.append(km.inertia_)
    kf = KneeFinder(np.array(iterator), wss)
    threeD_knee_x, _ = kf.find_knee()
    kf.plot("WSS error for 3D clustering (IAT/burst volume/burst duration)", benchlist.bench_path + "/characterization_output/3D_inertia.jpg" + nv + "_" + topo + ".jpg")
    wss = []
    for k in iterator:
        km = KMeans(n_clusters=k)
        km.fit(list(oneD.values()))
        wss.append(km.inertia_)
    kf = KneeFinder(np.array(iterator), wss)
    oneD_knee_x, _ = kf.find_knee()
    kf.plot("WSS error for 1D clustering (IAT)", benchlist.bench_path + "/characterization_output/1D_inertia.jpg" + nv + "_" + topo + ".jpg")
    return oneD_knee_x, twoD_knee_x, threeD_knee_x


def optimum_clustering(oneD, twoD, threeD, oneD_cluster, twoD_cluster, threeD_cluster, benchmark_category):
    if not os.path.exists(benchlist.bench_path + "/characterization_output/"):
        os.mkdir(benchlist.bench_path + "/characterization_output/")

    km = KMeans(n_clusters=oneD_cluster, init='k-means++')
    fit = km.fit_predict(list(oneD.values()))
    x_val = []
    for kernel_id, values in oneD.items():
        x_val.append(values)
    x_center = []
    for center_point in km.cluster_centers_:
        x_center.append(center_point)
    print(x_center)

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
    plt.savefig(benchlist.bench_path + "/characterization_output/2D_clustering.jpg")
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
    minimum = min(fit)
    maximum = max(fit)
    for i in range(minimum, maximum + 1):
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
    fig.write_html(benchlist.bench_path + "/characterization_output/3D_clustering.html")

    category_list = {}
    for i in range(len(labels)):
        kernel_index = list(threeD)[i][0]
        traffic_charcteristics = list(threeD)[i][1]
        cluster_id = labels[i]
        for suite in benchmark_category.keys():
            for bench in benchmark_category[suite].keys():
                for kernel_num, bench_values in benchmark_category[suite][bench].items():
                    if kernel_index == bench_values[4]:
                        assert(bench_values[1] == traffic_charcteristics[0])
                        assert(bench_values[2] == traffic_charcteristics[1])
                        assert(bench_values[3] == traffic_charcteristics[2])
                        if suite not in category_list.keys():
                            category_list.setdefault(suite, {}).setdefault(bench, {}).setdefault(kernel_num, {})
                        else:
                            if bench not in category_list[suite].keys():
                                category_list[suite].setdefault(bench, {}).setdefault(kernel_num, {})
                            else:
                                if kernel_num not in category_list[suite][bench].keys():
                                    category_list[suite][bench].setdefault(kernel_num, {})
                        category_list[suite][bench][kernel_num]["hurst"] = bench_values[0]
                        category_list[suite][bench][kernel_num]["IAT_CoV"] = bench_values[1]
                        category_list[suite][bench][kernel_num]["Vol_CoV"] = bench_values[2]
                        category_list[suite][bench][kernel_num]["Dur_CoV"] = bench_values[3]
                        category_list[suite][bench][kernel_num]["ratio_CoV"] = bench_values[4]
                        category_list[suite][bench][kernel_num]["Cluster_id"] = cluster_id
    df = pd.DataFrame(category_list, columns=["suite", "benchmark", "kernel_num", "hurst", "IAT_CoV", "Vol_CoV", "Dur_CoV", "ratio_CoV", "Cluster_id"])
    df.set_index(["suite", "benchmark", "kernel_num", "hurst", "IAT_CoV", "Vol_CoV", "Dur_CoV", "ratio_CoV", "Cluster_id"], inplace=True)
    df.to_html(benchlist.bench_path + "/" + ch + "_" + nv + "_kernel_clustering.html", index=True)
    df.to_csv(benchlist.bench_path + "/" + ch + "_" + nv + "_kernel_clustering.csv", index=True)


if __name__ == "__main__":
    ch = "4chiplet"
    for nv in benchlist.NVLink:
        for topo in benchlist.topology:
            oneD, twoD, threeD, benchmark_category = collect_data(topo, nv, ch)
            oneD_cluster, twoD_cluster, threeD_cluster = measure_inertia(oneD, twoD, threeD, nv, topo)
            optimum_clustering(oneD, twoD, threeD, oneD_cluster, twoD_cluster, threeD_cluster, benchmark_category)
