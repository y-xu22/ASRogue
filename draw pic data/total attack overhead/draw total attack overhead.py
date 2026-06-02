import os
import json
import seaborn as sns
import matplotlib.pyplot as plt
import math
import matplotlib.colors as mcolors
import pandas as pd

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
line_style = ["-", "dashed", "dashdot", (0, (1, 1))]

plt.rcParams.update(params)

tg = []
tg_log10 = []
if os.path.exists("./tg_diff.json"):
    with open("./tg_diff.json", "r") as f:
        tg_log10 = json.load(f)

for i in tg_log10:
    tg.append(10**i)

cnt = 0
for i in tg:
    if i <= 100:
        cnt += 1
print(cnt, cnt/len(tg))

sns.ecdfplot(data=tg, log_scale=True)
plt.xlabel("attack overhead")
plt.ylabel("proportion")
plt.xticks([1, 10, 100, 1000, 10000], [r'$1$', r'$10^1$', r'$10^2$', r'$10^3$', r'$10^4$'])

plt.annotate(
    "100 attack triplets, \nreversing 52.9% of results.",
    xy=(100, 0.529),              
    xytext=(150, 0.25),           
    textcoords='data',
    arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
    fontsize=20,
    ha='left',
    va='center'
)

plt.grid(True, linestyle='--', color='lightgray', linewidth=1)
plt.savefig(f"./total attack overhead.pdf", bbox_inches="tight")