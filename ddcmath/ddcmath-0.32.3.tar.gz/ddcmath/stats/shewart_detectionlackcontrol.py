# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 15:15:18 2016

@author: Bachand-Tremblay
"""

import pandas as pd
import math 
from bokeh.plotting import figure, output_file, show
from bokeh.models import HoverTool, BoxSelectTool
from tables import c2 as findC2

def detect_lack_of_control(serie, target_mean, target_std):
    """
    Based on Shewart lack of control algorithm
    """
    # Will have to find c2 vs Table 29
    n = len(serie)
    c2 = findC2(n)
    if not isinstance(serie, pd.Series):
        try:
            serie = pd.Series(serie)
        except:
            raise ValueError("Provide a Pandas Series")
    
    # Finding control limit of mean
    avg_variability = (3 * (target_std / math.sqrt(2*n)))
    avg_hl = target_mean + avg_variability
    avg_ll = target_mean - avg_variability
    
    # Finding control limit of standard deviation
    std_dev_variability = (3 * (target_std / math.sqrt(2*n)))
    std_dev_hl = (c2*target_std) + std_dev_variability
    std_dev_ll = (c2*target_std) - std_dev_variability

    avg_result = {'mean': serie.mean(),
                  'hl': avg_hl,
                  'll': avg_ll} 
       
    std_result = {'std': serie.std(),
                  'hl': std_dev_hl,
                  'll': std_dev_ll}    

    index = ['low limit', 'value', 'high limit']
    avg = [avg_result['ll'], avg_result['mean'], avg_result['hl']]
    std = [std_result['ll'], std_result['std'], std_result['hl']]
    
    df = pd.DataFrame()
    df['average'] = avg
    df['standard dev'] = std
    df['index'] = index
    df = df.set_index('index')
    return (serie, df)


def draw_chart(serie, df):    
    #TOOLS = [HoverTool(),]
    #p = figure(plot_width=400, plot_height=400, tools=TOOLS)
    p = figure(plot_width=400, plot_height=400)
    
    r = p.circle(df['average'],df['standard dev'], size=20, name='glyph')
    p.title.text = 'Statistical control limits'
    p.xaxis.axis_label = "Average"
    p.yaxis.axis_label = "Standard dev"

    if serie.std() > df['standard dev']['high limit'] or \
                serie.mean() > df['average']['high limit']:
        r.glyph.fill_color="red"
    elif serie.std() < df['standard dev']['low limit'] or \
                  serie.mean() < df['average']['low limit']:
        r.glyph.fill_color="navy"
    else:
        r.glyph.fill_color="green" 
    if serie.mean() > df['average']['high limit'] or serie.mean() < df['average']['low limit']:
        p.xaxis.axis_line_width = 3
        p.xaxis.axis_line_color = "red"
    elif serie.std() > df['standard dev']['high limit'] or serie.std() < df['standard dev']['low limit']:
        p.yaxis.axis_line_width = 3
        p.yaxis.axis_line_color = "red"
    return(p)
    
if __name__ == '__main__':
    COMPANY1 = [12600, 13750, 13440, 13960, 13570, 13550, 13570, 13430, 13250, 13320, 
                    13800,14250, 13370, 13510, 13110, 13400, 13860, 13440, 13900, 13910]
                    
    COMPANY2 = [14300, 13900, 14460, 14480, 14170, 13610, 13990, 14140, 13400, 14290, 
                14550, 14250, 13390, 14130, 13910, 13180, 13790, 13810, 13260, 14550]
    
    TABLE_42 = {'Company_1' : COMPANY1,
                'Company_2' : COMPANY2}
    
    X_bar = 13540
    STD_DEV = 440
    output_file('result.html')
    serie, df = detect_lack_of_control(COMPANY1, X_bar, STD_DEV)
    show(draw_chart(serie, df))
    #show(detect_lack_of_control(COMPANY2, X_bar, STD_DEV))
