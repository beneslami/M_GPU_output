import os.path
import sys
sys.path.append("..")
import benchlist
import csv
import pandas as pd


def read_csv_files(path, nv, ch):
    data = {}
    for suite in benchlist.suits:
        for bench in benchlist.benchmarks[suite]:
            for topo in benchlist.topology:
                if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/bench_info.csv"):
                    df = pd.read_csv(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/bench_info.csv")
                    for row in df.index:
                        kernel_num = df["kernel_num"][row]
                        hurst = df["hurst"][row]
                        iat = df["IAT CoV"][row]
                        vol = df["Vol CoV"][row]
                        ratio = df["dur CoV"][row]
                        duration = df["ratio CoV"][row]
                        rw = df["R/W"][row]
                        reqinst = df["req/inst"][row]
                        cta = df["CTA"][row]
                        local = df["local"][row]
                        remote = df["remote"][row]
                        cycle = df["gpu_cycle"][row]
                        instruction = df["instruction"][row]
                        platency = df["P latency"][row]
                        nlatency = df["N latency"][row]
                        throughput = df["throughput"][row]
                        ipc = df["ipc"][row]
                        gpu_occ = df["GPU occupancy"][row]
                        info = {"ipc": ipc, "throughput": throughput, "hurst": hurst, "IAT_CoV": iat, "Vol_CoV": vol,
                                "dur_CoV": duration, "ratio_CoV": ratio, "R_W": rw, "reqinst": reqinst, "CTA": cta,
                                "local": local, "remote": remote, "gpu_cycle": cycle, "instruction": instruction,
                                "p_latency": platency, "n_latency": nlatency, "GPU_occupancy": gpu_occ}
                        if suite not in data.keys():
                            data.setdefault(suite, {}).setdefault(bench, {}).setdefault(kernel_num, {})[topo] = info
                        else:
                            if bench not in data[suite].keys():
                                data[suite].setdefault(bench, {}).setdefault(kernel_num, {})[topo] = info
                            else:
                                if kernel_num not in data[suite][bench].keys():
                                    data[suite][bench].setdefault(kernel_num, {})[topo] = info
                                else:
                                    data[suite][bench][kernel_num][topo] = info
                else:
                    #print("WARNING: bench_info.csv does not exist in " + str(suite) + " " + str(bench) + " " + str(topo) + " " + str(nv))
                    pass
    return data


def collect_data(path, nv, ch, data):
    data_per_suite = []
    for suite in data.keys():
        suits = []
        benchmarks = []
        kernels = []
        topology = []
        ipc = []
        throughput = []
        hurst = []
        iat_cov = []
        vol_cov = []
        dur_cov = []
        ratio_cov = []
        r_w = []
        reqinst = []
        cta = []
        local = []
        remote = []
        gpu_cycle = []
        instruction = []
        platency = []
        nlatency = []
        gpu_occ = []
        for bench in data[suite].keys():
            for kernel in data[suite][bench].keys():
                for topo in data[suite][bench][kernel].keys():
                    suits.append(suite)
                    benchmarks.append(bench)
                    kernels.append(kernel)
                    topology.append(topo)
                    for key, value in data[suite][bench][kernel][topo].items():
                        if key == "ipc":
                            ipc.append(value)
                        elif key == "throughput":
                            throughput.append(value)
                        elif key == "hurst":
                            hurst.append(value)
                        elif key == "IAT_CoV":
                            iat_cov.append(value)
                        elif key == "Vol_CoV":
                            vol_cov.append(value)
                        elif key == "dur_CoV":
                            dur_cov.append(value)
                        elif key == "ratio_CoV":
                            ratio_cov.append(value)
                        elif key == "R_W":
                            r_w.append(value)
                        elif key == "reqinst":
                            reqinst.append(value)
                        elif key == "CTA":
                            cta.append(value)
                        elif key == "local":
                            local.append(value)
                        elif key == "remote":
                            remote.append(value)
                        elif key == "gpu_cycle":
                            gpu_cycle.append(value)
                        elif key == "instruction":
                            instruction.append(value)
                        elif key == "p_latency":
                            platency.append(value)
                        elif key == "n_latency":
                            nlatency.append(value)
                        elif key == "GPU_occupancy":
                            gpu_occ.append(value)
        table = {"suite": suits, "benchmarks": benchmarks, "kernels": kernels, "topology": topology, "ipc": ipc,
             "throughput": throughput, "hurst": hurst, "IAT_CoV": iat_cov, "Vol_CoV": vol_cov, "Dur_CoV": dur_cov,
             "ratio_CoV": ratio_cov, "R/W": r_w, "Req/Kinst": reqinst, "CTA": cta, "local": local, "remote": remote,
             "gpu_cycle": gpu_cycle, "instruction": instruction, "P_latency": platency, "N_latency": nlatency,
             "GPU_occupancy": gpu_occ}
        df = pd.DataFrame(table)
        df.set_index(['suite', 'benchmarks', 'topology', 'kernels', 'ipc', 'throughput', 'hurst', 'IAT_CoV', 'Vol_CoV',
                          'Dur_CoV', 'ratio_CoV', 'R/W', 'Req/Kinst', 'CTA', 'local', 'remote', 'gpu_cycle', 'instruction',
                          'P_latency', 'N_latency', 'GPU_occupancy'], inplace=True)
        data_per_suite.append(df)
        df.to_html(path + suite + "/" + ch + "_" + nv + "_characterization.html", index=True)
        df.to_csv(path + suite + "/" + ch + "_" + nv + "_characterization.csv", index=True)
    result = pd.concat(data_per_suite)
    if not os.path.exists(path + "characterization_output/"):
        os.mkdir(path + "characterization_output")
    result.to_html(path + "characterization_output/" + ch + "_" + nv + "_characterization.html", index=True)
    result.to_csv(path + "characterization_output/" + ch + "_" + nv + "_characterization.csv", index=True)


if __name__ == "__main__":
    ch = "4chiplet"
    suits = benchlist.suits
    benchmarks = benchlist.benchmarks
    topology = benchlist.topology
    NVLink = benchlist.NVLink
    path = benchlist.bench_path
    for nv in NVLink:
        data = read_csv_files(path, nv, ch)
        collect_data(path, nv, ch, data)