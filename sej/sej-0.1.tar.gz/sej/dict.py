from pytrie import SortedStringTrie
import  pickle
import  os
from .util import Util

class Seg:

    def __init__(self, dictpath = None):

        self.data_dir = Util.get_data_dir(os.path.realpath(__file__))
        if dictpath is not None:
            self.trie = self.update_dict(dictpath)
        else:
            self.trie = self.load()

    def _forward_match(self, s):
        trie = self.trie
        res = []
        while len(s)!=0:
            try:
                wd = trie.longest_prefix_item(s)
                res.append(wd[0])
                s = s[len(wd[0]):]
            except KeyError:
                res.append(s[0])
                s = s[1:]
        return  res

    def cut(self, s , forward_match =True):
        if forward_match:
            return self.forward_match(s)
        else:
            return self.back_match()

    def forward_match(self,s):
        res = []
        sentences = Util.split_sentence(s)
        for sentence in sentences:
            res += self._forward_match(sentence)
        return res

    def back_match(self,s):
        res = []
        sentences = Util.split_sentence(s)
        for sentence in sentences:
            res += self._back_match(sentence)
        return res

    def _back_match(self, s):
        trie = self.trie
        res = []
        while len(s)!=0:
            for i in range(0,len(s)):
                try:
                    wd = trie.longest_prefix_item(s[i:])
                    if wd[0] != s[i:] : continue
                    res.append(wd[0])
                    s = s[:i]
                except KeyError:
                    if i == len(s)-1:
                        res.append(s[i:])
                        s = s[:i]

        res.reverse()
        return  res

    def update_dict(self, path):
        try:
            dict = {}
            with open(path,'r',encoding='utf8') as f:
                for word in f.readlines():
                    dict[word[:-1]] = 1

            trie = SortedStringTrie(dict)
            fw = open(self.data_dir + 'my.trie','wb')
            pickle.dump(trie,fw)
        except FileNotFoundError:
            print("cant not find file {0}".format(path))
        return  trie


    def load(self):
        fr = open(self.data_dir +'my.trie', 'rb')
        return  pickle.load(fr)



if __name__ == '__main__':
    seg = Seg()
    print(seg.back_match('不过有类似的方法'))