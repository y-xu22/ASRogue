import random
import time
import pickle

# import pandas as pd
# pd.read_csv
clique = ["174", "209", "286", "701", "1239", "1299", "2828", "2914", "3257", "3320", "3356", "3491", "5511", "6453", "6461", "6762", "6830", "7018", "12956"]

AS_pool_limit = 100000 
Add_limit = 10 

class P2C_DICT:
    def __init__(self, att_announcer, att_source):
        # 1. read files
        self.AS = []         # [AS1, AS2, ...]
        self.TG = []         # [(AS1, tg1), (AS2, tg2), ...]
        self.P2C = []        # [[(AS2, rel2), (AS3, rel3), ...], [(AS3, rel3), ...], ...]
        self.P2C_head = []   # [AS1, AS2, ...]，每个 AS 对应 P2C 中关系的 provider
        self.AS_pool = []
        self.P2C_dict = {}
        self.att_announcer = att_announcer
        self.att_source = att_source
        self.file_name = "./data/p2c rel tg.txt"

    def in_TG(self, asn):
        flag = False
        for i in self.TG:
            if i[0] == asn:
                flag = True
                break
        return flag

    def search_P2C_head(self, asn):
        id = -1
        for i in range(len(self.P2C_head)):
            if self.P2C_head[i] == asn:
                id = i
                break
        return id

    def in_P2C(self, asn1_id, asn2):
        flag = False
        for j in self.P2C[asn1_id]:
            if j[0] == asn2:
                flag = True
                break
        return flag

    def P2C_add(self, asn1_id, asn1, asn2, relation):
        if asn1_id != -1:
            self.P2C[asn1_id].append((asn2, relation))
        if asn1_id == -1:
            self.P2C_head.append(asn1)
            self.P2C.append([(asn2, relation)])

    def read_file(self):
        with open(self.file_name, "r") as f:
            f_list = f.readlines()
            # print("file read done! time0: ", time.time() - start)
            for line in f_list[1:]:
                # time_prev = time.time()
                relation = line.split("\t")
                if relation[0] not in self.AS:
                    self.AS.append(relation[0])
                    self.TG.append((relation[0], relation[3]))
                    if int(relation[3]) < AS_pool_limit and relation[0] != self.att_announcer and relation[0] != self.att_source:
                        self.AS_pool.append(relation[0])
                if relation[1] not in self.AS:
                    self.AS.append(relation[1])
                    self.TG.append((relation[1], relation[4]))
                    if int(relation[4]) < AS_pool_limit and relation[1] != self.att_announcer and relation[1] != self.att_source:
                        self.AS_pool.append(relation[1])
            # print("file read done! time1: ", time.time() - start, len(self.AS))
            for line in f_list[1:]:
                relation = line.split("\t")
                self.P2C_dict[(relation[0], relation[1])] = relation[2]
                # id = search_P2C_head(relation[0])
                # if id == -1 or not in_P2C(id, relation[1]):
                    # P2C_add(id, relation[0], relation[1], relation[2])
            # print("file read done! time2: ", time.time() - start)
        return self

    def get_tg(self, asn):
        tg = 0
        for i in self.TG:
            if i[0] == asn:
                tg = i[1]
                break
        return int(tg)

    def rel(self, asn1, asn2):
        relation = -2
        for i in self.P2C:
            if i[0] == asn1:
                for j in i[1:]:
                    if j[0] == asn2:
                        relation = j[1]
                        break
            if not relation == -2:
                break
        return int(relation)
    
    def dump_model(self, output_path):
        pickle.dump(self, open(output_path, "wb"), protocol=5)
        return self

class Gen_path:
    def __init__(self, rvs_provider, rvs_customer, att_announcer, att_source):
        # 0. input ASN
        self.rvs_provider = rvs_provider # "39647"
        self.rvs_customer = rvs_customer # "200020"

        self.att_announcer = att_announcer # "18403"
        self.att_source = att_source # "63737"

        self.attack_AS_path = []
        self.output_path = "./data/p2c_model.pkl"

        self.start = time.time()

    def gen_path(self):
        # p2c_dict = P2C_DICT(self.att_announcer, self.att_source).read_file().dump_model(output_path)
        p2c_dict = pickle.load(open(self.output_path, "rb"))

        ## 1.2 get information
        rvs_p_ori_tg = p2c_dict.get_tg(self.rvs_customer)
        rvs_c_ori_tg = p2c_dict.get_tg(self.rvs_provider)

        print("rvs_p_ori_tg:", rvs_p_ori_tg)
        print("rvs_c_ori_tg:", rvs_c_ori_tg)

        # 2. select and set bridge
        bridge_provider = -1
        bridge_customer = -2  

        for relation in p2c_dict.P2C_dict.keys():
            if p2c_dict.P2C_dict[relation] == "-1" and p2c_dict.get_tg(relation[1]) > rvs_p_ori_tg + 2 and\
                not relation[0] == self.rvs_customer and not relation[0] == self.rvs_provider and not relation[1] == self.rvs_customer and not relation[1] == self.rvs_provider and\
                not relation[0] in clique and not relation[1] in clique :
                # not relation[0] in clique and not relation[1] in clique and p2c_dict.get_tg(relation[1]) < 1000 and p2c_dict.get_tg(relation[0]) < 1000 :
                bridge_provider = relation[0]
                bridge_customer = relation[1]
                break

        ## rvs_customer_tg +1, rvs_provider_tg +1
        ## bridge_provider_tg +1, bridge_customer_tg +1
        self.attack_AS_path.append([self.att_announcer, bridge_provider, bridge_customer, self.rvs_provider, self.rvs_customer, self.att_source])

        print("select bridge done! time: ", time.time() - self.start)

        # 3. add transit degree

        random.shuffle(p2c_dict.AS_pool)

        # print("AS pool:\n", AS_pool)

        pool_flag = -3
        rvs_c_att_tg = rvs_c_ori_tg
        while rvs_c_att_tg <= rvs_p_ori_tg + Add_limit:
            # pool_flag = -2
            pool_flag_1 = -1
            pool_flag_2 = -1
            while not p2c_dict.rel(p2c_dict.AS_pool[pool_flag], self.rvs_provider) == -2:
                pool_flag -= 1
            pool_flag_1 = pool_flag
            pool_flag -= 1
            while not p2c_dict.rel(p2c_dict.AS_pool[pool_flag], self.rvs_provider) == -2:
                pool_flag -= 1
            pool_flag_2 = pool_flag
            pool_flag -= 1
            
            # self.attack_AS_path.append([self.att_announcer, p2c_dict.AS_pool[pool_flag - 1], self.rvs_provider, p2c_dict.AS_pool[pool_flag], self.att_source])
            # self.attack_AS_path.append([self.att_announcer, p2c_dict.AS_pool[-2], p2c_dict.AS_pool[pool_flag - 1], self.rvs_provider, p2c_dict.AS_pool[pool_flag], p2c_dict.AS_pool[-1], self.att_source])
            self.attack_AS_path.append([self.att_announcer, p2c_dict.AS_pool[-2], p2c_dict.AS_pool[pool_flag_1], self.rvs_provider, p2c_dict.AS_pool[pool_flag_2], p2c_dict.AS_pool[-1], self.att_source])
            rvs_c_att_tg += 2

        print("change transit degree done! time: ", time.time() - self.start)

        # 4. print attack path
        # print("attack AS path:\n", self.attack_AS_path)

        attack_path = []
        for line in self.attack_AS_path:
            string = ""
            for AS in line:
                string += str(AS) + " "
            attack_path.append(string)

        # add random noise
        # attack_path = []
        # for i in range(100):
        #     attack_path.append(str(random.choice(p2c_dict.AS)) + " " + str(random.choice(p2c_dict.AS)) + " " + str(random.choice(p2c_dict.AS)))
        # end add random noise

        # test p2p
        attack_path = []
        if p2c_dict.get_tg(self.rvs_customer) < p2c_dict.get_tg(self.rvs_provider):
            attack_path.append(str(self.att_announcer) + " " + str(self.rvs_customer) + " " + str(self.rvs_provider) + " " + str(self.att_source))
        if p2c_dict.get_tg(self.rvs_provider) < p2c_dict.get_tg(self.rvs_customer):
            attack_path.append(str(self.att_announcer) + " " + str(self.rvs_provider) + " " + str(self.rvs_customer) + " " + str(self.att_source))
        if p2c_dict.get_tg(self.rvs_customer) == p2c_dict.get_tg(self.rvs_provider):
            attack_path.append(str(self.att_announcer) + " " + str(self.rvs_customer) + " " + str(self.rvs_provider) + " " + str(self.att_source))
            attack_path.append(str(self.att_announcer) + " " + str(self.rvs_provider) + " " + str(self.att_source))
        # end test p2p

        print(attack_path)
        return attack_path, rvs_p_ori_tg, rvs_c_ori_tg 