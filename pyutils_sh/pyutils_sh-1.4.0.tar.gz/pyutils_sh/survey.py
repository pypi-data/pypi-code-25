"""
Functions for aggregating and analyzing different types of survey data.
"""

import numpy as np
import pandas as pd


def ipaq_to_minutes(hours, mins):
    """
    Convert hours and minutes into minutes, following IPAQ data cleaning rules.

    Internal function used by :func:`survey.ipaq_long_aggregate`. Takes a
    hours and a minutes column (Pandas series) and calculates total time in
    minutes. Follows IPAQ data cleaning rules as outlined in the scoring
    guide, such as handling out-of-bound hour values (no conversion), and
    removing individuals that reported too large of a time value (> 24 hours).

    Parameters
    ----------
    hours : series
        Pandas series containing reported hours for all participants.
    mins : series
        Pandas series containing reported minutes for all participants.

    Returns
    -------
    converted : series
        Pandas series containing time spent in minutes.
    """

    # Scoring guide - 7.1.II
    # Mask hours that are NOT out of bounds
    mask = ~hours.isin([15, 30, 45, 60, 90])

    # Inbound hour values converted to minutes and added. Contains nans
    converted = (hours.where(mask) * 60 + mins)

    # Out of bound hours (nans) added directly to minutes without conversion
    converted = converted.fillna(hours + mins)

    # Nan participants that reported more minutes than there are in a day
    converted[converted >= 1440] = np.nan

    return converted.astype(float)


def ipaq_long_aggregate(q_map, domains=False):
    """
    Aggregate self-reported activity values into IPAQ summary data.

    Calculates MET/minutes and IPAQ category for each individual based on
    self-reported physical activity levels. The scoring follows the official
    IPAQ scoring guide as closely as possible.

    Section 7.4 (Truncation rules) of the scoring guide is extremely unclear
    about how to truncate time data for the long form IPAQ. The rule doesn't
    allow for the separation of weekly time or weekly METs. This rule has not
    been followed here.

    Additionally, the American College of Sports Medicine (ACSM) provides
    minimum recommended physical activity levels. In addition to the IPAQ
    categorical variable, an ACSM activity variable is also calculated, which
    indicates whether the individual met the minimum recommended levels.

    Parameters
    ----------
    q_map : dict
        Dictionary mapping question names to separate Pandas columns/series.
        This is used so internally the function uses a consistent name for
        each column of the survey (which may be named differently).

        The dictionary keys follow a strict naming scheme of `qXX` where `XX`
        is question number. Time variables need to be split, and hours and
        minutes must be stored under separate keys. The naming scheme
        for the time variables are `qXX_h` and `qXX_m`. The dictionary must
        also contain a column of subject numbers under the key `sub_num`. All
        questions must be included in the dictionary (41 IPAQ questions,
        plus 1 subject number).

        An example dictionary might look like this:

        >>> q_map = {'sub_num': data['subject_id'],
                     'q1': data['IPAQ_1'],
                     'q2': data['IPAQ_2'],
                     'q3_h': data['IPAQ_3_1'],
                     'q3_m': data['IPAQ_3_2'],
                     ...
                     'q27_h': data['IPAQ_27_1'],
                     'q27_m': data['IPAQ_27_2']}
    domains : bool, optional
        If True, MET minutes and time values will be included separately for
        each IPAQ activity domain.

    Returns
    -------
    aggregated : dataframe
        Pandas dataframe containing the calculated IPAQ summary data.
    """

    # Check that the map contains all 42 IPAQ long questions
    if len(q_map) != 42:
        raise Exception("IPAQ: Please map all 42 IPAQ (long form) questions "
                        "(41 IPAQ questions, and 1 subject number column). "
                        "Refer to documentation for mapping rules.")

    sub_num = q_map.pop('sub_num').reset_index(drop=True)
    q_map.pop('q1')  # Remove q1 as it'll cause problems with float conversion

    df = pd.DataFrame(q_map).fillna(0).astype(float).reset_index(drop=True)

    vehicle_time_items = ['q9']
    active_time_items = ['q3', 'q5', 'q7', 'q11', 'q13', 'q15', 'q17',
                         'q19', 'q21', 'q23', 'q25']
    sedentary_time_items = ['q26', 'q27']

    # Scoring guide - 7.1 Data cleaning
    for q in vehicle_time_items + active_time_items + sedentary_time_items:
        df[q] = ipaq_to_minutes(df[q + '_h'], df[q + '_m'])

    # Scoring guide - 7.2 Maximum values for excluding outliers. Remove later
    df['ipaq_outlier'] = df.filter(items=active_time_items).sum(axis=1)

    # Scoring guide - 7.3 Minimum values for duration of activity
    for q in vehicle_time_items + active_time_items:
        mask = df[q] < 10
        df[q][mask] = 0

        q_num = int(q[1:])
        df['q{}'.format(q_num-1)][mask] = 0  # Code associated day value as 0

    # Scoring guide - 6.2 MET values for continuous score

    # Work domain
    work_walk_time = df['q6'] * df['q7']
    work_walk_met = 3.3 * work_walk_time

    work_mod_time = df['q4'] * df['q5']
    work_mod_met = 4.0 * work_mod_time

    work_vig_time = df['q2'] * df['q3']
    work_vig_met = 8.0 * work_vig_time

    # Transportation domain
    transport_walk_time = df['q12'] * df['q13']
    transport_walk_met = 3.3 * transport_walk_time

    transport_cycle_time = df['q10'] * df['q11']
    transport_cycle_met = 6.0 * transport_cycle_time

    # Domestic domain
    domestic_vig_time = df['q14'] * df['q15']
    domestic_vig_met = 5.5 * domestic_vig_time

    domestic_mod_yard_time = df['q16'] * df['q17']
    domestic_mod_yard_met = 4.0 * domestic_mod_yard_time

    domestic_mod_inside_time = df['q18'] * df['q19']
    domestic_mod_inside_met = 3.0 * domestic_mod_inside_time

    # Leisure domain
    leisure_walk_time = df['q20'] * df['q21']
    leisure_walk_met = 3.3 * leisure_walk_time

    leisure_mod_time = df['q24'] * df['q25']
    leisure_mod_met = 4.0 * leisure_mod_time

    leisure_vig_time = df['q22'] * df['q23']
    leisure_vig_met = 8.0 * leisure_vig_time

    # Totals by intensity over 7 days
    total_walk_time = work_walk_time + transport_walk_time + leisure_walk_time
    total_walk_met = work_walk_met + transport_walk_met + leisure_walk_met

    total_mod_time = work_mod_time + domestic_mod_yard_time + \
        domestic_mod_inside_time + leisure_mod_time + transport_cycle_time + \
        domestic_vig_time
    total_mod_met = work_mod_met + domestic_mod_yard_met + \
        domestic_mod_inside_met + leisure_mod_met + transport_cycle_met + \
        domestic_vig_met

    total_vig_time = work_vig_time + leisure_vig_time
    total_vig_met = work_vig_met + leisure_vig_met

    # Total physical activity scores over 7 days
    total_pa_time = total_walk_time + total_mod_time + total_vig_time
    total_pa_met = total_walk_met + total_mod_met + total_vig_met

    # Scoring guide - 6.3 Categorical score
    walk_days = df['q6'] + df['q12'] + df['q20']
    mod_days = df['q4'] + df['q10'] + df['q14'] + df['q16'] + \
        df['q18'] + df['q24']
    vig_days = df['q2'] + df['q22']

    # Low category
    category = pd.Series(np.zeros(df.shape[0]))

    # Moderate category
    days = pd.concat([df['q2'], df['q22']], axis=1)
    times = pd.concat([df['q3'], df['q23']], axis=1)
    mask = (days * (times >= 20)).sum(1)
    category[mask.reset_index(drop=True) >= 3] = 1

    days = pd.concat([df['q6'], df['q12'], df['q20'], df['q4'], df['q10'],
                      df['q14'], df['q16'], df['q18'], df['q24']], axis=1)
    times = pd.concat([df['q7'], df['q13'], df['q21'], df['q5'], df['q11'],
                       df['q15'], df['q17'], df['q19'], df['q25']], axis=1)
    mask = (days * (times >= 30)).sum(1)
    category[mask.reset_index(drop=True) >= 5] = 1

    mask = ((walk_days + mod_days + vig_days) >= 5) & (total_pa_met >= 600)
    category[mask.reset_index(drop=True)] = 1

    # High category
    mask = (vig_days >= 3) & (total_vig_met >= 1500)
    category[mask.reset_index(drop=True)] = 2

    mask = ((walk_days + mod_days + vig_days) >= 7) & (total_pa_met >= 3000)
    category[mask.reset_index(drop=True)] = 2

    # Scoring guide - 6.4 Time value for sitting/sedentary behavior over 7 days
    total_sit_time = (df['q26'] * 5) + (df['q27'] * 2)

    # American College of Sports Medicine recommended level of activity
    acsm_category = pd.Series(np.zeros(df.shape[0]))

    mask = (mod_days >= 5) | (vig_days >= 3)
    acsm_category[mask.reset_index(drop=True)] = 1

    dict_totals = {'ipaq_total_walk_time': total_walk_time,
                   'ipaq_total_walk_MET': total_walk_met,
                   'ipaq_total_mod_time': total_mod_time,
                   'ipaq_total_mod_MET': total_mod_met,
                   'ipaq_total_vig_time': total_vig_time,
                   'ipaq_total_vig_MET': total_vig_met,
                   'ipaq_total_pa_time': total_pa_time,
                   'ipaq_total_pa_MET': total_pa_met,
                   'ipaq_total_sit_time': total_sit_time,
                   'ipaq_category': category,
                   'acsm_active': acsm_category}

    if domains:
        # Totals by domain over 7 days
        work_total_time = work_walk_time + work_mod_time + work_vig_time
        work_total_met = work_walk_met + work_mod_met + work_vig_met

        transport_total_time = transport_walk_time + transport_cycle_time
        transport_total_met = transport_walk_met + transport_cycle_met

        domestic_total_time = domestic_vig_time + domestic_mod_yard_time + \
            domestic_mod_inside_time
        domestic_total_met = domestic_vig_met + domestic_mod_yard_met + \
            domestic_mod_inside_met

        leisure_total_time = leisure_walk_time + leisure_mod_time + \
            leisure_vig_time
        leisure_total_met = leisure_walk_met + leisure_mod_met + \
            leisure_vig_met

        dict_domain = {'ipaq_work_total_time': work_total_time,
                       'ipaq_work_total_MET': work_total_met,
                       'ipaq_transport_total_time': transport_total_time,
                       'ipaq_transport_total_MET': transport_total_met,
                       'ipaq_domestic_total_time': domestic_total_time,
                       'ipaq_domestic_total_MET': domestic_total_met,
                       'ipaq_leisure_total_time': leisure_total_time,
                       'ipaq_leisure_total_MET': leisure_total_met}

        aggregated = pd.DataFrame({**dict_domain, **dict_totals})
    else:
        aggregated = pd.DataFrame(dict_totals)

    # Scoring guide - 7.2 Calculated earlier, remove them here
    aggregated['ipaq_outlier'] = df['ipaq_outlier']
    aggregated[aggregated['ipaq_outlier'] > 960] = np.nan
    aggregated['ipaq_outlier'][~aggregated['ipaq_outlier'].isna()] = 0
    aggregated['ipaq_outlier'][aggregated['ipaq_outlier'].isna()] = 1

    aggregated['sub_num'] = sub_num.astype(int)

    return aggregated
