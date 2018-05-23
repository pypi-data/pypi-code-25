import os

import numpy as np

def exp_func(x, a, b, c):
    #y = a * np.exp(-b * x) + c
    y = (a - c) * np.exp(-b * x) + c
    return y

class FlourescentColours():
    """
    Object with fluorescent html colours from https://www.w3schools.com/colors/colors_crayola.asp
    """
    def __init__(self):
        self.red = "#FF355E"
        self.watermelon = "#FD5B78"
        self.orange = "#FF6037"
        self.tangerine = "#FF9966"
        self.carrot = "#FF9933"
        self.sunglow = "#FFCC33"
        self.lemon = "#FFFF66"
        self.yellow = "#FFFF66"
        self.lime = "#CCFF00"
        self.green = "#66FF66"
        self.mint = "#AAF0D1"
        self.blue = "#50BFE6"
        self.pink = "#FF6EFF"
        self.rose = "#EE34D2"
        self.magenta = "#FF00CC"
        self.pizzazz = "FF00CC"
        self.colourlist = ['#50BFE6', '#FF9933', '#66FF66', '#FFFF66', '#CCFF00', '#FF00CC', '#AAF01', '#FF6037', '#FF6EFF', 'FF00CC', '#FF355E', '#EE34D2', '#FFCC33', '#FF9966', '#FD5B78', '#FFFF66']

def get_fluorescent_colours():
    """
    DEPRECATED. Use the FlourescentColours object instead.

    Usage
    -----
    fc_dict, fl_col_keys, fl_col_list = blitzcurve.utils.get_fluorescent_colours()
    """
    # get dict and list of fluorescent colours
    #https://www.w3schools.com/colors/colors_crayola.asp
    fc_dict = {"Red":"#FF355E","Watermelon":"#FD5B78","Orange":"#FF6037","Tangerine":"#FF9966","Carrot":"#FF9933","Sunglow":"#FFCC33","Lemon":"#FFFF66","Yellow":"#FFFF66","Lime":"#CCFF00","Green":"#66FF66","Mint":"#AAF01","Blue":"#50BFE6","Pink":"#FF6EFF","Rose":"#EE34D2","Magenta":"#FF00CC","Pizzazz":"FF00CC"}
    fl_col_keys = sorted(fc_dict)
    fl_col_list = [fc_dict[k] for k in fl_col_keys]
    return fc_dict, fl_col_keys, fl_col_list

def setup_matplotlib_dark_background(plt):
    """ Initialises the dark background style of matplotlib, which applies to all following plots.
    Adds error caps to barcharts, sets figure size and dpi.

    Parameters
    ----------
    plt : matplotlib library
    """
    plt.style.use('dark_background')
    plt.rcParams['errorbar.capsize'] = 3
    plt.rcParams['figure.figsize'] = (5, 5)
    plt.rcParams["savefig.dpi"] = 240

# class OutFilepaths:
#     def __init__(self, data_dir, csv):
#         self.fits_dir = os.path.join(data_dir, "fits")
#         self.rotat_dir = os.path.join(self.fits_dir, "rotat")
#         self.savgol_dir = os.path.join(self.fits_dir, "savgol")
#         self.seg1_dir = os.path.join(self.fits_dir, "seg1")
#         self.seg2_dir = os.path.join(self.fits_dir, "seg2")
#         self.fitdata_dir = os.path.join(self.fits_dir, "fitdata")
#
#         for path in [self.fits_dir, self.rotat_dir, self.savgol_dir, self.seg1_dir, self.seg2_dir, self.fitdata_dir]:
#             if not os.path.isdir(path):
#                 os.makedirs(path)
#         self.filename = os.path.basename(csv)
#         self.rotat_fit_png = os.path.join(self.rotat_dir, self.filename[:-4] + "_rotat_fit.png")
#         self.savgol_fit_png = os.path.join(self.savgol_dir, self.filename[:-4] + "_savgol_fit.png")
#         self.savgol_fit_peak_png = os.path.join(self.savgol_dir, self.filename[:-4] + "_savgol_fit_peak.png")
#         self.savgol_fit_desc_png = os.path.join(self.seg1_dir, self.filename[:-4] + "_savgol_fit_desc.png")
#         self.exp_fit_seg1_png = os.path.join(self.seg1_dir, self.filename[:-4] + "_seg1.png")
#         self.exp_fit_seg2_png = os.path.join(self.seg2_dir, self.filename[:-4] + "_seg2.png")
#
#         self.fitdata_pickle = os.path.join(self.fitdata_dir, self.filename[:-4] + "_fitdata.pickle")


class OutDirPaths:
    """
    Creates paths for subdirectories and makes sure that they exist
    """
    def __init__(self, data_dir):
        self.fits_dir = os.path.join(data_dir, "fits")
        self.rotat_dir = os.path.join(self.fits_dir, "rotat")
        self.savgol_dir = os.path.join(self.fits_dir, "savgol")
        self.seg1_dir = os.path.join(self.fits_dir, "seg1")
        self.seg2_dir = os.path.join(self.fits_dir, "seg2")
        self.fitdata_dir = os.path.join(self.fits_dir, "fitdata")
        self.summary_figs_dir = os.path.join(data_dir, "summary", "figs")

        for path in [self.fits_dir, self.rotat_dir, self.savgol_dir, self.seg1_dir, self.seg2_dir, self.fitdata_dir, self.summary_figs_dir]:
            if not os.path.isdir(path):
                os.makedirs(path)

class FitFilePaths(OutDirPaths):
    """
    Adds file paths to the OutDirPaths object that are specific to a single sample, based on the original sample filename.
    """
    def __init__(self, data_dir, csv):
        # instantiate the parent OutDirPaths object, giving the relevant directories
        OutDirPaths.__init__(self, data_dir)
        # create various paths
        self.filename = os.path.basename(csv)
        self.rotat_fit_png = os.path.join(self.rotat_dir, self.filename[:-4] + "_rotat_fit.png")
        self.savgol_fit_png = os.path.join(self.savgol_dir, self.filename[:-4] + "_savgol_fit.png")
        self.savgol_fit_peak_png = os.path.join(self.savgol_dir, self.filename[:-4] + "_savgol_fit_peak.png")
        self.savgol_fit_desc_png = os.path.join(self.seg1_dir, self.filename[:-4] + "_savgol_fit_desc.png")
        self.exp_fit_seg1_png = os.path.join(self.seg1_dir, self.filename[:-4] + "_seg1.png")
        self.exp_fit_seg2_png = os.path.join(self.seg2_dir, self.filename[:-4] + "_seg2.png")
        self.fitdata_pickle = os.path.join(self.fitdata_dir, self.filename[:-4] + "_fitdata.pickle")

class CompareFilePaths(OutDirPaths):
    """
    Adds file paths to the OutDirPaths object that are specific to the compare function, e.g. for barcharts.
    """
    def __init__(self, data_dir):
        # instantiate the parent OutDirPaths object, giving the relevant directories
        OutDirPaths.__init__(self, data_dir)
        # barchart paths
        self.barchart_r_max = os.path.join(self.summary_figs_dir, "01_barchart_r_max.png")
        self.barchart_r_inf = os.path.join(self.summary_figs_dir, "02_barchart_r_inf.png")
        self.barchart_variable_a_png = os.path.join(self.summary_figs_dir, "03_barchart_a.png")
        self.barchart_variable_b_png = os.path.join(self.summary_figs_dir, "04_barchart_b.png")
        self.barchart_variable_c_png = os.path.join(self.summary_figs_dir, "05_barchart_c.png")
        # linechart paths
        self.linechart_savgol = os.path.join(self.summary_figs_dir, "06_linechart_savgol.png")
        self.linechart_seg1 = os.path.join(self.summary_figs_dir, "07_linechart_seg1.png")
        self.linechart_seg2 = os.path.join(self.summary_figs_dir, "08_linechart_seg2.png")

