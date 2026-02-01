#!/usr/bin/env python
import click
import re
import bz2
from pathlib import Path
import sys
from tqdm import tqdm
from functools import cache
from collections import Counter
from heapq import heappush, heappop
import pickle

def add(key2set, key, ele):
    key2set.setdefault(key, set()).add(ele)

def add2(key2key2set, key0, key1, ele):
    add(key2key2set.setdefault(key0, dict()), key1, ele)

def incr2(key2key2cnt, key0, key1, key2):
    key2key2cnt.setdefault(key0, dict()).setdefault(key1, Counter())[key2] += 1

class ASRank:
    C2P =  1
    P2P =  0
    P2C = -1

    def __init__(self, ixp, clique, exclvps, verbose, input_path, output_path):
        self.ixp = set(re.findall(r"\d+", ixp))
        self.clique = set(re.findall(r"\d+", clique))
        self.exclvps = set(re.findall(r"\d+", exclvps))
        self.verbose = verbose
        self.input_path = Path(input_path).resolve()
        self.output_path = Path(output_path).resolve()

        self.vp2triplets = dict()
        self.vp2origins = dict()
        self.links = dict()
        self.trans = dict()
        self.trips = dict()
        self.upstr = dict()
        self.povup = dict()
        self.trip_z = dict()
        self.rels = dict()
        self.cone = dict()

        self.output_buf = []

        if self.output_path.exists():
            self.eprint(f"Override the existing output file: {self.output_path}")
            self.output_path.unlink()

    def eprint(self, *args, **kwargs):
        if self.verbose:
            print(*args, file=sys.stderr, **kwargs)

    def output(self, content, end="\n", verbose=False, flush=False, limit=10000):
        self.output_buf.append(content+end)
        if flush or len(self.output_buf) > limit:
            with open(self.output_path, "a") as fd:
                fd.write("".join(self.output_buf))
            self.output_buf = []
        if verbose: self.eprint(content, end=end)

    def clean_path(self, line):
        _, path, _, _, _ = line.strip().split(" ")
        path = path.split("|")

        # skip over path if the VP is to be excluded.
        if path[0] in self.exclvps: return ()

        clean_path = []
        asn_set = set()
        clique_seen = False

        for asn in path:
            # reserved ASN (last updated: 2024-04-10)
            # https://www.iana.org/assignments/as-numbers/as-numbers.xhtml
            # https://www.iana.org/assignments/as-numbers/as-numbers.xhtml
            asi = int(asn)
            if (asi == 0 or asi == 112 or asi == 23456 or
               (asi >= 64496  and asi <= 131071) or
               (asi >= 153914 and asi <= 196607) or
               (asi >= 216476 and asi <= 262143) or
               (asi >= 274845 and asi <= 327679) or
               (asi >= 329728 and asi <= 393215) or
                asi >= 402333):
                self.eprint(f"reserved ASN: {asi} in {line.strip()}")
                return ()

            # skip over IXP ASes.
            if asn in self.ixp:
                continue

            # loop detection
            if asn in asn_set:
                if clean_path[-1] == asn:
                    continue
                else:
                    self.eprint(f"looped ASN: {asn} in {line.strip()}")
                    return ()

            # detect and discard invalid paths (probably caused by poisoning)
            # where a clique AS is inserted into a poisoned path.
            if asn in self.clique:
                if clique_seen and clean_path[-1] not in self.clique:
                    self.eprint(f"clique poisoning: {asn} in {line.strip()}")
                    return ()
                clique_seen = True

            asn_set.add(asn)
            clean_path.append(asn)

        return clean_path

    def gen_clean_file(self):
        clean_file = Path(f"{self.input_path}.clean")
        if not clean_file.exists():
            with open(clean_file, "w") as output_fd:
                if self.input_path.suffix == ".bz2":
                    opener = lambda f: bz2.open(f, "rt")
                else:
                    opener = lambda f: open(f, "r")

                with opener(self.input_path) as input_fd:
                    for line in tqdm(input_fd, desc="clean path", disable=not self.verbose):
                        path = self.clean_path(line)
                        if path: output_fd.write(" ".join(path)+"\n")
        else:
             self.eprint("Use clean path cache")
        return clean_file

    def read_paths(self):
        clean_file = self.gen_clean_file()

        vp2origins = self.vp2origins
        vp2triplets = self.vp2triplets
        links = self.links
        trans = self.trans
        trips = self.trips
        upstr = self.upstr
        povup = self.povup
        trip_z = self.trip_z

        def parse_line(line):
            path = line.strip().split(" ")

            if len(path) < 2: return

            add(vp2origins, path[0], path[-1]) 

            if len(path) == 3:
                add2(vp2triplets, path[0], path[1], path[2])

            add(links, path[0], path[1])
            add(links, path[1], path[0])
            for a, x, b in zip(path[:-2], path[1:-1], path[2:]):
                add(links, x, b)
                add(links, b, x)
                add(trans, x, a)
                add(trans, x, b)
                incr2(trips, a, x, b)
                incr2(trips, b, x, a)
                add2(upstr, b, x, a)
                add2(povup, x, a, b)

            if len(path) >= 3:
                add2(trip_z, a, x, b)

        with open(clean_file, "r") as fd:
            for line in tqdm(fd, desc="parse path", disable=not self.verbose): parse_line(line)

        # attack_line_list = ['18403 3356 6939 39647 200020 63737 ', '18403 44723 39647 273474 63737 ', '18403 400730 39647 27606 63737 ', '18403 56068 39647 268800 63737 ', '18403 43031 39647 206674 63737 ', '18403 29626 39647 211657 63737 ', '18403 24517 39647 29510 63737 ', '18403 58097 39647 50471 63737 ', '18403 14754 39647 210409 63737 ', '18403 205501 39647 39220 63737 ', '18403 29197 39647 2648 63737 ', '18403 266214 39647 9131 63737 ', '18403 200147 39647 145772 63737 ', '18403 53904 39647 329279 63737 ', '18403 57954 39647 263921 63737 ', '18403 208922 39647 8947 63737 ', '18403 34167 39647 399611 63737 ', '18403 135468 39647 214436 63737 ', '18403 205911 39647 136917 63737 ']
        # for line in attack_line_list: parse_line(line)

        for asn in self.clique: assert asn in links

        return self

    def add_paths(self, lines):
        vp2origins = self.vp2origins
        vp2triplets = self.vp2triplets
        links = self.links
        trans = self.trans
        trips = self.trips
        upstr = self.upstr
        povup = self.povup
        trip_z = self.trip_z

        def parse_line(line):
            path = line.strip().split(" ")

            if len(path) < 2: return

            add(vp2origins, path[0], path[-1]) 

            if len(path) == 3:
                add2(vp2triplets, path[0], path[1], path[2])

            add(links, path[0], path[1])
            add(links, path[1], path[0])
            for a, x, b in zip(path[:-2], path[1:-1], path[2:]):
                add(links, x, b)
                add(links, b, x)
                add(trans, x, a)
                add(trans, x, b)
                incr2(trips, a, x, b)
                incr2(trips, b, x, a)
                add2(upstr, b, x, a)
                add2(povup, x, a, b)

            if len(path) >= 3:
                add2(trip_z, a, x, b)

        for line in lines: parse_line(line)

        for asn in self.clique: assert asn in links

        return self

    def get_rel(self, a, b):
        if a in self.rels:
            for rel, ngbrs in self.rels[a].items():
                if b in ngbrs: return rel
        return None

    def get_ngbrs(self, asn, rel):
        return self.rels.setdefault(asn, dict()).setdefault(rel, set())

    def get_cone(self, a):
        return self.cone.setdefault(a, {a})

    def update_cone(self, a, b):
        # assert self.get_rel(a, b) == self.P2C
        to_merge = self.get_cone(b)
        queue = [a]
        while queue:
            current_cone = self.get_cone(queue.pop(0))
            if b in current_cone:
                continue
            current_cone.update(to_merge)
            for prov in self.get_ngbrs(a, self.C2P):
                queue.append(prov)

    def update_rel(self, a, b, rel):
        assert self.get_rel(a, b) is None, \
            f"Fatal: a relationship already exists for {a} and {b}"

        self.output(f"{a}|{b}|{rel}")

        add2(self.rels, a, +rel, b)
        add2(self.rels, b, -rel, a)

        if rel == self.P2C:
            self.update_cone(a, b)

    def transit_degree(self, asn):
        return len(self.trans[asn]) if asn in self.trans else 0

    def global_degree(self, asn):
        return len(self.links[asn])

    @cache
    def sort_key(self, asn):
        k0 = asn in self.clique
        k1 = self.transit_degree(asn)
        k2 = self.global_degree(asn)
        k3 = -int(asn)
        return k0, k1, k2, k3

    def iter_asn(self):
        for asn in self.links: yield asn

    def upstr_check(self, x, y, z):
        return x in self.upstr and y in self.upstr[x] and z in self.upstr[x][y]

    def trips_check(self, x, y, z):
        return x in self.trips and y in self.trips[x] and z in self.trips[x][y]

    def p2c_ok(self, x, y):
        return y not in self.clique and x not in self.get_cone(y)

    def select_providers(self, x):
        def rule(y, x, rel_yz): # does Y pass the route from X to a provider/peer Z? (Z>Y?X or Z-Y?X)
            for z in self.get_ngbrs(y, rel_yz):
                if self.upstr_check(x, y, z) and self.p2c_ok(y, x):
                    self.update_rel(y, x, self.P2C)
                    return True
            return False

        for y in sorted(self.links[x], key=self.sort_key, reverse=True):
            if self.get_rel(x, y) is not None: continue
            rule(y, x, self.C2P) or rule(y, x, self.P2P)

    def provider_to_larger_customer(self):
        # collect a list of x:y:z triplets where x is a provider of y but no
        # relationship has been inferred for y:z because z has a larger transit
        # degree than y.  rank the triplets by the number of paths they appear
        # in, and then assign p2c relationships between y and z, and then
        # assign p2c relationships for y:z:zz triplets subsequent to that.
        # this part focuses only on cases where y has a smaller transit degree
        # because these are the only p2c relationships that would have been missed
        # in the first part.
        hp = [] # heap stores the candidates

        def hp_push(priority, item):
            heappush(hp, (priority, item))

        def hp_pop():
            return heappop(hp)[1]

        for x in self.trip_z:
            for y in self.trip_z[x]:
                if self.get_rel(x, y) != self.P2C: continue
                for z in self.trip_z[x][y]:
                    if self.get_rel(y, z) is not None: continue
                    if self.sort_key(y)[1] > self.sort_key(z)[1]: continue
                    freq = self.trips[x][y][z]
                    if freq < 3: continue
                    if not self.p2c_ok(y, z): continue
                    hp_push(-freq, (y, z))

        while hp:
            y, z = hp_pop()

            if self.get_rel(y, z) is not None: continue
            if not self.p2c_ok(y, z): continue
            self.update_rel(y, z, self.P2C)

            for zz in self.links[z]:
                if self.get_rel(z, zz) is not None: continue
                if not self.upstr_check(zz, z, y): continue

                if self.sort_key(z)[1] < self.sort_key(zz)[1]:
                    freq = self.trips[y][z][zz]
                    if freq < 3: continue
                    if not self.p2c_ok(z, zz): continue
                    hp_push(-freq, (z, zz))
                elif self.p2c_ok(z, zz):
                    self.update_rel(z, zz, self.P2C)

    def provider_less_network(self, x):
        for y in sorted(self.links[x], key=self.sort_key, reverse=True):
            if y not in self.trips: continue
            if x not in self.trips[y]: continue
            if self.get_rel(x, y) is not None: continue

            self.update_rel(x, y, self.P2P)

            for z in self.trips[y][x]:
                if self.get_rel(x, z) is not None: continue
                if not self.p2c_ok(x, z): continue

                self.update_rel(x, z, self.P2C)

                for zz in self.links[z]:
                    if self.get_rel(z, zz) is not None: continue
                    if not self.upstr_check(zz, z, x): continue
                    if self.sort_key(zz)[1] >= self.sort_key(z)[1]: continue
                    if not self.p2c_ok(z, zz): continue
                    self.update_rel(z, zz, self.P2C)

    def fold_p2p(self, x):
        # this method tries to fold sequences of p2p links
        lr_set = set()
        l_set = set()
        r_set = set()

        # determine candidate links that need to be folded.
        for l in self.povup[x]:
            if self.get_rel(x, l) is not None and self.get_rel(x, l) != self.P2P:
                continue

            # l?-x
            skip = False
            for r in self.get_ngbrs(x, self.C2P):
                if self.trips_check(l, x, r): # There exists (l?-x<r)
                    skip = True
                    break

            if skip: continue

            for r in self.povup[x][l]:
                if self.get_rel(x, r) is None: # (l?-x?r)
                    lr_set.add((l, r))
                    l_set.add(l)
                    r_set.add(r)

        if not lr_set: return

        r_cnt = Counter()
        for l, r in lr_set:
            if l in r_set or r in l_set: continue
            r_cnt[r] += 1

        for r,_ in r_cnt.most_common():
            if self.sort_key(x)[1] < self.sort_key(r)[1]: continue
            if not self.p2c_ok(x, r): continue
            if self.get_rel(x, r) is not None: continue
            self.update_rel(x, r, self.P2C)

            if r not in self.povup: continue
            if x not in self.povup[r]: continue
            for rr in self.povup[r][x]:
                if self.get_rel(r, rr) is not None: continue
                if self.sort_key(r)[1] < self.sort_key(rr)[1]: continue
                if not self.p2c_ok(r, rr): continue
                self.update_rel(r, rr, self.P2C)

    def infer_rel(self):

        step = 1

        # set peering in the clique
        self.output(f"# step {step}: set peering in clique", verbose=self.verbose); step += 1
        clique_sorted = sorted(self.clique)
        for idx, x in enumerate(clique_sorted):
            for y in clique_sorted[idx+1:]:
                self.update_rel(x, y, self.P2P)

        # assign providers. these inferences have a 99.4% PPV.
        self.output(f"# step {step}: initial provider assignment", verbose=self.verbose); step += 1
        asn_sorted = sorted(self.iter_asn(), key=self.sort_key, reverse=True)
        for asn in asn_sorted[len(clique_sorted):]:
            self.select_providers(asn)

        # assign providers for stub ASes (transit degree zero), using the
        # assumption that a triplet observed by a VP which only supplies
        # routes to 5% of origin ASes is giving us routes from its customers
        # and peers, not its providers.  these inferences have a 100% PPV
        self.output(f"# step {step}: providers for stub ASes #1", verbose=self.verbose); step += 1
        for x in self.vp2origins:
            if len(self.vp2origins[x]) * 50 > len(asn_sorted): continue
            if x not in self.vp2triplets: continue
            for y in self.vp2triplets[x]:
                for z in self.vp2triplets[x][y]:
                    if self.get_rel(y, z) is None and self.sort_key(z)[1] == 0:
                        self.update_rel(y, z, self.P2C)

        self.output(f"# step {step}: provider to larger customer", verbose=self.verbose); step += 1
        self.provider_to_larger_customer();

        # assemble a list of ASes that have no provider inferred, yet are not
        # part of the clique.  these are likely to be regional or R&E networks
        # that have no provider but do have customers.
        self.output(f"# step {step}: provider-less networks", verbose=self.verbose); step += 1
        for x in asn_sorted[len(clique_sorted):]:
            if self.get_ngbrs(x, self.C2P) or self.sort_key(x)[1] < 10: continue
            self.provider_less_network(x)

        self.output(f"# step {step}: c2p for stub-clique relationships", verbose=self.verbose); step += 1
        for x in clique_sorted:
            for y in self.links[x]:
                if self.sort_key(y)[1] == 0 and self.get_rel(x, y) is None:
                    self.update_rel(x, y, self.P2C)

        self.output(f"# step {step}: fold p2p links", verbose=self.verbose); step += 1
        for x in asn_sorted:
            if self.sort_key(x)[1] == 0: break
            self.fold_p2p(x)

        self.output(f"# step {step}: everything else is p2p", verbose=self.verbose); step += 1
        for x in self.links:
            for y in self.links[x]:
                if self.get_rel(x, y) is None:
                    self.update_rel(x, y, self.P2P)

        self.output("", end="", flush=True)

    def __call__(self):
        self.read_paths().infer_rel()
        return self

    def dump_model(self, output_path):
        pickle.dump(self, open(output_path, "wb"), protocol=5)
        return self

@click.command()
@click.option("--ixp", type=str, default="", help="IXP string")
@click.option("--clique", type=str, default="", help="Clique string")
@click.option("--exclvps", type=str, default="", help="Exclvps string")
@click.option("--verbose", is_flag=True, help="Verbose output")
@click.argument("input-path", type=click.Path(exists=True))
@click.argument("output-path", type=click.Path())
def main(ixp, clique, exclvps, verbose, input_path, output_path):
    """Python version of the asrank.pl script."""
    ASRank(ixp, clique, exclvps, verbose, input_path, output_path)()

if __name__ == "__main__":
    main()
