#-*- coding:utf-8 -*-
import pandas as pd
import numpy as np
import json
import codecs
pd.set_option('precision',4)
class LuwakStat:
    import pandas as pd
    import numpy as np
    def __init__(self,df=None,path=None):
        import pandas as pd
        import numpy as np
        self.path=path
        self.df=df
        if self.path <> None:
            self.df=pd.read_csv(self.path)
        else:
            pass
        print '欢迎使用Luwak统计模块！'

    #获得用户输入的列名
    def getcolumns(self,df):
        column_index=input('请输入Index:')
        if isinstance(column_index,int) is False:
            columns=list(df.iloc[:,column_index].columns)
        else:
            columns=list(df.iloc[:,[column_index]].columns)
        return columns

    #获得用户输入的结局名
    def getoutcome(self,df):
        outcome_index=input('请输入Index:')
        if outcome_index is not None:
           outcome=df.columns[outcome_index]
        else:
            pass
        return outcome

    #两独立样本t检验方法。
    def ttest(self,df=None,columns=[],outcome=None,outfile=None):
        print '您正在调用独立样本t检验模块'
        '''
        对样本中的连续变量进行t检验和Wilcoxon检验模块，并绘制密度图。
        param df:pd.DataFrame 导入的可分析样本数据
        param columns: list 需要分析的变量 ['col1', 'col2','col3'...]
        param outcome: df中的因变量，作为分组依据
        param outfile:output json file
        '''
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        from scipy.stats import ttest_ind,mannwhitneyu,normaltest
        import seaborn as sns
        if df is None:
            df=self.df

        if columns==[] or outcome==None:
            print u'读取的变量列表：','\n',pd.Series(df.columns),'\n'
        else:
            pass
        #调用变量或获得输入变量
        if columns ==[]:
            print '指定变量应当为连续变量'
            columns=self.getcolumns(df=df)
        else:
            pass
        print u'选定连续变量为:','\n',pd.Series(columns)

        #调用结局或获得输入结局
        if outcome==None:
            print '结局应当为分组变量'
            outcome=self.getoutcome(df=df)
        else:
            pass
        print u'选定结局:',outcome
        print u'该程序将进行独立样本t检验和Wilcoxon检验。',outcome,u'作为结局','\n'
        print u'变量包含:','\n',pd.Series(pd.unique(df[outcome]))

        grp0_index=input('请输入group0的Index:')
        grp1_index=input('请输入group1的Index:')
        grp0=pd.unique(df[outcome])[grp0_index]
        grp1=pd.unique(df[outcome])[grp1_index]

        for var in columns:
            r0=df[df[outcome]==grp0][var].dropna().astype(float)
            r1=df[df[outcome]==grp1][var].dropna().astype(float)
            m0=r0.mean()
            m1=r1.mean()
            sd0=r0.std()
            sd1=r1.std()
            median0=r0.median()
            median1=r1.median()
            quatile25_0=r0.quantile(0.25)
            quatile25_1 = r1.quantile(0.25)
            quatile75_0 = r0.quantile(0.75)
            quatile75_1 = r1.quantile(0.75)
            n0=len(r0)
            n1=len(r1)
            t,p=ttest_ind(r0,r1)
            u,xp=mannwhitneyu(r0,r1)

            if p<0.05:
                value=u'有统计学差异'
            else:
                value=u'无统计学差异'

            if xp<0.05:
                value2=u'有统计学差异'
            else:
                value2=u'无统计学差异'
            #绘制t检验概率分布图
            plt.figure(figsize=(8,4),dpi=100,facecolor='white',edgecolor='black')
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei'] #指定默认字体
            p2=sns.distplot(r0,hist=False,label=grp0,color='g')
            p2=sns.distplot(r1,hist=False,label=grp1,color='r')
            plt.title(var+u'分组比较')
            plt.show()
            #正态检验
            r=r0.append(r1)
            assert len(r)==len(r0)+len(r1)
            if len(r.dropna().astype(float))>=8:
                s,np=normaltest(r.dropna().astype(float))
                if np<0.05:
                    normal=u'非正态,用Wilcoxon检验更可靠'
                else:
                    normal=u'正态，用t检验可靠'
                print u'正态检验结果',s,np,normal
            else:
                s=None
                np=None
                normal=u'n<8'
                print normal
            # 打印t检验结果
            print u'对',var,u'在',outcome,u'分组中检验结果如下：'
            print var,'group0(n)',grp0,'=',n0,',group1(n)',grp1,'=',n1,'\n','均数:',grp0,'=',m0,',',grp1,'=',m1,
            print '标准差:',grp0,'=',sd0,grp1,'=',sd1
            print u'中位数:',grp0,'=',median0,grp1,'=',median1
            print u'Q25:',grp0,'=',quatile25_0,grp1,'=',quatile25_1
            print u'Q75:',grp0,'=',quatile75_0,grp1,'=',quatile75_1
            print '差值group1-group0=',m1-m0
            print '独立样本t检验：','t=',t,'p=',p,value,
            print '独立样本Wilcoxon检验:','U=',u,'p=',xp,value2
            #output json file
            result_dict = {}
            result_dict[u'theme'] = u'outcome=' + outcome + u',group=' + grp0+ u',' + grp1
            result_dict[u'result'] = {}
            result_dict[u'result'][var]={}
            result_dict[u'result'][var][u'normal-test']={u'normal-test-p':np,u'normal-test-result':normal}
            result_dict[u'result'][var][u'basic']={u'Group0':{u'N':n0,u'mean':m0,u'std':sd0,u'median':median0,u'q25': quatile25_0,u'q75': quatile75_0},
                                                   u'Group1':{u'N': n1, u'mean': m1, u'std': sd1,u'median':median0,
                                                              u'q25':quatile25_0,u'q75':quatile75_0},
                                         u'difference':m1-m0,
                                         }
            result_dict[u'result'][var][u'test']={u't':t,u'p(t)':p,u't-result':value,
                                                  u'Wilcoxon-U':u,u'Wilcoxon-p':xp,u'WilcoxonResult':value2}
        if outfile is not None:
            print result_dict
            with codecs.open(outfile,'w','gbk') as fp:
                json.dump(result_dict,fp,indent=6,ensure_ascii=False)

    #2*n的卡方检验方法。
    def chisq_2n(self,df=None,columns=[],outcome=None,logname=None,outfile=None):
        print '您正在调用卡方检验模块'
        '''
        对样本中的连续变量进行t检验，并绘制密度图。
        param df:pd.DataFrame 导入的可分析样本数据
        param columns: list 需要分析的变量 ['col1', 'col2','col3'...]
        param outcome: df中的因变量，作为分组依据
        param logname：输出log路径
        param outfile:输出json路径
        '''
        import logging
        import os
        import pandas as pd
        import numpy as np
        from scipy.stats import chi2_contingency
        from scipy.stats import fisher_exact
        if df is None:
            df=self.df
        if columns==[] or outcome==None:
            print u'读取的变量列表：','\n',pd.Series(df.columns),'\n'
        else:
            pass
        if columns ==[]:
            print '指定变量应当为离散变量'
            columns=self.getcolumns(df=df)
        else:
            pass
        print u'选定离散变量为:','\n',pd.Series(columns)

        #调用结局或获得输入结局
        if outcome==None:
            print '结局应当为分组变量'
            outcome=self.getoutcome(df=df)
        else:
            pass
        print u'选定结局:',outcome
        print u'该程序将进行卡方检验。',outcome,u'作为结局','\n'
        print u'变量包含:','\n',pd.Series(pd.unique(df[outcome]))

        grp0_index=input('请输入group0的Index:')
        grp1_index=input('请输入group1的Index:')
        grp0=pd.unique(df[outcome])[grp0_index]
        grp1=pd.unique(df[outcome])[grp1_index]
        result_dict={}
        result_dict[u'theme']=u'outcome:'+outcome+u'---group'+str(grp0)+','+str(grp1)
        result_dict[u'result']={}
        for var in columns:
            table_r0=df[df[outcome]==grp0][var].value_counts(sort=False).sort_index() #选出数据做表格并且对齐index
            table_r1=df[df[outcome]==grp1][var].value_counts(sort=False).sort_index() #选出数据做表格并且对齐index
            if len(table_r0)==len(table_r1):
                pass
                #对齐两个table的index
            else:
                print '表格中有异常或空值'
                # print '\n',grp0,table_r0,table_r0/table_r0.sum(),
                # print '\n',grp1,table_r1,table_r1/table_r1.sum()
                if len(table_r0)>len(table_r1):
                    for ind in table_r0.index:
                        if ind in table_r1.index:
                            pass
                        elif ind not in table_r1.index:
                            table_r1.ix[ind]=0.1
                            table_r1=table_r1.sort_index()
                if len(table_r1)>len(table_r0):
                    for ind in table_r1.index:
                        if ind in table_r0.index:
                            pass
                        elif ind not in table_r0.index:
                            table_r0.ix[ind]=0.1
                            table_r0 = table_r0.sort_index()
            table_test=np.array([table_r0,table_r1])
                #进行卡方检验
            chi2,p,dof,expct=chi2_contingency(table_test)
            if table_test.shape==(2,2):
                oddsratio,p_fisher=fisher_exact(table_test)
            else:
                print'表格中有异常或空值，不能使用fisher检验'
            if p<0.05:
                stat=u'有统计学差异'
            else:
                stat=u'无统计学差异'
                #输出卡方检验结果
            print var
            print outcome,grp0,'频数与频率为','\n',table_r0,'\n',table_r0/table_r0.sum()
            print outcome,grp1,'频数与频率为','\n',table_r1,'\n',table_r1/table_r1.sum()
            print 'chisquare=',chi2,'\n','p=',p,'\n',stat
            print 'fisher p=',p_fisher
            #输出json结果

            result_dict[u'result'][var]={}
            result_dict[u'result'][var][u'test'] = {
                u'chisquare': chi2, u'chisuqare-p': p, u'chisqare-result': stat,
                u'fisher-p': p_fisher}
            try:
                for i in table_r0.index:
                    result_dict[u'result'][var][outcome+u':'+str(grp0)+u'-'+var+u':'+str(i)]=[table_r0[i],(table_r0/table_r0.sum())[i]]
                for i in table_r1.index:
                    result_dict[u'result'][var][outcome+u':'+str(grp1)+u'-'+var+u':'+str(i)]=[table_r1[i],(table_r1/table_r1.sum())[i]]
            except:
                print Exception



            #logging输出卡方检验结果
            # logging.basicConfig(level=logging.DEBUG,
            #                     format=' %(levelname)s %(message)s',
            #                     datefmt='%a, %d %b %Y %H:%M:%S',
            #                     filename=logname,
            #                     filemode='w')
            #
            # logging.info('--------------------------------------------------')
            # logging.info('variable:'+var)
            # logging.info('outcome:'+outcome)
            # logging.info('分组group0')
            # logging.info(grp0)
            # logging.info(table_r0.index)
            # logging.info(np.array(table_r0))
            # logging.info(np.array(table_r0*100/table_r0.sum()))
            # logging.info('分组group1')
            # logging.info(grp1)
            # logging.info(table_r1.index)
            # logging.info(np.array(table_r1))
            # logging.info(np.array(table_r1*100 / table_r1.sum()))
            # if chi2:
            #     logging.info('chisquare='+str(round(chi2,3)))
            #     if p < 0.05:
            #         logging.warning('p='+str(round(p,3)))
            #     else:
            #         logging.info('p='+str(round(p,3)))
            # if p_fisher:
            #     if p_fisher<0.05:
            #         logging.warning('fisher-p='+str(round(p_fisher,3)))
            #     else:
            #         logging.info('fisher-p='+str(round(p_fisher,3)))
            # logging.info('--------------------------------------------------')
            # if len(table_r0)>=len(table_r1):
            #     idx=table_r0.index
            # else:
            #     idx=table_r1.index
            # table_test=pd.DataFrame(table_test,index=idx)
            # for i in table_test.index:
            #     logging.info(i)
            #     logging.info(np.array(table_test.ix[i]))

        if outfile!=None:
            print result_dict
            with codecs.open(outfile,'w','gbk') as fp:
                json.dump(result_dict,fp,indent=6,ensure_ascii=False)


    #logistic回归方法
    def logistic_regression(self,df=None,columns=[],outcome=None):
        '''
        针对样本建立logistic模型。
        param df:pd.DataFrame 导入的可分析样本数据
        param columns: list 需要代入模型的的变量 ['col1', 'col2','col3'...]
        param outcome: df中的因变量
        '''
        print '您正在调用logistic建模模块'
        import pandas as pd
        import numpy as np
        # from sklearn.linear_model import LogisticRegression
        import statsmodels.api as sm
        import matplotlib.pyplot as plt

        if df is None:
            df=self.df
        else:
            pass
        if columns==[] or outcome==None:
            print u'读取的变量列表：','\n',pd.Series(df.columns),'\n'
        else:
            pass
         #调用变量或获得输入变量
        if columns ==[]:
            print '指定变量应当为0，1变量'
            columns=self.getcolumns(df=df)
        else:
            pass
        print u'选定连续变量为:','\n',pd.Series(columns)

        #调用结局或获得输入结局
        if outcome==None:
            print '结局应当为0，1变量'
            outcome=self.getoutcome(df=df)
        else:
            pass
        print u'选定结局:',outcome
        import copy
        ncol=copy.copy(columns)
        ncol.append(outcome)
        df_ana=df[ncol].dropna()
        x=df_ana[columns]
        print x.head(2)
        y=df_ana[outcome]
        print y.head(2)
        model = sm.Logit(y, sm.add_constant(x))
        result = model.fit()
        print 'logistic模型参数：','\n',result.summary()
        print '去log化结果参数：','\n',np.exp(result.params)

    #方差分析方法
    def anova(self,df=None,columns=[],outcome=None):
        print '将进行ANOVA和Kruskal-Wallis检验，前者针对正态样本后者针对非正态：'
        '''
        针对样本进行方差分析。
        param df:pd.DataFrame 导入的可分析样本数据
        param columns: list 需要代入模型的的变量 ['col1', 'col2','col3'...]
        param outcome: df中的因变量
        '''
        from statsmodels.formula.api import ols
        from statsmodels.stats.anova import anova_lm
        import pandas as pd
        import numpy as np
        from scipy.stats import f_oneway,kruskal

        if df is None:
            df=self.df
        else:
            pass

        if columns==[] or outcome==None:
            print u'读取的变量列表：','\n',pd.Series(df.columns),'\n'
        else:
            pass
         #调用变量或获得输入变量
        if columns ==[]:
            print '指定变量应当为连续变量'
            columns=self.getcolumns(df=df)
        else:
            pass
        print u'选定连续变量为:','\n',pd.Series(columns)

        #调用结局或获得输入结局
        if outcome==None:
            print '结局应当为分组变量'
            outcome=self.getoutcome(df=df)
        else:
            pass
        print u'选定结局:',outcome
        grp=pd.unique(df[df[outcome].isnull()==False][outcome])
        print '剔除结局缺失数：',len(df[df[outcome].isnull()==True][outcome])
        df_ana = df[df[outcome].isnull() == False]
        args=[]
        u=[]
        p2=[]
        f=[]
        p=[]
        for col in columns:
            print col
            for var in grp:
               df_group=df_ana[df_ana[outcome]==var][col]
               args.append(df_group)
               print 'Group Tag:',var,'N=',len(df_group),'--Means:',df_group.mean(),'std=',df_group.std()
            f.append(f_oneway(*args)[0])
            p.append(f_oneway(*args)[1])
            u.append(kruskal(*args)[0])
            p2.append(kruskal(*args)[1])

        print 'ANOVA方差分析结果为：'
        print columns,'\n','F=',f,'\n','p=',p
        print 'Kruskal_Wallis非参数检验结果为：'
        print columns,'\n','U=',u,'\n','p=',p2

    def continous_des(self,df=None,columns=[],outfile=None):
        '''
        对连续变量进行统计学描述
        :param df: pd.DataFrame 分析数据
        :param columns: 需要描述的连续变量
        :return: 无
        '''

        if df is None:
            df=self.df
        else:
            pass
        #调取所有列
        print u'读取的变量列表：','\n',pd.Series(df.columns),'\n'

        #输入选定的变量
        if columns ==[]:
            print '指定变量应当为连续变量'
            columns=self.getcolumns(df=df)
        else:
            pass
        print u'选定连续变量为:','\n',pd.Series(columns)
        #输出统计量
        def constat(x):
            return pd.Series([len(x),x.min(),x.max(), x.mean(), x.std(), x.median(), x.quantile(0.25), x.quantile(0.75)],
                             index=['N','最小值', '最大值', '均数', '标准差', '中位数', 'Q1', 'Q3'])
        result=df[columns].apply(constat)
        print result
        #csv output
        if outfile!=None:
            result.transpose().to_csv(outfile,encoding='gbk')
        #输出箱形图
        import matplotlib.pyplot as plt
        for col in columns:
            plt.boxplot(np.array(df[col].dropna()))
            plt.ylabel(col)
            plt.show()
        #输出散点图
        #输出直方图



    def categorical_des(self,df=None,columns=[],outfile=None):
        '''
        对离散变量进行统计学描述
               :param df: pd.DataFrame 分析数据
               :param columns: 需要描述的离散变量
               :outfile:txt 文件路径
               :return: 无
               
        '''
        import matplotlib.pyplot as plt
        if df is None:
            df = self.df
        else:
            pass
        # 调取所有列
        print u'读取的变量列表：', '\n', pd.Series(df.columns), '\n'
        # 输入选定的变量
        if columns == []:
            print '指定变量应当为离散变量'
            columns = self.getcolumns(df=df)

        else:
            pass
        print u'选定离散变量为:', '\n', pd.Series(columns)
        #构建dataframe和字典，以生成外置的excel文件
        result_df=pd.DataFrame(index=columns)
        result_dict={}
        #输出统计量
        for col in columns:
            table=df[col].value_counts()
            result_dict[col]={}
            rate=table/table.sum()
            for i in table.index:
                #读取table的数据
                result_dict[col][i]={u'freq':table[i],u'rate':rate[i]}
            # result_df[col]=pd.DataFrame(columns=table.index)
            # for i in table.index:
            #     result_df.loc[col,i]=table[i]
            #打印统计量
            print col
            print table
            print table/table.sum()
        #输出饼图
            plt.figure()
            labels=table.index
            plt.pie(table,labels=labels)
            plt.show()
        print result_dict
        print pd.DataFrame(result_dict)
        if outfile!=None:
            with codecs.open(outfile,'w','gbk') as fp:
                json.dump(result_dict,fp,indent=6,ensure_ascii=False)





        #输出直方图

    def correlation(self,df=None,feature_A=None,feature_B=None):
        '''
            对变量进行相关性评估
          :param df: pd.DataFrame 分析数据
          :param feature_A,feature_B: 需要代入矩阵的连续变量
          :return: 无
        '''
        from scipy.stats import pearsonr,spearmanr

        if df is None:
            df = self.df
        else:
            pass
            # 调取所有列
        if feature_A is None or feature_B is None:
            print u'读取的变量列表：', '\n', pd.Series(df.columns), '\n'
        else:
            pass
        #输入相关矩阵X轴
        if feature_A is None:
            print '指定变量应当为连续变量'
            feature_A = self.getoutcome(df=df)
        else:
            pass
        print u'选定A:', '\n', pd.Series(feature_A)
        #输入相关矩阵Y轴
        if feature_B is None:
            print '指定变量应当为连续变量'
            feature_B = self.getoutcome(df=df)
        else:
            pass
        print u'选定B:', '\n', pd.Series(feature_B)
        #计算Peason相关系数
        df_ana=df[[feature_A,feature_B]].dropna()
        r,p=pearsonr(np.array(df_ana[feature_A]), np.array(df_ana[feature_B]))
        r2,p2=spearmanr(np.array(df_ana[feature_A]), np.array(df_ana[feature_B]))
        print feature_A,'vs',feature_B,'Pearson r=',r,'p=',p
        print feature_A,'vs',feature_B,'Spearman r=',r2,'p=',p2
        print 'N=',len(df_ana)

    def scatter_plot(self,df=None,feature_A=None,feature_B=None,label=None):
        '''
        对变量进行相关性评估
            :param df: pd.DataFrame 分析数据
            :param feature_A,feature_B: 需要代入矩阵的连续变量
            :param label:分组方式，可选择输入
            :return: 无
        '''

        import matplotlib
        import matplotlib.pyplot as plt
        #创建data
        if df is None:
            df = self.df
        else:
            pass
        # 调取所有列
        if feature_A is None or feature_B is None:
            print u'读取的变量列表：', '\n', pd.Series(df.columns), '\n'
        else:
            pass
        #输入相关矩阵X轴
        if feature_A is None:
            print '请输入A变量，指定变量应当为连续变量'
            feature_A = self.getoutcome(df=df)
        else:
            pass
        print u'选定A:', '\n', feature_A
        #输入相关矩阵Y轴
        if feature_B is None:
            print '请输入B变量，指定变量应当为连续变量'
            feature_B = self.getoutcome(df=df)
        else:
            pass
        print u'选定B:', '\n', feature_B
        print u'选定label:', '\n', label
        #输出散点图
        if label is not None:
            df_ana=df[[feature_A,feature_B,label]].dropna()
        else:
            df_ana=df[[feature_A,feature_B]].dropna()
        #一般散点图
        if label is None:
            plt.figure(figsize=(8,4),dpi=100,facecolor='white',edgecolor='black')
            plt.scatter(df[feature_A],df[feature_B],marker='.')
            plt.xlabel(feature_A)
            plt.ylabel(feature_B)
            plt.title(feature_A+' vs '+feature_B)
            plt.show()
        #带分组的散点图
        else:
            plt.figure(figsize=(8,4),dpi=100,facecolor='white',edgecolor='black')
            for grp in df_ana[label].unique():
                area=np.pi*4**2
                d1=df_ana[df_ana[label]==grp][feature_A]
                d2=df_ana[df_ana[label]==grp][feature_B]
                plt.scatter(d1,d2, label=grp, marker='.',s=area)
            plt.legend(loc='upper right')
            plt.xlabel(feature_A)
            plt.ylabel(feature_B)
            plt.title(feature_A+' vs '+feature_B+' by '+label)
            plt.show()













