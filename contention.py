import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd


def measure_contention(input_, chiplet_num):
    base_path = os.path.dirname(input_)
    if os.path.exists(base_path + "/contention"):
        contention_degree = {}
        sub_contention_degree = {}
        for i in range(chiplet_num):
            for j in range(chiplet_num):
                if i != j:
                    for k in range(3):
                        type = ""
                        if k == 0:
                            type = "src"
                        elif k == 1:
                            type = "path"
                        elif k == 2:
                            type = "dest"
                        path = base_path + "contention/contention_" + str(i) + "_" + str(j) + "_" + type + ".csv"
                        if os.path.exists(path):
                            if i not in sub_contention_degree.keys():
                                sub_contention_degree.setdefault(i, {}).setdefault(j, {})
                                contention_degree.setdefault(i, {}).setdefault(j, {})
                            else:
                                if j not in sub_contention_degree[i].keys():
                                    sub_contention_degree[i].setdefault(j, {})
                                    contention_degree[i].setdefault(j, {})
                            df = pd.read_csv(path)
                            x = df['cycle']
                            y = df['degree']
                            if type == "src":
                                for cycle, degree in zip(x, y):
                                    sub_contention_degree[i][j].setdefault("src", {})[cycle] = degree
                            elif type == "dest":
                                for cycle, degree in zip(x, y):
                                    sub_contention_degree[i][j].setdefault("dest", {})[cycle] = degree
                            elif type == "path":
                                for cycle, degree in zip(x, y):
                                    sub_contention_degree[i][j].setdefault("path", {})[cycle] = degree
        for x in sub_contention_degree.keys():
            for y in sub_contention_degree[x].keys():
                for type in sub_contention_degree[x][y].keys():
                    if type == "src" or type == "path":
                        for cycle, degree in sub_contention_degree[x][y][type].items():
                            if cycle not in contention_degree[x][y].keys():
                                contention_degree[x][y][cycle] = degree
                            else:
                                contention_degree[x][y][cycle] += degree
        contention_degree_pdf = {}
        for x in contention_degree.keys():
            if x not in contention_degree_pdf.keys():
                contention_degree_pdf.setdefault(x, {})
            for y in contention_degree[x].keys():
                if y not in contention_degree_pdf[x].keys():
                    contention_degree_pdf[x].setdefault(y, {})
                for cycle, degree in contention_degree[x][y].items():
                    if degree not in contention_degree_pdf[x][y].keys():
                        contention_degree_pdf[x][y][degree] = 1
                    else:
                        contention_degree_pdf[x][y][degree] += 1
        contention_degree_pdf = dict(sorted(contention_degree_pdf.items(), key=lambda x: x[0]))
        for x in contention_degree_pdf.keys():
            contention_degree_pdf[x] = dict(sorted(contention_degree_pdf[x].items(), key=lambda x: x[0]))
            for y in contention_degree_pdf[x].keys():
                contention_degree_pdf[x][y] = dict(sorted(contention_degree_pdf[x][y].items(), key=lambda x: x[0]))

        for x in contention_degree_pdf.keys():
            for y in contention_degree_pdf[x].keys():
                total = sum(contention_degree_pdf[x][y].values())
                for degree in contention_degree_pdf[x][y].keys():
                    contention_degree_pdf[x][y][degree] = contention_degree_pdf[x][y][degree] / total

        if os.path.exists(base_path + "/plots/link_contention"):
            pass
        else:
            os.system("mkdir " + base_path + "/plots/link_contention")
            for x in contention_degree_pdf.keys():
                plot_num = len(contention_degree_pdf[x].keys())
                row = int(np.ceil(plot_num / 2))
                col = row + 1
                counter = 1
                fig, ax = plt.subplots(row, col)
                fig.tight_layout()
                for y in contention_degree_pdf[x].keys():
                    plt.subplot(row, col, counter)
                    plt.plot(list(contention_degree_pdf[x][y].keys()), list(contention_degree_pdf[x][y].values()), marker="*")
                    plt.xticks(list(contention_degree_pdf[x][y].keys()))
                    plt.xlabel("contention degree")
                    plt.ylabel("PDF")
                    plt.title("chiplet " + str(x) + " to chiplet " + str(y))
                    counter += 1
                plt.savefig(base_path + "/plots/link_contention/link_contention" + str(x) + ".jpg")
                plt.close()
