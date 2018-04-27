# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 14:53:23 2015

@author: rbanderson
"""
import pandas as pd
import libpysat.transform.remove_baseline as remove_baseline
import libpysat.transform.interp as interp
import libpysat.transform.mask as mask
import libpysat.transform.multiply_vector as multiply_vector
import libpysat.transform.peak_area as peak_area
import libpysat.utils.folds as folds
import libpysat.transform.norm as norm
import libpysat.transform.deriv as deriv
import libpysat.transform.dim_red as dim_red
import libpysat.clustering.cluster as cluster
import libpysat.utils.outlier_removal as outlier_removal

class spectral_data(object):
    def __init__(self, df):

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
        #this is a temporary fix to keep track of dimensionality reduction loadings for plotting purposes.
                                    #TODO: Make this robust to other transforms being applied to the data. Currently, many transforms will strip this off when they re-define the spectral data object


    def cal_tran(self):
        pass #Not yet implemented

    def cluster(self, col, method, params, kws):
        self.df = cluster.cluster(self.df, col = col, method = method, params = params, kws = kws)

    def deriv(self):
        self.df = deriv.deriv(self.df)

    def dim_red(self, col, method, params, kws, load_fit):
        self.df, self.dim_red = dim_red.dim_red(self.df, col = col, method = method, params = params, kws = kws, load_fit = load_fit)

    def interp(self, xnew):
        self.df = interp.interp(self.df, xnew)

    def mask(self, maskfile, maskvar):
        self.df = mask.mask(self.df,maskfile,maskvar=maskvar)

    def multiply_vector(self, vectorfile):
        self.df = multiply_vector.multiply_vector(self.df,vectorfile=vectorfile)

    def norm(self, ranges, col_var):
        self.df = norm.norm(self.df,ranges, col_var=col_var)

    def outlier_removal(self, col, method, params):
        self.df, self.outlier_removal = outlier_removal.outlier_removal(self.df, col = col, method = method, params = params)

    def peak_area(self, peaks_mins_file):
        self.df, self.peaks, self.mins = peak_area.peak_area(self.df,peaks_mins_file = peaks_mins_file)

    def random_folds(self, nfolds):
        self.df = folds.random(self.df,nfolds)

    def remove_baseline(self, method, segment, params):
        self.df = remove_baseline.remove_baseline(self.df, method = method, segment = segment, params = params)

    def stratified_folds(self):
        self.df, self.df_baseline = folds.stratified_folds(self.df, nfolds = 5, sortby = None)





