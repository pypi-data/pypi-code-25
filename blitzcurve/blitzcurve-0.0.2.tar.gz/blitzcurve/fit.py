import glob
import os
import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
import blitzcurve.utils as utils
from blitzcurve.utils import setup_matplotlib_dark_background, FitFilePaths


def run_fit(data_dir, figs_to_plot="all", testing_mode=False):
    """Runs fit_single_sample on all files in a designated directory.

    Saves detailed output for each input data file as a pickle.

    For details, see docstring for fit_single_sample.

    Parameters
    ----------
    data_dir : str
        Path to directory with the input text files.
    figs_to_plot : str, list
        List of figures to plot. Default is "all" (all figures).
        Use during testing to speed up the analysis.
        "rotat" = rotation fit
            Figure from fit in original input file, designed to measure w (rotation).
        "savgol" = Savitzky-Golay fit
        "seg1" = fit to segment 1 of anisotropy data
        "seg2" = fit to segment 2 of anisotropy data
    testing_mode : bool
        If true, only the first two input data files in the folder will be analysed.

    Usage
    -----
    import blitzcurve
    data_dir = r"D:\data\20180229_TRdata"
    # fit
    blitzcurve.run_fit(data_dir, figs_to_plot=figs_to_plot, testing_mode=False)
    # compare
    name_dict = {"10nM-FGC1-2min_aniso.txt": "FGC1", "10nM-FGC2-2min_aniso.txt": "FGC2", "10nM-FGC3-2min_aniso.txt": "FGC3"}
    blitzcurve.run_compare(data_dir, name_dict=name_dict)
    """
    # setup colours and plot style
    setup_matplotlib_dark_background(plt)
    fc = utils.FlourescentColours()

    # get list of all text files in directory
    csv_files = glob.glob(os.path.join(data_dir, "*.txt"))

    # in testing mode, analyse only first 2 files
    if testing_mode:
        csv_files = csv_files[0:2]

    # iterate through the input files
    nested_summ_dict = {}
    for csv in csv_files:
        print(csv)
        # setup paths for the output files for that sample
        p = FitFilePaths(data_dir, csv)
        # run fit_single_sample to fit various curves
        summ_dict, fd = fit_single_sample(csv, fc, p, figs_to_plot)
        # collect summary for that sample
        nested_summ_dict[p.filename] = summ_dict
        # save output object with fitted curves etc for that sample
        with open(p.fitdata_pickle, "wb") as pic:
            pickle.dump(fd, pic, protocol=pickle.HIGHEST_PROTOCOL)

    # convert nested dict to dataframe and save.
    # this is the input for the barcharts ind the "compare.py" functions
    summ_dir = os.path.join(data_dir, "summary")
    if not os.path.isdir(summ_dir):
        os.makedirs(summ_dir)
    summ_csv = os.path.join(summ_dir, "fit_summary.csv")
    df_summ = pd.DataFrame(nested_summ_dict).T
    df_summ.to_csv(summ_csv)

def fit_single_sample(csv, fc, p, figs_to_plot):
    """

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe from .txt file, with raw time_ns and anisotropy data, as well as matlab-generated fits.
    fc : utils.FlourescentColours
        Fluorescent colours object with some useful colours for plotting.
    p : FitFilePaths
        File path object with the various output file locations
    figs_to_plot : str, list
        List of figures to plot. Default is "all" (all figures).
        Use during testing to speed up the analysis.
        "rotat" = rotation fit
            Figure from fit in original input file, designed to measure w (rotation).
        "savgol" = Savitzky-Golay fit
        "seg1" = fit to segment 1 of anisotropy data
        "seg2" = fit to segment 2 of anisotropy data

    Saved Files
    -----------
    p.rotat_fit_png : rotation fit and scatter plot
    p.savgol_fit_png : savitzky-golay fit and scatter plot
    p.savgol_fit_peak_png : zoom of savitzky-golay fit to show only the peak, to check accuracy of r_max
    p.exp_fit_seg1_png : exponential fit to segment 1
    p.exp_fit_seg2_png : exponential fit to segment 2

    Returns
    -------
    summ_dict : dict
        Dictionary with summary data for that single sample.
    fd : OutputFitData
        Output fit data object

    """
    df = pd.read_csv(csv)

    df2 = df[["time_ns", "anisotropy"]]
    df2.to_csv(r"D:\xDelete\smFRET_fit_test\20171017_data\example.csv")


    """Input dataframe looks like this:
         time_ns  anisotropy       fit      wres
    150    2.400    0.379667  0.383769 -0.004102
    151    2.416    0.378772  0.382971 -0.004199
    152    2.432    0.376986  0.382180 -0.005193
    153    2.448    0.376041  0.381395 -0.005355
    154    2.464    0.375459  0.380617 -0.005158
    155    2.480    0.375113  0.379846 -0.004732
    156    2.496    0.376228  0.379081 -0.002853
    157    2.512    0.373975  0.378323 -0.004347
    158    2.528    0.374096  0.377571 -0.003475
    """

    # initialise fit-data-object to hold fitted curves, and add filename and raw data
    fd = OutputFitData()
    fd.filename = p.filename
    fd.time = df.time_ns
    fd.anisotropy = df.anisotropy

    #########################################################################
    #    Scatter/Line plot with original fit designed to measure rotation   #
    #########################################################################
    if all(["all" or "rotat" in figs_to_plot, "fit" in df.columns]):
        plt.close("all")
        fig, ax = plt.subplots()
        df.plot(kind="scatter", x="time_ns", y="anisotropy", ax=ax, color=fc.green, label="data")
        df.plot(x="time_ns", y="fit", ax=ax, color=fc.red, label="rotational correlation fit")
        fig.savefig(p.rotat_fit_png)

    #########################################################################
    #               Scatter/Line plot with Savitzky-Golay fit               #
    #########################################################################
    x = df.time_ns.as_matrix()
    y = df.anisotropy.as_matrix()
    # get fit using window of 51 residues, and polynomial degrees of 3
    y_fit_savgol = savgol_filter(y, 51, 3)
    # save fit datapoints to output object
    fd.y_fit_savgol = y_fit_savgol

    # create a summary dictionary for this sample, and add r_max, etc
    summ_dict = {}
    summ_dict["r_max"] = y_fit_savgol.max()
    summ_dict["r_max_index"] = y_fit_savgol.argmax()
    summ_dict["r_max_time"] = x[summ_dict["r_max_index"]]

    if "all" or "savgol" in figs_to_plot:
        #########################################################################
        #                          plot with all datapoints                     #
        #########################################################################
        plt.close("all")
        fig, ax = plt.subplots()
        #plot raw data
        df.plot(kind="scatter", x="time_ns", y="anisotropy", ax=ax, color=fc.green, label="data", s=1)
        # plot fit data
        ax.plot(x, y_fit_savgol, color=fc.red, label="savitzky-golay fit")
        ax.set_title("savitzky-golay fit")
        ax.legend()
        
        # annotate the anosotropy associated with the peak on the graph
        peak_string = "max anisotropy : {:.02f}\n   time : {:.02f} ns".format(summ_dict["r_max"], summ_dict["r_max_time"])
        ax.annotate(peak_string, (summ_dict["r_max_time"] + 0.2, summ_dict["r_max"] - 0.02), color=fc.red)
        
        fig.savefig(p.savgol_fit_png, dpi=240)


        #########################################################################
        #       plot of only the peak region, to check accuracy of r_max        #
        #########################################################################
        plt.close("all")
        fig, ax = plt.subplots()
        df.plot(kind="scatter", x="time_ns", y="anisotropy", ax=ax, color=fc.green, label="data", s=1)
        ax.plot(x, y_fit_savgol, color=fc.red, label="savitzky-golay fit")
        ax.set_title("savitzky-golay fit")
        ax.legend()
        #  hard-coded xlim and ylim are not very flexible, but work right now..
        ax.set_xlim(0.4, 2)
        ax.set_ylim(0.3, 0.6)
        ax.set_title("savitzky-golay fit for peak only")

        # annotate the anosotropy associated with the peak on the graph
        peak_string = "max anisotropy : {:.02f}\ntime : {:.02f} ns".format(summ_dict["r_max"], summ_dict["r_max_time"])
        ax.annotate(peak_string, (summ_dict["r_max_time"] + 0.1, summ_dict["r_max"] + 0.005), color=fc.red)
        
        fig.savefig(p.savgol_fit_peak_png)


    #########################################################################
    #          Scatter/Line plot with segment 1 exponential fit             #
    #########################################################################
    
    # define start and end of segment 1 and segment 2
    # currently segment 1 starts 40 datapoints after the peak, which is not very flexible
    datapoints_after_peak = 40
    start_seg1 = summ_dict["r_max_index"] + datapoints_after_peak
    end_seg1 = 300
    start_seg2 = end_seg1

    if "all" or "seg1" in figs_to_plot:
        # plot raw datapoints
        plt.close("all")
        fig, ax = plt.subplots()
        df.plot(kind="scatter", x="time_ns", y="anisotropy", ax=ax, color=fc.green, label="data", s=1, zorder=2)

        # get x (time) and y (anisotropy) for only this segment
        df_seg1 = df.loc[start_seg1:end_seg1, :]
        x = df_seg1.time_ns.as_matrix()
        y = df_seg1.anisotropy.as_matrix()

        # fit to exponential. Extract a, b and c from fitted exponential formula.
        guess = (0.7, 0.7, 0.2)
        popt, pcov = curve_fit(utils.exp_func, x, y, p0=guess)
        a_seg1, b_seg1, c_seg1 = popt
        summ_dict["a_seg1"], summ_dict["b_seg1"] ,summ_dict["c_seg1"] = a_seg1, b_seg1, c_seg1

        # annotate the function on the graph
        function_string = r"y = %0.2f * $e^{(-%0.2fx)}$ + %0.2f" % (a_seg1, b_seg1, c_seg1)
        ax.annotate(function_string, (np.median(x) + 0.2, np.median(y) + 0.05), color=fc.magenta)

        # plot the exponential fit to this section
        xmax_seg1 = df.time_ns[end_seg1]
        seg1_xfit = np.linspace(0, xmax_seg1, 500)
        seg1_yfit = utils.exp_func(seg1_xfit, *popt)
        ax.plot(seg1_xfit, seg1_yfit, color=fc.magenta, label="exponential fit")

        # add the shading rectangle behind the fitted segment
        # zorder is used to send the rectangle to the back
        ymin, ymax = ax.get_ylim()
        height = ymax - ymin
        width = x[-1] - x[0]
        rect = Rectangle((x[0], ymin), width, height, color="0.2", zorder=1)
        ax.add_patch(rect)

        ax.set_title("fit to segment 1")
        ax.legend()
        fig.savefig(p.exp_fit_seg1_png)

        # add data to output curve dictionary
        #curve_dict["seg1_xfit"] = seg1_xfit
        #curve_dict["seg1_yfit"] = seg1_yfit
        fd.seg1_xfit = seg1_xfit
        fd.seg1_yfit = seg1_yfit

    #########################################################################
    #          Scatter/Line plot with segment 2 exponential fit             #
    #########################################################################
    if "all" or "seg2" in figs_to_plot:
        # plot raw datapoints
        plt.close("all")
        fig, ax = plt.subplots()
        df.plot(kind="scatter", x="time_ns", y="anisotropy", ax=ax, color=fc.green, label="data", s=1, zorder=2)

        # get x (time) and y (anisotropy) for only this segment
        df_seg2 = df.loc[start_seg2:, :]
        x = df_seg2.time_ns.as_matrix()
        y = df_seg2.anisotropy.as_matrix()

        # fit to exponential. Extract a, b and c from fitted exponential formula.
        guess = (0.4, 0.2, 0.2)
        popt, pcov = curve_fit(utils.exp_func, x, y, p0=guess)
        a_seg2, b_seg2, r_inf = popt
        summ_dict["a_seg2"], summ_dict["b_seg2"] ,summ_dict["r_inf"] = a_seg2, b_seg2, r_inf

        # annotate the function on the graph
        function_string = r"y = %0.2f * $e^{(-%0.2fx)}$ + %0.2f" % (a_seg2, b_seg2, r_inf)
        ax.annotate(function_string, (x[0] + 0.2, y[0] + 0.05), color=fc.pink)

        # plot the exponential fit to this section
        xmax_fit = x.max() + 3
        seg2_xfit = np.linspace(0, xmax_fit, 500)
        seg2_yfit = utils.exp_func(seg2_xfit, *popt)
        ax.plot(seg2_xfit, seg2_yfit, color=fc.pink, label="exponential fit segment 2")

        # plot the r_inf as a horizontal line
        ax.hlines(r_inf, 0, xmax_fit, color=fc.pink)

        # add the shading rectangle behind the fitted segment
        # zorder is used to send the rectangle to the back
        ymin, ymax = ax.get_ylim()
        height = ymax - ymin
        width = x[-1] - x[0]
        rect = Rectangle((x[0], ymin), width, height, color="0.2", zorder=1)
        ax.add_patch(rect)

        ax.set_title("fit to segment 2")
        ax.legend()
        fig.savefig(p.exp_fit_seg2_png)

        # save fitted data to output object
        fd.seg2_xfit = seg2_xfit
        fd.seg2_yfit = seg2_yfit

    return summ_dict, fd


class OutputFitData:
    """

    Object to hold the output fitted curves, which consists of arrays of different lengths.

    I know this is probably easier to store in a dictionary, but I was having a little "OOP moment".

    """

    def __init__(self, name=None, time=None, y_fit_savgol=None, seg1_xfit=None, seg1_yfit=None, seg2_xfit=None, seg2_yfit=None):
        self.name = name
        self.y_fit_savgol = y_fit_savgol
        self.time = time
        self.seg1_xfit = seg1_xfit
        self.seg1_yfit = seg1_yfit
        self.seg2_xfit = seg2_xfit
        self.seg2_yfit = seg2_yfit