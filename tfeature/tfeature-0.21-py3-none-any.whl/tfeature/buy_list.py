def third_buy(current_df, lower_df):
    if len(current_df) and len(lower_df):
        current = hist_sum(current_df)
        lower = hist_sum(lower_df)
        if (len(current) >= 6) and (len(lower) >= 3):
            if current.iloc[-1]['parting'] < 0:
                center = inter(current.iloc[-5:-1])
                return center and (
                    current.iloc[-2]['highpoint'] >
                    current.iloc[-6]['highpoint']) and (
                        0 < (current_df.iloc[-1]['close'] /
                             current.iloc[-1]['lowpoint'] - 1) <
                        0.05) and (lower.iloc[-1]['parting'] < 0) and (
                            lower.iloc[-3:]['low'].min() >
                            max(center)) and (lower.iloc[-1]['hist_sum'] >
                                              lower.iloc[-3]['hist_sum'])
            else:
                center = inter(current.iloc[-4:])
                return center and (
                    current.iloc[-1]['highpoint'] >
                    current.iloc[-5]['highpoint']
                ) and (lower.iloc[-1]['parting'] < 0) and (
                    lower.iloc[-3:]['low'].min() > max(center)
                ) and (lower.iloc[-1]['hist_sum'] > lower.iloc[-3]['hist_sum'])


def buy_list(codes,
             current_freq='D',
             low_freq='30min',
             startc='2017-01-01',
             startl='2017-11-01',
             end='2018-12-31'):
    tbl = []
    for code in codes:
        current = ts.bar(code, start_date=startc, freq=current_freq)
        lower = ts.bar(code, start_date=startc, freq=low_freq)
        try:
            if third_buy(current, lower):
                print(code)
                tbl.append(code)
        except:
            print('error on {}'.format(code))
    return tbl



def min_max_scale(df):
    df = df.copy()
    scaler = preprocessing.MinMaxScaler(feature_range=(10, 30))
    values = df.values.reshape(-1, 1)
    df.loc[:, :] = scaler.fit_transform(values).reshape(-1, 4)
    return df


def standard_scale(df):
    df = df.copy()
    scaler = preprocessing.StandardScaler()
    values = df.values.reshape(-1, 1)
    df.loc[:, :] = scaler.fit_transform(values).reshape(-1, 4) + 4
    return df