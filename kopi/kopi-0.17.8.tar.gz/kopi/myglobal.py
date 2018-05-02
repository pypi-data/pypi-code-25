
"""
    Global Constants
"""
DEFAULT_PLOTSTYLE_FILENAME = "plotstyle.cson"
DEFAULT_MULTI_PLOTSTYLE_FILENAME = "multiplotstyle.cson"

DEFAULT_PDF_VIEWER_FOR_DARWIN = "open"
DEFAULT_PDF_VIEWER_FOR_LINUX = "evince"
DEFAULT_PDF_VIEWER_FOR_WINDOW = "start explorer.exe"

DEFAULT_PDF_FILENAME = "plotX.pdf"

#minimum linewidth is needed to draw smooth
#gradient color for, say, bar chart using the
#color map.
#If it were set to 0, segment border would appear.
LINEWIDTH_FOR_COLORMAP = 1
TAB_LENGTH = "    "
TAB = "    "
#So far only 4 space tab is stable.

GAP_PER_FONTSIZE_FOR_YLABEL = 0.5
GAP_PER_FONTSIZE_FOR_XLABEL = 0.25

# (My estimated Actual Font Height) / (Font Size)
FONT_HEIGHT_RATIO = 0.7
