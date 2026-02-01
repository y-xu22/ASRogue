import os
import glob
import math

# P2C_FILE = "./20241001.as-rel.txt"
P2C_FILE = "./inference-20241001_ori.txt"
BASE_FILE = "./20241001.all-paths.bz2.TD.txt"
TD_DIR = "./BGP 5d TD"

clique = [174, 209, 286, 701, 1239, 1299, 2828, 2914, 3257, 3320, 3356, 3491, 5511, 6453, 6461, 6762, 6830, 7018, 12956]

def load_td_file(path):
    mapping = {}
    with open(path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            n1, n2 = parts
            if not n2.lstrip("-").isdigit():
                continue
            mapping[n1] = int(n2)
    return mapping


def process():
    base_map = load_td_file(BASE_FILE)

    td_files = sorted(glob.glob(os.path.join(TD_DIR, "*.TD.txt")))
    td_data = {path: load_td_file(path) for path in td_files}

    success_count = {path: 0 for path in td_files}
    total_count = 0

    with open(P2C_FILE, "r") as f:
        for line in f:
            # parts = line.strip().split()
            parts = line.strip().split("|")
            if len(parts) < 2:
                continue

            A1, A2, rel = parts[0], parts[1], parts[2]

            # clique
            # if int(A1) in clique or int(A2) in clique:
            #     continue

            # p2p
            # if rel == "0":
            #     continue

            if not A1.isdigit() or not A2.isdigit():
                continue

            if A1 not in base_map:
                base_map[A1] = 0
            if A2 not in base_map:
                base_map[A2] = 0

            V1 = base_map[A1]
            V2 = base_map[A2]
            D1 = V1 - V2

            total_count += 1

            for path, mapping in td_data.items():
                if A1 not in mapping:
                    mapping[A1] = 0
                if A2 not in mapping:
                    mapping[A2] = 0

                v1 = mapping[A1]
                v2 = mapping[A2]
                D2 = v1 - v2

                if rel == "0":
                    success_count[path] += 1
                    continue

                if D1 <= 0:
                    success_count[path] += 1
                elif 0 < D1 <= D2:
                    success_count[path] += 1

    for path in td_files:
        rate = success_count[path] / total_count if total_count > 0 else 0
        print(f"{os.path.basename(path)}: success={success_count[path]}, "
              f"total={total_count}, rate={rate:.4f}")


if __name__ == "__main__":
    process()
