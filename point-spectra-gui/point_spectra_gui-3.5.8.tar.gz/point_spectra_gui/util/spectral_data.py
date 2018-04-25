# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 14:53:23 2015

@author: rbanderson
"""
import pandas as pd

class spectral_data(object):
    def __init__(self, df, dim_red = None):

        try:
            uppercols = df.columns.levels[0]
            lowercols = list(df.columns.levels[1].values)
        except:
            df.columns = pd.MultiIndex.from_tuples(list(df.columns))
            uppercols = df.columns.levels[0]
            lowercols = list(df.columns.levels[1].values)

        for i, val in enumerate(lowercols):
            try:
                lowercols[i] = float(val)
            except:
                lowercols[i] = val

        levels = [uppercols, lowercols]
        df.columns.set_levels(levels, inplace=True)
        self.df = df
        if dim_red is not None:
            self.dim_red = dim_red  #this is a temporary fix to keep track of dimensionality reduction loadings for plotting purposes.
                                    #TODO: Make this robust to other transforms being applied to the data. Currently, many transforms will strip this off when they re-define the spectral data object



