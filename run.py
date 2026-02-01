#!/usr/bin/env python
from asrank import ASRank
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from GeneratePath import Gen_path, P2C_DICT
import os
import time
import argparse
import sys

data_dir = Path(__file__).resolve().parent/"data"
clique = ["174", "209", "286", "701", "1239", "1299", "2828", "2914", "3257", "3320", "3356", "3491", "5511", "6453", "6461", "6762", "6830", "7018", "12956"]
attack_line_list = []

# 支持增量更新，但每次inference内容是续写不是重写，需要删除旧推断结果
def model_run():
    # ASRank(
    #     ixp="1200 4635 5507 6695 7606 8714 9355 9439 9560 9722 9989 11670 15645 17819 18398 21371 24029 24115 24990 35054 40633 42476 43100 47886 48850 50384 55818 57463",
    #     clique = "174 209 286 701 1239 1299 2828 2914 3257 3320 3356 3491 5511 6453 6461 6762 6830 7018 12956",
    #     exclvps = "",
    #     verbose = True,
    #     input_path = "./data/20241001.all-paths.bz2",
    #     output_path = "./data/inference-20241001.txt"
    # ).read_paths().dump_model("./data/model_ori.pkl").infer_rel()
    # pickle.load(open(data_dir/"model.pkl", "rb")).infer_rel()
    model = open(data_dir/"model_ori.pkl", "rb")
    # pickle.load(open(data_dir/"model_ori.pkl", "rb")).add_paths(attack_line_list).infer_rel()
    pickle.load(model).add_paths(attack_line_list).infer_rel()
    del model
# model_run()

def degree_difference_1():
    delta_cache = data_dir/"delta.cache"
    if delta_cache.exists():
        delta = pickle.load(open(delta_cache, "rb"))
    else:
        asr = pickle.load(open(data_dir/"model.pkl", "rb"))
        cols = ["asn", "clique", "transit-degree", "global-degree", "break-tie"]
        df = pd.DataFrame([(i, *asr.sort_key(i)) for i in asr.iter_asn()],
                columns=cols).sort_values(by=cols[1:], ascending=False)
        degrees = df.iloc[len(asr.clique):, 2:4].values
        delta = np.array([t if t > 0 else g for t,g in degrees[:-1]-degrees[1:]])
        pickle.dump(delta, open(delta_cache, "wb"), protocol=5)

    p = [100, 500, 1000, 2000, 5000, 10000, len(delta)]
    x = np.arange(len(p))
    y1, y2, y3, y4 = np.array([np.percentile(delta[:i], [50, 80, 90, 95]) for i in p]).T

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(5,3))
    ax = fig.add_subplot(111)

    ax.plot(x, y4, linestyle='-.', color='#F0E442', marker='d', label='95th')
    ax.plot(x, y3, linestyle=':', color='#009E73', marker='^', label='90th')
    ax.plot(x, y2, linestyle='--', color='#56B4E9', marker='s', label='80th')
    ax.plot(x, y1, linestyle='-', color='#E69F00', marker='o', label='50th')

    ax.set_title("Sorting Sensitivity")
    ax.set_ylabel('Degree Difference (Gaps)')
    ax.set_xlabel('Top-K ASes')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{i}" for i in p], rotation=25)
    ax.legend()
    ax.grid()

    fig.tight_layout()
    fig.savefig(data_dir/f"degree_difference_1.pdf", bbox_inches="tight")
# degree_difference_1()

def degree_difference_2():
    infered_file = data_dir/"inference-20241001.txt"

    delta_cache = data_dir/"delta2.cache"
    if delta_cache.exists():
        delta = pickle.load(open(delta_cache, "rb"))
    else:
        def get_step2_p2c():
            ret = []
            with open(infered_file, "r") as f:
                record = False
                while True:
                    l = f.readline()
                    if not l or l.startswith("# step 3"):
                        break
                    if l.startswith("# step 2"):
                        record = True
                        continue
                    if record:
                        try:
                            a, b = l.split("|")[:2]
                        except:
                            print(l)
                            exit()
                        if a in asr.clique or b in asr.clique:
                            continue
                        ret.append([a, b])
            return ret
        asr = pickle.load(open(data_dir/"model.pkl", "rb"))
        rels = pd.DataFrame(get_step2_p2c(), dtype=str, columns=["a", "b"])
        def get_delta(a, b):
            _, td_a, gd_a, _ = asr.sort_key(a)
            _, td_b, gd_b, _ = asr.sort_key(b)
            d_td = td_a - td_b
            d_gd = gd_a - gd_b
            return d_td if d_td != 0 else d_gd
        vf = np.vectorize(get_delta)
        delta = vf(rels.a.values, rels.b.values)
        pickle.dump(delta, open(delta_cache, "wb"), protocol=5)

    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(5,3))
    ax = fig.add_subplot(111)

    import seaborn as sns
    sns.ecdfplot(x=delta, ax=ax)
    t60, t80 = np.percentile(delta, [60, 80])
    ax.axvline(t60, 0, 0.6, ls="--")
    ax.axvline(t80, 0, 0.8, ls="--")

    # ax.scatter(np.arange(len(delta)), delta, s=1)
    # ax.set_title("P2C Inference (Step 2)")
    # ax.set_ylabel('Degree Difference')
    # ax.set_xlabel('Inference Order')
    # ax.set_xticks([])

    ax.grid(True, axis="y")

    fig.tight_layout()
    fig.savefig(data_dir/f"degree_difference_2.pdf", bbox_inches="tight")
    fig.savefig(data_dir/f"degree_difference_2.png", bbox_inches="tight")
# degree_difference_2()

def check_accuracy(rvs_provider, rvs_customer, att_announcer, att_source, rvs_p_ori_tg, rvs_c_ori_tg):
    # inferred_file = data_dir/"inference-20241001_att1.txt"
    inferred_file = data_dir/"inference-20241001.txt"
    # baseline_file = data_dir/"baseline-20241001.txt"
    baseline_file = data_dir/"inference-20241001_ori.txt"

    def parse_rel(file_path):
        ret = set()
        step = 0
        with open(file_path, "r") as f:
            for l in f:
                if l.startswith("# step"):
                    step += 1
                    continue
                a, b, rel = l.strip().split("|")
                if rel == "0" and int(a) > int(b):
                    a, b = b, a
                ret.add((a, b, rel, step))
        return ret

    inferred_set = parse_rel(inferred_file)
    baseline_set = parse_rel(baseline_file)
    diff_set = inferred_set^baseline_set

    # diff_setA = inferred_set-baseline_set
    # diff_setB = baseline_set-inferred_set
    # for i,j in zip(sorted(diff_setA), sorted(diff_setB)):
    #     print(i)
    #     print(j)
    #     input()
    with open("./data/attack p2p N0+all 100 100.txt", "a") as f:
        f.write("----ATT----\n")
        f.write(f"rvs_provider = {rvs_provider}\n")
        f.write(f"rvs_customer = {rvs_customer}\n")
        f.write(f"att_announcer = {att_announcer}\n")
        f.write(f"att_source = {att_source}\n")
        f.write(f"rvs_p_ori_tg = {rvs_p_ori_tg}\n")
        f.write(f"rvs_c_ori_tg = {rvs_c_ori_tg}\n")
        # f.write(f"attack path = {attack_line_list}\n")
        flag = False
        for line in attack_line_list:
            for AS in line.strip().split(" "):
                if AS in clique:
                    flag = True
        f.write(f"has clique = {flag}\n")
        f.write(f"att len: {len(attack_line_list)}\n")
        flag = False
        for diff in diff_set:
            # p2c reverse
            # if rvs_provider == diff[0] and rvs_customer == diff[1] and diff[2] == '-1':
            #     flag = True
            #     break
            # p2p
            if rvs_provider == diff[0] and rvs_customer == diff[1] and diff[2] == '0':
                flag = True
                break
            if rvs_provider == diff[1] and rvs_customer == diff[0] and diff[2] == '0':
                flag = True
                break
            # end p2p
        for diff in diff_set:
            if rvs_provider == diff[1] and rvs_customer == diff[0]:
                f.write(f"att ori: {diff}\n")
        f.write(f"att successful: {flag}\n")
        if flag == False:
            if len(attack_line_list) < 100:
                f.write(f"att line: {attack_line_list}\n")
            f.write("att fail rel change: ")
            for diff in inferred_set|baseline_set:
                if rvs_provider in diff and rvs_customer in diff:
                    f.write(f"{diff}, ")
            f.write("\n")
        # f.write(f"diff set: {diff_set}\n")
        f.write(f"diff set len: {len(diff_set)}\n")
        f.write(f"Difference: {len(diff_set)/len(inferred_set):.2%}\n")

        diff_list = [0, 0, 0, 0]
        other_influenced = []
        for s in diff_set:
            if rvs_provider in s:
                diff_list[0] += 1
            if rvs_customer in s:
                diff_list[1] += 1
            if att_announcer in s:
                diff_list[2] += 1
            if att_source in s:
                diff_list[3] += 1
            if rvs_provider not in s and rvs_customer not in s and att_announcer not in s and att_source not in s:
                other_influenced.append(s)
        # f.write(f"\nother influenced relationships: {other_influenced}\n")
        f.write(f"other influenced rel len: {len(other_influenced)}\n")
        f.write(f"diff [rvs_provider, rvs_customer, att_announcer, att_source] = {diff_list}\n")
        f.write("\n")

# model_run()
rvs_provider = sys.argv[1]
rvs_customer = sys.argv[2]
att_announcer = sys.argv[3]
att_source = sys.argv[4]
gen_path = Gen_path(rvs_provider, rvs_customer, att_announcer, att_source)
attack_line_list, rvs_p_ori_tg, rvs_c_ori_tg = gen_path.gen_path()
del gen_path
model_run()
check_accuracy(rvs_provider, rvs_customer, att_announcer, att_source, rvs_p_ori_tg, rvs_c_ori_tg)
if os.path.exists("./data/inference-20241001.txt"):
    os.remove("./data/inference-20241001.txt")