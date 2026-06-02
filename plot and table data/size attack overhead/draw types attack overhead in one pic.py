import os
import json
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

params = {
    'figure.figsize': (24, 4),           
    'font.family': ['Times New Roman'],
    'axes.titlesize': 20,
    'axes.labelsize': 20,
    'xtick.labelsize': 20,
    'ytick.labelsize': 20,
    'lines.linewidth': 3,
    'legend.fontsize': 20
}
plt.rcParams.update(params)

line_style = ["-", "dashed", "dashdot", (0, (1, 1))]

size_list = ["0", "Small", "Medium", "Large"]

attack_cost_log = {}
attack_cost = {}

if os.path.exists("./att_cost_log.json"):
    with open("./att_cost_log.json", "r") as f:
        attack_cost_log = json.load(f)

for key in attack_cost_log.keys():
    attack_cost[key] = [10**float(v) for v in attack_cost_log[key]]

fig, axes = plt.subplots(1, 4, figsize=(24, 4), sharey=False)

for idx, provider_size in enumerate(size_list):
    ax = axes[idx]

    for j, cust_size in enumerate(size_list):
        key = provider_size + " " + cust_size
        sns.ecdfplot(
            data=attack_cost[key],
            ax=ax,
            label=cust_size + " size",
            linestyle=line_style[j],
            log_scale=True
        )

    ax.set_xlabel("attack overhead")
    ax.set_ylabel("proportion")

    ax.set_xticks([1, 10, 100, 1000, 10000])
    ax.set_xticklabels([r'$1$', r'$10^1$', r'$10^2$', r'$10^3$', r'$10^4$'])

    ax.grid(True, linestyle='--', color='lightgray', linewidth=1)

    ax.text(
        0.5, -0.4,
        f"Provider is {provider_size}-size ASes",
        ha='center', va='top',
        fontsize=22,
        transform=ax.transAxes
    )

handles, labels = axes[0].get_legend_handles_labels()

prefix_handle = plt.Line2D([], [], linestyle='none', markersize=0, linewidth=0)

handles = [prefix_handle] + handles
labels = ["Customer size :"] + labels

fig.legend(
    handles, labels,
    loc='upper center',
    ncol=5,              
    frameon=False,
    bbox_to_anchor=(0.5, 1.12)
)


plt.tight_layout(rect=[0, 0, 1, 0.95])  

plt.savefig("./att_cost_all_in_one.pdf", bbox_inches="tight")
plt.close()
