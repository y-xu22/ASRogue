import os
import json
import seaborn as sns
import matplotlib.pyplot as plt
import math
import matplotlib.colors as mcolors
import pandas as pd

params = {
    'figure.figsize': (10, 3),           
    'figure.figsize': (10, 3),
    'font.family': ['Times New Roman'],
    'axes.titlesize': 24,
    'axes.labelsize': 24,
    'xtick.labelsize': 20,
    'ytick.labelsize': 20,
    'lines.linewidth': 4,
    'legend.fontsize': 20
}
line_style = ["-", "dashed", "dashdot", (0, (1, 1))]
line_style = ["-", "dashed", "dashdot", (0, (1, 1))]
plt.rcParams.update(params)

tg = []
tg_log10 = []
if os.path.exists("./tg.json"):
    with open("./tg.json", "r") as f:
        tg = json.load(f)
if os.path.exists("./tg_log10.json"):
    with open("./tg_log10.json", "r") as f:
        tg_log10 = json.load(f)

print((83913-len(tg_log10))/83913)

for i in range(83913-len(tg_log10)):
    tg_log10.append(0)
    tg.append(1)

cnt = 0
for i in tg:
    if i > 100:
        cnt += 1
print(1 - cnt/83913)

sns.ecdfplot(data=tg, log_scale=True)
plt.xlabel("transit degree")
plt.ylabel("proportion")
plt.xticks([1, 10, 100, 1000, 10000], [r'$1$', r'$10^1$', r'$10^2$', r'$10^3$', r'$10^4$'])
plt.axvline(x=100, color='red', linestyle='--', linewidth=1.5)
plt.annotate(
            'transit degree of more than\n98% ASes is less than 100',
            xy=(100, 0.98),
            xytext=(200, 0.6),
            arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
            fontsize=20,
            color='black')
plt.text(
        1.3, 0.05,
        "* ASes with a transit degree\nof 0 are marked as 1",
        fontsize=20, color='black',
        ha='left', va='bottom'
        )
plt.grid(True, linestyle='--', color='lightgray', linewidth=1)
plt.tight_layout()
plt.savefig(f"./transit degree.pdf", bbox_inches="tight")