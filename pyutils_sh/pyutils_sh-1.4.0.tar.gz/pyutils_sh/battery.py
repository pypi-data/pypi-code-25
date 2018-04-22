"""
Functions for aggregating subject data from 
Cognitive Battery (https://github.com/sho-87/cognitive-battery)
"""

import os
import pandas as pd


def aggregate_wide(dir_battery, dir_output, response_type="full",
                   use_file=False, save=True):
    """
    Aggregate data from all battery tasks.

    Takes a directory containing individual subject data files created from 
    the Cognitive Battery, and calculates summary statistics for all 
    subjects across all tasks. A single output summary file is created 
    containing the aggregated battery data.

    Parameters
    ----------
    dir_battery : str
        Path to the directory containing subject data files created by the 
        Cognitive Battery.
    dir_output : str
        Path to the directory where the output summary file will be saved. A 
        filed named 'battery_data.csv' will be created in this directory.
    response_type : {'full', 'correct', 'incorrect'}, optional
        Should the summary data be calculated using all trials? Only correct 
        trials? Or only incorrect trials? This is not supported in all tasks.
    use_file : bool, optional
        If True, aggregated battery data will be imported from the existing
        summary file instead of being re-aggregated.
    save : bool, optional
        Set to True to save an output summary file to the output directory. 
        If False, then no file will be saved, but a dataframe will still be 
        returned from this function.

    Returns
    -------
    all_data : dataframe
        Pandas dataframe containing the aggregated summary data for all tasks.
    """

    if use_file:
        if os.path.isfile(os.path.join(dir_output,
                                       "battery_data_{}.csv".format(response_type))):
            print("Importing battery summary file...")
            return pd.read_csv(os.path.join(dir_output,
                                            "battery_data_{}.csv".format(response_type)))

    # Create dataframes
    df_info = pd.DataFrame(columns=["sub_num", "datetime",
                                    "condition", "age", "sex", "RA"])
    
    df_ant = pd.DataFrame(columns=["sub_num",
        "ant_follow_error_rt", "ant_follow_correct_rt",
        "ant_neutral_rt", "ant_congruent_rt", "ant_incongruent_rt",
        "ant_neutral_rtsd", "ant_congruent_rtsd", "ant_incongruent_rtsd",
        "ant_neutral_rtcov", "ant_congruent_rtcov", "ant_incongruent_rtcov",
        "ant_neutral_correct", "ant_congruent_correct", "ant_incongruent_correct",
        "ant_nocue_rt", "ant_center_rt", "ant_spatial_rt", "ant_double_rt",
        "ant_nocue_rtsd", "ant_center_rtsd", "ant_spatial_rtsd", "ant_double_rtsd",
        "ant_nocue_rtcov", "ant_center_rtcov", "ant_spatial_rtcov", "ant_double_rtcov",
        "ant_nocue_correct", "ant_center_correct", "ant_spatial_correct", "ant_double_correct",
        "ant_conflict_intercept", "ant_conflict_slope", "ant_conflict_slope_norm",
        "ant_alerting_intercept", "ant_alerting_slope", "ant_alerting_slope_norm",
        "ant_orienting_intercept", "ant_orienting_slope", "ant_orienting_slope_norm"])
    
    df_flanker_compat = pd.DataFrame(columns=["sub_num",
                "flanker_compat_follow_error_rt", "flanker_compat_follow_correct_rt",
                "flanker_compat_congruent_rt", "flanker_compat_incongruent_rt",
                "flanker_compat_congruent_rtsd", "flanker_compat_incongruent_rtsd",
                "flanker_compat_congruent_rtcov", "flanker_compat_incongruent_rtcov",
                "flanker_compat_congruent_correct", "flanker_compat_incongruent_correct",
                "flanker_compat_conflict_intercept", "flanker_compat_conflict_slope",
                "flanker_compat_conflict_slope_norm"])
    
    df_flanker_incompat = pd.DataFrame(columns=["sub_num",
                "flanker_incompat_follow_error_rt", "flanker_incompat_follow_correct_rt",
                "flanker_incompat_congruent_rt", "flanker_incompat_incongruent_rt",
                "flanker_incompat_congruent_rtsd", "flanker_incompat_incongruent_rtsd",
                "flanker_incompat_congruent_rtcov", "flanker_incompat_incongruent_rtcov",
                "flanker_incompat_congruent_correct", "flanker_incompat_incongruent_correct",
                "flanker_incompat_conflict_intercept", "flanker_incompat_conflict_slope",
                "flanker_incompat_conflict_slope_norm"])
    
    df_flanker_both = df_flanker_compat.merge(df_flanker_incompat, on="sub_num")
    cols = list(df_flanker_both.columns.values)
    cols.pop(cols.index("sub_num")) #  Remove sub_num from list
    df_flanker_both = df_flanker_both[["sub_num"] + cols]
    
    df_digit = pd.DataFrame(columns=["sub_num", "digit_correct_count",
                                     "digit_correct_prop", "digit_num_items"])
    
    df_mrt = pd.DataFrame(columns=["sub_num", "mrt_count",
                                   "mrt_prop", "mrt_num_items"])
    
    df_ravens = pd.DataFrame(columns=["sub_num", "ravens_rt", "ravens_count",
                                      "ravens_prop", "ravens_num_items"])
    
    df_sart = pd.DataFrame(
                    columns=["sub_num", "sart_follow_error_rt",
                             "sart_follow_correct_rt", "sart_total_rt",
                             "sart_total_rtsd", "sart_total_rtcov", 
                             "sart_frequent_rt", "sart_frequent_rtsd",
                             "sart_frequent_rtcov", "sart_infrequent_rt",
                             "sart_infrequent_rtsd", "sart_infrequent_rtcov",
                             "sart_error_count"," sart_errors_prop",
                             "sart_errors_num_items"])
    
    df_sternberg = pd.DataFrame(
                    columns=["sub_num",
                    "stern_follow_error_rt", "stern_follow_correct_rt",
                    "stern_set_2_rt", "stern_set_6_rt",
                    "stern_set_2_rtsd", "stern_set_6_rtsd",
                    "stern_set_2_rtcov", "stern_set_6_rtcov",
                    "stern_set_2_correct", "stern_set_6_correct",
                    "stern_intercept", "stern_slope", "stern_slope_norm"])
    
    # Aggregate all data
    for f in os.listdir(dir_battery):
        if f.endswith(".xls"):
            print("Summarizing {}".format(f))
    
            sub = pd.read_excel(os.path.join(dir_battery, f), None,
                                converters={"sub_num":str})
            
            try:
                sub_num = sub["info"].loc[0,"sub_num"]
            except KeyError:
                sub_num = sub["info"].loc[0,"subNum"]
            datetime = sub["info"].loc[0,"datetime"]
            condition = int(sub["info"]["condition"])
            age = int(sub["info"]["age"])
            sex = sub["info"].loc[0,"sex"]
            ra = sub["info"].loc[0,"RA"]
    
            for task, data in sub.items():
                if task == "info":
                    df_info.loc[df_info.shape[0]] = [sub_num, datetime, condition, age, sex, ra]
                elif task == "ANT":
                    # full / correct / incorrect
                    df_ant.loc[df_ant.shape[0]] = aggregate_ant(data, sub_num, response_type)
                elif task == "Digit span (backwards)":
                    df_digit.loc[df_digit.shape[0]] = aggregate_digit_span(data, sub_num)
                elif task == "Eriksen Flanker":
                    compat_conditions = data["compatibility"].unique()
                    # full / correct / incorrect
                    if len(compat_conditions) == 1 and compat_conditions == "compatible":
                        df_flanker_compat.loc[df_flanker_compat.shape[0]] = aggregate_flanker(data, sub_num, response_type)
                    elif len(compat_conditions) == 1 and compat_conditions == "incompatible":
                        df_flanker_incompat.loc[df_flanker_incompat.shape[0]] = aggregate_flanker(data, sub_num, response_type)
                    else:
                        df_flanker_both.loc[df_flanker_both.shape[0]] = aggregate_flanker(data, sub_num, response_type)
                elif task == "MRT":
                    df_mrt.loc[df_mrt.shape[0]] = aggregate_mrt(data, sub_num)
                elif task == "Ravens Matrices":
                    df_ravens.loc[df_ravens.shape[0]] = aggregate_ravens(data, sub_num)
                elif task == "SART":
                    df_sart.loc[df_sart.shape[0]] = aggregate_sart(data, sub_num)
                elif task == "Sternberg":
                    # full / correct / incorrect
                    df_sternberg.loc[df_sternberg.shape[0]] = aggregate_sternberg(data, sub_num, response_type)
    
    # Merge task data
    # Only merge tasks that were used
    tasks = [df_ant, df_digit, df_flanker_compat, df_flanker_incompat,
             df_flanker_both, df_mrt, df_ravens, df_sart, df_sternberg]
    
    all_data = df_info
    for task in tasks:
        if task.shape[0] != 0:
            all_data = all_data.merge(task, on="sub_num", how="left")
    
    all_data['sub_num'] = all_data['sub_num'].astype(int)
    all_data = all_data.sort_values("sub_num").reset_index(drop=True)
    
    # Save output csv
    if save:
        all_data.to_csv(os.path.join(dir_output,
                                     "battery_data_{}.csv".format(response_type)),
                        index=False, sep=",")

    return all_data


def aggregate_ant(data, sub_num, response_type="full"):
    """
    Aggregate data from the ANT task.

    Calculates various summary statistics for the ANT task for a given subject.

    Parameters
    ----------
    data : dataframe
        Pandas dataframe containing a single subjects trial data for the task.
    sub_num : str
        Subject number to which the data file belongs.
    response_type : {'full', 'correct', 'incorrect'}, optional
        Should the summary data be calculated using all trials? Only correct 
        trials? Or only incorrect trials? This is not supported in all tasks.

    Returns
    -------
    stats : list
        List containing the calculated data for the subject.
    """
    
    # Calculate times following errors and correct responses
    df = data
    follow_error_rt = df.loc[df.correct.shift() == 0, "RT"].mean()
    follow_correct_rt = df.loc[df.correct.shift() == 1, "RT"].mean()

    if response_type == "correct":
        df = data[data["correct"] == 1]
    elif response_type == "incorrect":
        df = data[data["correct"] == 0]
    elif response_type == "full":
        df = data

    # Aggregated descriptives

    ## congruency conditions
    grouped_congruency = df.groupby("congruency")
    neutral_rt = grouped_congruency.mean().get_value("neutral", "RT")
    congruent_rt = grouped_congruency.mean().get_value("congruent", "RT")
    incongruent_rt = grouped_congruency.mean().get_value("incongruent", "RT")

    neutral_rtsd = grouped_congruency.std().get_value("neutral", "RT")
    congruent_rtsd = grouped_congruency.std().get_value("congruent", "RT")
    incongruent_rtsd = grouped_congruency.std().get_value("incongruent", "RT")

    neutral_rtcov = neutral_rtsd / neutral_rt
    congruent_rtcov = congruent_rtsd / congruent_rt
    incongruent_rtcov = incongruent_rtsd / incongruent_rt

    neutral_correct = grouped_congruency.sum().get_value("neutral", "correct")
    congruent_correct = grouped_congruency.sum().get_value("congruent", "correct")
    incongruent_correct = grouped_congruency.sum().get_value("incongruent", "correct")

    ## cue conditions
    grouped_cue = df.groupby("cue")
    nocue_rt = grouped_cue.mean().get_value("nocue", "RT")
    center_rt = grouped_cue.mean().get_value("center", "RT")
    spatial_rt = grouped_cue.mean().get_value("spatial", "RT")
    double_rt = grouped_cue.mean().get_value("double", "RT")

    nocue_rtsd = grouped_cue.std().get_value("nocue", "RT")
    center_rtsd = grouped_cue.std().get_value("center", "RT")
    spatial_rtsd = grouped_cue.std().get_value("spatial", "RT")
    double_rtsd = grouped_cue.std().get_value("double", "RT")

    nocue_rtcov = nocue_rtsd / nocue_rt
    center_rtcov = center_rtsd / center_rt
    spatial_rtcov = spatial_rtsd / spatial_rt
    double_rtcov = double_rtsd / double_rt

    nocue_correct = grouped_cue.sum().get_value("nocue", "correct")
    center_correct = grouped_cue.sum().get_value("center", "correct")
    spatial_correct = grouped_cue.sum().get_value("spatial", "correct")
    double_correct = grouped_cue.sum().get_value("double", "correct")

    # OLS regression
    conflict_intercept, conflict_slope = congruent_rt, incongruent_rt - congruent_rt
    conflict_slope_norm = conflict_slope / congruent_rt

    alerting_intercept, alerting_slope = double_rt, nocue_rt - double_rt
    alerting_slope_norm = alerting_slope / double_rt

    orienting_intercept, orienting_slope = spatial_rt, center_rt - spatial_rt
    orienting_slope_norm = orienting_slope / spatial_rt

    return [sub_num,
            follow_error_rt, follow_correct_rt,
            neutral_rt, congruent_rt, incongruent_rt,
            neutral_rtsd, congruent_rtsd, incongruent_rtsd,
            neutral_rtcov, congruent_rtcov, incongruent_rtcov,
            neutral_correct, congruent_correct, incongruent_correct,
            nocue_rt, center_rt, spatial_rt, double_rt,
            nocue_rtsd, center_rtsd, spatial_rtsd, double_rtsd,
            nocue_rtcov, center_rtcov, spatial_rtcov, double_rtcov,
            nocue_correct, center_correct, spatial_correct, double_correct,
            conflict_intercept, conflict_slope, conflict_slope_norm,
            alerting_intercept, alerting_slope, alerting_slope_norm,
            orienting_intercept, orienting_slope, orienting_slope_norm]


def aggregate_digit_span(data, sub_num):
    """
    Aggregate data from the digit span task.

    Calculates various summary statistics for the digit span task for a 
    given subject.

    Parameters
    ----------
    data : dataframe
        Pandas dataframe containing a single subjects trial data for the task.
    sub_num : str
        Subject number to which the data file belongs.

    Returns
    -------
    stats : list
        List containing the calculated data for the subject.
    """
    
    digit_correct_count = data["correct"].sum()
    digit_correct_num_items = data.shape[0]
    digit_correct_prop = digit_correct_count / digit_correct_num_items

    return [sub_num, digit_correct_count, digit_correct_prop, 
            digit_correct_num_items]


def aggregate_flanker(data, sub_num, response_type="full"):
    """
    Aggregate data from the Flanker task.

    Calculates various summary statistics for the Flanker task for a 
    given subject.

    Parameters
    ----------
    data : dataframe
        Pandas dataframe containing a single subjects trial data for the task.
    sub_num : str
        Subject number to which the data file belongs.
    response_type : {'full', 'correct', 'incorrect'}, optional
        Should the summary data be calculated using all trials? Only correct 
        trials? Or only incorrect trials? This is not supported in all tasks.

    Returns
    -------
    stats : list
        List containing the calculated data for the subject.
    """
    
    columns = [sub_num]
    
    # split compatibility conditions
    for comp_type in sorted(list(data["compatibility"].unique()), reverse=False):
        df_cur = data[data["compatibility"] == comp_type]
        
        # Calculate times following errors and correct responses
        follow_error_rt = df_cur.loc[df_cur.correct.shift() == 0, "RT"].mean()
        follow_correct_rt = df_cur.loc[df_cur.correct.shift() == 1, "RT"].mean()

        if response_type == "correct":
            df = df_cur[df_cur["correct"] == 1]
        elif response_type == "incorrect":
            df = df_cur[df_cur["correct"] == 0]
        elif response_type == "full":
            df = df_cur
        
        grouped_congruency = df.groupby(["congruency"])
        
        congruent_rt = grouped_congruency.mean().get_value("congruent", "RT")
        incongruent_rt = grouped_congruency.mean().get_value("incongruent", "RT")
    
        congruent_rtsd = grouped_congruency.std().get_value("congruent", "RT")
        incongruent_rtsd = grouped_congruency.std().get_value("incongruent", "RT")
    
        congruent_rtcov = congruent_rtsd / congruent_rt
        incongruent_rtcov = incongruent_rtsd / incongruent_rt
    
        congruent_correct = grouped_congruency.sum().get_value("congruent", "correct")
        incongruent_correct = grouped_congruency.sum().get_value("incongruent", "correct")
    
        # OLS regression
        conflict_intercept, conflict_slope = congruent_rt, incongruent_rt - congruent_rt
        conflict_slope_norm = conflict_slope / congruent_rt

        columns += [follow_error_rt, follow_correct_rt,
                    congruent_rt, incongruent_rt,
                    congruent_rtsd, incongruent_rtsd,
                    congruent_rtcov, incongruent_rtcov,
                    congruent_correct, incongruent_correct,
                    conflict_intercept, conflict_slope, conflict_slope_norm]

    return columns


def aggregate_mrt(data, sub_num):
    """
    Aggregate data from the MRT task.

    Calculates various summary statistics for the MRT task for a given subject.

    Parameters
    ----------
    data : dataframe
        Pandas dataframe containing a single subjects trial data for the task.
    sub_num : str
        Subject number to which the data file belongs.

    Returns
    -------
    stats : list
        List containing the calculated data for the subject.
    """
    
    mrt_count = data["correct"].sum()
    mrt_num_items = data.shape[0]
    mrt_prop = mrt_count / mrt_num_items

    return [sub_num, mrt_count, mrt_prop, mrt_num_items]


def aggregate_ravens(data, sub_num):
    """
    Aggregate data from the Raven's Matrices task.

    Calculates various summary statistics for the Raven's Matrices task for a 
    given subject.

    Parameters
    ----------
    data : dataframe
        Pandas dataframe containing a single subjects trial data for the task.
    sub_num : str
        Subject number to which the data file belongs.

    Returns
    -------
    stats : list
        List containing the calculated data for the subject.
    """
    
    ravens_rt = data["RT"].mean()
    ravens_count = data["correct"].sum()
    ravens_num_items = data.shape[0]
    ravens_prop = ravens_count / ravens_num_items

    return [sub_num, ravens_rt, ravens_count, ravens_prop, ravens_num_items]


def aggregate_sart(data, sub_num):
    """
    Aggregate data from the SART task.

    Calculates various summary statistics for the SART task for a given subject.

    Parameters
    ----------
    data : dataframe
        Pandas dataframe containing a single subjects trial data for the task.
    sub_num : str
        Subject number to which the data file belongs.

    Returns
    -------
    stats : list
        List containing the calculated data for the subject.
    """
    
    # Calculate times following errors and correct responses
    follow_error_rt = data.loc[data.accuracy.shift() == 0, "RT"].mean()
    follow_correct_rt = data.loc[data.accuracy.shift() == 1, "RT"].mean()

    total_rt = data["RT"].mean()
    total_rtsd = data["RT"].std()
    total_rtcov = total_rtsd / total_rt

    frequent_rt = data[data["stimulus"] != 3]["RT"].mean()
    frequent_rtsd = data[data["stimulus"] != 3]["RT"].std()
    frequent_rtcov = frequent_rtsd / frequent_rt

    infrequent_rt = data[data["stimulus"] == 3]["RT"].mean()
    infrequent_rtsd = data[data["stimulus"] == 3]["RT"].std()
    infrequent_rtcov = infrequent_rtsd / infrequent_rt

    sart_error_count = data[data["stimulus"] == 3]["key press"].sum()
    sart_errors_num_items = data[data["stimulus"] == 3].shape[0]
    sart_errors_prop = sart_error_count / sart_errors_num_items

    return [sub_num, follow_error_rt, follow_correct_rt,
            total_rt, total_rtsd, total_rtcov,
            frequent_rt, frequent_rtsd, frequent_rtcov,
            infrequent_rt, infrequent_rtsd, infrequent_rtcov,
            sart_error_count, sart_errors_prop, sart_errors_num_items]


def aggregate_sternberg(data, sub_num, response_type="full"):
    """
    Aggregate data from the Sternberg task.

    Calculates various summary statistics for the Sternberg task for a 
    given subject.

    Parameters
    ----------
    data : dataframe
        Pandas dataframe containing a single subjects trial data for the task.
    sub_num : str
        Subject number to which the data file belongs.
    response_type : {'full', 'correct', 'incorrect'}, optional
        Should the summary data be calculated using all trials? Only correct 
        trials? Or only incorrect trials? This is not supported in all tasks.

    Returns
    -------
    stats : list
        List containing the calculated data for the subject.
    """
    
    # Calculate times following errors and correct responses
    df = data
    follow_error_rt = df.loc[df.correct.shift() == 0, "RT"].mean()
    follow_correct_rt = df.loc[df.correct.shift() == 1, "RT"].mean()

    if response_type == "correct":
        df = data[data["correct"] == 1]
    elif response_type == "incorrect":
        df = data[data["correct"] == 0]
    elif response_type == "full":
        df = data

    # Aggregated descriptives
    grouped_set_size = df.groupby("setSize")
    set_2_rt = grouped_set_size.mean().get_value(2, "RT")
    set_2_rtsd = grouped_set_size.std().get_value(2, "RT")
    set_2_rtcov = set_2_rtsd / set_2_rt
    set_2_correct = grouped_set_size.sum().get_value(2, "correct")

    set_6_rt = grouped_set_size.mean().get_value(6, "RT")
    set_6_rtsd = grouped_set_size.std().get_value(6, "RT")
    set_6_rtcov = set_6_rtsd / set_6_rt
    set_6_correct = grouped_set_size.sum().get_value(6, "correct")

    # OLS regression
    intercept, slope = set_2_rt, set_6_rt - set_2_rt
    slope_norm = slope / set_2_rt

    return [sub_num,
            follow_error_rt, follow_correct_rt,
            set_2_rt, set_6_rt,
            set_2_rtsd, set_6_rtsd,
            set_2_rtcov, set_6_rtcov,
            set_2_correct, set_6_correct,
            intercept, slope, slope_norm]
