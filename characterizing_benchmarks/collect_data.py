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
                if os.path.exists(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/"):
                    df = csv.reader(path + suite + "/" + bench + "/" + topo + "/" + nv + "/" + ch + "/bench_info.csv")
                    for row in df:
                        kernel_num = row[0]
                        hurst = row[1]
                        iat = row[2]
                        vol = row[3]
                        ratio = row[4]
                        duration = row[5]
                        rw = row[6]
                        reqinst = row[7]
                        cta = row[8]
                        local = row[9]
                        remote = row[10]
                        cycle = row[11]
                        instruction = row[12]
                        platency = row[13]
                        nlatency = row[14]
                        throughput = row[15]
                        ipc = row[16]
                        gpu_occ = row[17]
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
    return data


def collect_data(path, nv, ch, data):
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
    data_per_suite = []
    for suite in data.keys():
        for bench in data[suite].keys():
            topo = list(data[suite][bench].keys())[0]
            for kernel in data[suite][bench][topo][nv][ch].keys():
                suits.append(suite)
                benchmarks.append(bench)
                kernels.append(kernel)
                topology.append(topo)
                for key, value in data[suite][bench][topo][nv][ch][kernel].items():
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
                          'Dur_CoV', 'ratio_CoV', 'R/W', 'req/Kinst', 'CTA', 'local', 'remote', 'gpu_cycle', 'instruction',
                          'P_latency', 'N_latency', 'GPU_occupancy'], inplace=True)
        data_per_suite.append(df)
        df.to_html(path + suite + "/" + ch + "_" + nv + "_characterization.html", index=True)
        df.to_csv(path + suite + "/" + ch + "_" + nv + "_characterization.csv", index=True)
    result = pd.concat(data_per_suite)
    result.to_html(path + "/" + ch + "_" + nv + "_characterization.html", index=True)
    result.to_csv(path + "/" + ch + "_" + nv + "_characterization.csv", index=True)


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