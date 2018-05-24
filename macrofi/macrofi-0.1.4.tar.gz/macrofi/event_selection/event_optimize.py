import numpy as np
from macrofi.event_selection import excess_sp
from macrofi.event_selection import *

NEGATIVE = -1
POSITIVE = 1


def optimize(events_config, data, base, opt_func, direction=1, shift=1):
    best_value = {}
    for evt in events_config:
        best_value[evt] = opt_func(evt, events_config[evt],
                                   data=data,
                                   base=base,
                                   direction=direction,
                                   shift=shift)
    return best_value


def product(args_list):
    """生成多参数的样本集"""
    result = [[]]
    for pool in args_list:
        result = [x + [y] for x in result for y in pool]
    # for prod in result:
    #     yield tuple(prod)
    return result


def sp_bool_optimize(event_name, config, data, base, direction=POSITIVE, shift=2, **args):
    """将信号看成bool事件进行优化，正值做多，负值做空，进行最大夏普比率优化
    :param event_name: 因子事件名称，必须在event包内
    :param config: 参数配置 [[min, max, step],[...],[...]]
    :param data: pandas.Series
    :param direction: 方向
    """
    et = eval(event_name)
    args_list = []
    for i in range(len(config)):  # 遍历各个参数
        args_list.append(np.arange(config[i][0], config[i][1], config[i][2]))  # arg_list个数和参数个数一致
    sample_list = product(args_list)  # 产生所有的样本参数组迭代器
    excess_sp_max = -100
    best_fit = []
    count = 0
    for sample in sample_list:
        count += 1
        # for debug
        # print(count)
        # if count == 14800:
        #     print(count)
        # print(count)
        # 计算多空信号
        if len(sample) == 3:
            event_list = et(data, sample[0], sample[1], sample[2])
        elif len(sample) == 2:
            event_list = et(data, sample[0], sample[1])
        elif len(sample) == 1:
            event_list = et(data, sample[0])
        event_list = event_list.shift(shift).dropna()  # 信号时间迁移，形成实际有效的信号时间
        # 计算持仓信号
        if direction == NEGATIVE:
            _pos = event_list.apply(lambda x: 0 if x > 0 else 1)
        else:  # POSTIVE
            _pos = event_list.apply(lambda x: 1 if x > 0 else 0)
        # 计算回测夏普比率
        base = base[(base.index >= event_list.index[0]) & (base.index <= event_list.index[-1])]  # 基准时间和信号重叠
        # 将仓位信号转为日度
        pos = pd.Series(_pos, index=base.index).ffill()
        # 和当前最大夏普比率比较，如果更好，则替换
        bt = Backtest(pos, base)
        pct = bt.pct
        base_pct = bt.base_pct
        ex_sp = excess_sp(pct, base_pct)
        if ex_sp > excess_sp_max:
            excess_sp_max = ex_sp
            best_fit = sample
            print("{event} {count} iteration: current best value is {sp_max} and best fit is {config}"
                  .format(event=event_name, count=count, sp_max=excess_sp_max, config=str(sample)))
    return [excess_sp_max, best_fit]


def bool_excess_sp():
    pass


def sp_five_optimize(event_name, config, data, base, direction=POSITIVE, shift=2):
    """将资产五等分，从5分打到1分，看多程度依次递减，5分最为乐观，1分最为悲观
    1分：0
    2分：25%
    3分：50%（中性）
    4分：75%
    5分：100%
    """
    pass


def sp_neg_optimize(event_name, config):
    """将信号看成"""


def risk_bool_optimize(event_name, config):
    """将信号看成bool事件，进行风险最小化优化，即触发风险事件之后，资产价格回撤的IR值最大化"""
    pass


def target(event_name, series):
    pass


def case1():
    from datetime import datetime
    from pyfi import WindHelper
    begin_date = datetime(2009, 1, 1)
    end_date = datetime(2018, 4, 1)
    factor = WindHelper.edb(codes="玻璃综合指数", begin_date=begin_date, end_date=end_date).iloc[:, 0]

    base = WindHelper.wsd(code="gz10yind",
                          begin_date=begin_date,
                          end_date=end_date,
                          paras=["close"]).iloc[:, 0]
    event_name = "mg"
    config = [[1, 5, 1], [10, 100, 1], [-5, 5, 0.1]]
    sp_bool_optimize(event_name, config, data=factor, base=base, direction=NEGATIVE)


def case2():
    from pyfi import WindHelper
    from datetime import datetime
    begin_date = datetime(2007, 1, 1)
    end_date = datetime(2018, 1, 1)
    data = WindHelper.edb(codes="cpi", begin_date=begin_date, end_date=end_date).iloc[:, 0]
    base = WindHelper.wsd(code="CBA01551.CS", begin_date=begin_date, end_date=end_date,
                          paras=["close"]).iloc[:, 0]  # 1结尾为财富值， 2结尾为净价
    # base = base.resample("M").last()
    mg_config = [[1, 5, 1], [3, 40, 1], [-5, 5, 0.1]]
    cmo_config = [[10, 40, 1]]
    threshold_config = [[-10, 10, 0.1]]
    events = {
        # "mg": mg_config,
        "cmo": cmo_config,
        "threshold": threshold_config
    }
    results = optimize(events, data, base, opt_func=sp_bool_optimize, direction=-1, shift=1)
    print(results)


def case3():
    from pyfi import WindHelper
    from datetime import datetime
    begin_date = datetime(2007, 1, 1)
    end_date = datetime(2018, 1, 1)
    # data = WindHelper.edb(codes="水泥价格指数",begin_date=begin_date, end_date=end_date).iloc[:,0]
    data = WindHelper.wsd(code="000300.SH", begin_date=begin_date, end_date=end_date, paras=["close"]).iloc[:, 0]
    base = WindHelper.wsd(code="CBA01552.CS", begin_date=begin_date, end_date=end_date, paras=["close"]).iloc[:,
           0]  # 1结尾为财富值， 2结尾为净价
    mg_config = [[1, 5, 1], [5, 40, 1], [-5, 5, 0.1]]
    cmo_config = [[5, 36, 1]]
    threshold_config = [[-10, 10, 0.1]]
    events = {
        "mg": mg_config,
        #     "cmo":cmo_config,
        #     "threshold":threshold_config
    }
    optimize(events, data, base, opt_func=sp_bool_optimize, direction=1,
             shift=2)  # 月度数据shift为1，日度数据shift为2，只看有效性，shift再相继减1


def case4():
    from pyfi import WindHelper
    from datetime import datetime
    from pyfi import macro_adjust
    begin_date = datetime(2007, 1, 1)
    end_date = datetime(2018, 5, 1)
    # data = WindHelper.edb(codes="水泥价格指数",begin_date=begin_date, end_date=end_date).iloc[:,0]
    ip = WindHelper.edb(codes=["ip_yoy", "ip_cyoy"],
                        begin_date=begin_date,
                        end_date=end_date, adjust=True)
    base = WindHelper.wsd(code="CBA01552.CS", begin_date=begin_date, end_date=end_date, paras=["close"]).iloc[:,
           0]  # 1结尾为财富值， 2结尾为净价
    # base = base.resample("M").last().iloc[:,0]
    ip = macro_adjust(ip.ip_yoy, ip.ip_cyoy)
    data = ip
    mg_config = [[1, 5, 1], [5, 36, 1], [-5, 5, 0.1]]
    cmo_config = [[5, 36, 1]]
    threshold_config = [[-10, 10, 0.1]]
    events = {
        "mg": mg_config,
        #     "cmo":cmo_config,
        #     "threshold":threshold_config
    }
    optimize(events, data, base, opt_func=sp_bool_optimize, direction=-1, shift=1)


if __name__ == "__main__":
    case4()
