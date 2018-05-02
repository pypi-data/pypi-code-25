#!python3
__all__ = ["make_cafe", "make_latte", "brew", "Kopio"]
import platform
from . import myglobal
#import myglobal
TAB = myglobal.TAB_LENGTH
COLON = ":"
EOL = "\n"
SHARP = "#"
SPACE = " "
def mystr(x):
    if isinstance(x, str):
        return "\"" + x + "\""
    elif isinstance(x, bool):
        if x ==True:
            return "true"
        else:
            return "false"
    elif isinstance(x, int):
        return str(x)
    else:
        return str(x)
GreetOne =(
    "# Preferences to adjust the appearance of a single plot\n" +
    "#\n"+
    "#    For the case of multi-subplot in a single graph,\n"+
    "#    the adjustment of subplots is controlled\n"+
    "#    by another cson file, e.g. \"multiplotattrib.cson\"\n"+
    "#    The appearance of Each subplot is however,\n"+
    "#    adjusted by this file.\n\n"+
    "#    PS:\n"+
    "#    Standard cson file does not have comments.\n"+
    "#    The comments are discarded before sending\n"+
    "#    to the cson.loads\n"+
    "#\n"+
    "#     So far so good.\n")

GreetMulti =(
    "# Preferences to adjust the appearance of of multiplot\n" +
    "#\n"+
    "#    The appearance of Each subplot is however,\n"+
    "#    adjusted by another cson file.\n")

Kopio ={
    "PDF":
        {
            "PDF_Filename"      : myglobal.DEFAULT_PDF_FILENAME,
            "ShowPDF"           : True,
            "PDF_Viewer"        : "open",
            "PDF_Compression"   : False,
            "UseJPEGForJPEGFile": False,
            "UseHTMLCanvas"     : False
        },
    "Paper":
        {
            "Portrait" : True,
            "Size"     : [500,400],
            "Unit"     : "pt",
            "Color"    : ""
        },
    "PlotRange":
        {
            "Width"     : 300,
            "Height"    : 300,
            "Unit"      : "pt" ,
            "AutoOrigin": True,
            "Origin"    : [60,50]
        },

    "Plot":
        {
            "LineColor" : [ "black","red","blue","green"],
            "LineType"  : ["-","--"],
            "LineWidth" : 1.5,
            "xlimit"    :[],
            "ylimit"    :[],
            "x2limit"   :[],
            "y2limit"   :[],
            "FillAreaUnderGraph" : False,
            "FillAreaColor"      : ["red","blue"],
            "Point":
                {
                "Show"          :True,
                "Type"          :["SolidCircle","SolidSquare","SolidTriangle"],
                "Color"         :["red","blue","green"],
                "AutoSize"      :True,
                "SizeOverHeight":0.04,
                "Size"          :12,
                },
            "BarChart":
                {
                "Show"      : False,
                "BarWidth"  : 2,
                "LineWidth" : 1,
                "LineColor" : "blue",
                "Fill"      : True,
                "FillColor" : "green", #also accept color map
                "ColorMapNormalization": "G" #L:local, G:global
                },
            "PlotBox":
                {
                "Show"      : False,
                "BoxColor"  : "gray",
                "LineWidth" : 1.0,
                "LineColor" : "black",
                "LineType"  : "-",
                },
            "ErrorBar":
                {
                "Show"           : True,
                "Color"          : "blue",
                "LineWidth"      : 1,
                "AutoLength"     : True,
                "LengthOverWidth": 0.04,
                "Length"         : 10
                },
        },
    "xLabel"                 :{
        "Text"               : "Time (min)",
        "Font"               : "Helvetica",
        "OffsetX"            : 0,
        "OffsetY"            : 0,
        "AutoFontSize"       : True,
        "FontSizeOverHeight" : 0.06,
        "FontSize"           : 14,
        "FontColor"          : "blue"
        },
    "yLabel":
        {
        "Text"              :"Signal",
        "Font"              :"Helvetica",
        "OffsetX"           :0,
        "OffsetY"           :0,
        "AutoFontSize"      : True,
        "FontSizeOverHeight":0.06,
        "FontSize"          : 14,
        "FontColor"         : "blue"
        },
    "Title"                  :
        {
        "Show"               : True,
        "Text"               : "Title",
        "Font"               : "Helvetica",
        "FontSize"           : 14,
        "FontColor"          : "black",
        "Alignment"          : "l",
        "Spacing"            : 0,
        "Yoffset"            : 0,
        "Xoffset"            : 0,
        "WidthRatio"         : 0.8,
        "AutoFontSize"       : True,
        "FontSizeOverHeight" : 0.08
        },

    "Xaxis":
        {
        "Show"     : True,
        "Log"          : False,
        "LineWidth"    : 1.5,
        "LineColor"    : "black",
        "LineType"     : "-",
        "ShowTickText" : True,
        "Yposition"    : "",
        "YoffsetInPt"  :0,
        "Tick" :
            {
            "Show"              : True,
            "TickOut"           :True, #Tick "in" if false.
            "Length"            : 3, #If negative, tick to the opposite direction
            "Width"             : 1.0,
            "Color"             : "black",
            "Font"              : "Helvetica",
            "FontSize"          : 12,
            "FontColor"         : "black",
            "AutoLength"        : True,
            "LengthOverHeight"  : 0.03, #If negative, tick to the opposite direction
            "AutoFontSize"      : True,
            "FontSizeOverHeight": 0.05
            },
        "MinorTick":
            {
            "Show"                 : True,
            "TickNumber"           : 5,
            "LineWidth"            : 0.5,
            "LineColor"            : "black",
            "LengthOverTickLength" : 0.6
            },
        "Grid":
            {
            "Show"      : False,
            "LineColor" : "blue",
            "LineWidth" : 0.25,
            "LineType"  : "-",
            },
        "MinorGrid":
            {
            "Show" : False,
            "LineColor" : "green",
            "LineWidth" : 0.1,
            "LineType" : "-"
            }
        },

    "Yaxis":
        {
        "Show"     : True,
        "Log"          : False,
        "LineWidth"    : 1.5,
        "LineColor"    : "black",
        "LineType"     : "-",
        "ShowTickText" :True,
        "Xposition"    : "",
        "XoffsetInPt"  :0,
        "Tick":
            {
            "Show" : True,
            "TickOut": True, #Tick "in" if false.
            "Length" : 5, # Use this value if auto length is False
            "Width" : 1.0,
            "Color" : "black",
            "Font" : "Helvetica",
            "FontSize" : 12,
            "FontColor" : "black",
            "AutoLength" : True,
            "LengthOverHeight" : 0.03,
            "AutoFontSize" : True,
            "FontSizeOverHeight" : 0.05,
            "OffsetOfTextFromTickOverWidth" : 0.01
            },
        "MinorTick":
            {
            "Show" : True,
            "TickNumber"    : 5,
            "LineWidth" : 0.5,
            "LineColor" : "black",
            "LengthOverTickLength":0.6,
            },
        "Grid":
            {
            "Show" : False,
            "LineColor" : "blue",
            "LineWidth" : 0.25,
            "LineType" : "-"
            },
        "MinorGrid":
            {
            "Show" : False,
            "LineColor" : "green",
            "LineWidth" : 0.1,
            "LineType" : "-"
            }
        },

    "y2Label"    :    "Intensity2",

    "Plot2Color"    :["red"],
    "Annotate" :[],
    "AnnotateFont" : "Helvetica",
    "AnnotateFontSize" : 8,
    "AnnotateFontColor" : "blue",
    "AnnotateWidth" : 100,
    "AnnotateAlignment" : 0,
    "AnnotateSpacing" :1,

    "Picture":
        {
        "InsertPicture"    :False,
        "PictureFilename" :["Example.jpg","PNG_example.png", "image1.jpg"],
        "PictureSize"     :[[200,200],[100,100], [100,100]],
        "PictureOrigin"    :[[0,100],[200,100],[300,100]],
        "PictureCustom"    :True
        },

    "ShowDataOnly":False,

    "Debug":
        {
        "ShowErrorMessage":True,
        "ShowPrint":True,
        "VerbalEchoForMpretty":False,
        "EchoThisContent":False
        },


    "ColorMap":"viridis",
                # Available color map developed for
                # New matplotlib colormaps
                # by Nathaniel J. Smith, Stefan van der Walt,
                # and (in the case of viridis) Eric Firing:
                # Available colormap so far:
                # magma, inferno, plasma, viridis, custom made jet
    "SecondaryAxis":False,
    "LayoutSequence" : ["Axes","AreaUnderGraph", "PlotLine", "BarChart","ErrorBar", "PlotPoint"]
    }

HelpKopio ={
    "PDF":
        {
            "PDF_Filename"      : "    # The file name to store the plotted pdf file. Default : \"plotX.pdf\"\n",
            "ShowPDF"           : "    # Open the pdf viewer when the plot file is ready. Default: True\n",
            "PDF_Viewer"        : "    # Default in Mac: \"open\"\n",
            "PDF_Compression"   : "    # E.g.: false\n",
            "UseJPEGForJPEGFile": "    # E.g.: false\n",
            "UseHTMLCanvas"     : "    # E.g.: false\n",
        },
    "Paper":
        {
            "Portrait"  : "    # true for portrait and false for landscape. Default: true\n",
            "Size"      : "    # [width, height] for the pdf paper. Defalt: [500,400]\n",
            "Unit"      : "    # only pt is stable\n",
            "Color"     : "    # leave it \"\" for white color\n"
        },
    "PlotRange":
        {
            "Width"     : "    # Plot width in pt. Default : 300\n",
            "Height"    : "    # Plot heigth in pt. Default : 300\n",
            "Unit"      : "    # so far only \"pt\" is stable\n",
            "AutoOrigin": "    # True for auto, False for manual\n",
            "Origin"    : "    # This will be used for manual origin. Default: [60,50]\n"
        },

    "Plot":
        {
            "LineColor"    :     "    # Accept verbal name or HTML color code\n"+\
                            "    # e.g. [\"black\",\"red\",\"blue\"] for multiple lines\n"+\
                            "    # or [#000000, #FF0000, #0000FF]\n"+\
                            "    # or just \"black\" for single line\n",

            "LineType"    :    "    # Available linetype:\n"+\
                            "    # \"\":    no line\n"+\
                            "    # \"-\":    normal continuous line\n"+\
                            "    # \"--\":    dashed line\n"+\
                            "    # \".\":    dotted line\n"+\
                            "    # \"-.-\"    :dashed dotted dashed line\n"+\
                            "    # E.g.: [\"-\",\"--\"]for multiple line\n"+\
                            "    # Also accept custom line type defination in pdf format\n"+\
                            "    # e.g. [[10,20],0]\n",
            "LineWidth" :   "    # In pt. Default: 1.5\n",
            "xlimit"    :   "    # The range to be plotted. E.g. [xmin, xmax]. Auto: []\n",
            "ylimit"    :   "    # E.g. [ymin, ymax]. Auto: []\n",
            "x2limit"   :   "    # For second axis. E.g. [xmin, xmax]. Auto: []\n",
            "y2limit"   :   "    # For second axis. E.g. [xmin, xmax]. Auto: []\n",
            "FillAreaUnderGraph"    :"    # E.g. False\n",
            "FillAreaColor"        :    "    # E.g.: [\"red\",\"blue\"]\n",
            "Point":
                {
                "Show"          : "        # Set true to draw points\n"+\
                                  "        # Also accept List. E.g. [true, true, false] for multiplot\n",
                "Type"          : "        # E.g.: \"SolidCircle\",\"SolidSquare\",\"SolidTriangle\"]\n",
                "Color"         : "        # E.g.: [\"red\",\"blue\",\"green\"]\n",
                "AutoSize"      : "        # E.g.: true\n",
                "SizeOverHeight": "        # Height_of_point/Height_of_plot. Default: 0.04\n",
                "Size"          : "        # This value will be used if AuotoSize is false\n",
                },
            "BarChart":
                {
                "Show"      : "        # Set true to show bar chart.\n",
                "BarWidth"  : "        # width in pt\n",
                "LineWidth" : "        # line width in pt\n",
                "LineColor" : "        # line color\n",
                "Fill"      : "        # Set true to fill the bar\n",
                "FillColor" : "        # Color name or code. Also Accept Color map\n",
                "ColorMapNormalization": "        # \"L\":local, \"G\": global\n"
                },
            "PlotBox":
                {
                "Show"     :"        # Set true to color the background. Default: false\n",
                "BoxColor" :"        # E.g.: \"gray\"\n",
                "LineWidth":"        # Line width in pt. E.g.: 1.0",
                "LineColor":"        # E.g.: \"black\"\n",
                "LineType" :"        # E.g.: \"-\"\n",
                },
            "ErrorBar":
                {
                "Show"           :"        # Set true to draw error bar. Default: false\n",
                "Color"          :"        # Color of the error bar\n",
                "LineWidth"      :"        # Default: 1.0\n",
                "AutoLength"     :"        # Set true to auto adjust the error bars\n",
                "LengthOverWidth":"        # Length of the error bar/Plot width. Default: 0.05\n",
                "Length"         :"        # This value will be used if AuotoLength is false. Default: 10\n",
                },
        },
    "xLabel":{
        "Text"        :     "    # The label for x axis\n",
        "Font"        :    "    # The name of the font. E.g.: Helvetica\n",
        "OffsetX"    :    "    # Offset in pt in x-direction\n"+\
                        "    # Adjust this value to move the xlabel horizontally\n",
        "OffsetY"    :    "    # Offset in pt in x-direction\n"+\
                        "    # Adjust this value to move the xlabel vertically\n",

        "AutoFontSize":         "    # Default : true\n",
        "FontSizeOverHeight" :     "    # Heigth_font/Height_plot. E.g. : 0.06\n",
        "FontSize" :             "    # This value will be used if AuotoFontSize is false. E.g. 12\n",
        "FontColor" :             "    # E.g.: \"black\"\n",
        },
    "yLabel":
        {
        "Text":                    "    # The label for y axis\n",
        "Font":                    "    # The name of the font. E.g.: Helvetica\n",
        "OffsetX":                "    # Offset in pt in x-direction\n"+\
                                "    # Adjust this value to move the ylabel vertically\n",
        "OffsetY":                "    # Offset in pt in y-direction\n"+\
                                "    # Adjust this value to move the ylabel vertically\n",
        "AutoFontSize" :         "    # Default : true\n",
        "FontSizeOverHeight":    "    # Heigth_font/Height_plot. E.g. : 0.06\n",
        "FontSize"     :             "    # This value will be used if AuotoFontSize is false. E.g. 12\n",
        "FontColor"     :         "    # E.g.: \"black\"\n",
        },
    "Title":
        {
        "Show"    :                "    # Set true to show title\n",
        "Text"    :                "    # The text for the Title\n",
        "Font"    :                "    # The name of the font. E.g.: Helvetica\n",
        "FontSize" :             "    # This value will be used if AuotoFontSize is false. E.g. 14\n",
        "FontColor" :             "    # E.g.: \"black\"\n",
        "Alignment" :             "    # \"l\" for align to the left\n",
        "Spacing" :             "    # I dont know !\n",
        "Yoffset" :             "    # Offset in pt in y-direction\n",
        "Xoffset" :             "    # Offset in pt in x-direction\n",
        "WidthRatio":             "    # I dont know !. Defult: 0.8\n",
        "AutoFontSize":         "    # Default : true\n",
        "FontSizeOverHeight" :     "    # Heigth_font/Height_plot. E.g. : 0.1\n"
        },

    "Xaxis":
        {
        "Show"      : "    # Default : true\n",
        "Log"       : "    # Set true to use Log scale for X-axis\n",
        "LineWidth" : "    # axis line width in pt. E.g.: 1.5\n",
        "LineColor" : "    # E.g. \"black\"\n",
        "LineType" :  "    # Default: \"-\"\n",
        "ShowTickText": "    # Default: true",
        "Yposition":    "    # Y-position to put the Xaxis\n"+\
                        "    # Use the unit in your graph\n"+\
                        "    # E.g.: \"\" for auto\n" +\
                        "    # E.g.: 10.0 for drawing X-axis at y=10",
        "YoffsetInPt":  "    # Shift Xaxis vertically. Unit in pt",

        "Tick":
            {
            "Show"              :"        # Set true to draw the tick\n",
            "TickOut"           :"        # Tick \'out\' if true, tick \'in\' if false\n",
            "Length"            :"        # E.g.: 3. If negative, tick to the opposite direction\n",
            "Width"             :"        # E.g.: 1.0\n",
            "Color"             :"        # E.g.: \"black\"\n",
            "Font"              :"        # E.g.: \"Helvetica\"\n",
            "FontSize"          :"        # E.g.: 12\n",
            "FontColor"         :"        # E.g. \"black\"\n",
            "AutoLength"        :"        # E.g. true\n",
            "LengthOverHeight"  :"        # E.g.: 0.03. If negative, tick to the opposite direction\n",
            "AutoFontSize"      :"        # Default: true\n",
            "FontSizeOverHeight":"        # E.g.: 0.05\n"
            },
        "MinorTick":
            {
            "Show":                 "        # Set true to display the minor tick\n",
            "TickNumber" :             "        # E.g.: 5. \n"+\
                                    "        # It is actually the number to step from major tick to another\n",
            "LineWidth" :             "        # E.g.: 0.5\n",
            "LineColor" :             "        # E.g. \"black\"\n",
            "LengthOverTickLength":    "        # MinorTickLength/MajorTickLength. E.g.: 0.6\n"
            },
        "Grid":
            {
            "Show" :         "        # Set true to display the grid for the major tick\n",
            "LineColor" :     "        # E.g. \"blue\"\n",
            "LineWidth" :     "        # E.g.: 0.25\n",
            "LineType" :     "        # E.g. \"-\"\n",
            },
        "MinorGrid":
            {
            "Show" :         "        # Set true to display the grid for the minor tick\n",
            "LineColor" :     "        # E.g.: \"green\"\n",
            "LineWidth" :     "        # E.g.: 0.1\n",
            "LineType" :     "        # E.g. \"-\"\n",
            }
        },

    "Yaxis":
        {
        "Show"      :  "    # Default : true\n",
        "Log"       :  "    # Set true to use Log scale for Y-axis\n",
        "LineWidth" :     "    # axis line width in pt. E.g.: 1.5\n",
        "LineColor" :     "    # E.g. \"black\"\n",
        "LineType" :     "    # Default: \"-\"\n",
        "ShowTickText":    "    # Default: true",
        "Xposition":    "    # X-position to put the Yaxis\n"+\
                        "    # Use the unit in your graph\n"+\
                        "    # E.g.: \"\" for auto\n" +\
                        "    # E.g.: 10.0 for drawing Y-axis at x=10",
        "XoffsetInPt":    "    # Shift Yaxis horizontally. Unit in pt",

        "Tick":
            {
            "Show" :                             "        # Set true to draw the tick\n",
            "TickOut":                            "        # Tick \'out\' if true, tick \'in\' if false\n",
            "Length" :                            "        # E.g.: 3. If negative, tick to the opposite direction\n",
            "Width" :                            "        # E.g.: 1.0\n",
            "Color" :                            "        # E.g.: \"black\"\n",
            "Font" :                            "        # E.g.: \"Helvetica\"\n",
            "FontSize" :                        "        # E.g.: 12\n",
            "FontColor" :                         "        # E.g. \"black\"\n",
            "AutoLength":                         "        # E.g. true\n",
            "LengthOverHeight" :                 "        # E.g.: 0.03. If negative, tick to the opposite direction\n",
            "AutoFontSize":                     "        # Default: true\n",
            "FontSizeOverHeight":                 "        # E.g.: 0.05\n",
            "OffsetOfTextFromTickOverWidth":    "        # Distance from the y-tick/ Plot width. E.g: 0.01\n"
            },
        "MinorTick":
            {
            "Show":                     "        # Set true to display the minor tick\n",
            "TickNumber" :                 "        # E.g.: 5. \n"+\
                                        "        # It is actually the number to step from major tick to another\n",
            "LineWidth" :                 "        # E.g.: 0.5\n",
            "LineColor" :                 "        # E.g. \"black\"\n",
            "LengthOverTickLength" :    "        # MinorTickLength/MajorTickLength. E.g.: 0.6\n"
            },
        "Grid":
            {
            "Show" :         "        # Set true to display the grid for the major tick\n",
            "LineColor" :     "        # E.g. \"blue\"\n",
            "LineWidth" :     "        # E.g.: 0.25\n",
            "LineType" :     "        # E.g. \"-\"\n",
            },
        "MinorGrid":
            {
            "Show" :         "        # Set true to display the grid for the minor tick\n",
            "LineColor" :     "        # E.g.: \"green\"\n",
            "LineWidth" :     "        # E.g.: 0.1\n",
            "LineType" :     "        # E.g. \"-\"\n",
            }
        },

    "y2Label"    :    "    # Label for secondary y-axis\n",

    "Plot2Color"    :     "    # E.g.: [\"red\"]\n",
    "Annotate" :            "    # Not available yet. E.g. []\n",
    "AnnotateFont" :         "    # E.g. \"Helvetica\"\n",
    "AnnotateFontSize" :     "    # E.g.: 8\n",
    "AnnotateFontColor" :     "    # E.g.: \"blue\"\n",
    "AnnotateWidth" :         "    # I dont know\n",
    "AnnotateAlignment" :     "    # I dont know\n",
    "AnnotateSpacing" :        "    # I dont know\n",

    "Picture":
        {
        "InsertPicture"    :     "    # Set true to insert JPG picture as the background",
        "PictureFilename" :    "    # Valid filename or a list of filenames for the picture\n"+\
                            "    # E.g.: [\"Example.jpg\",\"PNG_example.png\", \"image1.jpg\"]\n",
        "PictureSize"     :    "    # E.g.: [[200,200],[100,100], [100,100]]\n",
        "PictureOrigin"    :    "    # E.g.: [[0,100],[200,100],[300,100]]\n",
        "PictureCustom"    :    "    # Not sure what it is\n"
        },

    "ShowDataOnly":"    # Set true to draw curve only. No axes, title, label etc. Default: false\n",

    "Debug":
        {
        "ShowErrorMessage":     "    # Not available yet\n",
        "ShowPrint":             "    # Not available yet\n",
        "VerbalEchoForMpretty":    "    # Not available yet\n",
        "EchoThisContent":        "    # Not available yet\n",
        },

    "ColorMap":    "    # E.g. \"viridis\""+\
                "    # Available color map developed for\n"+\
                "    # New matplotlib colormaps\n"+\
                "    # by Nathaniel J. Smith, Stefan van der Walt\n"+\
                "    # and (in the case of viridis) Eric Firing:\n"+\
                "    # Available colormap so far:\n"+\
                "    # magma, inferno, plasma, viridis\n",
    "SecondaryAxis"  : "    # Default: False\n",
    "LayoutSequence" : "    # [\"Axes\", \"AreaUnderGraph\", \"PlotLine\", \"BarChart\", \"ErrorBar]\", \"PlotPoint\"]"

    }



Theme_0 ={
    "PDF":
        {
            "PDF_Filename": {
                "value": myglobal.DEFAULT_PDF_FILENAME,
                "help" : "The file name to store the plotted pdf file."
                },
            "ShowPDF":{
                "value": True,
                "help" : "Open the pdf viewer when the plot file is ready."
                },
            "PDF_Viewer":
                {
                "value":"open",
                "help" :"The valid command for pdf viewer.\n"+\
                        "Make sure you have the right to open it."
                },
            "PDF_Compression":
                {
                "value": False,
                "help" : "ASCII85 compression for the pdf script."
                },
            "UseJPEGForJPEGFile":
                {
                "value": False,
                "help" : "Embed the JPEG file directly without open it with Pillow."
                },
            "UseHTMLCanvas":
                {
                "value": False,
                "help" : "Write the canvas script for quick preview. Quality not guaranteed."
                }
        },
    "Paper":
        {
            "Portrait" :
                {
                "value": True,
                "help" : "True for portrait and false for landscape."
                },
            "Size" :
                {
                "value": [500,400],
                "help" : "[width, height] for the pdf paper\n"+\
                         "In the other word, the Margin of the Figure"
                },
            "Unit":
                {
                "value": "pt",
                "help" : "Only pt is stable so far"
                },
            "Color":
                {
                "value": "",
                "help" : "Leave it \"\" for white "
                },
        },
    "PlotRange":
        {
            "Width":
                {
                "value": 300,
                "help" : "Plot width in pt.",
                },
            "Height":
                {
                "value": 300,
                "help" : "Plot heigth in pt.",
                },
            "Unit":
                {
                "value": "pt",
                "help" : "So far only \"pt\" is stable."
                },
            "AutoOrigin":
                {
                "value": True,
                "help" : "True for auto, False for manual.\n"+\
                         "If True, the Plot Space will be set to the middle of the Pdf Paper"
                },
            "Origin":
                {
                "value": [60,50],
                "help" : "This will be used for manual origin.\n" +\
                         "Origin is the most Lower-Left point of the Plot Space."
                },
        },

    "Plot":
        {
            "LineColor":
                {
                "value": ["black","red","blue","green"],
                "help" : "Accept verbal name or HTML color code\n"+\
                         "e.g.[\"black\",\"red\", ...] for multiple lines\n"+\
                         "or [#000000, #FF0000, ...]\n"+\
                         "or just \"black\" for single line\n"
                },
            "LineType" :
                {
                "value": ["-","--"],
                "help" : "Available linetype:\n"+\
                         "\"\":    no line\n"+\
                         "\"-\":    normal continuous line\n"+\
                         "\"--\":    dashed line\n"+\
                         "\".\":    dotted line\n"+\
                         "\"-.-\"    :dashed dotted dashed line\n"+\
                         "E.g.: [\"-\",\"--\"]for multiple line\n"+\
                         "Also accept custom line type defination in pdf format\n"+\
                         "e.g. [[10,20],0]\n"
                },
            "LineWidth" :
                {
                "value": 1.5,
                "help" : "In pt."
                },
            "xlimit" :
                {
                "value": [],
                "help" :"The plot range, [xmin, xmax] for x-axis.\n" +\
                        "Leave the List blank for Auto adjustment."
                },
            "ylimit" :
                {
                "value": [],
                "help" :"The plot range, [ymin, ymax] for y-axis.\n" +\
                        "Leave the List blank for Auto adjustment."
                },
            "x2limit":
                {
                "value":[],
                "help": "For the secondary axis"
                },
            "y2limit"   :
                {
                "value":[],
                "help": "For the secondary Axis"
                },
            "FillAreaUnderGraph" :
                {
                "value": False,
                "help": "Set true to fill"
                },
            "FillAreaColor" :
                {
                "value": ["red","blue"],
                "help": "Fill color"
                },
            "Point":
                {
                "Show"          :
                    {
                    "value": True,
                    "help": "Set true to draw points\n"+\
                            "Allow multiple entries for mutil-plot\n"+\
                            "e.g. [false, true] : show plot points only for the first plot."
                    },
                "Type":
                    {
                    "value": ["SolidCircle","SolidSquare","SolidTriangle"],
                    "help": "The type of the plot point."
                    },
                "Color":
                    {
                    "value":["red","blue","green"],
                    "help": "Verbal color or HTML color code"
                    },
                "AutoSize" :
                    {
                    "value": True,
                    "help": "True for auto."
                    },
                "SizeOverHeight":
                    {
                    "value":0.04,
                    "help":"Height_of_point/Height_of_plot."
                    },
                "Size":
                    {
                    "value":12,
                    "help":"This value will be used if AuotoSize is false"
                    },
                },
            "BarChart":
                {
                "Show":
                    {
                    "value":False,
                    "help":"Set true to show bar chart."
                    },
                "BarWidth":
                    {
                    "value":2,
                    "help": "Bar width in pt"
                    },
                "LineWidth" :
                    {
                    "value": 1,
                    "help": "Line width of the bar in pt"
                    },
                "LineColor" :
                    {
                    "value": "blue",
                    "help": "Line color of the bar"
                    },
                "Fill" :
                    {
                    "value": True,
                    "help": "Set True to fill"
                    },
                "FillColor" :
                    {
                    "value":"green",
                    "help": "Color name, color code, or color map name\n"+\
                            "Use color map if the name of a available colormap is entered"
                    },
                "ColorMapNormalization":
                    {
                    "value": "G",
                    "help": "\"L\":local  -> Normalized to each y value\n"+\
                            "\"G\":global -> Normalized to the y maximum."
                    },
                },
            "PlotBox":
                {
                "Show":
                    {
                    "value":False,
                    "help":"Set true to draw the plot space."
                    },
                "BoxColor"  :
                    {
                    "value":"gray",
                    "help": "Color fo the plot space"
                    },
                "LineWidth":
                    {
                    "value":1.0,
                    "help": "Line width of the border lines"
                    },
                "LineColor" :
                    {
                    "value":"black",
                    "help": "Line color of the border lines"
                    },
                "LineType":
                    {
                    "value":"-",
                    "help": "Line type"
                    },
                },
            "ErrorBar":
                {
                "Show":
                    {
                    "value":True,
                    "help":"Set true to draw error bar."
                    },
                "Color":
                    {
                    "value":"blue",
                    "help":"Color of the error bar"
                    },
                "LineWidth":
                    {
                    "value":1,
                    "help": "Line width of the error bar."
                    },
                "AutoLength":
                    {
                    "value":True,
                    "help": "Set true for auto adjusting the width length."
                    },
                "LengthOverWidth":
                    {
                    "value":0.04,
                    "help":"Length of the error bar/Plot width."
                    },
                "Length":
                    {
                    "value":10,
                    "help":"Use this value for manual."
                    },
                },
        },
    "xLabel":{
        "Text":
                {
                "value":"Time (min)",
                "help":"The label for x axis."
                },
        "Font":
                {
                "value":"Helvetica",
                "help":"The name of the font."
                },
        "OffsetX":
                {
                "value": 0,
                "help":"Positional offfset of the label x-direction. (Unit: pt)"
                },
        "OffsetY":
                {
                "value": 0,
                "help":"Positional offfset of the label y-direction. (Unit: pt)"
                },
        "AutoFontSize":
                {
                "value":True,
                "help":"Set true for auto."
                },
        "FontSizeOverHeight":
                {
                "value":0.06,
                "help":"Heigth_font/Height_plot."
                },
        "FontSize":
                {
                "value":14,
                "help":"This value will be used if AuotoFontSize is set false."
                },
        "FontColor":
                {
                "value":"blue",
                "help":""
                },
        },
    "yLabel":
        {
        "Text":
                {
                "value":"Signal",
                "help":"The label for y axis."
                },
        "Font"              :
                {
                "value":"Helvetica",
                "help":"The name of the font."
                },
        "OffsetX":
                {
                "value":0,
                "help":"Positional offfset of the label x-direction. (Unit: pt)"
                },
        "OffsetY"           :
                {
                "value":0,
                "help":"Positional offfset of the label y-direction. (Unit: pt)"
                },
        "AutoFontSize":
                {
                "value":True,
                "help":"Set true for auto."
                },
        "FontSizeOverHeight":
                {
                "value":0.06,
                "help":""
                },
        "FontSize":
                {
                "value":14,
                "help":"Heigth_font/Height_plot."
                },
        "FontColor":
                {
                "value":"blue",
                "help":""
                },
        },
    "Title":
        {
        "Show":
                {
                "value":True,
                "help":"Set true to show title"
                },
        "Text" :
                {
                "value":"Title",
                "help": "The text for the Title"
                },
        "Font" :
                {
                "value":"Helvetica",
                "help":""
                },
        "FontSize":
                {
                "value":14,
                "help":"This value will be used if AuotoFontSize is false."
                },
        "FontColor":
                {
                "value":"black",
                "help":""
                },
        "Alignment":
                {
                "value":"l",
                "help":"\"l\" for align to the left."
                },
        "Spacing":
                {
                "value":0,
                "help":" !? To be made sure later. "
                },
        "Yoffset":
                {
                "value": 0,
                "help":"Positional offset in pt in y-direction"
                },
        "Xoffset" :
                {
                "value":0,
                "help":"Positional offset in pt in x-direction"
                },
        "WidthRatio":
                {
                "value":0.8,
                "help":"To be made sure later."
                },
        "AutoFontSize":
                {
                "value":True,
                "help":""
                },
        "FontSizeOverHeight" :
                {
                "value":0.08,
                "help":""
                },
        },

    "Xaxis":
        {
        "Show":
                {
                "value":True,
                "help":"Set true to show"
                },
        "Log":
                {
                "value":False,
                "help":"Set true to use log scale for x-axis."
                },
        "LineWidth":
                {
                "value":1.5,
                "help":""
                },
        "LineColor":
                {
                "value":"black",
                "help":""
                },
        "LineType":
                {
                "value":"-",
                "help":""
                },
        "ShowTickText":
                {
                "value":True,
                "help": "Set true to show the value of the tick"
                },
        "Yposition":
                {
                "value":"",
                "help": "Y-position to put the Xaxis\n"+\
                        "Use the unit in your graph\n"+\
                        "Leave it \"\" for auto\n" +\
                        "E.g.: 12.5 for drawing X-axis at y=12.5",
                },
        "YoffsetInPt":
                {
                "value":0,
                "help":"Shift Xaxis vertically. Unit in pt"
                },
        "Tick" :
            {
            "Show":
                {
                "value":True,
                "help": "Set true to show"
                },
            "TickOut":
                {
                "value":True,
                "help":"Tick \'out\' if true, tick \'in\' if false"
                },
            "Length":
                {
                "value":3,
                "help": "Tick length in pt in the direction set by TickOut\n."+\
                        " If negative value, tick to the opposite direction set by TickOut"
                },
            "Width":
                {
                "value":1,
                "help":"Tick Line Width in pt"
                },
            "Color":
                {
                "value":"black",
                "help":"Tick line color"
                },
            "Font":
                {
                "value":"Helvetica",
                "help":"Font for the tick value"
                },
            "FontSize":
                {
                "value": 12,
                "help": "Font size of the tick value"
                },
            "FontColor":
                {
                "value":"black",
                "help":""
                },
            "AutoLength":
                {
                "value":True,
                "help":"Set true for auto"
                },
            "LengthOverHeight"  :
                {
                "value":0.03, #If negative, tick to the opposite direction
                "help":""
                },
            "AutoFontSize":
                {
                "value": True,
                "help":""
                },
            "FontSizeOverHeight":
                {
                "value": 0.05,
                "help":""
                },
            },
        "MinorTick":
            {
            "Show":
                {
                "value":True,
                "help":"Set true to show"
                },
            "TickNumber":
                {
                "value":5,
                "help":"The number of step from major tick to another."
                },
            "LineWidth":
                {
                "value": 0.5,
                "help": "Tick line width"
                },
            "LineColor":
                {
                "value":"black",
                "help":""
                },
            "LengthOverTickLength" :
                {
                "value":0.6,
                "help":"MinorTickLength/MajorTickLength."
                },
            },
        "Grid":
            {
            "Show":
                {
                "value": False,
                "help": "Set true to show."
                },
            "LineColor" :
                {
                "value":"blue",
                "help":""
                },
            "LineWidth" :
                {
                "value":0.25,
                "help":""
                },
            "LineType" :
                {
                "value":"-",
                "help":""
                },
            },
        "MinorGrid":
            {
            "Show" :
                {
                "value":False,
                "help":"Set true to display the grid for the minor tick."
                },
            "LineColor":
                {
                "value":"green",
                "help":""
                },
            "LineWidth" :
                {
                "value":0.1,
                "help":""
                },
            "LineType" :
                {
                "value":"-",
                "help":""
                },
            }
        },

    "Yaxis":
        {
        "Show":
                {
                "value":True,
                "help":"Set true to show"
                },
        "Log":
                {
                "value":False,
                "help":"Set true to use log scale for x-axis."
                },
        "LineWidth":
                {
                "value":1.5,
                "help":""
                },
        "LineColor":
                {
                "value":"black",
                "help":""
                },
        "LineType":
                {
                "value":"-",
                "help":""
                },
        "ShowTickText":
                {
                "value":True,
                "help": "Set true to show the value of the tick"
                },
        "Xposition":
                {
                "value":"",
                "help": "X-position to put the Yaxis\n"+\
                        "Use the unit in your graph\n"+\
                        "Leave it \"\" for auto\n" +\
                        "E.g.: 12.5 for drawing Y-axis at x=12.5",
                },
        "XoffsetInPt":
                {
                "value":0,
                "help":"Shift Yaxis vertically. Unit in pt"
                },
        "Tick" :
            {
            "Show":
                {
                "value":True,
                "help": "Set true to show"
                },
            "TickOut":
                {
                "value":True,
                "help":"Tick \'out\' if true, tick \'in\' if false"
                },
            "Length":
                {
                "value":3,
                "help": "Tick length in pt in the direction set by TickOut\n."+\
                        " If negative value, tick to the opposite direction set by TickOut"
                },
            "Width":
                {
                "value":1,
                "help":"Tick Line Width in pt"
                },
            "Color":
                {
                "value":"black",
                "help":"Tick line color"
                },
            "Font":
                {
                "value":"Helvetica",
                "help":"Font for the tick value"
                },
            "FontSize":
                {
                "value": 12,
                "help": "Font size of the tick value"
                },
            "FontColor":
                {
                "value":"black",
                "help":""
                },
            "AutoLength":
                {
                "value":True,
                "help":"Set true for auto"
                },
            "LengthOverHeight"  :
                {
                "value":0.03, #If negative, tick to the opposite direction
                "help":""
                },
            "AutoFontSize":
                {
                "value": True,
                "help":""
                },
            "FontSizeOverHeight":
                {
                "value": 0.05,
                "help":""
                },
            },
        "MinorTick":
            {
            "Show":
                {
                "value":True,
                "help":"Set true to show"
                },
            "TickNumber":
                {
                "value":5,
                "help":"The number of step from major tick to another."
                },
            "LineWidth":
                {
                "value": 0.5,
                "help": "Tick line width"
                },
            "LineColor":
                {
                "value":"black",
                "help":""
                },
            "LengthOverTickLength" :
                {
                "value":0.6,
                "help":"MinorTickLength/MajorTickLength."
                },
            },
        "Grid":
            {
            "Show":
                {
                "value": False,
                "help": "Set true to show."
                },
            "LineColor" :
                {
                "value":"blue",
                "help":""
                },
            "LineWidth" :
                {
                "value":0.25,
                "help":""
                },
            "LineType" :
                {
                "value":"-",
                "help":""
                },
            },
        "MinorGrid":
            {
            "Show" :
                {
                "value":False,
                "help":"Set true to display the grid for the minor tick."
                },
            "LineColor":
                {
                "value":"green",
                "help":""
                },
            "LineWidth" :
                {
                "value":0.1,
                "help":""
                },
            "LineType" :
                {
                "value":"-",
                "help":""
                },
            }
        },

    "y2Label"    :
                {
                "value":"Intensity2",
                "help":"Label for secondary y-axis"
                },

    "Plot2Color"    :
                {
                "value":["red"],
                "help":""
                },
    "Annotate" :
                {
                "value":[],
                "help":""
                },
    "AnnotateFont" :
                {
                "value":"Helvetica",
                "help":""
                },
    "AnnotateFontSize" :
                {
                "value":8,
                "help":""
                },
    "AnnotateFontColor" :
                {
                "value": "blue",
                "help":""
                },
    "AnnotateWidth" :
                {
                "value":100,
                "help":""
                },
    "AnnotateAlignment" :
                {
                "value":0,
                "help":""
                },
    "AnnotateSpacing" :
                {
                "value":1,
                "help":""
                },

    "Picture":
        {
        "InsertPicture"    :
                {
                "value":False,
                "help":"Set true to insert JPG picture in the background"
                },
        "PictureFilename" :
                {
                "value":["Example.jpg","PNG_example.png", "image1.jpg"],
                "help":"A valid filename or a list of filenames for the pictures"
                },
        "PictureSize":
                {
                "value":[[200,200],[100,100], [100,100]],
                "help":""
                },
        "PictureOrigin":
                {
                "value":[[0,100],[200,100],[300,100]],
                "help":""
                },
        "PictureCustom":
                {
                "value":True,
                "help":""
                },
        },

    "ShowDataOnly":
                {
                "value":False,
                "help":"Set true to draw curve only without axes"
                },

    "Debug":
        {
        "ShowErrorMessage":
                {
                "value":True,
                "help":"Not available yet."
                },
        "ShowPrint":
                {
                "value":True,
                "help":"Not available yet."
                },
        "VerbalEchoForMpretty":
                {
                "value":False,
                "help":"Not available yet."
                },
        "EchoThisContent":
                {
                "value":False,
                "help":"Not available yet."
                },
        },

    "ColorMap":
                {
                "value":"viridis",
                "help": "Available color map developed for\n"+\
                        "New matplotlib colormaps developed by\n"+\
                        "Nathaniel J. Smith, Stefan van der Walt\n"+\
                        "and (in the case of viridis) Eric Firing:\n"+\
                        "Available colormap so far:\n"+\
                        "magma, inferno, plasma, viridis, jet (made by me)\n",
                },

    "SecondaryAxis":
                {
                "value":False,
                "help":""
                },
    "LayoutSequence" :
                {
                "value":["Axes","AreaUnderGraph", "PlotLine", "BarChart","ErrorBar", "PlotPoint"],
                "help": "A list of layout sequence"
                },
    }

Theme_Multi_0={
    "PaperSize":[600,600],
    "Height":400,
    "Width":400,
    "RowColumn":[2,2],
    "AutoOrigin":True,
    "Origin":[50,50],
    "Origins":[[50,100],[200,100]],
    "AutoAdjust":True,
    #{}"HeightToWidthRatioThreshold":1
    "RowSpacing":60,    # in pt
    "ColumnSpacing":60,
    "SubPlotHeight":[100, 100],
    "SubPlotWidth": [100, 100],
    "PDF_Compression":True,
    "InsertPicture"            :False,
    "PictureFilename"        :["Example.jpg","PNG_example.png", "image1.jpg"],
    "PictureSize"        :[[200,200],[100,100], [100,100]],
    "PictureOrigin"            :[[0,100],[200,100],[300,100]],
    "UseJPEGForJPEGFile"    :False
    }
MultiPlotBasic={
    "PaperSize":[600,600],
    "Height":400,
    "Width":400,
    "RowColumn":[2,2],
    "AutoOrigin":True,
    "Origin":[50,50],
    "Origins":[[50,100],[200,100]],
    "AutoAdjust":True,
    #{}"HeightToWidthRatioThreshold":1
    "RowSpacing":60,    # in pt
    "ColumnSpacing":60,
    "SubPlotHeight":[100, 100],
    "SubPlotWidth": [100, 100],
    "PDF_Compression":True,
    "InsertPicture"            :False,
    "PictureFilename"        :["Example.jpg","PNG_example.png", "image1.jpg"],
    "PictureSize"        :[[200,200],[100,100], [100,100]],
    "PictureOrigin"            :[[0,100],[200,100],[300,100]],
    "UseJPEGForJPEGFile"    :False
    }
HelpMultiPlot={
    "PaperSize":        "# E.g: [600,600]\n",
    "Height":            "# E.g: 400\n",
    "Width":            "# E.g: 400\n",
    "RowColumn":        "# E.g: [2,2]\n",
    "AutoOrigin":        "# E.g: true\n",
    "Origin":            "# E.g: [50,50\n",
    "Origins":            "# E.g: [[50,100],[200,100]]\n",
    "AutoAdjust":        "# E.g: true\n",
    "RowSpacing":        "# E.g: 60  in pt\n",
    "ColumnSpacing":    "# E.g: 60\n",
    "SubPlotHeight":    "# E.g: [100, 100]\n",
    "SubPlotWidth":     "# E.g: [100, 100]\n",
    "PDF_Compression":     "# E.g: True\n",
    "InsertPicture":    "# E.g: False\n",
    "PictureFilename":    "# E.g:[\"Example.jpg\",\"PNG_example.png\", \"image1.jpg\"]\n",
    "PictureSize":        "# E.g.: [[200,200],[100,100], [100,100]]\n",
    "PictureOrigin"    :    "# E.g: [[0,100],[200,100],[300,100]]\n",
    "UseJPEGForJPEGFile": "# E.g: False\n"
}


def brew(what = "", filename = myglobal.DEFAULT_PLOTSTYLE_FILENAME):
    DetectPlatformThenSelectPDFViewer()
    cappuccino = Theme_0
    if what == "":
        pass
    elif what == "all":
        cappuccino = Kopio
        cappuccino["Xaxis"]["Grid"]["Show"]=True
        cappuccino["Yaxis"]["Grid"]["Show"]=True
        cappuccino["Xaxis"]["MinorGrid"]["Show"]=True
        cappuccino["Yaxis"]["MinorGrid"]["Show"]=True
    elif what == "journal":
        cappuccino = Journal

    createcson(filename, cappuccino, GreetOne)
    return

def HelpMessage(H):
    #if not isinstance(H, str):
    #    print("\a Here........")
    #    print (H)
    #    return "#" + mystr(H) + "\n"
    return H + "\n"

# D is the data dictionary
# H is the helper dictionary
def _createcson(filename, D, Welcome, H):
    S=""
    f = open(filename, 'w')
    S += Welcome
    #H = Help
    for x in D:
        if isinstance(D[x], dict):
            S += str(x) + ":\n"
            for y in D[x]:
                if isinstance(D[x][y], dict):
                    S += TAB+ str(y) + ":\n"
                    for z in D[x][y]:
                        S += TAB*2 +\
                             str(z) +\
                             ": " +\
                             mystr(D[x][y][z]) +\
                             "\n"
                        S += HelpMessage(H[x][y][z])
                else:
                    S += TAB + str(y) +\
                     ": " + mystr(D[x][y]) + "\n"
                    S += HelpMessage(H[x][y])
        else:
            S += str(x) + ": " + mystr(D[x]) + "\n"
            S += HelpMessage(H[x])

    f.write(S)
    print(filename, " created.")
    f.close()
def PrintCoffeeScript(TabNum, Key, Value):
    S = ""
    S += TabNum * TAB
    S += Key + COLON + mystr(Value) + EOL
    return S

def PrintCsComment(TabNum, Comment, Example):
    Comment = Comment.split(EOL)
    S = ""
    for x in Comment:
        S += TabNum * TAB + SHARP + SPACE
        S += x + EOL
    S += TabNum * TAB + SHARP + SPACE
    S += "Default => " + mystr(Example) + EOL
    S+= EOL
    return S

def createcson(filename, ThemeDic, Welcome):
    S=""
    f = open(filename, 'w')
    S += Welcome
    for x in ThemeDic:
        if ("value" in ThemeDic[x]) & ("help" in ThemeDic[x]):
            S += PrintCoffeeScript(0, x, ThemeDic[x]["value"])
            S += PrintCsComment(
                    0,
                    ThemeDic[x]["help"],
                    ThemeDic[x]["value"]
                    )
            continue
        S += x + COLON + EOL
        for y in ThemeDic[x]:
            if ("value" in ThemeDic[x][y]) &\
                    ("help" in ThemeDic[x][y]):
                S += PrintCoffeeScript(1, y, ThemeDic[x][y]["value"])
                S += PrintCsComment(
                        1,
                        ThemeDic[x][y]["help"],
                        ThemeDic[x][y]["value"]
                        )
                continue
            S += TAB + y + COLON + EOL

            for z in ThemeDic[x][y]:
                if ("value" in ThemeDic[x][y][z]) &\
                        ("help" in ThemeDic[x][y][z]):
                    S += PrintCoffeeScript(2, z, ThemeDic[x][y][z]["value"])
                    S += PrintCsComment(
                            2,
                            ThemeDic[x][y][z]["help"],
                            ThemeDic[x][y][z]["value"]
                            )
                    continue
                S += TAB*2 + z + COLON + EOL
    f.write(S)
    print(filename, " created.")
    f.close()
    return S


def DetectPlatformThenSelectPDFViewer():
    if platform.system() == "Darwin":
        Kopio["PDF"]["PDF_Viewer"] \
            = myglobal.DEFAULT_PDF_VIEWER_FOR_DARWIN

    elif platform.system() == "Linux":
        Kopio["PDF"]["PDF_Viewer"] \
            = myglobal.DEFAULT_PDF_VIEWER_FOR_LINUX

    elif platform.system() == "Window":
        Kopio["PDF"]["PDF_Viewer"] \
            = myglobal.DEFAULT_PDF_VIEWER_FOR_WINDOW
    else:
        print("Unknown platform.")
        print("You have to enter the PDF_Viewer by yourself.")
        Kopio["PDF"]["ShowPDF"] == False

def _make_cafe(coffeename):
    # coffeename is given by the user in Main()
    DetectPlatformThenSelectPDFViewer()
    createcson(coffeename, Kopio, GreetOne, HelpKopio)
    return
def make_cafe(coffeename):
    # coffeename is given by the user in Main()
    DetectPlatformThenSelectPDFViewer()
    createcson(coffeename, Theme_0, GreetOne)
    return
def make_latte(latte):
    createcson(latte, MultiPlotBasic, GreetMulti)
    return

#print("Test")
#print(createcson("a", Theme_0, ""))
