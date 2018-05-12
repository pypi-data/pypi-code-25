# -*- coding: utf-8 -*-

"""Main module."""

import pandas as pd


def missing_data_stats(df):
    """Check remaining missing value and print out if any.

    Arguments:
        df (pd.DataFrame): The dataframe need to check

    Returns:
        The missing dataframe

    Usage:
        from src.utils.utils import missing_data_stats
    """
    nan_df = (df.isnull().sum() / len(df)) * 100
    nan_df = nan_df.drop(nan_df[nan_df == 0].index).sort_values(ascending=False)
    missing_data = pd.DataFrame({'Missing Ratio': nan_df})

    return missing_data
