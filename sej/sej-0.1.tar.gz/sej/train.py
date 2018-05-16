from .dict import Seg
from collections import Counter
import math
import pickle
from .util import Util
import os
class Train:
    status_list = ['B', 'M', 'E', 'S']
    MIN_PRO = -100000000

    def __init__(self):
        self.data_dir = Util.get_data_dir(os.path.realpath(__file__))
        self.init_pro = [-0.26268660809250016, -3.14e+100, -3.14e+100, -1.4652633398537678]
        self.transfer_pro = {}
        self.emit_pro = {}

    def train_transfer_pro(self):
        for idx in Train.status_list:
            self.transfer_pro[idx] = Counter()

        with open(self.data_dir+'train.utf8', 'r', encoding='utf8') as f:
            pre_status = f.readline().split()[1]
            for line in f.readlines():
                cur_status = line.split()[1]
                self.transfer_pro[pre_status][cur_status] += 1
                pre_status = cur_status

        for idx in Train.status_list:
            total = sum(self.transfer_pro[idx].values())
            for j in Train.status_list:
                if self.transfer_pro[idx][j]!=0:
                    self.transfer_pro[idx][j] = math.log((self.transfer_pro[idx][j] ) / total)
                else:
                    self.transfer_pro[idx][j] = self.MIN_PRO

    def train_emit_pro(self):
        for idx in Train.status_list:
            self.emit_pro[idx] = Counter()

        with open(self.data_dir+'train.utf8', 'r', encoding='utf8') as f:
            for line in f.readlines():
                bricks = line.split()
                symbol = bricks[0] + bricks[2] + bricks[3]
                status = bricks[1]
                self.emit_pro[status][symbol] += 1


        for idx in Train.status_list:
            total = sum(self.emit_pro[idx].values())
            for k in self.emit_pro[idx]:
                self.emit_pro[idx][k] = math.log(self.emit_pro[idx][k] / total)



    def format_file(self, path):

        out = open(self.data_dir+ 'train.utf8', 'w', encoding='utf8')
        seg = Seg()

        with open(path, 'r', encoding='utf8') as  f:
            for line in f.readlines():
                line = line[:-1]
                word_list = line.split()
                real_status = Util.get_status(word_list)

                line = line.replace(' ', '')
                forward_status = Util.get_status(seg.forward_match(line))
                back_status = Util.get_status(seg.back_match(line))

                line_status = [line[i] + ' ' + real_status[i] + ' ' + forward_status[i] + ' ' + back_status[i]
                               for i in range(len(line))]

                for word in line_status:
                    out.write(word + '\n')

    def save(self):
        fw = open(self.data_dir+ "model.train", 'wb')
        pickle.dump(self.init_pro, fw)
        pickle.dump(self.transfer_pro, fw)
        pickle.dump(self.emit_pro, fw)
        fw.close()



    def train(self):
        self.train_emit_pro()
        self.train_transfer_pro()
        self.save()


if __name__ == '__main__':
    t = Train()
    #t.train_emit_pro()
    #t.train_transfer_pro()
    t.train()
    print(t.transfer_pro)
