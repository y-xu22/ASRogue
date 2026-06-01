import matplotlib.pyplot as plt
import seaborn as sns

params = {
    'figure.figsize': (10, 3.5),
    'font.family': ['Times New Roman'],
    'axes.titlesize': 24,
    'axes.labelsize': 24,
    'xtick.labelsize': 20,
    'ytick.labelsize': 20,
    'lines.linewidth': 4,
    'legend.fontsize': 20
}
plt.rcParams.update(params)

file_path1 = "./att_AS_size.txt"
file_path2 = "./att_AS_size_rvs.txt"

att_len_list = []
diff_set_len_list = []
rvs_c_ori_tg_list = []
rate_list = []

with open(file_path1, "r") as f:
    for line in f:
        line = line.strip()

        if line.startswith("att len:"):
            value = int(line.split(":")[1].strip())
            att_len_list.append(value)

        if line.startswith("diff set len:"):
            value = int(line.split(":")[1].strip())
            diff_set_len_list.append(value)
            
        if line.startswith("rvs_c_ori_tg"):
            value = int(line.split(" ")[-1].strip())
            rvs_c_ori_tg_list.append(value)

with open(file_path2, "r") as f:
    for line in f:
        line = line.strip()

        if line.startswith("att len:"):
            value = int(line.split(":")[1].strip())
            att_len_list.append(value)

        if line.startswith("diff set len:"):
            value = int(line.split(":")[1].strip())
            diff_set_len_list.append(value)
            
        if line.startswith("rvs_c_ori_tg"):
            value = int(line.split(" ")[-1].strip())
            rvs_c_ori_tg_list.append(value)

print("Parsed att len count:", len(att_len_list))
print("Parsed diff set len count:", len(diff_set_len_list))

for i in range(len(att_len_list)):
    if att_len_list[i] == 1:
        continue
    rate = diff_set_len_list[i]/att_len_list[i]/4 - 1
    if rate > 1:
        print(rate, diff_set_len_list[i], att_len_list[i])
        rate = 1
    rate_list.append(rate)

cnt = 0
for i in rate_list:
    if i < 0.4:
        cnt += 1
print(cnt/len(rate_list))

sns.ecdfplot(rate_list)

plt.xlabel("collateral impact")
plt.ylabel("proportion")
plt.grid(True, linestyle="--", alpha=0.5)

plt.annotate(
    "90% with collateral impact less than 0.4.",
    xy=(0.4, 0.9),          
    xytext=(0.43, 0.68),     
    textcoords='data',
    arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=8),
    fontsize=20,
    ha='left',
    va='center'
)

plt.text(
    0.98, 0.15,
    "* Values above 1 are clipped to 1.",
    ha='right', va='top',
    fontsize=20,
    transform=plt.gca().transAxes
)

plt.tight_layout()
plt.savefig(f"./collateral impact.pdf", bbox_inches="tight")
plt.close()
