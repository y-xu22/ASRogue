import matplotlib.pyplot as plt


params = {
    'figure.figsize': (10, 4),
    'font.family': ['Times New Roman'],
    'axes.titlesize': 24,
    'axes.labelsize': 24,
    'xtick.labelsize': 20,
    'ytick.labelsize': 20,
    'lines.linewidth': 4,
    'legend.fontsize': 20
}
plt.rcParams.update(params)

data = [57, 64, 55, 65, 39, 40, 54, 50, 65, 59, 26]

fig, ax = plt.subplots() 

bars = ax.bar(range(15, 26, 1), data, color='skyblue')

for bar in bars:
    yval = bar.get_height() 
    ax.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{yval}', ha='center', va='bottom', fontsize=18)
plt.xticks(range(15, 26, 1))
plt.yticks(range(0, 80, 10))
plt.xlabel('year 20XX')
plt.ylabel('# of papers')
ax.set_ylim(bottom=20)

plt.tight_layout()

plt.savefig(f"./number of papers.pdf", bbox_inches="tight")