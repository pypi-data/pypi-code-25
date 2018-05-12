"""
Created on Wed Feb 14 19:21:30 2018

@author: wes
"""
import pandas
import statsmodels.api as sm


def get_opr_matrices(df, teams=None, score_col='score'):
    red_score = 'red_' + score_col
    blue_score = 'blue_' + score_col
    df = df[['key', red_score, blue_score, 'red1', 'red2', 'red3', 'blue1', 'blue2', 'blue3']]
    melted = pandas.melt(df, ['key', red_score, blue_score]).sort_values('value')
    if teams is None:
        teams = melted.value.unique()
    scores = pandas.melt(df[['key', red_score, blue_score]], ['key']).sort_values('key')
    scores.index = scores.key + '_' + scores.variable
    oprmat = pandas.DataFrame(0, index=scores.key + '_' + scores.variable, columns=teams)

    for (i, record) in melted.iterrows():
        if record.variable.startswith('blue'): oprmat.loc[record.key + '_' + blue_score, record.value] = 1
        if record.variable.startswith('red'): oprmat.loc[record.key + '_' + red_score, record.value] = 1

    return oprmat, teams, scores


def get_epr_matrices(df, teams=None, score_col='score'):
    red_score = 'red_' + score_col
    blue_score = 'blue_' + score_col
    margin = 'margin_' + score_col
    df = df[['key', red_score, blue_score, 'red1', 'red2', 'red3', 'blue1', 'blue2', 'blue3']]
    df[margin] = df[red_score] - df[blue_score]
    melted = pandas.melt(df, ['key', red_score, blue_score, margin]).sort_values('value')

    if teams is None:
        teams = melted.value.unique()
    scores = pandas.melt(df[['key', red_score, blue_score, margin]], ['key']).sort_values('key')
    scores.index = scores.key + '_' + scores.variable
    oprmat = pandas.DataFrame(0, index=scores.key + '_' + scores.variable, columns=teams)

    for (i, record) in melted.iterrows():
        isblue = record.variable.startswith('blue')
        if isblue: oprmat.loc[record.key + '_' + blue_score, record.value] = 1
        else: oprmat.loc[record.key + '_' + red_score, record.value] = 1
        oprmat.loc[record.key + '_' + margin, record.value] = -1 if isblue else 1

    return oprmat, teams, scores


def get_opr_model(df, fit=True, score_col='score'):
    df = df[df.comp_level == 'qm']
    oprmat, teams, scores = get_opr_matrices(df, score_col=score_col)
    reg = sm.OLS(scores.value, oprmat)

    if fit:
        return reg.fit()
    else:
        return reg


def get_epr_model(df, fit=True, score_col='score'):
    df = df[df.comp_level == 'qm']
    eprmat, teams, scores = get_epr_matrices(df, score_col=score_col)
    reg = sm.OLS(scores.value, eprmat)

    if fit:
        return reg.fit()
    else:
        return reg


def epr_make_predictions(red, blue, teamspace, model):
    table = dict.fromkeys(teamspace, 0)
    for r, b in zip(red, blue):
        table[r] = 1
        table[b] = -1
    x = pandas.DataFrame(pandas.Series(table))
    return model.predict(x)
