# -*- coding: utf-8 -*-

import pandas as pd
from pyecharts.chart import Chart


class Map_Bin_Scatter(Chart):
    """
    <<< 散点图的变种 >>>
    背景是地图，被分为许多个小方格，根据指定指标决定方格颜色深浅，类似于热力图；
    前景是散点图
    """

    def __init__(self, title="", subtitle="", **kwargs):
        """

        notes:
            1. 考虑增加参数`theme`，指定使用某套预设的主题，如背景色、数据组颜色等

        :param title:
        :param subtitle:
        :param kwargs:
        """

        super(Map_Bin_Scatter, self).__init__(title, subtitle, **kwargs)

        # 用于存放一些自定义的设置
        self.my_option = {}

    def add_heatmap(self, df):
        pass