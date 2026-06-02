import os
import json
import seaborn as sns
import matplotlib.pyplot as plt
import math
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np

params = {
    'figure.figsize': (10, 3),
    'font.family': ['Times New Roman'],
    'axes.titlesize': 24,
    'axes.labelsize': 24,
    'xtick.labelsize': 20,
    'ytick.labelsize': 20,
    'lines.linewidth': 4,
    'legend.fontsize': 20
}
plt.rcParams.update(params)

data = {}
with open("./random_noise.txt", "r") as f:
    lines = f.readlines()
    att_len = ""
    diff_len = ""
    for line in lines:
        if line.startswith("att len: "):
            att_len = line.strip().split(" ")[-1]
            if att_len not in data.keys():
                data[att_len] = []
        if line.startswith("diff set len: "):
            diff_len = line.strip().split(" ")[-1]
            data[att_len].append(int(diff_len))

x = []
y = []
yerr = []

for key in data.keys():
    arr = np.array(data[key])
    mean = np.mean(arr)
    std = np.std(arr, ddof=1)
    n = len(arr)

    ci95 = 1.96 * std / np.sqrt(n)

    x.append(int(key))
    y.append(mean)
    yerr.append(ci95)

plt.errorbar(
    x, y, yerr=yerr,
    fmt='-o',
    ecolor='red',
    elinewidth=2.5,
    capsize=4,
    capthick=2.5,
)

plt.xlabel('synthetically injected triplets')
plt.ylabel('difference')
plt.grid(True, linestyle='--', color='lightgray', linewidth=1)
plt.xticks(np.arange(10, 110, 10))
plt.yticks(np.arange(20, 260, 40))

plt.tight_layout()

plt.text(
    0.5, 0.14,
    "* Error bars represent 95% confidence intervals",
    ha='center', va='top',
    fontsize=20,
    transform=plt.gca().transAxes
)

plt.savefig(f"./noise.pdf", bbox_inches="tight")
