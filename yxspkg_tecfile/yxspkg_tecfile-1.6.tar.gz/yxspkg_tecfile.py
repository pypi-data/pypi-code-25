
import numpy as np
from os.path import getsize
import re
__version__='1.6'
__author__='Blacksong'
class _zone_data(dict):
    def __init__(self,*d,**dd):
        super().__init__(*d,**dd)
        self.Elements = None
        self.tec_cellcentered=False
    def _setPlot3d_type(self):#文件格式为plot3d格式时运行这个函数  增加x,y,z,ptype这个变量 
        self.x=None
        self.y=None
        self.z=None
        self.ptype=None
        
        return self
    def rename(self,old,new):
        if old == new:return
        self[new]=self[old]
        self.pop(old)
    def set_data(self,names,values,attribute):
        self.names=names
        self.data=values
        self.attribute=attribute
        for i,v in zip(names,values):
            self[i]=v
    def __getitem__(self,k):
        if isinstance(k,str):
            return super().__getitem__(k)
        else:
            if self.attribute == 'fluent_prof':
                return self.data[:,k]
    def is_centered(self,name): #判断一个tecplot变量是不是centered变量
        nodes = int(self.attribute['Nodes'])
        if len(self[name])==nodes:
            return False
        else:
            return True

    def center_value(self,name):# 获取tecplot文件中某个变量在cell中心的值，即求出各个节点的平均值
        elements = self.Elements - 1
        n = len(elements[0])
        elements_flat = elements.flatten()
        data = self[name][elements_flat].reshape((-1,n))
        data = data.sum(1)/n
        return data
    def __add__(self,other):#重载加法运算
        z = class_read()
        names = list(self.keys())
        values = [self[i] + other[i] for i in names]
        z.update(zip(names,values))
        return z
    def __sub__(self,other):#重载减法运算
        z = class_read()
        names = list(self.keys())
        values = [self[i] - other[i] for i in names]
        z.update(zip(names,values))
        return z
    def __mul__(self,other):#重载乘法运算
        z = class_read()
        names = list(self.keys())
        if isinstance(other,_zone_data):
            values = [self[i] * other[i] for i in names]
        else:
            values = [self[i] * other for i in names]
        z.update(zip(names,values))
        return z
class class_read(dict):
    def __init__(self,filename=None,filetype=None,**kargs):
        if filename is None:return
        self.fp=open(filename,'r')
        self.default_filetypes={'prof':'fluent_prof','dat':'tecplot_dat','out':'fluent_residual_out',
        'out2':'fluent_monitor_out','csv':'csv','txt':'txt','fmt':'plot3d','plot3d':'plot3d'}
        self.data=None
        if filetype is None:
            key=filename.split('.')[-1].lower()
            if key=='out':key=self.__recognize_out(self.fp)
            self.filetype=self.default_filetypes[key]
        else:
            self.filetype=filetype
        self.filesize=getsize(filename)
        if self.filetype=='tecplot_dat':
            self._read_dat()
        elif self.filetype=='fluent_prof':
            self._read_prof()
        elif self.filetype=='fluent_residual_out':
            self._read_out()
        elif self.filetype=='fluent_monitor_out':
            self.__read_out2()
        elif self.filetype=='csv':
            self.__read_csv(filename)
        elif self.filetype == 'plot3d':
            self.__read_plot3d(filename)
        self.fp.close()
    def __read_plot3d(self,filename):
        self.data=list()
        d=np.array(self.fp.read().split(),dtype='float64')
        n=int(d[0])
        shape=d[1:1+n*3].astype('int')
        start=1+n*3
        for i in range(n):
            zt,yt,xt=shape[i*3:i*3+3]
            block=_zone_data()._setPlot3d_type()
            block.x=d[start:start+xt*yt*zt]
            start+=xt*yt*zt
            block.y=d[start:start+xt*yt*zt]
            start+=xt*yt*zt
            block.z=d[start:start+xt*yt*zt]
            start+=xt*yt*zt
            block.ptype=d[start:start+xt*yt*zt].astype('int')
            start+=xt*yt*zt
            block.x.shape=(xt,yt,zt)
            block.y.shape=(xt,yt,zt)
            block.z.shape=(xt,yt,zt)
            block.ptype.shape=(xt,yt,zt)

            block.x=block.x.swapaxes(2,0)
            block.y=block.y.swapaxes(2,0)
            block.z=block.z.swapaxes(2,0)
            block.ptype=block.ptype.swapaxes(2,0)

            self[i]=block
            self.data.append(block)
    def __read_csv(self,filename):
        title=self.fp.readline()
        tmp=np.loadtxt(self.fp,dtype='float64',delimiter=',')
        title=title.strip().split(',')
        for i,j in enumerate(title):
            self[j]=tmp[:,i]
        self.data=tmp
    def __recognize_out(self,fp):
        fp.readline()
        t=fp.readline()
        t=t.split()
        key='out'
        if t:
            if t[0]=='"Iteration"':
                key='out2'
        fp.seek(0,0)
        return key
    def __read_out2(self):
        self.fp.readline()
        t=self.fp.readline()
        t=t.lstrip()[11:].strip()[1:-1]
        d=self.fp.read().encode().strip()
        d=d.split(b'\n')
        d=[tuple(i.split()) for i in d]
        x=np.array(d,dtype=np.dtype({'names':["Iteration",t],'formats':['int32','float64']}))
        self["Iteration"]=x['Iteration']
        self[t]=x[t]
        self.data=x
    def _read_out(self):#fluent residual file
        items=[]
        items_n=0
        data=[]
        iter_pre='0'
        time_index=False
        for i in self.fp:
            if i[:7]=='  iter ':
                if items_n!=0:continue
                j=i.strip().split()
                items.extend(j)
                if items[-1]=='time/iter':
                    items.pop()
                    items.extend(('time','iter_step'))
                    time_index=True
                items_n=len(items)
            if items_n==0:continue
            else:
                j=i.split()
                if len(j)==items_n:
                    if j[0].isdigit():
                        if j[0]==iter_pre:continue
                        iter_pre=j[0]
                        if time_index:j.pop(-2)
                        data.append(tuple(j))
        if time_index:items.pop(-2)
        a=np.array(data,dtype=np.dtype({'names':items,'formats':['i']+['f']*(len(items)-2)+['i']}))
        for i,k in enumerate(items):
            self[k]=a[k]
        self.data=a
    def _read_prof(self):
        fp=self.fp
        d=fp.read()
        d=d.replace('\r','')
        d=d.split('((')
        d.pop(0)
        data=[]
        def read(x):
            x=x.split('(')
            title=x[0].split()[0]
            x.pop(0)
            data=[]
            name=[]
            ii=0
            for i in x:
                c=i.split('\n')
                ii+=1
                name.append(c[0])
                data.append(c[1:-2])
            data[-1].pop()
            values=np.array(data,dtype='float32')
            if len(values)!=len(name):return False
            t=_zone_data()
            t.set_data(name,values,self.filetype)
            return title,t
        for i in d:
            k,v=read(i)
            self[k]=v
    
    def _parse_variables(self,string_list):#解析tecplot文件的变量名有哪些
        return re.findall('"([^"]*)"',''.join(string_list))

    def _parse_zone_type(self,string_list):# 解析tecplot文件
        s=' '.join(string_list)
        attri = dict(re.findall('(\w+)=([^ ,=]+)',s))
        attri.update( dict(re.findall('(\w+)="([\w ]+)"',s)))
        k = re.findall('VARLOCATION=\(([^=]+)=CELLCENTERED\)',s)#检查是否有cellcentered变量
        auxdata = re.findall(' AUXDATA [^ ]*',s)
        if auxdata:
            attri['AUXDATA'] = '\n'.join(auxdata)
        a=[]
        if k:
            for i in k[0][1:-1].split(','):
                if i.find('-')!=-1:
                    start,end = i.split('-')
                    a.extend(range(int(start),int(end)+1))
                else:
                    a.append(int(i))
        a.sort()
        attri['CELLCENTERED'] = a 
        return attri
        
    def _read_dat(self):#解析tecplot_dat数据格式
        fp=self.fp
        title = fp.readline()
        assert title.lstrip().startswith('TITLE')!=-1#查看文件开头是否是TITLE

        string = fp.readline().strip()
        assert string.startswith('VARIABLES') #查看文件第二行开头是否是VARIABLES

        string_list=[string,]#获取包含所有变量名的字符串
        for i in fp:
            i=i.strip()
            if not i.startswith('"'):
                string = i
                break
            else:
                string_list.append(i)
        self._variables=self._parse_variables(string_list) #对字符串进行解析得到变量名
        print('variables',self._variables)
        while True:
            if not string:
                string = fp.readline()
                if not string:
                    break
            string_list=[string,]#获取包含zone name， element， nodes，zonetype, datapacking的字段
            for i in fp:
                i=i.strip()
                if i.startswith("DT=("):
                    string = i 
                    break
                else:
                    string_list.append(i)
            self._tecplot_attribute=self._parse_zone_type(string_list) #获取包含zone name， element， nodes，zonetype, datapacking 返回形式为字典
            print('zone info',self._tecplot_attribute)
            string = string[len('DT=('):-1].strip().split()
            self._DT=string  #保存每个变量的类型
            assert len(self._variables) == len(string)

            if self._tecplot_attribute['DATAPACKING']=='BLOCK':
                self._parse_block()
            if self._tecplot_attribute['DATAPACKING'] == 'POINT':
                self._parse_point()
            string = None
    def _read_numbers(self,fp,nums):#读取文件一定数目的 数据
        data = fp.readline().split()
        n = len(data)
    
        strings = [fp.readline() for _ in range(int(nums/n)-1)]
        data.extend(''.join(strings).split())
        nn = nums - len(data)
        assert nn>=0
        if nn>0:
            for i in fp:
                data.extend(i.split())
                if len(data) == nums:
                    break 
        return data
    def _parse_Elements(self,zonedata):#解析tecplot的Element
        elements = int(self._tecplot_attribute['Elements'])
        data_elements = self.fp.readline().split()
        num_points = len(data_elements)
        data = self._read_numbers(self.fp,num_points*(elements-1))
        data_elements += data
        zonedata.Elements = np.array(data_elements,dtype=np.int).reshape((-1,num_points))

    def _parse_block(self,isElements=True,isBlock=True):#解析tecplot block方式存储的数据
        cellcentered = self._tecplot_attribute['CELLCENTERED']
        if cellcentered:
            variables,nodes,elements = self._variables,int(self._tecplot_attribute['Nodes']),int(self._tecplot_attribute['Elements'])
            
            value_list = []
            for i in range(len(variables)):
                if i+1 in cellcentered:
                    nums = elements 
                else:
                    nums = nodes
                data = self._read_numbers(self.fp,nums)
                value_list.append( np.array(data,dtype = 'float64'))
            zonedata = _zone_data()
            zonedata.set_data(variables,value_list,self._tecplot_attribute)
            self[self._tecplot_attribute['T']] = zonedata

            if isElements:
                self._parse_Elements(zonedata)

        else:
            self._parse_point(isElements,isBlock)
        

    def _parse_point(self,isElements=True,isBlock=False):
        variables,nodes,elements = self._variables,int(self._tecplot_attribute['Nodes']),int(self._tecplot_attribute['Elements'])
        nn=nodes*len(variables)
        data = self._read_numbers(self.fp,nn)
        if isBlock:
            data = np.array(data,dtype = 'float').reshape((len(variables),-1))
        else:
            data = np.array(data,dtype = 'float').reshape((-1,len(variables))).T
        
        zonedata = _zone_data()  #设置zonedata数据
        zonedata.set_data(self._variables,data,self._tecplot_attribute) 
        self[self._tecplot_attribute['T']] = zonedata
        
        if isElements:
            #添加Elements的属性
            self._parse_Elements(zonedata)
    def __getitem__(self,k):
        if isinstance(k,str):
            return super().__getitem__(k)
        else:return self.data[k]
    def enable_short_name(self):#启用简单名 即将名字命名为 原来名字的第一个单词
        for i in list(self.keys()):
            for j in list(self[i].keys()):
                self[i].rename(j,j.split()[0])
            self.rename(i,i.split()[0])
    def rename(self,old,new):
        if old == new:return
        self[new]=self[old]
        self.pop(old)
    def write(self,filename):
        write(self,filename)

    def __add__(self,other):#重载加法运算
        z = class_read()
        names = list(self.keys())
        values = [self[i] + other[i] for i in names]
        z.update(zip(names,values))
        return z
    def __sub__(self,other):#重载减法运算
        z = class_read()
        names = list(self.keys())
        values = [self[i] - other[i] for i in names]
        z.update(zip(names,values))
        return z
    def __mul__(self,other):#重载乘法运算
        z = class_read()
        names = list(self.keys())
        if isinstance(other,class_read):
            values = [self[i] * other[i] for i in names]
        else:
            values = [self[i] * other for i in names]
        z.update(zip(names,values))
        return z
class data_ndarray(np.ndarray):
	def write(self,filename):
		write(self,filename)
	def setfiletype(self,filetype):
		self.filetype=filetype
def read(filename,filetype=None,**kargs):
	ext=filename.split('.')[-1].lower()
	if ext=='txt':
		data = [i.split() for i in open(filename) if i.lstrip() and i.lstrip()[0]!='#']
		data=np.array(data,dtype='float64')
		data=data_ndarray(data.shape,dtype=data.dtype,buffer=data.data)
		data.setfiletype('txt')
	else:
		data=class_read(filename)
	return data
class write:
    def __init__(self,data,filename,filetype=None):
        default_filetypes={'prof':'fluent_prof','dat':'tecplot_dat','out':'fluent_residual_out',
        'out2':'fluent_monitor_out','csv':'csv','txt':'txt','fmt':'plot3d','plot3d':'plot3d'}
        ext=filename.split('.')[-1].lower()
        if filetype is None:
            filetype=default_filetypes.get(ext,None)
        if filetype is None:
            filetype=data.filetype

        if filetype=='fluent_prof':
            self.__write_prof(data,filename)
        elif filetype=='tecplot_dat':
            self.__write_dat(data,filename)
        elif filetype=='csv':
            self.__write_csv(data,filename)
        elif filetype=='fluent_monitor_out':
            self.__write_out2(data,filename)
        elif filetype=='fluent_residual_out':
            self.__write_out(data,filename)
        elif filetype=='txt':
        	np.savetxt(filename,data)
        elif filetype=='plot3d':
            self.__write_plot3d(data,filename)
        else:
            raise EOFError('file type error!')

    def __write_plot3d(self,data,filename):
        fp=open(filename,'w')
        def writelines(ffp,write_data,line_max):
            ffp.write('\n')
            n_line=int(write_data.size/line_max)
            write_data.reshape((-1,n_line))
            s=write_data.astype('U')[:n_line*line_max]
            s.resize((n_line,line_max))
            s_lines=[' '.join(i) for i in s]
            ffp.write('\n'.join(s_lines))
            n = write_data.size-n_line*line_max
            if n:
                ffp.write('\n'+ ' '.join(write_data[-n:]))
        shape=list()
        for i,v in enumerate(data.data):
            shape.extend(v.x.shape)

        fp.write(str(i+1)+'\n')
        fp.write(' '.join([str(i) for i in shape]))
        for i,v in enumerate(data.data):
            x=v.x.swapaxes(0,2)
            x.resize(x.size)
            y=v.y.swapaxes(0,2)
            y.resize(y.size)
            z=v.z.swapaxes(0,2)
            z.resize(z.size)
            p=v.ptype.swapaxes(0,2)
            p.resize(p.size)
            writelines(fp,x,5)
            writelines(fp,y,5)
            writelines(fp,z,5)
            writelines(fp,p,5)

    def __write_out(self,data,filename):
        fp=open(filename,'w')
        self.__write_delimiter(data,fp,'  ',title_format='',specified_format=' %d',specified_titles=['iter'],other_format='%.8e')
        fp.close()
    def __write_out2(self,data,filename):
        fp=open(filename,'w')
        value=[i for i in data.keys() if i!='Iteration'][0]
        fp.write('"Convergence history of %s"\n' % value)
        self.__write_delimiter(data,fp,' ',title_format='"',specified_format='%d',specified_titles=['Iteration'])
        fp.close()
    def __write_csv(self,data,filename):
        fp=open(filename,'w')
        self.__write_delimiter(data,fp,',')
        fp.close()
    def __write_delimiter(self,data,fp,delimiter,title_format='',specified_format='',specified_titles=[],other_format='%.15e'):
        other_titles=[i for i in data.keys() if i not in specified_titles]
        title=specified_titles+other_titles
        title_w=[title_format+i+title_format for i in title]
        fp.write(delimiter.join(title_w)+'\n')
        s=np.vstack([data[i] for i in title]).T
        data_format=specified_format+delimiter+delimiter.join([other_format]*len(other_titles))+'\n'
        for i in s:
            fp.write(data_format % tuple(i))
    def __write_prof(self,data,filename):
        fp=open(filename,'wb')
        for i in data.keys():
            keys=list(data[i].keys())
            keys.sort()
            keys.sort(key=lambda x:len(x))
            n=len(data[i][keys[0]])
            fs='(('+i+' point '+str(n)+')\n'
            fp.write(fs.encode())
            for k in keys:
                fs='('+k+'\n'
                fp.write(fs.encode())
                [fp.write((str(j)+'\n').encode()) for j in data[i][k]]
                fp.write(')\n'.encode())
            fp.write(')\n'.encode())
    def __write_dat(self,data,filename):#写入tecplot dat文件，目前只支持写入DATAPACKING=POINT类型的数据DATAPACKING=BLOCK类型的数据也会被改写为POINT类型
        fp = open(filename,'w')
        fp.write('TITLE  = "Python Write"\n')
        zones = list(data.keys())  #获取所有zone的名字
        variables = list(data[zones[0]].keys())#获取变量名
        fp.write('VARIABLES = ')
        fp.writelines(['"{}"\n'.format(i) for i in variables])
        for i in zones:
            zonedata = data[i]
            z = zonedata.attribute
            nodes, elements = int(z['Nodes']), int(z['Elements'])
            fp.write('ZONE T="{}"\n'.format(i))
            fp.write(' STRANDID={}, SOLUTIONTIME={}\n'.format(z.get('STRANDID',1),z.get('SOLUTIONTIME',0)))
            fp.write(' Nodes={0}, Elements={1}, ZONETYPE={2}\n'.format(nodes, elements, z['ZONETYPE']))
            if z['DATAPACKING'] == 'POINT':
                fp.write('DATAPACKING=POINT\n')
                if z.get('AUXDATA') is not None:
                    fp.write(z.get('AUXDATA')+'\n')
                fp.write('DT=('+'SINGLE '*len(variables)+')\n')
                fs = ' {}'*len(variables)+'\n'
                for value in zip(*([zonedata[j] for j in variables])):
                    fp.write(fs.format(*value))
                fs = ' {}'*len(zonedata.Elements[0])+'\n'
            else:
                fp.write(' DATAPACKING=BLOCK\n')
                cellcentered = [str(i+1) for i,v in enumerate(variables) if zonedata.is_centered(v)]
                if cellcentered:
                    s =','.join(cellcentered)
                    fs = ' VARLOCATION=([{}]=CELLCENTERED)\n'.format(s)
                    fp.write(fs)
                if z.get('AUXDATA') is not None:
                    fp.write(z.get('AUXDATA')+'\n')
                fp.write('DT=('+'SINGLE '*len(variables)+')\n')
                ofs = ' {}'*5+'\n'
                for var in variables:
                    
                    value = zonedata[var]
                    
                    for i in range(5,len(value)+1,5):
                        
                        fp.write(ofs.format(*value[i-5:i]))

                    leave = len(value) % 5

                    if leave != 0:
                        fs = ' {}'*leave+'\n'
                        fp.write(fs.format(*value[-leave:]))
                

            if zonedata.Elements is not None:
                fs = ' {}'*len(zonedata.Elements[0])+'\n'
                for i in zonedata.Elements:
                    fp.write(fs.format(*i))

if __name__=='__main__':
    # from matplotlib import pyplot as plt
    import time
    from IPython import embed
    # s=time.time()
    a=read('lumley.dat')
    # print(time.time()-s)
    # embed()
    a.write('lumley_2.dat')
    # b = read('lumley_2.dat')
    # print(a.keys(),b.keys())
    # for zone in a.keys():
    #     for var in a[zone].keys():
    #         print(zone,var)
    #         print(np.allclose(a[zone][var], b[zone][var]))
    # print(a.elements)
    # embed()
    # a.write('test_tec.dat')
    # for i in zip(range(3),range(4)):
    #     print(i)
    # a=read('lumley2.dat')
    # a.enable_short_name()
    # b=read('test_tec.dat')
    # b.enable_short_name()
    # for i in a.keys():
    #     for j in a[i].keys():
    #         print(i,j)
    # for i in a.keys():
    #     for j in a[i].keys():
    #         print(i,j)
    #         t=np.allclose(a[i][j] , b[i][j])
    #         print(t)
    # s='ZONE T="face_m Step 1 Incr 0" STRANDID=1, SOLUTIONTIME=0 Nodes=52796, Elements=104098, ZONETYPE=FELineSeg DATAPACKING=POINT'
    # m=re.findall('(\w+)=(\w+)',s)
    # attri = dict()
    # print(m)
    # 
    # print(attri,attri2)