class Sugar:
    class PDF:
        PDF_Filename = None
        ShowPDF = None
        PDF_Viewer = None
        PDF_Compression = None
        UseJPEGForJPEGFile = None
        UseHTMLCanvas = None
    class Paper:
        Portrait = None
        Size = None
        Unit = None
        Color = None
    class PlotRange:
        Width = None
        Height = None
        Unit = None
        AutoOrigin = None
        Origin = None
    class Plot:
        LineColor = None
        LineType = None
        LineWidth = None
        xlimit = None
        ylimit = None
        FillAreaUnderGraph = None
        FillAreaColor = None
        class Point:
            Show = None
            Type = None
            Color = None
            AutoSize = None
            SizeOverHeight = None
            Size = None
        class BarChart:
            Show = None
            BarWidth = None
            LineWidth = None
            LineColor = None
            Fill = None
            FillColor = None
            ColorMapNormalization = None
        class PlotBox:
            Show = None
            BoxColor = None
            LineWidth = None
            LineColor = None
            LineType = None
        class ErrorBar:
            Show = None
            Color = None
            LineWidth = None
            AutoLength = None
            LengthOverWidth = None
            Length = None
    class Title:
        Show = None
        Text = None
        Font = None
        FontSize = None
        FontColor = None
        Alignment = None
        Spacing = None
        Yoffset = None
        Xoffset = None
        WidthRatio = None
        AutoFontSize = None
        FontSizeOverHeight = None
    class xLabel:
        Text = None
        Font = None
        OffsetX = None
        OffsetY = None
        AutoFontSize = None
        FontSizeOverHeight = None
        FontSize = None
        FontColor = None
    class yLabel:
        Text = None
        Font = None
        OffsetX = None
        OffsetY = None
        AutoFontSize = None
        FontSizeOverHeight = None
        FontSize = None
        FontColor = None
    class Xaxis:
        Show = None
        Log = None
        LineWidth = None
        LineColor = None
        LineType = None
        ShowTickText = None
        Yposition = None
        YoffsetInPt = None
        class Tick:
            Show = None
            TickOut = None
            Length = None
            Width = None
            Color = None
            Font = None
            FontSize = None
            FontColor = None
            AutoLength = None
            LengthOverHeight = None
            AutoFontSize = None
            FontSizeOverHeight = None
        class MinorTick:
            Show = None
            TickNumber = None
            LineWidth = None
            LineColor = None
            LengthOverTickLength = None
        class Grid:
            Show = None
            LineColor = None
            LineWidth = None
            LineType = None
        class MinorGrid:
            Show = None
            LineColor = None
            LineWidth = None
            LineType = None
    class Yaxis:
        Show = None
        Log = None
        LineWidth = None
        LineColor = None
        LineType = None
        ShowTickText = None
        Xposition = None
        XoffsetInPt = None
        class Tick:
            Show = None
            TickOut = None
            Length = None
            Width = None
            Color = None
            Font = None
            FontSize = None
            FontColor = None
            AutoLength = None
            LengthOverHeight = None
            AutoFontSize = None
            FontSizeOverHeight = None
            OffsetOfTextFromTickOverWidth = None
        class MinorTick:
            Show = None
            TickNumber = None
            LineWidth = None
            LineColor = None
            LengthOverTickLength = None
        class Grid:
            Show = None
            LineColor = None
            LineWidth = None
            LineType = None
        class MinorGrid:
            Show = None
            LineColor = None
            LineWidth = None
            LineType = None
    SecondaryAxis = None
    class Second_Plot:
        LineColor = None
        LineType = None
        LineWidth = None
        xlimit = None
        ylimit = None
        FillAreaUnderGraph = None
        FillAreaColor = None
        class Point:
            Show = None
            Type = None
            Color = None
            AutoSize = None
            SizeOverHeight = None
            Size = None
        class BarChart:
            Show = None
            BarWidth = None
            LineWidth = None
            LineColor = None
            Fill = None
            FillColor = None
            ColorMapNormalization = None
        class PlotBox:
            Show = None
            BoxColor = None
            LineWidth = None
            LineColor = None
            LineType = None
        class ErrorBar:
            Show = None
            Color = None
            LineWidth = None
            AutoLength = None
            LengthOverWidth = None
            Length = None
    class Second_yLabel:
        Text = None
        Font = None
        OffsetX = None
        OffsetY = None
        AutoFontSize = None
        FontSizeOverHeight = None
        FontSize = None
        FontColor = None
    class Second_xLabel:
        Text = None
        Font = None
        OffsetX = None
        OffsetY = None
        AutoFontSize = None
        FontSizeOverHeight = None
        FontSize = None
        FontColor = None
    class Second_Xaxis:
        Show = None
        Log = None
        LineWidth = None
        LineColor = None
        LineType = None
        ShowTickText = None
        Yposition = None
        YoffsetInPt = None
        class Tick:
            Show = None
            TickOut = None
            Length = None
            Width = None
            Color = None
            Font = None
            FontSize = None
            FontColor = None
            AutoLength = None
            LengthOverHeight = None
            AutoFontSize = None
            FontSizeOverHeight = None
        class MinorTick:
            Show = None
            TickNumber = None
            LineWidth = None
            LineColor = None
            LengthOverTickLength = None
        class Grid:
            Show = None
            LineColor = None
            LineWidth = None
            LineType = None
        class MinorGrid:
            Show = None
            LineColor = None
            LineWidth = None
            LineType = None
    class Second_Yaxis:
        Show = None
        Log = None
        LineWidth = None
        LineColor = None
        LineType = None
        ShowTickText = None
        Xposition = None
        XoffsetInPt = None
        class Tick:
            Show = None
            TickOut = None
            Length = None
            Width = None
            Color = None
            Font = None
            FontSize = None
            FontColor = None
            AutoLength = None
            LengthOverHeight = None
            AutoFontSize = None
            FontSizeOverHeight = None
            OffsetOfTextFromTickOverWidth = None
        class MinorTick:
            Show = None
            TickNumber = None
            LineWidth = None
            LineColor = None
            LengthOverTickLength = None
        class Grid:
            Show = None
            LineColor = None
            LineWidth = None
            LineType = None
        class MinorGrid:
            Show = None
            LineColor = None
            LineWidth = None
            LineType = None
    class Annotate:
        Show = None
        Font = None
        FontSize = None
        FontColor = None
        TextWidth = None
        Alignment = None
        LineSpacing = None
    class Picture:
        InsertPicture = None
        PictureFilename = None
        PictureSize = None
        PictureOrigin = None
        PictureCustom = None
    ShowDataOnly = None
    class Debug:
        ShowErrorMessage = None
        ShowPrint = None
        VerbalEchoForMpretty = None
        EchoThisContent = None
    ColorMap = None
    LayoutSequence = None
