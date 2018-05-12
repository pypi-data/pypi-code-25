from numpy import arctanh, tanh
import pandas
import statsmodels.api as sm


def scoring(series):
    def setf(alliance, segment, field, value):
        series['_'.join([alliance, segment, field])] = value

    for alliance in ['red', 'blue']:
        breakdown = series['score_breakdown'][alliance]

        setf(alliance, 'total', 'adjustment', breakdown['adjustPoints'])
        setf(alliance, 'total', 'foul', breakdown['foulPoints'])
        setf(alliance, 'total', 'foul_count', breakdown['foulCount'])
        setf(alliance, 'total', 'tech_foul_count', breakdown['techFoulCount'])
        setf(alliance, 'total', 'rp', breakdown['rp'])
        setf(alliance, 'total', 'game_data', breakdown['tba_gameData'])
        setf(alliance, 'total', 'official', breakdown['totalPoints'])
        setf(alliance, 'total', 'points', breakdown['totalPoints'] - (
            breakdown['foulPoints'] + breakdown['adjustPoints']))

        setf(alliance, 'auto', 'scale_sec', breakdown['autoScaleOwnershipSec'])
        setf(alliance, 'auto', 'switch_sec', breakdown['autoSwitchOwnershipSec'])
        setf(alliance, 'auto', 'switch_at_zero', breakdown['autoSwitchAtZero'])
        setf(alliance, 'auto', 'robot1', breakdown['autoRobot1'])
        setf(alliance, 'auto', 'robot2', breakdown['autoRobot2'])
        setf(alliance, 'auto', 'robot3', breakdown['autoRobot3'])
        setf(alliance, 'auto', 'ownership', breakdown['autoOwnershipPoints'])
        setf(alliance, 'auto', 'run', breakdown['autoRunPoints'])
        setf(alliance, 'auto', 'rp', breakdown['autoQuestRankingPoint'])
        setf(alliance, 'auto', 'points', breakdown['autoPoints'])

        setf(alliance, 'vault', 'boost_played', breakdown['vaultBoostPlayed'])
        setf(alliance, 'vault', 'boost_total', breakdown['vaultBoostTotal'])
        setf(alliance, 'vault', 'force_played', breakdown['vaultForcePlayed'])
        setf(alliance, 'vault', 'force_total', breakdown['vaultForceTotal'])
        setf(alliance, 'vault', 'levitate_played', breakdown['vaultLevitatePlayed'])
        setf(alliance, 'vault', 'levitate_total', breakdown['vaultLevitateTotal'])
        setf(alliance, 'vault', 'cubes', breakdown['vaultPoints'] / 5)
        setf(alliance, 'vault', 'points', breakdown['vaultPoints'])

        setf(alliance, 'ownership', 'scale_sec', breakdown['teleopScaleOwnershipSec'])
        setf(alliance, 'ownership', 'scale_boost', breakdown['teleopScaleBoostSec'])
        setf(alliance, 'ownership', 'scale_force', breakdown['teleopScaleForceSec'])
        setf(alliance, 'ownership', 'switch_sec', breakdown['teleopSwitchOwnershipSec'])
        setf(alliance, 'ownership', 'switch_boost', breakdown['teleopSwitchBoostSec'])
        setf(alliance, 'ownership', 'switch_force', breakdown['teleopSwitchForceSec'])
        setf(alliance, 'ownership', 'points', breakdown['teleopOwnershipPoints'])

        climb_pts = 0
        true_climb_pts = 0
        park_pts = 0
        for robot in ['1', '2', '3']:
            endgame = breakdown['endgameRobot' + robot]
            if endgame == 'Climbing':
                true_climb_pts += 30
                climb_pts += 30
            elif endgame == 'Levitate':
                climb_pts += 30
            elif endgame == 'Parking':
                park_pts += 5
        setf(alliance, 'endgame', 'robot1', breakdown['endgameRobot1'])
        setf(alliance, 'endgame', 'robot2', breakdown['endgameRobot2'])
        setf(alliance, 'endgame', 'robot3', breakdown['endgameRobot3'])
        setf(alliance, 'endgame', 'true_climb', true_climb_pts)
        setf(alliance, 'endgame', 'climb', climb_pts)
        setf(alliance, 'endgame', 'park', park_pts)
        setf(alliance, 'endgame', 'rp', breakdown['faceTheBossRankingPoint'])
        setf(alliance, 'endgame', 'points', breakdown['endgamePoints'])

    return series


def psr_transform(x):
    return 2 * arctanh(((x + 2) / 138) - 1)


def psr_untransform(x):
    return (tanh(x / 2) + 1) * 138 / 3


def get_psr_matrices(df, score_col='score'):
    red_score = 'red_' + score_col
    blue_score = 'blue_' + score_col
    df = df[['key', red_score, blue_score, 'red1', 'red2', 'red3', 'blue1', 'blue2', 'blue3']]
    melted = pandas.melt(df, ['key', red_score, blue_score]).sort_values('value')
    teams = melted.value.unique()
    scores = pandas.melt(df[['key', red_score, blue_score]], ['key']).sort_values('key')
    scores.index = scores.key + '_' + scores.variable
    oprmat = pandas.DataFrame(0, index=scores.key + '_' + scores.variable, columns=teams)

    for (i, record) in melted.iterrows():
        if record.variable.startswith('blue'):
            oprmat.loc[record.key + '_' + blue_score, record.value] = 1
            oprmat.loc[record.key + '_' + red_score, record.value] = -1
        if record.variable.startswith('red'):
            oprmat.loc[record.key + '_' + blue_score, record.value] = -1
            oprmat.loc[record.key + '_' + red_score, record.value] = 1

    return oprmat, teams, scores


def get_psr_model(df, fit=True):
    df = df[df.comp_level == 'qm']
    df['red_ownership_norm'] = 2 * arctanh(((df.red_ownership_scale_sec + df.red_ownership_switch_sec + 2) / 139) - 1)
    df['blue_ownership_norm'] = 2 * arctanh(((df.blue_ownership_scale_sec + df.blue_ownership_switch_sec + 2) / 139) - 1)
    #df['red_ownership_norm'] = psr_transform(df.red_ownership_switch_sec + df.red_ownership_scale_sec)
    #df['blue_ownership_norm'] = psr_transform(df.blue_ownership_switch_sec + df.blue_ownership_scale_sec)
    oprmat, teams, scores = get_psr_matrices(df, score_col='ownership_norm')
    reg = sm.OLS(scores.value, oprmat)

    if fit:
        return reg.fit()
    else:
        return reg
