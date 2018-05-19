import pandas as pd
import matplotlib.pyplot as plt
from . import get_data


class TeamStat:
    
    def __init__(self,tid):
        self.tid = tid
        self.team_data = pd.DataFrame()
        self.personal_data = pd.DataFrame()
        
        
    def get_team_data(self,pages=-1):
        self.team_data = get_data.get_team(self.tid,pages).astype({'timestamp':int})

    def get_personal_data(self,source='https://www.dropbox.com/s/nr12wbnnx7m3w89/charcount.csv?dl=1'):
        df = pd.read_csv(source)
        if 'content' in df.columns and 'timestamp' in df.columns:
            if df.dtypes['content'] == int and df.dtypes['timestamp'] == int:
                self.personal_data = df
        else:
            print("personal data dataframe doesn't fit expected dtypes")

    def get_team_history(self):
        hdf = self.team_data[self.team_data['t1'] == str(self.tid)]
        adf = self.team_data[self.team_data['t2'] == str(self.tid)]

        oppos = pd.concat([hdf['t2-name'],adf['t1-name']]).value_counts().head(10)
        comps = self.team_data['compname'].value_counts()
        return {'opps':oppos,'comps':comps}
        
    def connect_personal(self,width=3000,minutebins=[0,46,46+15,46 + 15 + 48]):
        
        matchlength = 60 * minutebins[-1]

        o2 = pd.concat(list(self.team_data['timestamp'].apply(lambda x: getaround(x,self.personal_data,width,matchlength))))

        bins = list(range(-width,width + matchlength +1,int((width * 2 + matchlength)/20)))
        groups = o2['content'].groupby(pd.cut(o2['diff'], bins)).agg(['sum','count','median'])

        groups.index = bincrt(bins,minutebins)[0]
        spans = bincrt(bins,minutebins)[1]

        groups['sum'].plot(kind='bar',color='blue')

        plt.axvspan(spans[0], spans[1], color='r', alpha=0.3, lw=0)
        plt.axvspan(spans[2], spans[3], color='r', alpha=0.3, lw=0)
        plt.title('Total characters')
        plt.figure()

        groups['count'].plot(kind='bar',color='blue')

        plt.axvspan(spans[0], spans[1], color='r', alpha=0.3, lw=0)
        plt.axvspan(spans[2], spans[3], color='r', alpha=0.3, lw=0)
        plt.title('Total messages')
        plt.figure()

        groups['median'].plot(kind='bar',color='blue')

        plt.axvspan(spans[0], spans[1], color='r', alpha=0.3, lw=0)
        plt.axvspan(spans[2], spans[3], color='r', alpha=0.3, lw=0)
        plt.title('Median character count')

        plt.show()



def getaround(stamp,df,width,matchlength):
    odf = df[(df['timestamp'] < (stamp + matchlength + width)) & 
            (df['timestamp'] > (stamp - width))].copy()
    odf.loc[odf.index,'diff'] = odf['timestamp'] - stamp
    return odf

def bincrt(bins,minutebins):
    diff = (bins[1] - bins[0]) / 60
    span = [0] * 4
    out = []
    for i in range(len(bins)-1):
        b_s = bins[i] / 60
        b_e = bins[i+1] / 60
        b_m = int(b_s + diff / 2)
        #add labels for minutes and diffs
        if b_m < minutebins[0]:
            out.append(str(b_m))
            
        elif b_m < minutebins[1]:
            out.append(str(b_m) + "'")
        elif b_m < minutebins[2]:
            out.append("HT-" + str(b_m - minutebins[1]))
        elif b_m < minutebins[3]:
            out.append(str(b_m - (minutebins[2] - minutebins[1]) ) + "'")
        else:
            out.append('+' + str(b_m - minutebins[3]))
        #add points to shade in match on graphs:
        for j in range(4):
            if b_s < minutebins[j] and b_e > minutebins[j]:
                span[j] = i + (minutebins[j] - b_m)/ (diff)
    return [out,span]



