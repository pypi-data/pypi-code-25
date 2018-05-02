from pyupbit.core import *


class Upbit:
    def __init__(self):
        pass

    @staticmethod
    def get_tickers():
        pass

    @staticmethod
    def get_market_detail(currency):
        pass

    @staticmethod
    def get_current_price(currency):
        """
        최종 체결 가격 조회
        :param currency: BTC/ETH/DASH/LTC/ETC/XRP/BCH/XMR/ZEC/QTUM/BTG/EOS/ICX/VEN,TRX/ELF/MITH/MCO/OMG/KNC
        :return        : price
        """
        try:
            resp = (publicApi.recent_transactions(currency))
            return resp[0]['tradePrice']
        except TypeError:
            return resp

    @staticmethod
    def get_orderbook(currency):
        pass

    def get_trading_fee(self):
        pass



if __name__ == "__main__":
    pass
    # ----------------------------------------------------------------------------------------------
    # 최종 체결 가격
    # ----------------------------------------------------------------------------------------------
    # for coin in Bithumb.get_tickers():
    #     print(coin, Bithumb.get_current_price(coin))
    coin = "XRP"
    r = Upbit.get_current_price(coin)
    print(coin, r)
    # ----------------------------------------------------------------------------------------------
    # 시장 현황 상세정보
    # ----------------------------------------------------------------------------------------------
    # for coin in  Bithumb.get_tickers():
    #     print(coin, Bithumb.get_market_detail(coin))

    # ----------------------------------------------------------------------------------------------
    # 매수/매도 호가 (public)
    # ----------------------------------------------------------------------------------------------
    # for coin in  Bithumb.get_tickers():
    #     print(coin, Bithumb.get_orderbook(coin))

