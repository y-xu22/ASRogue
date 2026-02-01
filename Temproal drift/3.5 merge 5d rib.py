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


def load_paths_from_file(filepath):
    result = set()

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            tokens = line.split()
            expanded_lines = expand_braces(tokens)

            for tok_list in expanded_lines:
                result.add(" ".join(tok_list))

    return result


def filter_tokens(tokens):
    if len(tokens) < 3:
        return []

    clean_path = []
    asn_set = set()
    clique_seen = False

    for asn in tokens:
        # reserved ASN (last updated: 2024-04-10)
        # https://www.iana.org/assignments/as-numbers/as-numbers.xhtml
        # https://www.iana.org/assignments/as-numbers/as-numbers.xhtml
        try:
            asi = int(asn)
        except (ValueError, TypeError): # 会有路由聚合，即 a b {c d e}
            print(tokens)
            return []   # 或者你想要的默认值
        if (asi == 0 or asi == 112 or asi == 23456 or
            (asi >= 64496  and asi <= 131071) or
            (asi >= 153914 and asi <= 196607) or
            (asi >= 216476 and asi <= 262143) or
            (asi >= 274845 and asi <= 327679) or
            (asi >= 329728 and asi <= 393215) or
            asi >= 402333):
            # print(f"reserved ASN: {asi} in {tokens}")
            return []

        # skip over IXP ASes.
        if asn in ixp:
            continue

        # loop detection
        if asn in asn_set:
            if clean_path[-1] == asn:
                continue
            else:
                # print(f"looped ASN: {asn} in {tokens}")
                return []

        # detect and discard invalid paths (probably caused by poisoning)
        # where a clique AS is inserted into a poisoned path.
        if asn in clique:
            if clique_seen and clean_path[-1] not in clique:
                print(f"clique poisoning: {asn} in {tokens}")
                return []
            clique_seen = True

        asn_set.add(asn)
        clean_path.append(asn)
    return tokens


def main():
    files = []
    for fname in os.listdir(INPUT_DIR):
        full_path = os.path.join(INPUT_DIR, fname)
        if not os.path.isfile(full_path):
            continue

        date_obj = parse_date_from_filename(fname)
        if date_obj:
            files.append((date_obj, full_path))

    files.sort(key=lambda x: x[0])

    n = len(files)
    i = n-5

    while i < n:
        start_date = files[i][0]
        end_date = start_date + timedelta(days=4)

        window_files = []
        j = i
        while j < n and files[j][0] <= end_date:
            window_files.append(files[j])
            j += 1

        expected = {start_date + timedelta(days=k) for k in range(5)}
        actual = {d for d, _ in window_files}

        if expected != actual:
            i += 1
            continue  
        print(f"bgp_rib_{start_date.strftime('%Y%m%d')}_5d.txt")

        all_paths = set()
        for _, path in window_files:
            paths = load_paths_from_file(path)
            all_paths |= paths

        filtered_paths = set()
        for p in all_paths:
            tokens = p.split()

            new_tokens = filter_tokens(tokens)  
            if new_tokens:  
                filtered_paths.add(" ".join(new_tokens))
        out_name = f"bgp_rib_{start_date.strftime('%Y%m%d')}_5d.txt"
        out_path = os.path.join(INPUT_DIR, out_name)

        with open(out_path, "w") as f_out:
            for p in sorted(filtered_paths):
                f_out.write(p + "\n")

        i += 1


if __name__ == "__main__":
    main()
