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

new_buffers = {
    "buffer_0": [89.76, 88.42, 87.14, 86.35, 86.32, 86.47, 87.68, 87.86, 86.37, 86.0, 85.08],
    "buffer_1": [92.0, 91.97, 90.99, 90.65, 90.29, 90.16, 91.03, 91.27, 90.21, 89.63, 88.61],
    "buffer_2": [92.88, 92.82, 92.3, 92.23, 91.81, 91.78, 92.45, 92.47, 91.83, 91.6, 90.44],
    "buffer_5": [93.77, 93.58, 93.39, 93.12, 93.06, 93.13, 93.29, 93.58, 93.16, 92.69, 92.44],
    "buffer_10": [94.43, 94.41, 94.19, 93.88, 93.85, 93.81, 93.89, 93.99, 94.39, 93.3, 93.82],
    "buffer_15": [94.74, 94.71, 94.37, 94.29, 94.11, 94.07, 94.17, 94.28, 94.75, 94.22, 94.08],
}

for name, values in new_buffers.items():
    print(name, values)

plt.plot(new_buffers["buffer_0"], label = "no buffer", marker='o', linestyle='-')
plt.plot(new_buffers["buffer_1"], label = "buffer=1", marker='o', linestyle='dashed')
plt.plot(new_buffers["buffer_2"], label = "buffer=2", marker='o', linestyle='dashdot')
plt.plot(new_buffers["buffer_5"], label = "buffer=5", marker='o', linestyle=(0, (1, 1)))
plt.plot(new_buffers["buffer_10"], label = "buffer=10", marker='o', linestyle=(0, (5, 5)))
plt.plot(new_buffers["buffer_15"], label = "buffer=15", marker='o', linestyle=(0, (3, 1, 1, 1)))
plt.xlabel("# of days before ASRank inference window")
plt.ylabel("success rate (%)")
plt.yticks(range(70, 105, 5))
plt.xticks(range(len(new_buffers["buffer_0"])),["0", "1", "2", "3", "4", "5", "6", "7", "14", "21", "30"])
plt.grid(True, linestyle='--', color='lightgray', linewidth=1)
plt.legend(ncol = 3)
plt.savefig(f"./rate over time.pdf", bbox_inches="tight")