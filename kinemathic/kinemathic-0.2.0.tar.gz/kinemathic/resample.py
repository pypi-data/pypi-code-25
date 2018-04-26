import pandas as pd


def between_rows(df, n = 10, skip_objects=True):
    """ between_rows.

    Create new rows between existing rows.

    :param df: pandas dataframe
    :param n:  number of rows to insert
    :param skip_objects: Bool, if True, columns of type object will be skipped.
    :return: transformed dataframe
    """
    transitions = n
    new_df = []
    new_cols = []
    for col in df.columns:
        col_data = []
        if df.dtypes[col] in ('int64', 'float64'):
            start = df[col].values[0]
            end = df[col].values[1]
            diff = end - start
            increment = diff / transitions
            col_data.append(start)
            for i in range(transitions):
                val = start + increment * i
                col_data.append(val)
            col_data.append(end)
            new_df.append(col_data)
            new_cols.append(col)
        elif skip_objects:
            pass
        else:
            val = df[col].values[0]
            col_data.append(val)
            for i in range(transitions):
                between='{}-{:2}'.format(val,i)
                col_data.append(between)
            val = df[col].values[1]
            col_data.append(val)
            new_df.append(col_data)
            new_cols.append(col)
    dft = pd.DataFrame(new_df)
    new_cols_dict = {i: col for i,col in enumerate(new_cols)}
    return dft.T.rename(columns=new_cols_dict)


def num_only(df):
    """ num_only.

    Remove non numerical columns from a dataframe

    :param df: pandas dataframe
    :return: transformed dataframe
    """
    for col in df.columns:
        if df.dtypes[col] in ('int64', 'float64'):
            pass
        else:
            print("dropping", col)
            df.drop(col, axis=1, inplace=True)
    return df
