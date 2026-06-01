import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

params = {
    'figure.figsize': (12, 5),
    'font.family': ['Times New Roman'],
    'axes.titlesize': 44,
    'axes.labelsize': 44,
    'xtick.labelsize': 40,
    'ytick.labelsize': 40,
    'lines.linewidth': 4,
    'legend.fontsize': 40
}
plt.rcParams.update(params)

data = [[0.7, 0.98, 1, 1],
        [0.82, 0.98, 1, 0.99],
        [0.82, 1, 1, 1],
        [0.92, 1, 1, 1]]

df = pd.DataFrame(data, columns= ["Large", "Med.", "Small", "0-Size"], index= ["Large", "Med.", "Small", "0-Size"])

for i in range(len(data)): 
    for j in range(len(data[i])): 
        plt.text( j+0.5, i+0.5, f"{data[i][j]:.2f}", 
                ha='center', va='center', fontsize=40,
                color='black' if data[i][j] > 0.5 else 'white' 
                )

base = plt.cm.coolwarm

def lighten_cmap(cmap, factor=0.3):
    new_colors = cmap(np.linspace(0, 1, 256))
    white = np.array([1, 1, 1, 1])
    new_colors = white * factor + new_colors * (1 - factor)
    return mcolors.LinearSegmentedColormap.from_list('light_coolwarm', new_colors)

light_coolwarm = lighten_cmap(base, factor=0.6)

plt.pcolormesh(df, cmap=light_coolwarm, edgecolors='w', linewidth=2, vmin=0, vmax=1)
plt.xticks(np.arange(0.5, 4.5, 1), df.columns)
plt.yticks(np.arange(0.5, 4.5, 1), df.index)
plt.ylabel("Provider AS size")
plt.xlabel("Customer AS size")
plt.colorbar()  
plt.gca().invert_yaxis() 
plt.savefig(f"./attack success rate.pdf", bbox_inches="tight")