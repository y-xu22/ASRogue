import os
import json
import seaborn as sns
import matplotlib.pyplot as plt
import math
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np

params = {
    'figure.figsize': (10, 5),
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

if os.path.exists("./limit_att_cost.json"):
    with open("./limit_att_cost.json", "r") as f:
        data = json.load(f)

data_list = []
for key in data.keys():
    data_list.append(data[key])

row_labels = ["L", "M", "S", "0"]
col_labels = ["L", "M", "S", "0"]

fig, axes = plt.subplots(1, 5, figsize=(28, 5))
plt.subplots_adjust(wspace=0.2)

def lighten_cmap(cmap, factor=0.3):
    new_colors = cmap(np.linspace(0, 1, 256))
    white = np.array([1, 1, 1, 1])
    new_colors = white * factor + new_colors * (1 - factor)
    return mcolors.LinearSegmentedColormap.from_list('light_coolwarm', new_colors)

vmin, vmax = 0, 1

base = plt.cm.coolwarm

light_coolwarm = lighten_cmap(base, factor=0.6)

for idx, (ax, data) in enumerate(zip(axes, data_list)):

    df = pd.DataFrame(data, columns=col_labels, index=row_labels)

    im = ax.pcolormesh(df, cmap=light_coolwarm,
                    edgecolors='w', linewidth=1,
                    vmin=vmin, vmax=vmax)

    for i in range(4):
        for j in range(4):
            value = data[i][j]
            ax.text(j + 0.5, i + 0.5, f"{value:.2f}",
                    ha='center', va='center', fontsize=20,
                    color='black' if value > 0.5 else 'black')

    ax.set_xticks(np.arange(0.5, 4.5, 1))
    ax.set_yticks(np.arange(0.5, 4.5, 1))
    ax.set_xticklabels(col_labels, rotation=45, ha='right')
    ax.set_yticklabels(row_labels)

    if idx == 0:
        ax.set_title(f"{idx+1} day , {(idx+1)*33} triplets")
    else:
        ax.set_title(f"{idx+1} days , {(idx+1)*33} triplets")
    ax.set_xlabel("Customer AS size")
    if idx == 0:
        ax.set_ylabel("Provider AS size")

    ax.invert_yaxis()
    ax.set_aspect('equal')

cbar = fig.colorbar(im, ax=axes, location='right', shrink=0.81, pad=0.02)

plt.savefig(f"./limit attack cost 33-165.pdf", bbox_inches="tight")