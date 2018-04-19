from ratelimit import *
from vericoin.util import *
from vericoin.crypto.core import *
import pandas as pd


class Crypto:

    def __init__(self):
        self.api = RestApi()

    def get_ohlcv_gen(self, start, end, market="KRW", coin="BTC", exchange="Bithumb"):
        target = str2dt(end)
        while True:
            resp = self.get_ohlcv(start, end, market, coin, exchange)
            yield resp

            last = str2dt(resp.iloc[-1]['time'])
            if last == target:
                break
            start = last + datetime.timedelta(minutes=1)
            start = start.strftime("%Y-%m-%d %H:%M:%S")


    @rate_limited(1)
    def get_ohlcv(self, start, end, market="KRW", coin="BTC", exchange="Bithumb"):
        """
        target날짜부터 이전 time의 coin OHLCV를 가져온다.              
        :param target: 조회 날짜 "년-월-일" 형태의 문자열. 예) 2018-03-03        
        :param count: 조사 개수          
        :param market: 시장
        :param coin: 코인 이름 약어
        :return: (날짜, open, high, low, close, volume) dataframe       
        """
        start = str2dt(start)
        end = str2dt(end)
        count = int((end - start).seconds / 60)
        count = min(count, 1999)

        target = start + datetime.timedelta(minutes=count)

        resp = self.api.histominute(toTs=dt2ts(target), fsym=coin, tsym=market, limit=count, e=exchange)
        if resp['Response'] != 'Success':
            return resp['Message']
        else:
            # [-limit:] is used for API minor bug
            #   - 1개의 데이터를 요청해도 서버가 2개의 데이터를 반환한다.
            # dictionary to dataframe
            df = pd.DataFrame.from_records(resp['Data'][-count-1:]).loc[:, :'volumefrom'].rename(columns={'volumefrom': 'volume'})
            df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
            df['time'] = df.time.apply(ts2str)
            return df

    @rate_limited(1)
    def get_ohlcv_day(self, target, count=1, market="KRW", coin="BTC", exchange="Korbit"):
        """
        target날짜부터 이전 time의 coin OHLCV를 가져온다.              
        :param target: 조회 날짜 "년-월-일" 형태의 문자열. 예) 2018-03-03        
        :param count: 조사 개수       
        :param market: 시장
        :param coin: 코인 이름 약어
        :return: (날짜, open, high, low, close, volume) dataframe       
        """
        toTs = dt2ts(str2dt(target) + datetime.timedelta(hours=9))
        resp = self.api.histoday(toTs=toTs, fsym=coin, tsym=market, limit=count - 1, e=exchange)
        if resp['Response'] != 'Success':
            return resp['Message']
        else:
            # [-limit:] is used for API minor bug
            #   - 1개의 데이터를 요청해도 서버가 2개의 데이터를 반환한다.
            # dictionary to dataframe
            df = pd.DataFrame.from_records(resp['Data'][-count:]).loc[:, :'volumefrom'].rename(
                columns={'volumefrom': 'volume'})
            df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
            df['time'] = df.time.apply(ts2str)
            return df

if __name__ == "__main__":
    c = Crypto()

    days = c.get_ohlcv_gen(start='2018-04-18 09:00:00', end='2018-04-18 09:23:00')

    for df in days:
        print(df)