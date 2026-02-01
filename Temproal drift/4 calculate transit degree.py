import os
import itertools

INPUT_DIR = "./"
ixp = [1200, 4635, 5507, 6695, 7606, 8714, 9355, 9439, 9560, 9722, 9989, 11670, 15645, 17819, 18398, 21371, 24029, 24115, 24990, 35054, 40633, 42476, 43100, 47886, 48850, 50384, 55818, 57463]
clique = [174, 209, 286, 701, 1239, 1299, 2828, 2914, 3257, 3320, 3356, 3491, 5511, 6453, 6461, 6762, 6830, 7018, 12956]

def expand_braces(tokens):
    expanded = []

    parts = []
    for tok in tokens:
        tok = tok.strip()
        if tok.startswith("{") and tok.endswith("}"):
            items = tok[1:-1].split(",")
            parts.append([item.strip() for item in items])
        else:
            parts.append([tok])

    for combo in itertools.product(*parts):
        expanded.append(list(combo))

    # print(f"tokens: {tokens}")
    # print(f"expanded: {expanded}")

    return expanded

def extract_triplets(tokens):
    triplets = []
    for i in range(len(tokens) - 2):
        triplets.append((tokens[i], tokens[i+1], tokens[i+2]))
    return triplets

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
            # print(f"reserved ASN: {asi} in {tokens}")
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

def process_files():
    for fname in os.listdir(INPUT_DIR):

        if fname.endswith(".TD.txt"):
            continue

        if not fname.endswith("clean.txt"):
            continue

        full_path = os.path.join(INPUT_DIR, fname)

        if not os.path.isfile(full_path):
            continue


        unique_triplets = set()

        with open(full_path, "r") as f:
            for line in f:
                tokens = line.strip().split()
                expanded_lines = expand_braces(tokens)
                for tok_list in expanded_lines:
                    flag, tokens = filter(tok_list)
                    if not flag:
                        continue
                    for t in extract_triplets(tok_list):
                        unique_triplets.add(t)

        neighbors = {}  # key=N2, value=set of neighbors

        for n1, n2, n3 in unique_triplets:
            if n2 not in neighbors:
                neighbors[n2] = set()
            neighbors[n2].add(n1)
            neighbors[n2].add(n3)

        out_path = full_path.replace(".txt", ".TD.txt")

        with open(out_path, "w") as f_out:
            for n2 in sorted(neighbors.keys()):
                neigh_list = sorted(neighbors[n2])
                # f_out.write(f"{n2} {len(neigh_list)} {' '.join(neigh_list)}\n")
                f_out.write(f"{n2} {len(neigh_list)}\n")


if __name__ == "__main__":
    process_files()
