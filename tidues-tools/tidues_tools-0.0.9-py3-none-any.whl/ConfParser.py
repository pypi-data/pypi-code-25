import configparser as cp

class ConfigParser():
    def __init__(self,conf_file,sep=";"):
        # first commom parse
        self.conf = cp.ConfigParser(interpolation=cp.ExtendedInterpolation())
        self.conf.read(conf_file)
        
        # set default empty strings
        self.strip_str=' \t\n\r'
        self.sep = sep
        self.none_lst = ['None', 'none', '']

    def __getitem__(self, *keys):
        return self.get(*keys)

    def get(self, *keys):
        if len(keys) > 1:
            return self.get_sgl(*keys)
        else:
            res = {}
            for it in self.conf[keys[0]]:
                res[it] = self.get_sgl(keys[0], it)
            return res



    def get_sgl(self, *keys):
        res = self.conf.get(*keys)
        # first parse sep
        tmp_lst = self.parse_sep(res)
        # parse code
        res_lst = []
        for it in tmp_lst: 
            res_lst = res_lst + self.parse_code(it,keys[0])
        # if no code de_list
        if len(res_lst) == 1:
            op = res_lst[0]
        else:
            op = res_lst

        return op

    def opt_exist(self, opt, sec):
        if self.conf.has_option(sec, opt):
            if self.conf[sec][opt] not in self.none_lst:
                return True
            else:
                return False
        else:
            return False

    def parse_sep(self,ls_str):
        ls=ls_str.strip(self.strip_str).split(self.sep)
        ls=self.rm_empty(ls)
        res_ls = []
        for it in ls:
            it.strip(self.strip_str)
            if it[0]=="'" and it[-1]=="'":
                it = it[1:-1]
            res_ls.append(it)
        return res_ls 
        
    def rm_empty(self,ls):
        return list(filter(None,ls))
    
    def parse_code(self,it,sec):
        res_lst = []
        beg = it.find('${')
        # check is there any code exist
        if it.find('${')>= 0:
            end = it.find('}',beg)
            code_name = it[beg+2:end]
            # evaluate the code
            if self.conf.has_option(sec,code_name):
                code = self.conf.get(sec,code_name)
            elif self.conf.has_option('DEFAULT', code_name):
                code = self.conf.get('DEFAULT',code_name)
            else:
                raise Exception('Code for ', code_name, ' is not provided!')
            val = eval(code)
            # check if val is iterable
            try:
                if isinstance(val, str):
                    if_iter = False
                else:
                    iter(val)
                    if_iter = True
            except TypeError as te:
                if_iter = False
            
            if if_iter:
                for ele in val:
                    tmp_str = it[:beg] + str(ele) + it[end+1:]
                    my_lst = self.parse_code(tmp_str,sec)
                    res_lst = res_lst + my_lst
            else:
                tmp_str = it[:beg] + str(val) + it[end+1:]
                my_lst = self.parse_code(tmp_str,sec)
                res_lst = res_lst + my_lst
        else:
            # if no code exist
            res_lst = res_lst + [it]

        return res_lst

if __name__=='__main__':
    conf_file = './example.conf'
    conf = ConfigParser(conf_file)
    # print(conf.get('station','index')) 
    # print(conf.get('trip','dates_cols')) 
    # print(conf.get('DEFAULT','nan list')) 
    # print(conf.get('station','path')) 
    # print(conf.get('trip','path')) 
    # print(conf.get('test','myres')) 
    # print(conf['test','myres']) 
    # print(conf.get('test', 'myres'))
    # print(conf.get('test'))
    # print(conf.get('test')['myres'])
    # print(conf['test'])
    # print(conf['test']['myres'])
    print(conf.opt_exist('myres','test'))
    print(conf.opt_exist('myres1','test'))
    print(conf.opt_exist('myres2','test'))
    print(conf.opt_exist('myres3','test'))
