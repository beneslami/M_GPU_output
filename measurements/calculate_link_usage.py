import os
import gc

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import plotly.express as px
from colorama import Fore


def return_pdf(data):
    pdf = {}
    for k, v in data.items():
        if v not in pdf.keys():
            pdf[v] = 1
        else:
            pdf[v] += 1
    pdf = dict(sorted(pdf.items(), key=lambda x: x[0]))
    return pdf


def bar_distribution_plot(base_path, traffic, chiplet_num, plot_name):
    if base_path.__contains__("fly"):
        injection_per_chiplet_rate = traffic
        _x = np.arange(0, max(injection_per_chiplet_rate.keys()) + 1, 1)
        _y = np.arange(0, max(injection_per_chiplet_rate.keys()) + 1, 1)
        n_row = len(injection_per_chiplet_rate.keys())
        thikness = 0.5
        thikness *= 0.5
        fig = go.Figure()
        for x in injection_per_chiplet_rate.keys():
            x_cnt = x % n_row
            x_min = x_cnt - thikness
            x_max = x_cnt + thikness
            for y in injection_per_chiplet_rate[x].keys():
                y_cnt = y
                y_min = y_cnt - thikness
                y_max = y_cnt + thikness
                Z = injection_per_chiplet_rate[x][y]
                go.Layout(width=1024, height=1024, )
                fig.add_trace(go.Mesh3d(
                    x=[x_min, x_min, x_max, x_max, x_min, x_min, x_max, x_max],
                    y=[y_min, y_max, y_max, y_min, y_min, y_max, y_max, y_min],
                    z=[0, 0, 0, 0, Z, Z, Z, Z], opacity=1, alphahull=0, color="green",
                    intensity=np.linspace(0, 1, 12, endpoint=True), intensitymode='vertex', ))
        z_axis_name = ""
        if plot_name.__contains__("throughput"):
            z_axis_name = "average throughput (Bytes/cycle)"
        elif plot_name.__contains__("channel"):
            z_axis_name = "Average channel BW (normalized)"
        fig.update_layout(scene=dict(
            xaxis=dict(backgroundcolor="rgb(200, 200, 230)", gridcolor="white", showbackground=True,
                       zerolinecolor="white",
                       tickvals=list(range(0, len(injection_per_chiplet_rate.keys()) + 1)), showline=True,
                       titlefont=dict(family='arial, sans-serif', size=18)),
            yaxis=dict(backgroundcolor="rgb(230, 200, 230)", gridcolor="white", showbackground=True,
                       zerolinecolor="white",
                       tickvals=list(range(0, len(injection_per_chiplet_rate.keys()) + 1)), showline=True,
                       titlefont=dict(family='arial, sans-serif', size=18)),
            zaxis=dict(backgroundcolor="rgb(230, 230, 200)", gridcolor="white", showbackground=True,
                       zerolinecolor="white",
                       showline=True, titlefont=dict(family='arial, sans-serif', size=18), )))
        fig.update_layout(
            scene=dict(xaxis_title='source chiplet', yaxis_title='router', zaxis_title=z_axis_name,
                       aspectratio=dict(x=1, y=0.1, z=1)),
            margin=dict(l=65, r=50, b=65, t=90))
        fig.write_html(base_path + "/plots/link_usage/" + plot_name + ".html")
    else:
        injection_per_chiplet_rate = traffic
        for src in range(chiplet_num):
            if src not in injection_per_chiplet_rate.keys():
                injection_per_chiplet_rate.setdefault(src, {})
            for dest in range(chiplet_num):
                if dest not in injection_per_chiplet_rate[src].keys():
                    injection_per_chiplet_rate[src][dest] = 0
        _x = np.arange(0, max(injection_per_chiplet_rate.keys()) + 1, 1)
        _y = np.arange(0, max(injection_per_chiplet_rate.keys()) + 1, 1)
        n_row = len(injection_per_chiplet_rate.keys())

        thikness = 0.5
        thikness *= 0.5
        fig = go.Figure()
        for x in injection_per_chiplet_rate.keys():
            x_cnt = x % n_row
            x_min = x_cnt - thikness
            x_max = x_cnt + thikness
            for y in injection_per_chiplet_rate[x].keys():
                y_cnt = y % n_row
                y_min = y_cnt - thikness
                y_max = y_cnt + thikness
                Z = injection_per_chiplet_rate[x][y]
                go.Layout(width=1024, height=1024,)
                fig.add_trace(go.Mesh3d(
                    x=[x_min, x_min, x_max, x_max, x_min, x_min, x_max, x_max],
                    y=[y_min, y_max, y_max, y_min, y_min, y_max, y_max, y_min],
                    z=[0, 0, 0, 0, Z, Z, Z, Z], opacity=1, alphahull=0, color="green", intensity=np.linspace(0, 1, 12, endpoint=True), intensitymode='vertex',))
        z_axis_name = ""
        if plot_name.__contains__("throughput"):
            z_axis_name = "average throughput (Bytes/cycle)"
        elif plot_name.__contains__("channel"):
            z_axis_name = "Average channel BW (normalized)"
        fig.update_layout(scene=dict(
            xaxis=dict(backgroundcolor="rgb(200, 200, 230)", gridcolor="white", showbackground=True, zerolinecolor="white",
                       tickvals=list(range(0, len(injection_per_chiplet_rate.keys()) + 1)), showline=True,
                       titlefont=dict(family='arial, sans-serif', size=18)),
            yaxis=dict(backgroundcolor="rgb(230, 200, 230)", gridcolor="white", showbackground=True, zerolinecolor="white",
                       tickvals=list(range(0, len(injection_per_chiplet_rate.keys()) + 1)), showline=True,
                       titlefont=dict(family='arial, sans-serif', size=18)),
            zaxis=dict(backgroundcolor="rgb(230, 230, 200)", gridcolor="white", showbackground=True, zerolinecolor="white",
                       showline=True, titlefont=dict(family='arial, sans-serif', size=18),)))
        fig.update_layout(
            scene=dict(xaxis_title='source router', yaxis_title='destination router', zaxis_title=z_axis_name, aspectratio=dict(x=1, y=1, z=1)),
            margin=dict(l=65, r=50, b=65, t=90))
        if os.path.exists(base_path + "/plots/link_usage"):
            pass
        else:
            os.system("mkdir " + base_path + "/plots/link_usage/")
        fig.write_html(base_path + "/plots/link_usage/" + plot_name + ".html")
        #fig.show()
    gc.enable()
    gc.collect()


def measure_throughput_per_link(emp_links, syn_links, path):
    for src in emp_links.keys():
        for dest in emp_links[src].keys():
            emp_pdf = return_pdf(emp_links[src][dest])
            syn_pdf = return_pdf(syn_links[src][dest])
            if len(emp_pdf) != 0 and len(syn_pdf) != 0:
                plt.plot(list(emp_pdf.keys()), list(emp_pdf.values()), marker="o", labels="AccelSim")
                plt.plot(list(syn_pdf.keys()), list(syn_pdf.values()), marker="o", labels="Synthetic")
                plt.xlabel("byte per cycle")
                plt.ylabel("density")
                plt.legend()
                if not os.path.exists(path + "plots/link_usage/"):
                    os.makedirs(path + "plots/link_usage/")
                plt.savefig(path + "plots/link_usage/channel " + str(src) + str(dest) + ".jpg")
    gc.enable()
    gc.collect()


def extract_link_usage(file):
    print(Fore.YELLOW + "for now there is no data regarding link usage for this benchmark" + Fore.RESET)


def calculate_link_usage_(target_path, kernel_name):
    emp_links = {}
    syn_links = {}
    for input_ in target_path:
        base_path = os.path.dirname(input_)
        if "kernels" in input_:
            if os.path.exists(base_path + "/link_usage") and len(os.listdir(base_path + "/link_usage")) != 0:
                directory_path = base_path + "/link_usage/" + str(kernel_name) + "/"
                for files in os.listdir(directory_path):
                    src = int(files.split("_")[-1].split(".")[0][0])
                    dst = int(files.split("_")[-1].split(".")[0][1])
                    if src not in emp_links.keys():
                        emp_links.setdefault(src, {}).setdefault(dst, {})
                    else:
                        if dst not in emp_links[src].keys():
                            emp_links[src].setdefault(dst, {})
                    if os.path.getsize(files) > 50:
                        content = ""
                        with open(directory_path + files, "r") as f:
                            content = f.readlines()
                        x = []
                        y = []
                        if "cycle" in content[0]:
                            df = pd.read_csv(directory_path + files)
                            x = df['cycle']
                            y = df['byte']
                        else:
                            os.system("sed -i '1s/^/cycle,byte\n/' " + directory_path + str(files))
                            df = pd.read_csv(directory_path + files)
                            x = df['cycle']
                            y = df['byte']
                        fig = px.line(x=list(x), y=list(y))
                        if not os.path.exists(base_path + "/plots/" + str(kernel_name) + "/link_usage"):
                            os.mkdir(base_path + "/plots/" + str(kernel_name) + "/link_usage")
                        fig.write_html(base_path + "/plots/" + str(kernel_name) + "/link_usage/accelSim_link_" + str(src) + str(dst) + ".html")
                        for i in range(x):
                            emp_links[src][dst][x[i]] = y[i]
            else:
                for file in os.listdir(input_):
                    if Path(file).suffix == '.txt':
                        extract_link_usage(input_ + "/" + file)
        elif "synthetic_trace" in input_:
            if os.path.exists(input_ + "/link_usage/") and len(os.listdir(input_ + "/link_usage/")) != 0:
                directory_path = input_ + "/link_usage/"
                for file in os.listdir(directory_path):
                    src = int(file.split("_")[-1].split(".")[0][0])
                    dst = int(file.split("_")[-1].split(".")[0][1])
                    if src not in syn_links.keys():
                        syn_links.setdefault(src, {}).setdefault(dst, {})
                    else:
                        if dst not in syn_links[src].keys():
                            syn_links[src].setdefault(dst, {})
                    if os.path.getsize(file) > 50:
                        content = ""
                        with open(directory_path + file, "r") as f:
                            content = f.readlines()
                        x = []
                        y = []
                        if "cycle" in content[0]:
                            df = pd.read_csv(directory_path + file)
                            x = df['cycle']
                            y = df['byte']
                        else:
                            os.system("sed -i '1s/^/cycle,byte\n/' " + directory_path + str(file))
                            df = pd.read_csv(directory_path + file)
                            x = df['cycle']
                            y = df['byte']
                        fig = px.line(x=list(x), y=list(y))
                        if not os.path.exists(base_path + "/plots/" + str(kernel_name) + "/link_usage"):
                            os.mkdir(base_path + "/plots/" + str(kernel_name) + "/link_usage")
                        fig.write_html(base_path + "/plots/" + str(kernel_name) + "/link_usage/synthetic_link_" + str(src) + str(dst) + ".html")
                        for i in range(x):
                            syn_links[src][dst][x[i]] = y[i]
                else:
                    for file in os.listdir(input_):
                        if Path(file).suffix == '.txt':
                            extract_link_usage(input_ + "/" + file)

    if len(emp_links) != 0 and len(syn_links) != 0:
        measure_throughput_per_link(emp_links, syn_links, os.path.dirname(target_path[0]))
    else:
        print(Fore.YELLOW + "Unable to measure link usage" + Fore.RESET)
    gc.enable()
    gc.collect()