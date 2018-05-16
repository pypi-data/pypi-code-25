import pickle
from  .train import Train
from  . import dict
from  .util import Util
import os

class Seg:

    status_list = ['B', 'M', 'E', 'S']
    status_len = len(status_list)
    MIN_PRO = -100000000

    def __init__(self,dictpath=None):
        self.data_dir = Util.get_data_dir(os.path.realpath(__file__))
        self.dict_seg = dict.Seg(dictpath)
        self.init_pro , self.tranfer_pro, self.emit_pro = self.load_model()

    def load_model(self):
        with open(self.data_dir+ "model.train", 'rb') as fr:
            return pickle.load(fr), pickle.load(fr), pickle.load(fr)

    def viterbi(self, s):
        st = self.status_list
        weight = [ [0 for i in range(len(s))] for i in range(self.status_len) ]
        path = [ [0 for i in range(len(s))] for i in range(self.status_len) ]

        forward_status = Util.get_status( self.dict_seg.forward_match(s))
        back_status = Util.get_status( self.dict_seg.back_match(s))
        for i in range(self.status_len):
            weight[i][0] = self.init_pro[i] + self.emit_pro[ st[i]][
                s[0] + forward_status[0] + back_status[0]
            ]

        for i in range(1,len(s)):
            for j in range(self.status_len):
                path[j][i] = -1
                weight[j][i] = self.MIN_PRO
                for k in  range(self.status_len):
                    symbol = s[i] + forward_status[i] +back_status[i]
                    pre_s, cur_s = st[k], st[j]

                    if self.emit_pro[cur_s][ symbol] == 0:
                        self.emit_pro[cur_s][symbol] = self.MIN_PRO

                    tmp = weight[k][i-1] + self.tranfer_pro[pre_s][cur_s] + self.emit_pro[cur_s][ symbol]
                    if tmp > weight[j][i]:
                        weight[j][i] = tmp
                        path[j][i] = k

        end = 2 if weight[2][len(s)-1] > weight[3][len(s)-1] else 3
        res = [st[end]]
        pre = end

        for i in range(len(s)-1, 0, -1):
            res.append( st[path[pre][i]])
            pre = path[pre][i]
        res.reverse()
        return "".join(res)


    def cut(self, s):
        res = Util.split_sentence(s)

        word_list = []
        for em in res:
            word_list += Util.status_to_word(em, self.viterbi(em))
        return word_list

if __name__ == '__main__':
    seg = Seg()
    print(seg.cut("习近平指出，地方外事工作是党和国家对外工作的重要组成部分，对推动对外交往合作、促进地方改革发展具有重要意义。要在中央外事工作委员会集中统一领导下，统筹做好地方外事工作，从全局高度集中调度、合理配置各地资源，有目标、有步骤推进相关工作。"))
