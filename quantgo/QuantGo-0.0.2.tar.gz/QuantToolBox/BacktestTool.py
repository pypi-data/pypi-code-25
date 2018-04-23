#-*- coding:utf-8 -*-
import numpy as np

class StrategyData(object):
    def __init__(self):

        self.start_date = None
        self.end_date = None
        self. timestamp =None

        self. close =None
        self. open =None
        self. high =None
        self. low =None
        self. volume =None
        self. open_interest =None

        self. DailyOpen =None
        self. DailyClose =None
        self. DailyHigh =None
        self. DailyLow =None

        self. DayOpen =None
        self. DayClose =None

    def set_data(self ,raw_data):
        pass

class BacktestSetting(object):
    def __init__(self):
        print ("Use default instrument backtest setting")
        self.Slippage = 1  # 1 min_move
        self.Commission = 0.0001
        self.Margin_Rate = 0.1
        self.Tick_Value = 10
        self.Min_Move = 1
        self.Exchange = None

    def set_instrument(self, InstrumentConfig):
        self.Slippage = InstrumentConfig['Slippage']  # 1 min_move
        self.Commission = InstrumentConfig['Commission']
        self.Margin_Rate = InstrumentConfig['Margin_Rate']
        self.Tick_Value = InstrumentConfig['Tick_Value']
        self.Min_Move = InstrumentConfig['Min_Move']
        self.Exchange = InstrumentConfig['Exchange']


class BaseStrategy(StrategyData, BacktestSetting):
    def __init__(self,InstrumentConfig=None,strategy_id=None):

        super(StrategyData, self).__init__()
        super(BacktestSetting, self).__init__()

        self.strategy_id = strategy_id
        self.MarketPosition = 0  # 仓位状态 -1表示持有空头 0表示无持仓 1表示持有多头
        self.LongEntryPrice = None
        self.ShortEntryPrice = None
        self.DataLength = 0
        self.TotalLots = 0
        self.cur_bar = 0

        if InstrumentConfig is not None:
            self.set_instrument(InstrumentConfig)
            self.Performance = Performance(InstrumentConfig)
        self.Performance=Performance()
        self.Performance.strategy_id=self.strategy_id

    def strategy(self):
        pass

    def Buy(self, lots, EntryPrice=None):
        if lots <= 0:
            raise Exception("Error lots")

        # print "开多"
        if EntryPrice is None:
            EntryPrice = self.open[self.cur_bar]
            # 平空开多
        if self.MarketPosition == -1:
            print "平空开多", EntryPrice, self.timestamp[self.cur_bar]
            self.MarketPosition = 1
            self.Performance.ShortMargin[self.cur_bar] = 0  # 平空后空头保证金为0
            self.Performance.MyEntryPrice[self.cur_bar] = EntryPrice + self.Slippage * self.Min_Move  # 建仓价格(也是平空仓的价格)
            self.Performance.ClosePosNum = self.Performance.ClosePosNum + 1
            self.Performance.ClosePosPrice[self.Performance.ClosePosNum] = self.Performance.MyEntryPrice[
                self.cur_bar]  # 记录平仓价格
            self.Performance.CloseDate[self.Performance.ClosePosNum] = self.timestamp[self.cur_bar]  # 记录平仓时间
            self.Performance.OpenPosNum = self.Performance.OpenPosNum + 1
            self.Performance.OpenPosPrice[self.Performance.OpenPosNum] = self.Performance.MyEntryPrice[
                self.cur_bar]  # 记录开仓价格
            self.Performance.OpenDate[self.Performance.OpenPosNum] = self.timestamp[self.cur_bar]  # 记录开仓时间
            self.Performance.Type[self.Performance.OpenPosNum] = 1  # 记录开仓类型
            # 平空仓时的静态权益
            self.Performance.StaticEquity[self.cur_bar] = self.Performance.StaticEquity[self.cur_bar - 1] + (
                                                                                                            self.Performance.OpenPosPrice[
                                                                                                                self.Performance.OpenPosNum - 1] -
                                                                                                            self.Performance.ClosePosPrice[
                                                                                                                self.Performance.ClosePosNum]) / self.Min_Move * self.Tick_Value * self.TotalLots - \
                                                          self.Performance.OpenPosPrice[
                                                              self.Performance.OpenPosNum - 1] * self.Tick_Value * self.TotalLots * self.Commission - \
                                                          self.Performance.ClosePosPrice[
                                                              self.Performance.ClosePosNum] * self.Tick_Value * self.TotalLots * self.Commission
            self.Performance.DynamicEquity[self.cur_bar] = self.Performance.StaticEquity[self.cur_bar] + (self.close[
                                                                                                              self.cur_bar] -
                                                                                                          self.Performance.OpenPosPrice[
                                                                                                              self.Performance.OpenPosNum]) * self.Tick_Value * self.TotalLots / self.Min_Move
            self.TotalLots = lots

        if self.MarketPosition == 0:
            # print "Buy one"
            print "空仓开多", EntryPrice, self.timestamp[self.cur_bar]
            self.MarketPosition = 1
            self.TotalLots += lots
            self.Performance.MyEntryPrice[self.cur_bar] = EntryPrice + self.Slippage * self.Min_Move  # 建仓价格
            self.Performance.OpenPosNum = self.Performance.OpenPosNum + 1
            self.Performance.OpenPosPrice[self.Performance.OpenPosNum] = self.Performance.MyEntryPrice[
                self.cur_bar]  # 记录开仓价格
            self.Performance.OpenDate[self.Performance.OpenPosNum] = self.timestamp[self.cur_bar]  # 记录开仓时间
            self.Performance.Type[self.Performance.OpenPosNum] = 1  # 方向为多头
            self.Performance.StaticEquity[self.cur_bar] = self.Performance.StaticEquity[self.cur_bar - 1]
            self.Performance.DynamicEquity[self.cur_bar] = self.Performance.StaticEquity[self.cur_bar] + (self.close[
                                                                                                              self.cur_bar] -
                                                                                                          self.Performance.OpenPosPrice[
                                                                                                              self.Performance.OpenPosNum]) * self.Tick_Value * self.TotalLots / self.Min_Move
        self.Performance.LongMargin[self.cur_bar] = self.close[
                                                        self.cur_bar] * self.TotalLots * self.Tick_Value * self.Margin_Rate / self.Min_Move  # 多头保证金
        self.Performance.Cash[self.cur_bar] = self.Performance.DynamicEquity[self.cur_bar] - \
                                              self.Performance.LongMargin[self.cur_bar]  # 可用资金
        self.Performance.pos[self.cur_bar] = self.MarketPosition
        self.Performance.LotSeries[self.Performance.OpenPosNum] = self.TotalLots

    def SellShort(self, lots, EntryPrice=None):
        if lots <= 0:
            raise Exception("Error lots")

        # print "开空"
        if EntryPrice is None:
            EntryPrice = self.open[self.cur_bar]

        if self.MarketPosition == 1:
            print "平多开空", EntryPrice, self.timestamp[self.cur_bar]
            self.MarketPosition = -1
            self.Performance.LongMargin[self.cur_bar] = 0  # 平多后多头保证金为0了
            self.Performance.MyEntryPrice[self.cur_bar] = EntryPrice - self.Slippage * self.Min_Move
            self.Performance.ClosePosNum = self.Performance.ClosePosNum + 1
            self.Performance.ClosePosPrice[self.Performance.ClosePosNum] = self.Performance.MyEntryPrice[self.cur_bar]
            self.Performance.CloseDate[self.Performance.ClosePosNum] = self.timestamp[self.cur_bar]
            self.Performance.OpenPosNum = self.Performance.OpenPosNum + 1
            self.Performance.OpenPosPrice[self.Performance.OpenPosNum] = self.Performance.MyEntryPrice[self.cur_bar]
            self.Performance.OpenDate[self.cur_bar] = self.timestamp[self.cur_bar]
            self.Performance.Type[self.Performance.OpenPosNum] = -1
            self.Performance.StaticEquity[self.cur_bar] = self.Performance.StaticEquity[self.cur_bar - 1] + (
                                                                                                            self.Performance.ClosePosPrice[
                                                                                                                self.Performance.ClosePosNum] -
                                                                                                            self.Performance.OpenPosPrice[
                                                                                                                self.Performance.OpenPosNum - 1]) / self.Min_Move * self.Tick_Value * self.TotalLots - \
                                                          self.Performance.OpenPosPrice[
                                                              self.Performance.OpenPosNum - 1] * self.Tick_Value * self.TotalLots * self.Commission - \
                                                          self.Performance.ClosePosPrice[
                                                              self.Performance.ClosePosNum] * self.Tick_Value * self.TotalLots * self.Commission
            self.Performance.DynamicEquity[self.cur_bar] = self.Performance.StaticEquity[self.cur_bar] + (
                                                                                                         self.Performance.OpenPosPrice[
                                                                                                             self.Performance.OpenPosNum] -
                                                                                                         self.close[
                                                                                                             self.cur_bar]) * self.Tick_Value * self.TotalLots / self.Min_Move
            self.TotalLots = lots

        # 空仓开空
        if self.MarketPosition == 0:
            print "空仓开空", EntryPrice, self.timestamp[self.cur_bar]
            self.MarketPosition = -1
            self.TotalLots += lots
            self.Performance.MyEntryPrice[self.cur_bar] = EntryPrice - self.Slippage * self.Min_Move
            self.Performance.OpenPosNum = self.Performance.OpenPosNum + 1
            self.Performance.OpenPosPrice[self.Performance.OpenPosNum] = self.Performance.MyEntryPrice[self.cur_bar]
            self.Performance.OpenDate[self.Performance.OpenPosNum] = self.timestamp[self.cur_bar]
            self.Performance.Type[self.Performance.OpenPosNum] = -1
            self.Performance.StaticEquity[self.cur_bar] = self.Performance.StaticEquity[self.cur_bar - 1]
            self.Performance.DynamicEquity[self.cur_bar] = self.Performance.StaticEquity[self.cur_bar] + (
                                                                                                         self.Performance.OpenPosPrice[
                                                                                                             self.Performance.OpenPosNum] -
                                                                                                         self.close[
                                                                                                             self.cur_bar]) * self.Tick_Value * self.TotalLots / self.Min_Move
        self.Performance.ShortMargin[self.cur_bar] = self.close[
                                                         self.cur_bar] * self.TotalLots * self.Tick_Value * self.Margin_Rate / self.Min_Move
        self.Performance.Cash[self.cur_bar] = self.Performance.DynamicEquity[self.cur_bar] - \
                                              self.Performance.StaticEquity[self.cur_bar]
        self.Performance.pos[self.cur_bar] = self.MarketPosition
        self.Performance.LotSeries[self.Performance.OpenPosNum] = self.TotalLots

    def Sell(self, lots, EntryPrice=None):
        if lots <= 0:
            raise Exception("Error lots")

        # print "平多"
        if EntryPrice is None:
            EntryPrice = self.open[self.cur_bar]

        if self.MarketPosition == 1:
            print "平多", EntryPrice, self.timestamp[self.cur_bar]
            self.MarketPosition = 0
            self.Performance.LongMargin[self.cur_bar] = 0  # 平多后多头保证金为0了
            self.Performance.ClosePosNum = self.Performance.ClosePosNum + 1
            self.Performance.ClosePosPrice[self.Performance.ClosePosNum] = EntryPrice - self.Slippage * self.Min_Move
            self.Performance.CloseDate[self.Performance.ClosePosNum] = self.timestamp[self.cur_bar]

            self.Performance.StaticEquity[self.cur_bar] = self.Performance.StaticEquity[self.cur_bar - 1] + (
                                                                                                            self.Performance.ClosePosPrice[
                                                                                                                self.Performance.ClosePosNum] -
                                                                                                            self.Performance.OpenPosPrice[
                                                                                                                self.Performance.OpenPosNum]) / self.Min_Move * self.Tick_Value * self.TotalLots - \
                                                          self.Performance.ClosePosPrice[
                                                              self.Performance.ClosePosNum] * self.Tick_Value * self.TotalLots * self.Commission
            print "平多：", self.Performance.StaticEquity[self.cur_bar - 1], (self.Performance.ClosePosPrice[
                                                                               self.Performance.ClosePosNum] -
                                                                           self.Performance.OpenPosPrice[
                                                                               self.Performance.OpenPosNum]) / self.Min_Move * self.Tick_Value * self.TotalLots
            self.Performance.DynamicEquity[self.cur_bar] = self.Performance.StaticEquity[self.cur_bar]
            self.TotalLots -= lots

    def BuyToCover(self, lots, EntryPrice=None):
        if lots <= 0:
            raise Exception("Error lots")

        if EntryPrice is None:
            EntryPrice = self.open[self.cur_bar]
            # 平空
        if self.MarketPosition == -1:
            print "平空", EntryPrice, self.timestamp[self.cur_bar]
            self.MarketPosition = 0
            self.Performance.ShortMargin[self.cur_bar] = 0  # 平空后空头保证金为0
            self.Performance.ClosePosNum = self.Performance.ClosePosNum + 1
            self.Performance.ClosePosPrice[
                self.Performance.ClosePosNum] = EntryPrice + self.Slippage * self.Min_Move  # 记录平仓价格
            self.Performance.CloseDate[self.Performance.ClosePosNum] = self.timestamp[self.cur_bar]  # 记录平仓时间
            # 平空仓时的静态权益
            self.Performance.StaticEquity[self.cur_bar] = self.Performance.StaticEquity[self.cur_bar - 1] + (
                                                                                                            self.Performance.OpenPosPrice[
                                                                                                                self.Performance.OpenPosNum] -
                                                                                                            self.Performance.ClosePosPrice[
                                                                                                                self.Performance.ClosePosNum]) / self.Min_Move * self.Tick_Value * self.TotalLots - \
                                                          self.Performance.ClosePosPrice[
                                                              self.Performance.ClosePosNum] * self.Tick_Value * self.TotalLots * self.Commission
            print "平空：", self.Performance.StaticEquity[self.cur_bar - 1], (self.Performance.OpenPosPrice[
                                                                               self.Performance.OpenPosNum] -
                                                                           self.Performance.ClosePosPrice[
                                                                               self.Performance.ClosePosNum]) / self.Min_Move * self.Tick_Value * self.TotalLots
            self.Performance.DynamicEquity[self.cur_bar] = self.Performance.StaticEquity[self.cur_bar]
            self.TotalLots -= lots

    def iterations(self,start_bar=None):
        for i in xrange(self.DataLength):
            if start_bar is None and i <start_bar:
                continue

            if len(self.Performance.MyEntryPrice) == 0:
                raise Exception("Please set data length!")
            self.cur_bar = i

            if self.MarketPosition == 0:
                self.Performance.LongMargin[i] = 0  # 多头保证金
                self.Performance.ShortMargin[i] = 0  # 空头保证金
                self.Performance.StaticEquity[i] = self.Performance.StaticEquity[i - 1]  # 静态权益
                self.Performance.DynamicEquity[i] = self.Performance.StaticEquity[i]  # 动态权益
                self.Performance.Cash[i] = self.Performance.DynamicEquity[i]  # 可用资金
            if self.MarketPosition == 1:
                self.Performance.LongMargin[i] = self.close[i] * self.Performance.LotSeries[
                    self.Performance.OpenPosNum] * self.Tick_Value * self.Margin_Rate / self.Min_Move
                self.Performance.StaticEquity[i] = self.Performance.StaticEquity[i - 1]
                self.Performance.DynamicEquity[i] = self.Performance.StaticEquity[i] + (self.close[i] -
                                                                                        self.Performance.OpenPosPrice[
                                                                                            self.Performance.OpenPosNum]) * self.Tick_Value * \
                                                                                       self.Performance.LotSeries[
                                                                                           self.Performance.OpenPosNum] / self.Min_Move
                self.Performance.Cash[i] = self.Performance.DynamicEquity[i] - self.Performance.LongMargin[i]
                print "持有多头", self.TotalLots, self.Performance.DynamicEquity[i]
            if self.MarketPosition == -1:
                self.Performance.ShortMargin[i] = self.close[i] * self.Performance.LotSeries[
                    self.Performance.OpenPosNum] * self.Tick_Value * self.Margin_Rate / self.Min_Move
                self.Performance.StaticEquity[i] = self.Performance.StaticEquity[i - 1]
                self.Performance.DynamicEquity[i] = self.Performance.StaticEquity[i] + (self.Performance.OpenPosPrice[
                                                                                            self.Performance.OpenPosNum] -
                                                                                        self.close[
                                                                                            i]) * self.Tick_Value * \
                                                                                       self.Performance.LotSeries[
                                                                                           self.Performance.OpenPosNum] / self.Min_Move
                self.Performance.Cash[i] = self.Performance.DynamicEquity[i] - self.Performance.ShortMargin[i]
                print "持有空头", self.TotalLots, self.Performance.DynamicEquity[i]
            yield i


class Performance(BacktestSetting):
    def __init__(self, InstrumentConfig=None):
        BacktestSetting.__init__(self)
        # print self.Tick_Value
        if InstrumentConfig is not None:
            self.set_instrument(InstrumentConfig)
        self.strategy_id=None

    def set_performance(self, length, InitCash=10000):
        # 交易记录变量
        self.DataLength = length
        self.LotSeries = np.zeros((length, 1))
        self.MyEntryPrice = np.zeros((length, 1))  # 买卖价格
        self.pos = np.zeros((length, 1))  # 记录仓位情况，-1表示持有空头，0表示无持仓，1表示持有多头
        self.Type = np.zeros((length, 1))  # 买卖类型，1标示多头，-1标示空头
        self.OpenPosPrice = np.zeros((length, 1))  # 记录建仓价格
        self.ClosePosPrice = np.zeros((length, 1))  # 记录平仓价格
        self.OpenPosNum = 0  # 建仓价格序号
        self.ClosePosNum = 0  # 平仓价格序号
        self.OpenDate = [''] * length  # 建仓时间
        self.CloseDate = [''] * length  # 平仓时间
        self.NetMargin = np.zeros((length, 1))  # 净利
        self.CumNetMargin = np.zeros((length, 1))  # 累计净利
        self.ReturnRate = np.zeros((length, 1))  # 收益率
        self.CumReturnRate = np.zeros((length, 1))  # 累计收益率
        self.CostSeries = np.zeros((length, 1))  # 记录交易成本
        self.BackRatio = np.zeros((length, 1))  # 记录回撤比例

        ##记录资产变化变量
        self.LongMargin = np.zeros((length, 1))  # 多头保证金
        self.ShortMargin = np.zeros((length, 1))  # 空头保证金
        self.Cash = np.ones((length, 1)) * InitCash  # 可用资金,初始资金为Init_Cash
        self.DynamicEquity = np.ones((length, 1)) * InitCash  # 动态权益,初始资金为Init_Cash
        self.StaticEquity = np.ones((length, 1)) * InitCash  # 静态权益,初始资金为Init_Cash

    def analyze(self):
        # 记录交易长度
        RecLength = self.ClosePosNum

        # 净利润和收益率
        for i in xrange(0, RecLength):

            # 交易成本(建仓+平仓)
            self.CostSeries[i] = self.OpenPosPrice[i] * self.Tick_Value * self.LotSeries[i] * self.Commission + \
                                 self.ClosePosPrice[i] * self.Tick_Value * self.LotSeries[i] * self.Commission

            # 净利润
            # 多头建仓时
            if self.Type[i] == 1:
                self.NetMargin[i] = (self.ClosePosPrice[i] - self.OpenPosPrice[i]) / self.Min_Move * self.Tick_Value * \
                                    self.LotSeries[i] - self.CostSeries[i]
                print "多", self.Min_Move, self.Tick_Value, self.LotSeries[i], self.NetMargin[i], (
                self.ClosePosPrice[i] - self.OpenPosPrice[i])

            # 空头建仓时
            if self.Type[i] == -1:
                self.NetMargin[i] = (self.OpenPosPrice[i] - self.ClosePosPrice[i]) / self.Min_Move * self.Tick_Value * \
                                    self.LotSeries[i] - self.CostSeries[i]
                print "空", self.Min_Move, self.Tick_Value, self.LotSeries[i], self.NetMargin[i], (
                self.OpenPosPrice[i] - self.ClosePosPrice[i])
            # 收益率
            self.ReturnRate[i] = self.NetMargin[i][0] / \
                                 (self.OpenPosPrice[i] * self.Tick_Value * self.LotSeries[i] * self.Margin_Rate)[0]

        # 测试时间
        # start_date=Date[0]
        # end_date=Date[-1:]

        # 测试天数
        TotalTradeDays = self.DataLength

        # 累计净利
        self.CumNetMargin = self.NetMargin.cumsum()

        # 累计收益率
        self.CumReturnRate = self.ReturnRate.cumsum()

        # 回撤比例

        for i in range(self.DataLength):
            if i % 100 == 0:
                print i // 100
            c = max(self.DynamicEquity[0:i + 1])
            if c == self.DynamicEquity[i]:
                self.BackRatio[i] = 0
            else:
                self.BackRatio[i] = (self.DynamicEquity[i] - c) / c

        # 净利润
        self.ProfitTotal = self.NetMargin.sum()
        self.ProfitLong = (self.NetMargin[self.Type == 1]).sum()
        self.ProfitShort = (self.NetMargin[self.Type == -1]).sum()

        # 总盈利
        self.WinTotal = (self.NetMargin[self.NetMargin > 0]).sum()
        ans = self.NetMargin[self.Type == 1]
        self.WinLong = (ans[ans > 0]).sum()
        ans = self.NetMargin[self.Type == -1]
        self.WinShort = (ans[ans > 0]).sum()

        # 总亏损
        self.LossTotal = (self.NetMargin[self.NetMargin < 0]).sum()
        ans = self.NetMargin[self.Type == 1]
        self.LossLong = (ans[ans < 0]).sum()
        ans = self.NetMargin[self.Type == -1]
        self.LossShort = (ans[ans < 0]).sum()

        # 总盈利/总亏损
        self.WinTotalDLoseTotal = abs(self.WinTotal / float(self.LossTotal))
        self.WinLongDLoseLong = abs(self.WinLong / float(self.LossLong))
        self.WinShortDLoseShort = abs(self.WinShort / float(self.LossShort))

        # 交易手数
        self.LotsTotal = (len(self.Type[self.Type != 0]) * self.LotSeries).sum()
        self.LotsLong = (len(self.Type[self.Type == 1]) * self.LotSeries).sum()
        self.LotsShort = (len(self.Type[self.Type == -1]) * self.LotSeries).sum()

        # 盈利手数
        self.LotsWinTotal = len(self.NetMargin[self.NetMargin > 0]) * 1
        ans = self.NetMargin[self.Type == 1]
        self.LotsWinLong = len(ans[ans > 0]) * 1
        ans = self.NetMargin[self.Type == -1]
        self.LotsWinShort = len(ans[ans > 0]) * 1

        # 亏损手数
        self.LotsLoseTotal = len(self.NetMargin[self.NetMargin < 0]) * 1
        ans = self.NetMargin[self.Type == 1]
        self.LotsLoseLong = len(ans[ans < 0]) * 1
        ans = self.NetMargin[self.Type == -1]
        self.LotsLoseShort = len(ans[ans < 0]) * 1

        # 持平手数
        ans = self.NetMargin[self.Type == 1]
        self.LotsDrawLong = len(ans[ans == 0]) * 1
        ans = self.NetMargin[self.Type == -1]
        self.LotsDrawShort = len(ans[ans == 0]) * 1
        self.LotsDrawTotal = self.LotsDrawLong + self.LotsDrawShort

        # 盈利比率
        self.LotsWinTotalDLotsTotal = self.LotsWinTotal / float(self.LotsTotal)
        self.LotsWinLongDLotsLong = self.LotsWinLong / float(self.LotsLong)
        self.LotsWinShortDLotsShort = self.LotsWinShort / float(self.LotsShort)

        # 平均利润
        self.TotalAverageRet = self.ProfitTotal / float(self.LotsTotal)
        self.LongAverageRet = self.ProfitLong / float(self.LotsLong)
        self.ShortAverageRet = self.ProfitShort / float(self.LotsShort)

        # 平均盈利
        self.TotalAverageNetRet = self.WinTotal / float(self.LotsWinTotal)
        self.LongAverageNetRet = self.WinLong / float(self.LotsWinLong)
        self.ShortAverageNetRet = self.WinShort / float(self.LotsWinShort)

        # 平均亏损
        self.TotalAverageRetLoss = self.LossTotal / float(self.LotsLoseTotal)
        self.LongAverageRetLoss = self.LossLong / float(self.LotsLoseLong)
        self.ShortAverageRetLoss = self.LossShort / float(self.LotsLoseShort)

        # 平均盈利/平均亏损
        self.ToalRetVerseLoss = abs((self.WinTotal / float(self.LotsWinTotal)) / (self.LossTotal / float(self.LotsLoseTotal)))
        self.LongRetVerseLoss = abs((self.WinLong / float(self.LotsWinLong)) / (self.LossLong / float(self.LotsLoseLong)))
        self.ShortRetVerseLoss = abs((self.WinShort / float(self.LotsWinShort)) / (self.LossShort / float(self.LotsLoseShort)))

        # 最大盈利
        self.MaxWinTotal = max(self.NetMargin[self.NetMargin > 0])
        ans = self.NetMargin[self.Type == 1]
        self.MaxWinLong = max(ans[ans > 0])
        ans = self.NetMargin[self.Type == -1]
        self.MaxWinShort = max(ans[ans > 0])

        # 最大亏损
        self.MaxLoseTotal = min(self.NetMargin[self.NetMargin < 0])
        ans = self.NetMargin[self.Type == 1]
        self.MaxLoseLong = min(ans[ans < 0])
        ans = self.NetMargin[self.Type == -1]
        self.MaxLoseShort = min(ans[ans < 0])

        # 最大使用资金
        self.MaxMargin = max(max(self.LongMargin), max(self.ShortMargin))

        # 交易成本合计
        self.CostTotal = self.CostSeries.sum()

        # 总收益率
        if self.DynamicEquity[0]>0:
            self.TradingReturn = (self.DynamicEquity[-1] - self.DynamicEquity[0]) / float(self.DynamicEquity[0]) * 100

        # 持仓时间
        self.HoldingDays = round(self.DataLength * (len(self.pos[self.pos != 0]) / float(self.DataLength)))

        # 年化收益率(按240天算)
        if self.TradingReturn:
            self.RetOfYear = (1 + self.TradingReturn) ** (1 / (self.HoldingDays / 240.0)) * 100

        # 夏普比率
        self.Sharp = (np.sqrt(self.DataLength) * self.ReturnRate.mean()) / self.ReturnRate.std()

        # 最大回撤比例
        self.MaxDrawdownRate = abs(min(self.BackRatio)) * 100


