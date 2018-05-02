"""
    Main module to plot graph
"""
__all__ = ["plot", "image","polar","mplot", #from here
            "brew","addsugar","GetMasterCafe", #from brecson
            ]

import sys
import numpy as np
import math

# Yet complete:
# Allow the Axes Line to be drawn starting at the 0,0 origin
# Axis lines -> Done, but tick position -> not yet
#Problem:
#The display values not stable when dealt with large value like
# y x 10^21
from . import color
from . import dict2obj
from . import myglobal
from .brewcson import *
from .myfont import *
from .mypretty import *
#from . import pdf #I like to keep the pdf namespace
#from . import htmlcanvas as pdf
from .misc import *
from .myimage import *
from .mycson import *
# Try to add features to  Formated Text. e.g color, rotation , etc.

def _UpdateDict2WithDict1(Dict1, Dict2):
    for x in Dict1:
        if isinstance(Dict1[x], dict):
            for y in Dict1[x]:
                if isinstance(Dict1[x][y], dict):
                    for z in Dict1[x][y]:
                        Dict2[x][y][z] =\
                         Dict1[x][y][z]
                else:
                    Dict2[x][y] = Dict1[x][y]
        else:
            Dict2[x]=Dict1[x]
    return Dict2


def UpdateDict2WithDict1(Dict1, Dict2):
    for x in Dict1:
        if not isinstance(Dict1[x], dict):
            Dict2[x]=Dict1[x]
            continue

        for y in Dict1[x]:
            if not isinstance(Dict1[x][y], dict):
                Dict2[x][y] = Dict1[x][y]
                continue
            for z in Dict1[x][y]:
                Dict2[x][y][z] =\
                 Dict1[x][y][z]
    return Dict2


def loadtxt(Filename):
    #simple loadtxt to auto detect the skiprows
    #and return in X,Y
    def IsAllElementInListAreFloat(StringList):
        ans = True
        for s in StringList:
            try :
                float(s)
                #if ok, then do nothing
            except:
                ans = False
                return ans
        return ans
    def GetSkipRowsAndDelimiter(Filename):
        # Try to scan the first few lines to search for the start line
        # for valid data.
        # Assume the delimiter is "," or "    " or " "
        # PS. It does not scan the whole data !
        f = open(Filename,'r')
        n = 0
        while n<1000:
            try:
                s = f.readline()
                #print s.rstrip("\n")
                #replace "    " and " " with ",", then split the line
                SplitElement =  s.\
                    replace(",    ",",").\
                    replace(", ",",").\
                    replace('    ',",").\
                    replace("    ",",").\
                    replace("  ",",").\
                    replace(" ",",").\
                    rstrip("\n").\
                    split(",")
                if IsAllElementInListAreFloat(SplitElement):
                    break
                if s=="":
                    #if there is nothing, not even "\n", then break
                    n= -1
                    break
                n += 1
            except:
                print ("can not readline")
                return -1
        S=f.readline()
        Delimiter = ","    if "," in S else ""
        f.close()
        return n, Delimiter
    SkipRows,Delimiter = GetSkipRowsAndDelimiter(Filename)
    print("Number of Line to be skipped: ", SkipRows)
    print("Delimiter: ", [Delimiter])
    if Delimiter==",":
        Data = np.loadtxt(Filename, skiprows = SkipRows,
        delimiter = Delimiter)
    else:
        Data = np.loadtxt(Filename, skiprows = SkipRows)


    X=Data[:,0]
    Y=Data[:,1]
    return X,Y

def GenerateMinorTicks(MajorTick = [], TickNumber = 5, log = False):
    MinorTick = np.array([])
    if log == False:
        # e.g. For Major tick, [0, 1, 2]
        # generate
        # [0, 0.2, 0.4, 0.6, ...1, 1.2 ...2]
        spacing =  1.0*(MajorTick[1] - MajorTick[0])/TickNumber
        for i in range(len(MajorTick) -1):
            temp = MajorTick[i]
            for j in range(TickNumber):
                temp = temp + spacing
                MinorTick=np.append(MinorTick, temp)

    else:
        # e.g. For Major tick, [0.1, 1, 10, 100 ]
        # generate a list like this one for Log plot
        #[0.1, 0.2, 0.4, 0.6,0.8,1, 2, 4, 6, 8, 10, 20, 40 ...]
        spacing = (MajorTick[1]/MajorTick[0]) / TickNumber
        for i in range(len(MajorTick) -1):
            temp =    MajorTick[i]
            for j in range(TickNumber):
                if j ==1:
                    temp = spacing*MajorTick[i]
                if j > 1:
                    temp = temp + spacing*MajorTick[i]
                MinorTick=np.append(MinorTick, temp)

    return MinorTick

FontHeightRatio = 0.7
SuperScript_FontSizeReduction = 4
Superscript_YoffsetRatio = 0.8
Subscript_FontSizeReduction = 4
Subscript_YoffsetRatio = 0.5
FontSizeEnlargementStep = 2
KeepFontSize = True




def PDF_ObjForAllPages(OffsetNum, NumOfPage):
    S=""
    for i in range(NumOfPage):
        S+= str(OffsetNum + 2*i) + " 0 R "
    return S

# Make Multipages pdf.
# Each element in the GS stream vector is drawn in that
# particular page.
def MakeMultiplePDF(GraphicsStream, Compress=True):
    #{{{
    NumOfPage = len(GraphicsStream)
    if Compress==True:
        for i in range(NumOfPage):
            GraphicsStream[i]=gzip.compress(GraphicsStream[i])

    NumOfBasicObj = 21
    NumberOfPageObject = NumOfPage*2

    pdf_objects = []
    pdf_objects.append(
            "%PDF-1.4\n"+
            "% Created Manually\n"+
            "%%Creator: Lee Chuin CHEN\n" +
            "%% [leechuin@yamanashi.ac.jp, leechuin@gmail.com]\n" +
            "%%Title: Plot\n" +
            "%%CreationDate: "+ str(datetime.now()) + "\n"
            )

    pdf_objects.append(
            "1 0 obj\n"+
            "<</Type /Catalog\n" +
            "/Outlines 2 0 R\n" +
            "/Pages 3 0 R\n" +
            ">>\n" +
            "endobj\n"
            )

    pdf_objects.append(
            "2 0 obj\n" +
            "<</Type /Outlines\n" +
            "/Count 0\n" +
            ">>" +
            "endobj\n"
            )

    ObjOffsetNumber= 40

    pdf_objects.append(
            "3 0 obj\n" +
            "<</Type /Pages\n" +
            "/Kids ["+
            PDF_ObjForAllPages(ObjOffsetNumber, NumOfPage) +
            "]\n" +
            "/Count "+ str(NumOfPage) +"\n" +
            ">>\n" +
            "endobj\n"
            )
    pdf_objects.append(
            "4 0 obj\n"+
            "<<"+
            "/Producer (Univ. Yamanashi)" +
            ">>"+
            "endobj\n"
            )

    pdf_objects.append(
            "5 0 obj\n"+
            "<<"+
            "/Creater (LCCHEN))" +
            ">>"+
            "endobj\n"
            )

    pdf_objects.append(
            "6 0 obj\n" +
            "[/PDF /Text]\n"+
            "endobj\n"
            )

    pdf_objects.append(
            pdf.DefineFont(7, 0, fontname.Helvetica, "FH")
            )
    pdf_objects.append(
            pdf.DefineFont(8, 0, fontname.Helvetica_Bold, "FHB")
            )
    pdf_objects.append(
            pdf.DefineFont(9, 0, fontname.Helvetica_Oblique, "FHO")
            )
    pdf_objects.append(
            pdf.DefineFont(10, 0, fontname.Helvetica_BoldOblique, "FHBO")
            )
    pdf_objects.append(
            pdf.DefineFont(11, 0, fontname.Times_Roman, "FT")
            )
    pdf_objects.append(
            pdf.DefineFont(12, 0, fontname.Times_Italic, "FTI")
            )
    pdf_objects.append(
            pdf.DefineFont(13, 0, fontname.Times_Bold, "FTB")
            )
    pdf_objects.append(
            pdf.DefineFont(14, 0, fontname.Times_BoldItalic, "FTBI")
            )

    if PlotOnlyForAdobeIllustrator == True:
        pdf_objects.append(pdf.DefineFont(15,
                0,
                "SymbolMT",
                "FS") #For Illustrator, but can not open even with Adobe Reader
                )
    else:
        pdf_objects.append(
                pdf.DefineFont(15, 0, "Symbol", "FS") # Common
                )

    pdf_objects.append(
            pdf.DefineFont(16, 0, fontname.Symbol_ZapfDingbats, "FSZ")
            )
    pdf_objects.append(
            pdf.DefineFont(17, 0, fontname.Courier, "FC")
            )
    pdf_objects.append(
            pdf.DefineFont(18, 0, fontname.Courier_Bold, "FCB")
            )
    pdf_objects.append(
            pdf.DefineFont(19, 0, fontname.Courier_Oblique, "FCO")
            )
    pdf_objects.append(
            pdf.DefineFont(20, 0, fontname.Courier_BoldOblique, "FCBO")
            )

    for n in range(NumOfPage):
        pdf_objects.append(
            str(ObjOffsetNumber + 2*n) +
            " 0 obj\n" +
            "<</Type /Page\n" +
            "/Parent 3 0 R\n" +
            "/MediaBox [0 0 612 792]\n" +
            "/Contents " +
            str(ObjOffsetNumber + 2*n + 1) +
            " 0 R\n" +
            "/Resources<</ProcSet 6 0 R\n" +
            "/Font <<    /FH 7 0 R\n" +
            "        /FHB 8 0 R\n"+
            "        /FHO 9 0 R\n"+
            "        /FHBO 10 0 R\n"+
            "        /FT 11 0 R\n" +
            "        /FTI 12 0 R\n" +
            "        /FTB 13 0 R\n" +
            "        /FTBI 14 0 R\n" +
            "        /FS 15 0 R\n" +
            "        /FSZ 16 0 R\n" +
            "        /FC 17 0 R\n" +
            "        /FCB 18 0 R\n" +
            "        /FCO 19 0 R\n" +
            "        /FCBO 20 0 R\n" +
            ">>\n"+
            ">>\n"+
            ">>\n"+
            "endobj\n"
            )

        StreamObj= (
            str(ObjOffsetNumber + 2*n + 1) +
            " 0 obj\n" +
            "<< /Length %d "%len(GraphicsStream[n])
            )
        if Compress ==True:
            StreamObj +=  "/Filter /FlateDecode"

        StreamObj +=  (
            ">>\n"+
            "stream\n" +
            GraphicsStream[n] + "\n"+
            "endstream\n"+
            "endobj\n"
            )
        pdf_objects.append(StreamObj)


    NumOfPdfObj=NumOfBasicObj + 2*NumOfPage
    offset = [0]*(NumOfPdfObj)
    for i in range(1, NumOfPdfObj):
        offset[i] = offset[i-1] + len(pdf_objects[i-1])
    startxref = offset[NumOfPdfObj-1] + len(pdf_objects[NumOfPdfObj-1])

    Xref_0=""
    for i in range(1 , NumOfBasicObj):
        Xref_0 += Decimal_To_10_DigitsString(offset[i]) + " 00000 n\r\n"

    Xref_1=""
    for i in range(NumOfBasicObj, NumOfPdfObj):
        Xref_1 += Decimal_To_10_DigitsString(offset[i]) +\
                " 00000 n\r\n"

    pdf_xref = (
        "xref\n"+
        "0 "+ str(NumOfBasicObj) +" \r\n"+
        "0000000000 65535 f\r\n"+
        Xref_0 +
        str(ObjOffsetNumber) + " " + str(2*NumOfPage) + "\r\n"+
        Xref_1 +
        "trailer\n"+
        "<</Size 8\n"+
        "/Root 1 0 R\n"+
        ">>\n"+
        "startxref\n"+
        "%d"%(startxref) + "\n"
        "%%%EOF\n"
        )

    TargetFile = open(Cafe.PDF.PDF_Filename,"w")

    for X in pdf_objects:
        TargetFile.write(X)

    TargetFile.write(pdf_xref)
    TargetFile.close()
    os.system(Cafe.PDF.PDF_Viewer +" "+ Cafe.PDF.PDF_Filename)
    return#}}}

def GetMinMaxForXYarray(XList, YList):
    """GetMinMaxForXYarray(XList, YList):
    Return [xmin, xmax], [ymin, ymax]
    eg.    x = [ [1,2,3,6], [0,1,2] ]
        y = [ [-2, 2,3,4], [1, 2, 6]
    the return values are [0, 6], [-2, 6]
    """
    if isinstance(YList, list) != True:
        PrintError("Ydata is not a list")
        raise Exception("Ydata is not a valid list")
    if isinstance(XList, list) !=True:
        PrintError("Xdata is not a list like Ydata.!")
        raise Exception("Xdata is not a valid list")
    if len(XList) != len(YList):
        PrintError("The number of array for X and Y does not match !")
        raise Exception("Number of array does not match")
    Xmin = min(XList[0])
    Xmax = max(XList[0])
    Ymin = min(YList[0])
    Ymax = max(YList[0])
    for n in range(len(YList)):
        xa = XList[n]
        ya = YList[n]
        if len(ya) != len(xa) :
            PrintError("The Numbers of element in X and Y are not equal");
            raise Exception("Dimension for X and Y are not the same")
        if min(xa)< Xmin:
            Xmin = min(xa)
        if max(xa)> Xmax:
            Xmax = max(xa)
        if min(ya)< Ymin:
            Ymin = min(ya)
        if max(ya)> Ymax:
            Ymax = max(ya)
    return [Xmin, Xmax, Ymin, Ymax]


def load_Cafe_as_global(coffee, sugar):
    global Cafe
    global Origin
    global Width
    global Height

    try:
        with open(coffee, "r") as f:
            pass
    except:
        print("Can't find ", coffee, ".\n",
              "I will create one for you.\n")
        make_Cafe(coffee)

    # Load the existing cson file first.
    # It might be generated by previous version
    # If it were the old version, overlay its Contents
    # on the dictionary of the latest version
    UnknownVersionCson = loadcsonfile(coffee)
    #This is the latest format. May more content then the old one
    Cafe = UpdateDict2WithDict1(UnknownVersionCson,
                                GetMasterCafe()
                                )
    if len(sugar) !=0:
        Cafe = UpdateDict2WithDict1(sugar, Cafe)

    #from here, Cafe becomes Class Type from Dict
    Cafe = dict2obj.DictToObj(Cafe)

    if Cafe.Debug.EchoThisContent==True :
        PrintDictContent(a)
    Origin = Cafe.PlotRange.Origin
    Width = Cafe.PlotRange.Width
    Height = Cafe.PlotRange.Height

    global pdf
    if Cafe.PDF.UseHTMLCanvas:
        from . import htmlcanvas as pdf
    else:
        from . import pdf as pdf

    pdf.ResetPDF_FilenameNumber()
    pdf.Initialize(paperheight=Cafe.Paper.Size[1])
    return 0

def load_Latte_as_global(latte, milk):
    #{{{
    global Latte
    global OverallOrigin
    global OverallWidth
    global OverallHeight
    #try:

    try:
        check = open(latte,"r")
        check.close()
    except:
        print(    "Can't find multiplotstyle.cson file.\n",
                "I will create one for you.\n")
        make_Latte(latte)

    Latte=loadcsonfile(latte)
    UpdateDict2WithDict1(milk, Latte)

    #from here, Cafe becomes Class Type from Dict
    Latte= dict2obj.DictToObj(Latte)

    OverallOrigin = Latte["Origin"]
    OverallWidth = Latte["Width"]
    OverallHeight = Latte["Height"]
    return 0

    """Main function to create the pdf graphic script.
    Return valid graphic stream if successful, and -1 if not."""
def splot(DataXList, DataYList,
        SecondaryAxis = False,
        PlotAxesOnly = False,
        UpperError=[],
        LowerError=[]):

    global xmin
    global ymin
    global PS_ScalingFactor_Y
    global PS_ScalingFactor_X
    global YpositionForXaxis
    global XpositionForYaxis

    def pdf_DrawXtick():
        tickrgb = pdf.ToPSColor(Cafe.Xaxis.Tick.Color)
        textrgb = pdf.ToPSColor (Cafe.Xaxis.Tick.FontColor)
        XTickNumber = len(XTickArray_inPt)
        TextPosition_X = [0] * XTickNumber #create N elemetnts of 0

        TickDirection = 1.0 if Cafe.Xaxis.Tick.TickOut else -1.0

        CorrectionForTickLength  = TickDirection*\
                                Cafe.Xaxis.Tick.Length
        if CorrectionForTickLength < 0:
            CorrectionForTickLength = 0

        yTextPositionOffset = -1.0* (
                CorrectionForTickLength +\
                1.0 * Cafe.Xaxis.Tick.FontSize)

        TextPosition_Y = [ YpositionForXaxis +\
                         yTextPositionOffset ] * XTickNumber
        TickText = [""] * XTickNumber

        for n in range(XTickNumber):
            TickText[n] = ftos6( XTickArray[n] )
            TextPosition_X[n] = XTickArray_inPt[n]

        # The following correction is needed to draw the tick line
        # so that it will appear to connect to the Axes lines of finite
        # linewidth.
        # eg:    ==== Axis line
        #         |  | Tick
        correction = Cafe.Xaxis.LineWidth/2
        ReturnString =""
        ReturnString +=\
             pdf.DrawXTick(    [Origin[0], YpositionForXaxis + correction ],
                            XTickArray_inPt,
                            TickDirection *\
                            Cafe.Xaxis.Tick.Length + correction,
                            Cafe.Xaxis.Tick.Width,
                            tickrgb)
        if Cafe.Xaxis.ShowTickText==True:
            ReturnString += pdf.PutTextArray(
                TextPosition_X, TextPosition_Y,
                TickText, Cafe.Xaxis.Tick.Font,
                Cafe.Xaxis.Tick.FontSize,textrgb, 0, [0.5,0])

        return ReturnString

    def pdf_DrawMinorXtick():
        TickDirection = 1.0 if Cafe.Xaxis.Tick.TickOut else -1.0
        S =""
        S += pdf.DrawXTick(
                [    Origin[0],
                    YpositionForXaxis
                ],
                MinorXTickArray_inPt,
                TickDirection*\
                MinorTickLength,
                Cafe.Xaxis.MinorTick.LineWidth,
                pdf.ToPSColor(Cafe.Xaxis.MinorTick.LineColor))
        return S

    def pdf_DrawXgrid():
        gridlength = Height
        S =""
        S += pdf.DrawXTick(
                Origin,
                XTickArray_inPt,
                -1*gridlength,
                Cafe.Xaxis.Grid.LineWidth,
                pdf.ToPSColor(Cafe.Xaxis.Grid.LineColor),
                pdf.ToPSDash(Cafe.Xaxis.Grid.LineType))
        return S

    def pdf_DrawMinorXgrid():
        gridlength = Height
        S = pdf.DrawXTick(Origin, MinorXTickArray_inPt,
                -1*gridlength,
                Cafe.Xaxis.MinorGrid.LineWidth,
                pdf.ToPSColor(Cafe.Xaxis.MinorGrid.LineColor),
                pdf.ToPSDash(Cafe.Xaxis.MinorGrid.LineType))
        return S

    def pdf_DrawYtick():
        rgb = pdf.ToPSColor( Cafe.Yaxis.Tick.Color )
        textrgb = pdf.ToPSColor (Cafe.Yaxis.Tick.FontColor)
        YTickNumber = len(YTickArray_inPt)
        TextPosition_Y = [0] * YTickNumber
        TextPosition_X = [0] * YTickNumber
        TickText = [""] * YTickNumber

        TickDirection = 1.0 if\
             Cafe.Yaxis.Tick.TickOut else -1.0

        CorrectionForTickLength  = TickDirection*\
                                Cafe.Yaxis.Tick.Length
        if CorrectionForTickLength < 0:
            CorrectionForTickLength = 0

        for n in range(YTickNumber):
            TickText[n] = ftos6(YTickArray[n])
            xTextPositionOffset = -1.0*\
                    (Cafe.Yaxis.Tick.OffsetOfTextFromTickOverWidth*\
                    Cafe.PlotRange.Width +\
                    CorrectionForTickLength)
            TextPosition_X[n] = XpositionForYaxis + xTextPositionOffset
            yTextPositionOffset =\
                 (1.0- FontHeightRatio)*Cafe.Yaxis.Tick.FontSize
            TextPosition_Y[n] = (YTickArray_inPt[n] + yTextPositionOffset)
            if SecondaryAxis==True:
                xTextPositionOffset = 1.0* (2*Cafe.Yaxis.Tick.Length)
                TextPosition_X[n] = XpositionForYaxis + Width + xTextPositionOffset

        # The following correction is needed to draw the tick line
        # so that it will appear to connect to the Axes lines of finite
        # linewidth.
        # eg:
        #        Tick    -|
        #        Axis     |
        correction = Cafe.Yaxis.LineWidth/2

        S =""
        if SecondaryAxis==False:
            S += pdf.DrawYTick(
                [    XpositionForYaxis +correction, Origin[1]
                ],
                YTickArray_inPt,
                TickDirection*\
                (Cafe.Yaxis.Tick.Length + correction),
                Cafe.Yaxis.Tick.Width,
                rgb)
        else:
            S += pdf.DrawYTick(
                [    XpositionForYaxis + Width - correction,
                    Origin[1]
                    ],
                YTickArray_inPt,
                -1*TickDirection*\
                (Cafe.Yaxis.Tick.Length + correction),
                Cafe.Yaxis.Tick.Width,
                rgb)


        if(Cafe.Yaxis.ShowTickText==True):
            S += pdf.PutTextArray(TextPosition_X,
                                TextPosition_Y,
                                TickText,
                                Cafe.Yaxis.Tick.Font,
                                Cafe.Yaxis.Tick.FontSize,
                                textrgb,
                                0,
                                ([1, 0.5] #x:right justified
                                if SecondaryAxis==False else
                                [0, 0.5] #x:left justified
                                 ),
                                )
        return S

    def pdf_DrawMinorYtick():
        TickDirection = 1.0 if\
             Cafe.Yaxis.Tick.TickOut else -1.0
        rgb = pdf.ToPSColor( Cafe.Yaxis.MinorTick.LineColor )
        S = pdf.DrawYTick(
                [    XpositionForYaxis,
                    Origin[1]
                ],
                MinorYTickArray_inPt,
                TickDirection *\
                MinorTickLength,
                Cafe.Yaxis.MinorTick.LineWidth,
                rgb)
        return S

    def pdf_DrawMinorYgrid():
        gridlength = Width
        S =""
        S += pdf.DrawYTick(
                Origin,
                MinorYTickArray_inPt,
                -1*gridlength,
                Cafe.Yaxis.MinorGrid.LineWidth,
                pdf.ToPSColor(Cafe.Yaxis.MinorGrid.LineColor),
                pdf.ToPSDash(Cafe.Yaxis.MinorGrid.LineType))
        return S

    def pdf_DrawYgrid():
        gridlength = Width
        S =""
        S += pdf.DrawYTick(
                    Origin,
                    YTickArray_inPt,
                    -1*gridlength,
                    Cafe.Yaxis.Grid.LineWidth,
                    pdf.ToPSColor(Cafe.Yaxis.Grid.LineColor),
                    pdf.ToPSDash(Cafe.Yaxis.Grid.LineType))

        return S

    def pdf_PutYlabel():
        if SecondaryAxis ==True:
            Cafe.yLabel.Text = Cafe.y2Label

        S = ""
        LongestYValue=str(max(YTickArray))
        rgb=pdf.ToPSColor(Cafe.yLabel.FontColor)
        if SecondaryAxis == False:
            textposition_x = (
                XpositionForYaxis
                - Cafe.Yaxis.Tick.Length
                - GetStringWidth(LongestYValue,
                    Cafe.Yaxis.Tick.Font,
                    Cafe.Yaxis.Tick.FontSize)
                #- Cafe.yLabel.FontSize
                - Cafe.yLabel.OffsetX

                )
        #For Secondary Axis
        else:
            textposition_x = (
                    XpositionForYaxis +
                    Cafe.Yaxis.Tick.Length +
                    Width +

                    GetStringWidth(
                        LongestYValue,
                        Cafe.Yaxis.Tick.Font,
                        Cafe.Yaxis.Tick.FontSize) +
                    Cafe.yLabel.FontSize +
                    Cafe.yLabel.OffsetX
                    )
        textposition_y = (Origin[1] +
                            Height/2 +
                            Cafe.yLabel.OffsetY)

        S += pdf.PutText(textposition_x,
                            textposition_y,
                            Cafe.yLabel.Text,
                            Cafe.yLabel.Font,
                            Cafe.yLabel.FontSize,
                            rgb,
                            90, #rotation
                            [0.5,0]
                            )
        return S

    def pdf_PutXlabel():
        S = ""
        rgb=pdf.ToPSColor(Cafe.xLabel.FontColor)

        textposition_x = (    Origin[0]+
                            0.5*Width  +
                            1.0*Cafe.xLabel.OffsetX)

        TickDirection = 1.0 if Cafe.Xaxis.Tick.TickOut else -1.0

        CorrectionForTickLength  = TickDirection*\
                                Cafe.Xaxis.Tick.Length
        if CorrectionForTickLength < 0:
            CorrectionForTickLength = 0


        textposition_y = YpositionForXaxis -\
             1.0* (
                    CorrectionForTickLength+\
            1.0*Cafe.Xaxis.Tick.FontSize +\
            1.0*Cafe.xLabel.FontSize+\
            1.0*Cafe.xLabel.OffsetY)
        S += pdf.PutText(textposition_x,
                            textposition_y,
                            Cafe.xLabel.Text,
                            Cafe.xLabel.Font,
                            Cafe.xLabel.FontSize,
                            rgb,
                            0, [0.5,0])
        return S

    def pdf_PutTitle():
        S =""
        if Cafe.Title.Show:
            TitleLineNumber = len(BreakParagraphIntoLines(Cafe.Title.Text,
                                    TitleWidth,
                                    Cafe.Title.Font,
                                    Cafe.Title.FontSize))
            y = (    Origin[1] +
                Height +
                Cafe.Title.Yoffset*Height +
                Cafe.Title.FontSize*Cafe.Title.Spacing*\
                    (TitleLineNumber-1)
                )
            if (Cafe.Title.Alignment=="center") |\
                 (Cafe.Title.Alignment=="c"):
                pdf_TitleAlignment = 0.5
                x=Origin[0] + Width/2
            elif (Cafe.Title.Alignment=="right") |\
                     (Cafe.Title.Alignment=="r"):
                pdf_TitleAlignment = 1
                x = Origin[0] +Width - Cafe.Title.Xoffset*Width
            elif (Cafe.Title.Alignment=="left") |\
                     (Cafe.Title.Alignment=="l"):
                pdf_TitleAlignment = 0
                x = Origin[0] + Cafe.Title.Xoffset*Width
            else:
                pdf_TitleAlignment=0.5
                x=Origin[0] + Width/2
            S += pdf.Print(    Cafe.Title.Text,
                        x,
                        y,
                        TitleWidth,
                        Cafe.Title.Font,
                        Cafe.Title.FontSize,
                        pdf.ToPSColor(Cafe.Title.FontColor),
                        pdf_TitleAlignment,
                        Cafe.Title.Spacing)
        return S

    def pdf_Annotate():
        #{{{
        S =""
        for n in range(len(Annotate)):
            Peak = Annotate[n]
            MZ = Peak[0]
            Label = Peak[1]
            Id = np.where( (DataX - MZ)**2 < 0.001)
            PeakHeight = max( DataY[ Id[0] ] )

            x = (MZ - xmin) * PS_ScalingFactor_X +\
                    Origin[0] +\
                    FontHeightRatio*AnnotateFontSize/2

            y = (PeakHeight - ymin) * PS_ScalingFactor_Y +\
                    Origin[1] + AnnotateFontSize/2


            S += pdf.Print(    Label,
                            x,
                            y,
                            #AnnotateWidth,
                            20,
                            AnnotateFont,
                            AnnotateFontSize,
                            pdf.ToPSColor(AnnotateFontColor),
                            AnnotateAlignment,
                            AnnotateSpacing,
                            rotation = 90)
        return S#}}}

    def pdf_Draw2ndXtick():
        tickrgb = pdf.ToPSColor(Cafe.Xaxis.Tick.Color)
        textrgb = pdf.ToPSColor (Cafe.Xaxis.Tick.FontColor)
        XTickNumber = len(XTickArray_inPt)
        TextPosition_X = [0] * XTickNumber #create N elemetnts of 0

        TickDirection = 1.0 if Cafe.Xaxis.Tick.TickOut else -1.0

        CorrectionForTickLength  = TickDirection*\
                                Cafe.Xaxis.Tick.Length
        if CorrectionForTickLength < 0:
            CorrectionForTickLength = 0

        yTextPositionOffset = -1.0* (
                CorrectionForTickLength +\
                1.0 * Cafe.Xaxis.Tick.FontSize)

        TextPosition_Y = [ YpositionForXaxis +\
                         yTextPositionOffset ] * XTickNumber
        TickText = [""] * XTickNumber

        for n in range(XTickNumber):
            TickText[n] = ftos6( XTickArray[n] )
            TextPosition_X[n] = XTickArray_inPt[n]

        # The following correction is needed to draw the tick line
        # so that it will appear to connect to the Axes lines of finite
        # linewidth.
        # eg:    ==== Axis line
        #         |  | Tick
        correction = Cafe.Xaxis.LineWidth/2
        ReturnString =""
        ReturnString +=\
             pdf.DrawXTick(    [Origin[0], YpositionForXaxis + correction ],
                            XTickArray_inPt,
                            TickDirection *\
                            Cafe.Xaxis.Tick.Length + correction,
                            Cafe.Xaxis.Tick.Width,
                            tickrgb)
        if Cafe.Xaxis.ShowTickText==True:
            ReturnString += pdf.PutTextArray(
                TextPosition_X, TextPosition_Y,
                TickText, Cafe.Xaxis.Tick.Font,
                Cafe.Xaxis.Tick.FontSize,textrgb, 0, [0.5,0])

        return ReturnString

    def pdf_Draw2ndMinorXtick():
        TickDirection = 1.0 if Cafe.Xaxis.Tick.TickOut else -1.0
        S =""
        S += pdf.DrawXTick(
                [    Origin[0],
                    YpositionForXaxis
                ],
                MinorXTickArray_inPt,
                TickDirection*\
                MinorTickLength,
                Cafe.Xaxis.MinorTick.LineWidth,
                pdf.ToPSColor(Cafe.Xaxis.MinorTick.LineColor))
        return S

    def pdf_Draw2ndXgrid():
        gridlength = Height
        S =""
        S += pdf.DrawXTick(
                Origin,
                XTickArray_inPt,
                -1*gridlength,
                Cafe.Xaxis.Grid.LineWidth,
                pdf.ToPSColor(Cafe.Xaxis.Grid.LineColor),
                pdf.ToPSDash(Cafe.Xaxis.Grid.LineType))
        return S

    def pdf_Draw2ndMinorXgrid():
        gridlength = Height
        S = pdf.DrawXTick(Origin, MinorXTickArray_inPt,
                -1*gridlength,
                Cafe.Xaxis.MinorGrid.LineWidth,
                pdf.ToPSColor(Cafe.Xaxis.MinorGrid.LineColor),
                pdf.ToPSDash(Cafe.Xaxis.MinorGrid.LineType))
        return S

    def pdf_Draw2ndYtick():
        rgb = pdf.ToPSColor( Cafe.Yaxis.Tick.Color )
        textrgb = pdf.ToPSColor (Cafe.Yaxis.Tick.FontColor)
        YTickNumber = len(YTickArray_inPt)
        TextPosition_Y = [0] * YTickNumber
        TextPosition_X = [0] * YTickNumber
        TickText = [""] * YTickNumber

        TickDirection = 1.0 if\
             Cafe.Yaxis.Tick.TickOut else -1.0

        CorrectionForTickLength  = TickDirection*\
                                Cafe.Yaxis.Tick.Length
        if CorrectionForTickLength < 0:
            CorrectionForTickLength = 0

        for n in range(YTickNumber):
            TickText[n] = ftos6(YTickArray[n])
            xTextPositionOffset = -1.0*\
                    (Cafe.Yaxis.Tick.OffsetOfTextFromTickOverWidth*\
                    Cafe.PlotRange.Width +\
                    CorrectionForTickLength)
            TextPosition_X[n] = XpositionForYaxis + xTextPositionOffset
            yTextPositionOffset =\
                 (1.0- FontHeightRatio)*Cafe.Yaxis.Tick.FontSize
            TextPosition_Y[n] = (YTickArray_inPt[n] + yTextPositionOffset)
            if SecondaryAxis==True:
                xTextPositionOffset = 1.0* (2*Cafe.Yaxis.Tick.Length)
                TextPosition_X[n] = XpositionForYaxis + Width + xTextPositionOffset

        # The following correction is needed to draw the tick line
        # so that it will appear to connect to the Axes lines of finite
        # linewidth.
        # eg:
        #        Tick    -|
        #        Axis     |
        correction = Cafe.Yaxis.LineWidth/2

        S =""
        if SecondaryAxis==False:
            S += pdf.DrawYTick(
                [    XpositionForYaxis +correction, Origin[1]
                ],
                YTickArray_inPt,
                TickDirection*\
                (Cafe.Yaxis.Tick.Length + correction),
                Cafe.Yaxis.Tick.Width,
                rgb)
        else:
            S += pdf.DrawYTick(
                [    XpositionForYaxis + Width - correction,
                    Origin[1]
                    ],
                YTickArray_inPt,
                -1*TickDirection*\
                (Cafe.Yaxis.Tick.Length + correction),
                Cafe.Yaxis.Tick.Width,
                rgb)


        if(Cafe.Yaxis.ShowTickText==True):
            S += pdf.PutTextArray(TextPosition_X,
                                TextPosition_Y,
                                TickText,
                                Cafe.Yaxis.Tick.Font,
                                Cafe.Yaxis.Tick.FontSize,
                                textrgb,
                                0,
                                ([1, 0.5] #x:right justified
                                if SecondaryAxis==False else
                                [0, 0.5] #x:left justified
                                 ),
                                )
        return S

    def pdf_Draw2ndMinorYtick():
        TickDirection = 1.0 if\
             Cafe.Yaxis.Tick.TickOut else -1.0
        rgb = pdf.ToPSColor( Cafe.Yaxis.MinorTick.LineColor )
        S = pdf.DrawYTick(
                [    XpositionForYaxis,
                    Origin[1]
                ],
                MinorYTickArray_inPt,
                TickDirection *\
                MinorTickLength,
                Cafe.Yaxis.MinorTick.LineWidth,
                rgb)
        return S

    def pdf_Draw2ndMinorYgrid():
        gridlength = Width
        S =""
        S += pdf.DrawYTick(
                Origin,
                MinorYTickArray_inPt,
                -1*gridlength,
                Cafe.Yaxis.MinorGrid.LineWidth,
                pdf.ToPSColor(Cafe.Yaxis.MinorGrid.LineColor),
                pdf.ToPSDash(Cafe.Yaxis.MinorGrid.LineType))
        return S

    def pdf_Draw2ndYgrid():
        gridlength = Width
        S =""
        S += pdf.DrawYTick(
                    Origin,
                    YTickArray_inPt,
                    -1*gridlength,
                    Cafe.Yaxis.Grid.LineWidth,
                    pdf.ToPSColor(Cafe.Yaxis.Grid.LineColor),
                    pdf.ToPSDash(Cafe.Yaxis.Grid.LineType))

        return S

    def pdf_Put2ndYlabel():
        if SecondaryAxis ==True:
            Cafe.yLabel.Text = Cafe.y2Label

        S = ""
        LongestYValue=str(max(YTickArray))
        rgb=pdf.ToPSColor(Cafe.yLabel.FontColor)
        if SecondaryAxis == False:
            textposition_x = (
                XpositionForYaxis
                - Cafe.Yaxis.Tick.Length
                - GetStringWidth(LongestYValue,
                    Cafe.Yaxis.Tick.Font,
                    Cafe.Yaxis.Tick.FontSize)
                #- Cafe.yLabel.FontSize
                - Cafe.yLabel.OffsetX

                )
        #For Secondary Axis
        else:
            textposition_x = (
                    XpositionForYaxis +
                    Cafe.Yaxis.Tick.Length +
                    Width +

                    GetStringWidth(
                        LongestYValue,
                        Cafe.Yaxis.Tick.Font,
                        Cafe.Yaxis.Tick.FontSize) +
                    Cafe.yLabel.FontSize +
                    Cafe.yLabel.OffsetX
                    )
        textposition_y = (Origin[1] +
                            Height/2 +
                            Cafe.yLabel.OffsetY)

        S += pdf.PutText(textposition_x,
                            textposition_y,
                            Cafe.yLabel.Text,
                            Cafe.yLabel.Font,
                            Cafe.yLabel.FontSize,
                            rgb,
                            90, #rotation
                            [0.5,0]
                            )
        return S

    def pdf_Put2ndXlabel():
        S = ""
        rgb=pdf.ToPSColor(Cafe.xLabel.FontColor)

        textposition_x = (    Origin[0]+
                            0.5*Width  +
                            1.0*Cafe.xLabel.OffsetX)

        TickDirection = 1.0 if Cafe.Xaxis.Tick.TickOut else -1.0

        CorrectionForTickLength  = TickDirection*\
                                Cafe.Xaxis.Tick.Length
        if CorrectionForTickLength < 0:
            CorrectionForTickLength = 0


        textposition_y = YpositionForXaxis -\
             1.0* (
                    CorrectionForTickLength+\
            1.0*Cafe.Xaxis.Tick.FontSize +\
            1.0*Cafe.xLabel.FontSize+\
            1.0*Cafe.xLabel.OffsetY)
        S += pdf.PutText(textposition_x,
                            textposition_y,
                            Cafe.xLabel.Text,
                            Cafe.xLabel.Font,
                            Cafe.xLabel.FontSize,
                            rgb,
                            0, [0.5,0])
        return S

    def _pdf_DrawAxis(Axis):
        S=""
        if Axis ==1:
            #X axis
            S += pdf.DrawLines(
                    [    Origin[0],
                        Origin[0] + Width
                    ],
                    [    YpositionForXaxis,
                        YpositionForXaxis
                    ],
                    Cafe.Xaxis.LineWidth,
                    "miter",
                    pdf.ToPSColor(Cafe.Xaxis.LineColor),
                    pdf.ToPSDash(Cafe.Xaxis.LineType))

        elif Axis ==2:
            #Y axis
            S += pdf.DrawLines(
                    [   XpositionForYaxis,
                        XpositionForYaxis
                    ],
                    [    Origin[1],
                        Origin[1] + Height
                    ],
                    Cafe.Yaxis.LineWidth,
                    "miter",
                    pdf.ToPSColor(Cafe.Yaxis.LineColor),
                    pdf.ToPSDash(Cafe.Yaxis.LineType))

        if SecondaryAxis==True:
            S += pdf.DrawLines(
                [Origin[0]+Width,
                 Origin[0]+Width],
                [Origin[1],
                 Origin[1]+Height],
                Cafe.Yaxis.LineWidth,
                "miter",
                [0,0,0],
                [[],0]
                )

        return S

    def pdf_DrawXaxis():
        S=""
        S += pdf.DrawLines(
                [    Origin[0],
                    Origin[0] + Width
                ],
                [    YpositionForXaxis,
                    YpositionForXaxis
                ],
                Cafe.Xaxis.LineWidth,
                "miter",
                pdf.ToPSColor(Cafe.Xaxis.LineColor),
                pdf.ToPSDash(Cafe.Xaxis.LineType))
        return S

    def pdf_DrawYaxis():
        S=""
        S += pdf.DrawLines(
                [   XpositionForYaxis,
                    XpositionForYaxis
                ],
                [    Origin[1],
                    Origin[1] + Height
                ],
                Cafe.Yaxis.LineWidth,
                "miter",
                pdf.ToPSColor(Cafe.Yaxis.LineColor),
                pdf.ToPSDash(Cafe.Yaxis.LineType))
        return S

    def pdf_Draw2ndYaxis():
        S=""
        S += pdf.DrawLines(
            [Origin[0]+Width,
             Origin[0]+Width],
            [Origin[1],
             Origin[1]+Height],
            Cafe.Yaxis.LineWidth,
            "miter",
            [0,0,0],
            [[],0]
            )
        return S

    def pdf_PutErrorBar():
        if IsListOrArray(UpperError) and len(UpperError) == 0:
            return ""
        if IsListOrArray(LowerError) and len(LowerError) == 0:
            return ""


        #Check if Error contains list for multiplot
        if ThereIsListOrArrayWithinList( UpperError ):
            TheUpperError = UpperError[n]
            if not IsListOrArray(TheUpperError):
                TheUpperError = TheUpperError * np.ones(len(DataY))

        #if upper error and lower error are fixed value
        elif (     isinstance(UpperError,float) or
                isinstance(UpperError,int)
            ):
            TheUpperError = UpperError * np.ones(len(DataY))

        elif IsListOrArray(UpperError):
            TheUpperError = np.array(UpperError)
        else:
            print("[",n,"]"", ""Input Error for upper error bar !")
            return ""



        #Check if Error contains list for multiplot
        if ThereIsListOrArrayWithinList( LowerError ):
            TheLowerError = LowerError[n]
            if not IsListOrArray(TheLowerError):
                TheLowerError = TheLowerError * np.ones(len(DataY))

        #if upper error and lower error are fixed value
        elif ( isinstance(LowerError,float) or
                isinstance(LowerError,int)
            ):
            TheLowerError = LowerError * np.ones(len(DataY))
        elif IsListOrArray(LowerError):
            TheLowerError = np.array(LowerError)
        else:
            print("[",n,"]"", ""Input Error for Lower error bar !")
            return ""


        #Everthings look good :)
        UpperError_inPt = TheUpperError if Cafe.Yaxis.Log == False else\
                    np.log10(TheUpperError)

        #Just in case it is a List
        UpperError_inPt = np.array(UpperError_inPt)
        UpperError_inPt =    UpperError_inPt * PS_ScalingFactor_Y

        LowerError_inPt = TheLowerError if Cafe.Yaxis.Log == False else\
                        np.log10(TheLowerError)

        #Just in case it is a List
        LowerError_inPt = np.array(LowerError_inPt)

        LowerError_inPt = LowerError_inPt * PS_ScalingFactor_Y

        if Cafe.Plot.ErrorBar.AutoLength == True:
            ErrorLength = Cafe.Plot.ErrorBar.LengthOverWidth *Width
        else:
            ErrorLength = Cafe.Plot.ErrorBar.Length

        return pdf.PutErrorBar(
                    X_inPt,
                    Y_inPt,
                    UpperError_inPt,
                    LowerError_inPt,
                    ErrorLength,
                    pdf.ToPSColor(Drink(Cafe.Plot.ErrorBar.Color,n)),
                    Drink(Cafe.Plot.ErrorBar.LineWidth,n)
                    )

    def pdf_DrawBarChart(X, Y,
            barwidth = 1, barlinewidth = 1,
            rgb=[0,0,0], fill = False, fillrgb = [0,0,0]):
        S = ""
        for n in range(len(X)):
            S += pdf.DrawBox(
                        X[n] - barwidth/2,
                        Origin[1],
                        width    = barwidth,
                        height    = Y[n]-Origin[1],
                        linewidth    = barlinewidth,
                        linergb        = rgb,
                        dash        = [[],0],
                        fillbox        = fill,
                        fillrgb        = fillrgb
                        )
        return S

    # Non conventional bar chart
    # The bar is drawn from Y1 to Y2
    # It can be used to error box and
    # color mapped gradient filled bar chart
    # Beware: here X, Y1, Y2 are arrays
    def pdf_DrawDeferentialBarChart(X, Y1, Y2,
            barwidth = 1, barlinewidth = 1,
            rgb=[0,0,0], fill = False, fillrgb = [0,0,0]):
        S = ""
        for n in range(len(X)):
            S += pdf.DrawBox(
                        X[n] - barwidth/2,
                        Y1[n],
                        width    = barwidth,
                        height    = Y2[n]-Y1[n],
                        linewidth    = barlinewidth,
                        linergb        = rgb,
                        dash        = [[],0],
                        fillbox        = fill,
                        fillrgb        = fillrgb
                        )
        return S

    def pdf_DrawDeferentialBarChartWithColorArray(
            X, Y1, Y2,
            barwidth, barlinewidth,
            rgb, #array of color. Must match length of X, or Y
            fill,
            fillrgbarray):
        S = ""
        for n in range(len(X)):
            S += pdf.DrawBox(
                        X[n] - barwidth/2,
                        Y1[n],
                        width    = barwidth,
                        height    = Y2[n]-Y1[n],
                        linewidth    = barlinewidth,
                        linergb        = rgb[n],
                        dash        = [[],0],
                        fillbox        = fill,
                        fillrgb        = fillrgbarray[n]
                        )
        return S

    def xToPt(whatvalue):
        return (
                ((whatvalue-xmin) if Cafe.Xaxis.Log== False else
                    np.log10(whatvalue/xmin )
                        )* PS_ScalingFactor_X + Origin[0]
                )

    def yToPt(whatvalue):
        return (
                ((whatvalue-ymin) if Cafe.Yaxis.Log== False else
                    np.log10(whatvalue/ymin )
                        )* PS_ScalingFactor_Y + Origin[1]
                )


    def UpdatePropertiesForAutoResizing():
        #{{{
        if Cafe.Title.AutoFontSize == True:
            tfsoh = Cafe.Title.FontSizeOverHeight
            Cafe.Title.FontSize  = tfsoh * Cafe.PlotRange.Height
            Print("TitleFontSize : " + str(Cafe.Title.FontSize))

        global MinorTickLength
        if Cafe.Xaxis.Tick.AutoLength == True:
            h = 1.0 * Cafe.PlotRange.Height
            mtlotl = Cafe.Xaxis.MinorTick.LengthOverTickLength
            tloh = Cafe.Xaxis.Tick.LengthOverHeight
            MinorTickLength = h*mtlotl * tloh
        else:
            MinorTickLength =\
                 Cafe.Xaxis.MinorTick.LengthOverTickLength *\
                 Cafe.Xaxis.Tick.Length

        if Cafe.Yaxis.Tick.AutoLength == True:
            h = 1.0 * Cafe.PlotRange.Height
            mtlotl = Cafe.Yaxis.MinorTick.LengthOverTickLength
            tloh = Cafe.Yaxis.Tick.LengthOverHeight
            MinorTickLength = h*mtlotl * tloh
        else:
            MinorTickLength =\
             Cafe.Yaxis.MinorTick.LengthOverTickLength *\
              Cafe.Yaxis.Tick.Length

        if Cafe.Xaxis.Tick.AutoLength==True:
            tloh =  Cafe.Xaxis.Tick.LengthOverHeight
            Cafe.Xaxis.Tick.Length = tloh * Cafe.PlotRange.Height

        if Cafe.Yaxis.Tick.AutoLength==True:
            tloh =  Cafe.Yaxis.Tick.LengthOverHeight
            Cafe.Yaxis.Tick.Length = tloh * Cafe.PlotRange.Height

        if Cafe.Xaxis.Tick.AutoFontSize == True:
            tfsoh = Cafe.Xaxis.Tick.FontSizeOverHeight
            Cafe.Xaxis.Tick.FontSize = tfsoh * Cafe.PlotRange.Height
            Print("xTickFontSize : " + str(Cafe.Xaxis.Tick.FontSize) )

        if Cafe.Yaxis.Tick.AutoFontSize == True:
            tfsoh = Cafe.Yaxis.Tick.FontSizeOverHeight
            Cafe.Yaxis.Tick.FontSize = tfsoh * Cafe.PlotRange.Height
            Print("yTickFontSize : " + str(Cafe.Yaxis.Tick.FontSize) )

        if Cafe.xLabel.AutoFontSize == True:
            lfs = Cafe.xLabel.FontSizeOverHeight
            Cafe.xLabel.FontSize = lfs * Cafe.PlotRange.Height
            Print("xLabelFontSize : " + str(Cafe.xLabel.FontSize) )
        if Cafe.yLabel.AutoFontSize == True:
            lfs = Cafe.yLabel.FontSizeOverHeight
            Cafe.yLabel.FontSize = lfs * Cafe.PlotRange.Height
            Print("yLabelFontSize : " + str(Cafe.yLabel.FontSize) )

        return#}}}
        #}}}End of Local Fucntion

    def Lay_Axis():
        #Draw the frame, axes, tick etc
        if Cafe.ShowDataOnly:
            return ""
        GS=""
        if Cafe.Plot.PlotBox.Show:
            GS+= pdf.DrawBox(Origin[0],
                            Origin[1],
                            Width,
                            Height,
                            Cafe.Plot.PlotBox.LineWidth,
                            pdf.ToPSColor(Cafe.Plot.PlotBox.LineColor),
                            pdf.ToPSDash(Cafe.Plot.PlotBox.LineType),
                            True,
                            pdf.ToPSColor(Cafe.Plot.PlotBox.BoxColor)
                            )
        #Label
        if len(Cafe.xLabel.Text) != 0:
            GS +=     pdf_PutXlabel()
        if len(Cafe.yLabel.Text) != 0:
            GS +=     pdf_PutYlabel()

        #Minor Tick
        if Cafe.Xaxis.MinorTick.Show :
            GS +=     pdf_DrawMinorXtick()
        if Cafe.Yaxis.MinorTick.Show :
            GS +=     pdf_DrawMinorYtick()

        #Tick
        if Cafe.Xaxis.Tick.Show :
            GS +=     pdf_DrawXtick()
        if Cafe.Yaxis.Tick.Show :
            GS +=     pdf_DrawYtick()

        #Minor Grid
        if Cafe.Xaxis.MinorGrid.Show :
            GS +=     pdf_DrawMinorXgrid()
        if Cafe.Yaxis.MinorGrid.Show :
            GS +=     pdf_DrawMinorYgrid()

        #Grid
        if Cafe.Xaxis.Grid.Show :
            GS +=     pdf_DrawXgrid()
        if Cafe.Yaxis.Grid.Show :
            GS +=     pdf_DrawYgrid()

        if Cafe.Title.Show:
            GS +=     pdf_PutTitle()
        if len(Cafe.Annotate) !=0:
            GS +=    pdf_Annotate()

        #Axis Line
        if Cafe.Xaxis.Show :
            GS += pdf_DrawXaxis()
        if Cafe.Yaxis.Show :
            GS += pdf_DrawYaxis()

        return GS


    def Lay_2ndAxis():
        #Draw the frame, axes, tick etc
        if Cafe.ShowDataOnly:
            return ""
        GS=""

        #Label
        if len(Cafe.Second_xLabel.Text) != 0:
            GS +=     pdf_Put2ndXlabel()
        if len(Cafe.Second_yLabel.Text) != 0:
            GS +=     pdf_Put2ndYlabel()

        #Minor Tick
        if Cafe.Second_Xaxis.MinorTick.Show :
            GS +=     pdf_Draw2ndMinorXtick()
        if Cafe.Second_Yaxis.MinorTick.Show :
            GS +=     pdf_Draw2ndYaxisMinorYtick()

        #Tick
        if Cafe.Second_Xaxis.Tick.Show :
            GS +=     pdf_Draw2nd_Xtick()
        if Cafe.Second_Yaxis.Tick.Show :
            GS +=     pdf_Draw2nd_Ytick()

        #Minor Grid
        if Cafe.Second_Xaxis.MinorGrid.Show :
            GS +=     pdf_Draw2nd_MinorXgrid()
        if Cafe.Second_Yaxis.MinorGrid.Show :
            GS +=     pdf_Draw2nd_MinorYgrid()

        #Grid
        if Cafe.Second_Xaxis.Grid.Show :
            GS +=     pdf_Draw2nd_Xgrid()
        if Cafe.Second_Yaxis.Grid.Show :
            GS +=     pdf_Draw2nd_Ygrid()

        #Axis Line
        if Cafe.Second_Xaxis.Show :
            GS += pdf_DrawXaxis()
        if Cafe.Second_Yaxis.Show :
            GS += pdf_DrawYaxis()
        return GS


    def Lay_FillAreaUnderGragh(n):
        if Drink(Cafe.Plot.FillAreaUnderGraph, n):
            Xn = X_inPt[-1]
            X0 = X_inPt[0]
            Y0 = Y_inPt[0]
            if ymin > 0:
                Y00 = Origin[1]
            else:
                Y00 = (0 - ymin)*PS_ScalingFactor_Y + Origin[1]

            return pdf.DrawClosedLine(
                        np.append(X_inPt, [Xn, X0, X0]),
                        np.append(Y_inPt, [Y00, Y00, Y0]),
                        linewidth = 0,
                        linejoin = "round",
                        pdf_RGB = [0,0,0],
                        pdf_Dash=[[],0],
                        fill = True,
                        fillcolor = pdf.ToPSColor(
                                    Drink(Cafe.Plot.FillAreaColor,n)
                                    )
                        )
        return ""

    def Lay_PlotLine(n):
        if Drink(Cafe.Plot.LineType, n) != "":
            return  pdf.DrawLines(
                        X_inPt,
                        Y_inPt,
                        Drink(Cafe.Plot.LineWidth,n),
                        "round",
                        pdf.ToPSColor(Drink(Cafe.Plot.LineColor,n)),
                        pdf.ToPSDash(Drink(Cafe.Plot.LineType,n))
                    )
        else:
            return ""

    def Lay_SingleColorBarChart(n):
        return pdf_DrawBarChart(
                    X_inPt,
                    Y_inPt,
                    Drink(Cafe.Plot.BarChart.BarWidth,n),
                    Drink(Cafe.Plot.BarChart.LineWidth,n),
                    pdf.ToPSColor(
                        Drink(Cafe.Plot.BarChart.LineColor,n)
                        ),
                    Drink(Cafe.Plot.BarChart.Fill,n),
                    pdf.ToPSColor(
                        Drink(Cafe.Plot.BarChart.FillColor,n)
                        )
                    )

    def Lay_ColorMapBarChart_LocalNormalized(n):
        """
            color map is normalized to each Y  value
        """
        GS =""
        mapname=Cafe.Plot.BarChart.FillColor
        maplength = len(color.colormaps[mapname])
        dY_Pt = (Y_inPt - Origin[1])/maplength
        for m in range(maplength):
            Y1_inPt = Origin[1] + dY_Pt*m
            Y2_inPt = Y1_inPt + dY_Pt
            mapcolor = color.colormaps[mapname][m]
            GS += pdf_DrawDeferentialBarChart(
                X_inPt,
                Y1_inPt,
                Y2_inPt,
                Drink(Cafe.Plot.BarChart.BarWidth,n),
                myglobal.LINEWIDTH_FOR_COLORMAP,
                mapcolor,
                Drink(Cafe.Plot.BarChart.Fill,n),
                mapcolor
                )
        return GS

    def Lay_ColorMapBarChart_GlobalNormalized(n):
        """
            color map is normalized to each Y  value
        """
        GS =""
        mapname=Cafe.Plot.BarChart.FillColor
        maplength = len(color.colormaps[mapname])

        #Normalized to the global maximum
        #The max(Y) is used as reference, so here
        # dY_Pt is a single value, not array
        dY_Pt = (Y_inPt - Origin[1])/maplength
        Ymax = max(Y_inPt)
        for m in range(maplength):
            Y1_inPt = Origin[1] + dY_Pt*m
            Y2_inPt = Y1_inPt + dY_Pt
            colorindex = np.round((Y2_inPt-Origin[1])/(Ymax-Origin[1])*(maplength-1))
            mapcolor = np.array(color.colormaps[mapname])[colorindex.astype(int)]
            mapcolor = mapcolor.tolist()
            GS += pdf_DrawDeferentialBarChartWithColorArray(
                X_inPt,
                Y1_inPt,
                Y2_inPt,
                Drink(Cafe.Plot.BarChart.BarWidth,n),
                myglobal.LINEWIDTH_FOR_COLORMAP,
                mapcolor,
                Drink(Cafe.Plot.BarChart.Fill,n),
                mapcolor
                )
        return GS

    def Lay_BarChart(n):
        if Drink(Cafe.Plot.BarChart.Show,n):
            #See if the name hit the available colormap
            for availablecolormap in color.colormaps:
                if Drink(
                    Cafe.Plot.BarChart.FillColor,
                    n) == availablecolormap:
                    if Drink(
                        Cafe.Plot.BarChart.ColorMapNormalization,
                        n) == "L":
                        return Lay_ColorMapBarChart_LocalNormalized(n)
                    else:
                        return Lay_ColorMapBarChart_GlobalNormalized(n)
            #Nope:
            return Lay_SingleColorBarChart(n)
        else:
            return ""

    def Lay_ErrorBar(n):
        if Drink(Cafe.Plot.ErrorBar.Show,n) == True:
            return pdf_PutErrorBar()
        else:
            return ""

    def Lay_Point(n):
        if Drink(Cafe.Plot.Point.Show,n) == True:
            if Drink(Cafe.Plot.Point.AutoSize,n) == True:
                pointsize = Drink(Cafe.Plot.Point.SizeOverHeight,n) *\
                            Cafe.PlotRange.Height
            else:
                pointsize = Drink(Cafe.Plot.Point.Size,n)
            Print("pointsize : " + str(pointsize))
            return pdf.PutPoints (
                        X_inPt, Y_inPt,
                        Drink(Cafe.Plot.Point.Type,n),
                        pointsize,
                        pdf.ToPSColor(
                            Drink(Cafe.Plot.Point.Color,n))
                        )
        else:
            return ""



    #{{{main codes in splot
    # Check if the data ara lists. If not, turn them into lists
    if (isinstance(DataYList, list) == False) &\
        (isinstance(DataXList, list) == False):
        DataXList = [DataXList]
        DataYList = [DataYList]

    # the following assumes all data are list arrays
    [plotxmin, plotxmax, plotymin, plotymax] = GetMinMaxForXYarray(
                DataXList, DataYList)

    if SecondaryAxis==True:
        Cafe.Plot.LineColor = Cafe.Plot2Color
        Cafe.Plot.xlimit=Cafe.Plot.x2limit
        Cafe.Plot.ylimit=Cafe.Plot.y2limit
    if len(Cafe.Plot.xlimit) !=0:
        plotxmin = Cafe.Plot.xlimit[0]
        plotxmax = Cafe.Plot.xlimit[1]
    if len(Cafe.Plot.ylimit) !=0:
        plotymin = Cafe.Plot.ylimit[0]
        plotymax = Cafe.Plot.ylimit[1]

    NumberOfPlot = len(DataYList)
    TitleWidth = Cafe.Title.WidthRatio*Width

    UpdatePropertiesForAutoResizing()

    PrettyX= (mpretty([plotxmin, plotxmax],
                        VerbalEcho= Cafe.Debug.VerbalEchoForMpretty)
            if Cafe.Xaxis.Log==False else logpretty([plotxmin, plotxmax],
                        VerbalEcho= Cafe.Debug.VerbalEchoForMpretty)
            )
    PrettyY= (mpretty([plotymin, plotymax],
                        VerbalEcho= Cafe.Debug.VerbalEchoForMpretty)
            if Cafe.Yaxis.Log==False else logpretty([plotymin, plotymax],
                        VerbalEcho= Cafe.Debug.VerbalEchoForMpretty)
            )


    xmin = PrettyX[0]
    xmax =  PrettyX[len(PrettyX)-1]
    ymin = PrettyY[0]
    ymax = PrettyY[len(PrettyY)-1]

    PlotYRange = (    (ymax - ymin) if Cafe.Yaxis.Log==False else
                    np.log10(ymax/ymin)    )
    PlotXRange = (    (xmax - xmin) if Cafe.Xaxis.Log==False else
                    np.log10(xmax/xmin)    )

    PS_ScalingFactor_Y = 1.0* Height / PlotYRange
    PS_ScalingFactor_X = 1.0* Width / PlotXRange


    XTickArray = PrettyX
    YTickArray = PrettyY

    XTickArray_inPt = xToPt(PrettyX)
    YTickArray_inPt = yToPt(PrettyY)
    MinorYTickArray = GenerateMinorTicks(
            YTickArray,
            TickNumber = Cafe.Yaxis.MinorTick.TickNumber,
            log = Cafe.Yaxis.Log)

    MinorYTickArray_inPt =\
            (
                np.log10(MinorYTickArray/ymin)
                    if Cafe.Yaxis.Log else
                (MinorYTickArray - ymin)
            ) * PS_ScalingFactor_Y + Origin[1]

    MinorXTickArray = GenerateMinorTicks(
            XTickArray,
            TickNumber = Cafe.Xaxis.MinorTick.TickNumber,
            log = Cafe.Xaxis.Log)
    MinorXTickArray_inPt = (
            np.log10(MinorXTickArray/xmin) if Cafe.Xaxis.Log else
            (MinorXTickArray - xmin )
                            ) * PS_ScalingFactor_X + Origin[0]

    # Some customization for the Axies Position
    if isinstance(Cafe.Xaxis.Yposition, int) or\
        isinstance(Cafe.Xaxis.Yposition, float):
        YpositionForXaxis = yToPt(Cafe.Xaxis.Yposition)
    else:
        YpositionForXaxis = Origin[1]
    if isinstance(Cafe.Yaxis.Xposition, int) or\
        isinstance(Cafe.Yaxis.Xposition, float):
        XpositionForYaxis = xToPt(Cafe.Yaxis.Xposition)
    else:
        XpositionForYaxis = Origin[0]
    YpositionForXaxis += Cafe.Xaxis.YoffsetInPt
    XpositionForYaxis += Cafe.Yaxis.XoffsetInPt


    #Produce the important Graphic Stream
    GraphicsStream =""
    #GraphicsStream += Lay_Axis()

    #if PlotAxesOnly == True:
        #That 's all, good bye.
    #    return GraphicsStream

    for n in range(NumberOfPlot):
        DataX = DataXList[n]
        DataY = DataYList[n]

        # Just in case it is a List
        DataX = np.array(DataX)
        DataY = np.array(DataY)

        if len( Cafe.Plot.xlimit) !=0:
            Index = np.where((DataX > Cafe.Plot.xlimit[0]) &
                    (DataX < Cafe.Plot.xlimit[1]))
            DataX = DataX[Index[0]]
            DataY = DataY[Index[0]]

        X_inPt = (    (DataX-xmin) if Cafe.Xaxis.Log == False else
                    np.log10(DataX/xmin)
                    ) * PS_ScalingFactor_X + Origin[0]

        Y_inPt = (    (DataY-ymin) if Cafe.Yaxis.Log == False else
                    np.log10(DataY/ymin)
                    ) * PS_ScalingFactor_Y + Origin[1]


        for Lay in Cafe.LayoutSequence:
            if Lay == "AreaUnderGraph":
                GraphicsStream += Lay_FillAreaUnderGragh(n)
            if Lay == "Axes":
                #Only need to lay one time.
                if n == (NumberOfPlot-1):
                    GraphicsStream += Lay_Axis()
            elif Lay == "PlotLine":
                GraphicsStream += Lay_PlotLine(n)
            elif Lay == "BarChart":
                GraphicsStream += Lay_BarChart(n)
            elif Lay == "ErrorBar":
                GraphicsStream += Lay_ErrorBar(n)
            elif Lay == "PlotPoint":
                GraphicsStream += Lay_Point(n)
            else:
                GraphicsStream += ""

    return GraphicsStream#}}}

# Plot one graph in one page
def plot(X, Y, sugar={}, coffee=myglobal.DEFAULT_PLOTSTYLE_FILENAME,
    X2=[], Y2=[], uppererror = [], lowererror=[], output =""):

    #Check input format for X and Y
    if isinstance(X, np.ndarray):
        pass
    else:
        if isinstance(X, list):
            if isinstance(X[0], int) | isinstance(X[0], float):
                X = np.array(X)
            else:
                for x in X:
                    if not isinstance(x,np.ndarray):
                        x = np.array(x)
        else:
            print("Input Error")
            return -1
    if isinstance(Y, np.ndarray):
        pass
    else:
        if isinstance(Y, list):
            if isinstance(Y[0], int) | isinstance(Y[0], float):
                Y = np.array(Y)
            else:
                for y in Y:
                    if not isinstance(y,np.ndarray):
                        y = np.array(y)
        else:
            print("Input Error")
            return -1




    if load_Cafe_as_global(coffee, sugar)==-1:
        return -1
    if Cafe.PlotRange.AutoOrigin == True:
        Cafe.PlotRange.Origin[0] =\
             1.0*(Cafe.Paper.Size[0] - Cafe.PlotRange.Width)/2
        Cafe.PlotRange.Origin[1] =\
             1.0*(Cafe.Paper.Size[1] - Cafe.PlotRange.Height)/2
    S=""
    if Cafe.Paper.Color !="":
        papersizestring  = GetPaperSize(Cafe.Paper.Size)
        paperwidth = int(papersizestring.split(" ")[0])
        paperheight = int(papersizestring.split(" ")[1])

        S+=    pdf.DrawBox(0,0,
                width=paperwidth,
                height=paperheight,
                linewidth=0,
                linergb=[0,0,0],
                dash=[[],0],
                fillbox=True,
                fillrgb = pdf.ToPSColor(Cafe.Paper.Color)
                )
    if Cafe.Picture.InsertPicture == True:
        S += pdf.InsertPicture(
                Cafe.Picture.PictureOrigin,
                Cafe.Picture.PictureSize
                )
    S += splot(X, Y,SecondaryAxis=False, UpperError=uppererror,LowerError=lowererror)
    if Cafe.SecondaryAxis==True:
        S += splot(X2,Y2, SecondaryAxis=True,UpperError=uppererror,LowerError=lowererror)
    if S == -1:
        PrintError("Make no pdf")
        return -1
    else:
        if output != "":
            Cafe.PDF.PDF_Filename=output
        pdf.makepdf(S,
            Cafe.PDF.PDF_Compression,
            Cafe.Picture.InsertPicture,
            Cafe.Picture.PictureFilename,
            Cafe.PDF.UseJPEGForJPEGFile,
            PaperSize=Cafe.Paper.Size,
            Unit=Cafe.Paper.Unit,
            PaperColor=Cafe.Paper.Color,
            ShowPDF=Cafe.PDF.ShowPDF,
            PDF_Viewer=Cafe.PDF.PDF_Viewer,
            PDF_Filename=Cafe.PDF.PDF_Filename)
    return 0



# Plot multiple graph in one page
def mplot(DataSet=[],
            sugar={},
            milk={},
            coffees = myglobal.DEFAULT_PLOTSTYLE_FILENAME,
            latte = myglobal.DEFAULT_MULTI_PLOTSTYLE_FILENAME,
            uppererror = [], lowererror=[]):
    if load_Latte_as_global(latte, milk):
        return -1

    S=""
    if Latte["InsertPicture"] == True:
        S += pdf.InsertPicture(
                Latte["PictureOrigin"],
                Latte["PictureSize"]
                )

    if Latte["AutoOrigin"]:
        Latte["Origin"][0] = 1.0*(Latte["PaperSize"][0] - Latte["Width"])/2
        Latte["Origin"][1] = 1.0*(Latte["PaperSize"][1] - Latte["Height"])/2


    NumberOfMultiPlot = len(DataSet)
    if Latte["AutoAdjust"]:
        NumOfRow =  Latte["RowColumn"][0]
        NumOfColumn = Latte["RowColumn"][1]

        Latte["SubPlotWidth"] = 1.0*(Latte["Width"]-
                                (NumOfColumn-1)*Latte["ColumnSpacing"]
                                )/NumOfColumn
        Latte["SubPlotHeight"] = 1.0*(Latte["Height"]-
                            (NumOfRow-1)*Latte["RowSpacing"]
                            )/NumOfRow


        Latte["Origins"] = []
        for row in range(NumOfRow):
            for col in range(NumOfColumn):
                originx = Latte["Origin"][0] +\
                            col*(
                            Latte["ColumnSpacing"] +
                            Latte["SubPlotWidth"])

                originy = Latte["Origin"][1] + Latte["Height"] -\
                            Latte["SubPlotHeight"] -\
                            row*(
                            Latte["RowSpacing"] +
                            Latte["SubPlotHeight"]
                            )
                Latte["Origins"]+= [ [originx, originy] ]
    for n in range(NumberOfMultiPlot):
        coffee = Drink(coffees, n)

        if load_Cafe_as_global(coffee, sugar)==-1:
            return -1

        Cafe.PlotRange.Origin = Latte["Origins"][n]
        global Origin
        global Height
        global Width
        Origin = Cafe.PlotRange.Origin
        Height = Drink(Latte["SubPlotHeight"],n)
        Width = Drink(Latte["SubPlotWidth"],n)

        S+= splot(    DataSet[n][0],
                    DataSet[n][1],UpperError=uppererror,LowerError=lowererror)

    # Mutliplot settings overwrite
    # the settings for single plot
    Cafe.Paper.Size = Latte["PaperSize"]
    pdf.makepdf(S, Latte["PDF_Compression"],
            Latte["InsertPicture"],
            Latte["PictureFilename"],
            Latte["UseJPEGForJPEGFile"],
            PaperSize=Cafe.Paper.Size,
            Unit=Cafe.Paper.Unit,
            PaperColor=Cafe.Paper.Color,
            ShowPDF=Cafe.PDF.ShowPDF,
            PDF_Viewer=Cafe.PDF.PDF_Viewer,
            PDF_Filename=Cafe.PDF.PDF_Filename)
    return

def polar(theta, radius, sugar={}, coffee=myglobal.DEFAULT_PLOTSTYLE_FILENAME):
    if load_Cafe_as_global(coffee, sugar)== -1:
        return -1

    SecondaryAxis = False
    N = len(theta)
    if len(radius) != N:
        Print("Data Size error")
        return -1

    if isinstance (theta, list) == True:
        NumberOfDataSet = len(theta)
        x = [0] * NumberOfDataSet
        y = [0] * NumberOfDataSet

        for n in range(NumberOfDataSet):
            x[n] = abs(radius[n]) * np.cos(theta[n])
            y[n] = abs(radius[n]) * np.sin(theta[n])
    else:
        x = abs(radius) * np.cos(theta)
        y = abs(radius) * np.sin(theta)

    GraphicsStream = ""
    GraphicsStream += splot(x,y,SecondaryAxis)
    pdf.makepdf(GraphicsStream,
            Cafe.PDF.PDF_Compression,
            Cafe.Picture.InsertPicture,
            Cafe.Picture.PictureFilename,
            Cafe.PDF.UseJPEGForJPEGFile,
            PaperSize=Cafe.Paper.Size,
            Unit=Cafe.Paper.Unit,
            PaperColor=Cafe.Paper.Color,
            ShowPDF=Cafe.PDF.ShowPDF,
            PDF_Viewer=Cafe.PDF.PDF_Viewer,
            PDF_Filename=Cafe.PDF.PDF_Filename
            )

def image(Mat = np.matrix([]), Xrange =[], Yrange=[],
        sugar={}, coffee=myglobal.DEFAULT_PLOTSTYLE_FILENAME):
    if load_Cafe_as_global(coffee, sugar)== -1:
        return -1

    S =""
    if Cafe.Picture.InsertPicture == True:
        S += pdf.InsertPicture(
                    Cafe.Picture.PictureOrigin,
                    Cafe.Picture.PictureSize
                    )

    Cafe.Plot.PlotBox.Show=False
    #Set it false, or the PlotBox will Over

    S += pdf.InsertDataImage(
            Cafe.PlotRange.Origin,
            [Cafe.PlotRange.Width,Cafe.PlotRange.Height]
            )

    if len(Mat) == 0:
        return -1
    if isinstance(Mat, np.matrix) == False:
        print ("Data should be in the form of numpy matrix")
        return -1

    cm = color.colormaps[ Cafe.ColorMap ]
    Max = Mat.max()
    Min = Mat.min()
    Delta = Max -Min
    [Row,Col] = Mat.shape

    Data = [[0,0,0]]*(Col*Row)
    for c in range(Col):
        for r in range(Row):
            n = Col*r + c
            j = (Mat[r,c] - Min)/Delta * (len(cm) -1)
            j = int(round(j))
            Data[n] = [    cm[j][0]*128,
                        cm[j][1]*128,
                        cm[j][2]*128
                        ]
    #print(Data)
    if not isinstance(Xrange, np.ndarray):
        Xrange = np.array(Xrange)
    if not isinstance(Yrange, np.ndarray):
        Yrange = np.array(Yrange)

    S += splot(Xrange, Yrange, PlotAxesOnly=True)

    pdf.makepdf(S,
            Cafe.PDF.PDF_Compression,
            Cafe.Picture.InsertPicture,
            Cafe.Picture.PictureFilename,
            Cafe.PDF.UseJPEGForJPEGFile,
            Data,
            Col, Row,
            PaperSize=Cafe.Paper.Size,
            Unit=Cafe.Paper.Unit,
            PaperColor=Cafe.Paper.Color,
            ShowPDF=Cafe.PDF.ShowPDF,
            PDF_Viewer=Cafe.PDF.PDF_Viewer,
            PDF_Filename=Cafe.PDF.PDF_Filename)

def table(colnum = 4, rownum =4, prop ={}, propfile = myglobal.DEFAULT_PLOTSTYLE_FILENAME):
    try:
        global a
        JF=open(propfile,"r")
        Cafe = json.loads(
                RemoveJsonComment(JF.read())
                )
    except Exception as e:
        PrintFatalError("Exception in loading json")
        print (e)
        JF.close() #redundent ?
        return -1
    finally:
        JF.close()


    origin = [100,100]
    TableHeight = 200
    TableWidth = 200
    height = TableHeight/rownum
    width = TableWidth/colnum
    S = ""
    S+= pdf.Draw_Rounded_Box(200,200, 100,100,40)
    makepdf(S)
    return

#{{{Acknowledment that shall be executed when imported
#    print ("-----------------------")
#    print ("Kopi 2017     <lcchen>")
#    print ("-----------------------")
#table()

#}}}
