import os
import re
from datetime import datetime, timedelta
import itertools

INPUT_DIR = "./BGP RIB txt"
ixp = [1200, 4635, 5507, 6695, 7606, 8714, 9355, 9439, 9560, 9722, 9989, 11670, 15645, 17819, 18398, 21371, 24029, 24115, 24990, 35054, 40633, 42476, 43100, 47886, 48850, 50384, 55818, 57463]
clique = [174, 209, 286, 701, 1239, 1299, 2828, 2914, 3257, 3320, 3356, 3491, 5511, 6453, 6461, 6762, 6830, 7018, 12956]


def parse_date_from_filename(fname):
    m = re.match(r"bgp_rib_(\d{8})\.txt$", fname)
    if not m:
        return None
    return datetime.strptime(m.group(1), "%Y%m%d")


def expand_braces(tokens):
    parts = []
    for tok in tokens:
        tok = tok.strip()
        if tok.startswith("{") and tok.endswith("}"):
            items = tok[1:-1].split(",")
            parts.append([item.strip() for item in items])
        else:
            parts.append([tok])

    expanded = []
    for combo in itertools.product(*parts):
        expanded.append(list(combo))
    return expanded


def extract_triplets(tokens):
    return [(tokens[i], tokens[i+1], tokens[i+2])
            for i in range(len(tokens) - 2)]

def filter(tokens):
    if len(tokens) < 3:
        return False, []

    clean_path = []
    asn_set = set()
    clique_seen = False

    for asn in tokens:
        # reserved ASN (last updated: 2024-04-10)
        # https://www.iana.org/assignments/as-numbers/as-numbers.xhtml
        # https://www.iana.org/assignments/as-numbers/as-numbers.xhtml
        try:
            asi = int(asn)
        except (ValueError, TypeError): 
            print(tokens)
            return False, []  
        if (asi == 0 or asi == 112 or asi == 23456 or
            (asi >= 64496  and asi <= 131071) or
            (asi >= 153914 and asi <= 196607) or
            (asi >= 216476 and asi <= 262143) or
            (asi >= 274845 and asi <= 327679) or
            (asi >= 329728 and asi <= 393215) or
            asi >= 402333):
            return False, []

        # skip over IXP ASes.
        if asn in ixp:
            continue

        # loop detection
        if asn in asn_set:
            if clean_path[-1] == asn:
                continue
            else:
                # print(f"looped ASN: {asn} in {tokens}")
                return False, []

        # detect and discard invalid paths (probably caused by poisoning)
        # where a clique AS is inserted into a poisoned path.
        if asn in clique:
            if clique_seen and clean_path[-1] not in clique:
                print(f"clique poisoning: {asn} in {tokens}")
                return False, []
            clique_seen = True

        asn_set.add(asn)
        clean_path.append(asn)
    return True, clean_path

def process_5day_window(files):
    triplet_set = set()

    for path in files:
        with open(path, "r") as f:
            for line in f:
                tokens = line.strip().split()
                if len(tokens) < 3:
                    continue

                expanded_lines = expand_braces(tokens)

                for tok_list in expanded_lines:
                    flag, tok_list = filter(tok_list)
                    if not flag:
                        continue
                    for t in extract_triplets(tok_list):
                        triplet_set.add(t)

    return triplet_set


def compute_neighbors(triplets):
    neighbors = {}

    for n1, n2, n3 in triplets:
        if n2 not in neighbors:
            neighbors[n2] = set()
        neighbors[n2].add(n1)
        neighbors[n2].add(n3)

    return neighbors


def main():
    all_files = []
    for fname in os.listdir(INPUT_DIR):
        full_path = os.path.join(INPUT_DIR, fname)
        if not os.path.isfile(full_path):
            continue

        date_obj = parse_date_from_filename(fname)
        if date_obj:
            all_files.append((date_obj, full_path))

    all_files.sort(key=lambda x: x[0])

    i = 0
    n = len(all_files)

    while i < n:
        start_date = all_files[i][0]
        end_date = start_date + timedelta(days=4)

        window_files = []
        j = i
        while j < n and all_files[j][0] <= end_date:
            window_files.append(all_files[j][1])
            j += 1

        expected_dates = {start_date + timedelta(days=k) for k in range(5)}
        actual_dates = {d for d, _ in all_files[i:j]}

        if expected_dates != actual_dates:
            i += 1
            continue

        print(f"start date: {start_date}")

        triplets = process_5day_window(window_files)

        neighbors = compute_neighbors(triplets)

        out_name = f"bgp_rib_{start_date.strftime('%Y%m%d')}_5d.TD.txt"
        out_path = os.path.join(INPUT_DIR, out_name)

        with open(out_path, "w") as f_out:
            for n2 in sorted(neighbors.keys()):
                neigh_list = sorted(neighbors[n2])
                # f_out.write(f"{n2} {len(neigh_list)} {' '.join(neigh_list)}\n")
                f_out.write(f"{n2} {len(neigh_list)}\n")

        i += 1


if __name__ == "__main__":
    main()
