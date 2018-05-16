import os


class Util:

    @staticmethod
    def get_data_dir(path):
        data_dir = path
        cur = path.rfind('\\')
        data_dir = data_dir[:cur]+ '\\data\\'
        data_dir.replace('\\','/')
        return data_dir


    @staticmethod
    def split_sentence(sentence):
        punctuation = {'。':0, '，':0 ,'!':0 ,'……':0,' ；':0}
        res = []
        pre = 0
        for i in range(len(sentence)):
            if sentence[i] in punctuation or i == len(sentence)-1:
                res.append(sentence[pre:i+1])
                pre = i+1
        return res

    @staticmethod
    def get_status( word_list):
        status = ""
        for word in word_list:
            if len(word) == 1:
                status += 'S'
            elif len(word) == 2:
                status += 'BE'
            else:
                status += 'B' + 'M' * (len(word) - 2) + 'E'
        return status
    @staticmethod
    def status_to_word(s, status):
        table =[-1] + [ i for i in range(len(status)) if status[i] == 'E' or status[i] == 'S']
        res   = []
        for i in range(1,len(table)):
            res.append(s[table[i-1]+1:table[i]+1])
        return res
