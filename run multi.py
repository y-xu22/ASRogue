import os
import time
import random

round = 100

clique = ["174", "209", "286", "701", "1239", "1299", "2828", "2914", "3257", "3320", "3356", "3491", "5511", "6453", "6461", "6762", "6830", "7018", "12956"]

AS_size_dict = {}
AS_pool = []
AS_pool_N0 = []
with open("./data/AS_size.txt") as f:
    lines = f.readlines()
    AS_line = []
    for line in lines:
        if line[:2] == "AS" or line == "\n":
            continue
        else:
            AS_line.append(line)
    AS_size_dict["0"] = AS_line[0].strip().split(" ")
    AS_size_dict["S"] = AS_line[1].strip().split(" ")
    AS_size_dict["M"] = AS_line[2].strip().split(" ")
    AS_size_dict["L"] = AS_line[3].strip().split(" ")

AS_pool = AS_pool + AS_size_dict["0"] + AS_size_dict["S"] + AS_size_dict["M"] + AS_size_dict["L"]
with open("./data/all rel TD.txt") as f:
    f_list = f.readlines()
    for line in f_list[1:]:
        relation = line.split("\t")
        if not int(relation[3]) == 0 and relation[0] not in AS_pool_N0:
            AS_pool_N0.append(relation[0])
        if not int(relation[4]) == 0 and relation[1] not in AS_pool_N0:
            AS_pool_N0.append(relation[1])
        # if not int(relation[3]) == 0 and (relation[0], int(relation[3])) not in AS_pool_N0:
        #     AS_pool_N0.append((relation[0], int(relation[3])))
        # if not int(relation[4]) == 0 and (relation[1], int(relation[4])) not in AS_pool_N0:
        #     AS_pool_N0.append((relation[1], int(relation[4])))

with open("./data/inference-20241001_ori.txt", "r") as f:
    all_rel_list = f.readlines()
    rel_list = []
    step2_flag = False
    for line in all_rel_list:
        # step 2 p2c rel
        # if line[:9] == "# step 2:":
            # step2_flag = True
            # continue
        # if line[:9] == "# step 3:":
            # break
        # if step2_flag and line.split("|")[0] not in clique and line.split("|")[1] not in clique:
            # rel_list.append(line)

        # all p2c rel
        # if line[:6] == "# step":
        #     continue
        # if line.split("|")[0] not in clique and line.split("|")[1] not in clique and line.strip().split("|")[2] == "-1":
        #     rel_list.append(line)

        # # all rel
        if line[:6] == "# step":
            continue
        if line.split("|")[0] not in clique and line.split("|")[1] not in clique:
            rel_list.append(line)
    # print(rel_list)

    random.shuffle(rel_list)

    # test based on AS size
    # size = ["L", "M", "S", "0"]
    # for m in range(len(size)):
    #     for n in range(m + 1, len(size)):
    #         cnt = 0
    #         for i in range(len(rel_list)//2):
    #             if rel_list[2 * i].split("|")[0] in AS_size_dict[size[n]] and rel_list[2 * i].split("|")[1] in AS_size_dict[size[m]]:
    #                 cnt += 1
    #                 start = time.time()
    #                 rvs_provider = rel_list[2 * i].split("|")[1] # "39647"
    #                 rvs_customer = rel_list[2 * i].split("|")[0] # "200020"
    #                 att_announcer = rel_list[2 * i + 1].split("|")[0] # "18403"
    #                 att_source = rel_list[2 * i + 1].split("|")[1] # "63737"
    #                 os.system(f"python run.py {rvs_provider} {rvs_customer} {att_announcer} {att_source}")
    #                 print(f"{size[n]} {size[m]} round {cnt} done! time: {time.time() - start}")
    #                 if cnt == round:
    #                     break

    ### all random test
    # for i in range(round):
    #     start = time.time()
    #     rvs_provider = rel_list[2 * i].split("|")[1] # "39647"
    #     rvs_customer = rel_list[2 * i].split("|")[0] # "200020"
    #     att_announcer = rel_list[2 * i + 1].split("|")[0] # "18403"
    #     att_source = rel_list[2 * i + 1].split("|")[1] # "63737"
    #     os.system(f"python run.py {rvs_provider} {rvs_customer} {att_announcer} {att_source}")
    #     print(f"round {i} done! time: {time.time() - start}")

    ### p2p test
    for i in range(round):
        start = time.time()
        flag = False
        rvs_provider = ""
        rvs_customer = ""
        while(not flag):
            rvs_provider = random.choice(AS_pool)
            rvs_customer = random.choice(AS_pool)
            # rvs_provider = random.choice(AS_pool_N0)
            # rvs_customer = random.choice(AS_pool_N0)
            ### test same TD
            # if not rvs_customer[1] == rvs_provider[1]:
            #     continue
            # rvs_customer = rvs_customer[0]
            # rvs_provider = rvs_provider[0]
            ### end
            flag = True
            for rel in rel_list:
                p0 = rel.split("|")[0]
                p1 = rel.split("|")[1]
                if p0 == rvs_customer and p1 == rvs_provider:
                    flag = False
                    break
                if p0 == rvs_provider and p1 == rvs_customer:
                    flag = False
                    break
        att_announcer = rel_list[2 * i + 1].split("|")[0] # "18403"
        att_source = rel_list[2 * i + 1].split("|")[1] # "63737"
        os.system(f"python run.py {rvs_provider} {rvs_customer} {att_announcer} {att_source}")
        print(f"round {i} done! time: {time.time() - start}")