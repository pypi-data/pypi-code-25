import pandas as pd


def ccode_df(ccode_dict):
    df = pd.DataFrame(columns=['c_code', 'code'])
    for k, v in ccode_dict.items():
        df = df.append(pd.DataFrame({'c_code': k, 'code': v}))
    return df


def concepts_df(ccode_df, cname_df):
    return ccode_df.merge(cname_df, on='c_code')


def clean_code_suffix(concepts_df):
    codes = [c[:6] for c in concepts_df.code]
    concepts_df.loc[:, 'code'] = codes
