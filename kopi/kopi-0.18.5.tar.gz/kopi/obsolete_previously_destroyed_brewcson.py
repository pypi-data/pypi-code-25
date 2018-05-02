__all__ = ["make_Cafe", "make_Latte", "brew", "Theme_0", "MakeMasterTheme"]
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

"""
    Master Copy of the default Theme
    The dictionary contains the value and the
    help for each property.

    This dict is used to create the default cson file.

    In its present form, it can not be used directly
    in the Main module, but needs
    to be converted using MakeMasterTheme function
    in this module.
"""
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
            "OffsetOfTextFromTickOverWidth" :
                {
                "value": 0.01,
                "help" : "For the adjustment of the tick value text"
                }
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
    "PaperSize":
        {
        "value":[600,600],
        "help":""
        },
    "Height":
        {
        "value":400,
        "help":""
        },
    "Width":
        {
        "value":400,
        "help":""
        },
    "RowColumn":
        {
        "value":[2,2],
        "help":""
        },
    "AutoOrigin":
        {
        "value":True,
        "help":""
        },
    "Origin":
        {
        "value":[50,50],
        "help":""
        },
    "Origins":
        {
        "value":[[50,100],[200,100]],
        "help":""
        },
    "AutoAdjust":
        {
        "value":True,
        "help":""
        },
    "RowSpacing":
        {
        "value":60,    # in pt
        "help":""
        },
    "ColumnSpacing":
        {
        "value":60,
        "help":""
        },
    "SubPlotHeight":
        {
        "value":[100, 100],
        "help":""
        },
    "SubPlotWidth":
        {
        "value":[100, 100],
        "help":""
        },
    "PDF_Compression":
        {
        "value":True,
        "help":""
        },
    "InsertPicture":
        {
        "value":False,
        "help":""
        },
    "PictureFilename":
        {
        "value":["Example.jpg","PNG_example.png", "image1.jpg"],
        "help":""
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
    "UseJPEGForJPEGFile":
        {
        "value":False,
        "help":""
        }
    }


"""
Convert the The dictionary that contains "value" and "help"
key to standard dictionary.
e.g. You = {"happy":{"value": True,
                "help": "Set True if happy, False if not"
                }
            }
    MakeMasterTheme(You) = {"happy":True}

Create a Master Theme Dictionary
from Theme_0
This Master copy can be used to open
the cson file created by previous version
"""
def MakeMasterTheme(D):

    S = {}
    for x in D:
        if ("value" in D[x]) & ("help" in D[x]):
            S.update({x:D[x]["value"]})
            continue
        S.update({x:{}})

        for y in D[x]:
            if ("value" in D[x][y]) &\
                    ("help" in D[x][y]):
                S[x].update({y:D[x][y]["value"]})
                continue
            S[x].update({y:{}})

            for z in D[x][y]:
                if ("value" in D[x][y][z]) &\
                        ("help" in D[x][y][z]):
                    S[x][y].update({z:D[x][y][z]["value"]})
                    continue
                S[x][y].update({z:{}})
    return S


def brew(what = "", filename = myglobal.DEFAULT_PLOTSTYLE_FILENAME):
    DetectPlatformThenSelectPDFViewer()
    cappuccino = Theme_0
    if what == "":
        pass
    elif what == "all":
        cappuccino = MakeMasterTheme(Theme_0)
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
        Theme_0["PDF"]["PDF_Viewer"]["value"] \
            = myglobal.DEFAULT_PDF_VIEWER_FOR_DARWIN

    elif platform.system() == "Linux":
        Theme_0["PDF"]["PDF_Viewer"]["value"] \
            = myglobal.DEFAULT_PDF_VIEWER_FOR_LINUX

    elif platform.system() == "Window":
        Theme_0["PDF"]["PDF_Viewer"]["value"] \
            = myglobal.DEFAULT_PDF_VIEWER_FOR_WINDOW
    else:
        print("Unknown platform.")
        print("You have to enter the PDF_Viewer by yourself.")
        Theme_0["PDF"]["ShowPDF"]["value"] == False
def make_Cafe(coffeename):
    # coffeename is given by the user in Main()
    DetectPlatformThenSelectPDFViewer()
    createcson(coffeename, Theme_0, GreetOne)
    return
def make_Latte(latte):
    createcson(latte, Theme_Multi_0, GreetMulti)
    return

#print("Test")
#print(createcson("killa.cson", Theme_Multi_0, GreetMulti))
#print(MakeMasterTheme(Theme_Multi_0))
