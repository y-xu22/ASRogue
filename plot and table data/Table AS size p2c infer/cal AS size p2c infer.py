AS_size_dict = {}
size = ["0", "S", "M", "L"]

clique = ["174", "209", "286", "701", "1239", "1299", "2828", "2914", "3257", "3320", "3356", "3491", "5511", "6453", "6461", "6762", "6830", "7018", "12956"]

def locate_AS(AS, dic):
    loc = ""
    if AS in dic["0"]:
        loc = "0"
    elif AS in dic["S"]:
        loc = "S"
    elif AS in dic["M"]:
        loc = "M"
    elif AS in dic["L"]:
        loc = "L"
    return loc

with open("./AS_size.txt", "r") as f:
    cnt = 0
    flag = False
    for line in f:
        if flag:
            flag = False
            AS_size_dict[size[cnt]] = line.strip().split()
            cnt += 1
        if line.startswith("AS"):
            flag = True

p2c_infer = {}
for i in size:
    for j in size:
        p2c_infer[(i, j)] = 0

total = 0

with open("./all rel TD.txt", "r") as f:
    for line in f:
        if line.startswith("p"):
            continue
        rel = line.strip().split()
        AS1 = rel[0]
        AS2 = rel[1]
        loc1 = locate_AS(AS1, AS_size_dict)
        loc2 = locate_AS(AS2, AS_size_dict)
        if loc1 == "" or loc2 == "":
            continue
        p2c_infer[(loc1, loc2)] += 1
        total += 1

with open("./AS size p2c infer.txt", "w", encoding="utf-8") as f:
    for i in size:
        for j in size:
            f.write(f"{i} {j} : {p2c_infer[(i, j)]}\n")
    f.write(f"total : {total}\n")