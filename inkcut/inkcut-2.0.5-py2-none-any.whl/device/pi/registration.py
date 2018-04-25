"""
Copyright (c) 2017, Vinylmark LLC.

Distributed under the terms of the GPL v3 License.

The full license is in the file LICENSE, distributed with this software.

Created on Jan 24, 2015

@author: jrm
@author: jjm
"""
#: Moved here so I can still test it on the desktop
from PIL import Image
from matplotlib import pyplot as plt
import cv2
import zbar


def process(
        self, SKU = "VF207" ,
        CameraImage = "QRimageWithGlobals.jpg"):
    if not self.config.crop_mark_registration:
        return 0, 0, 0

    imageRaw = cv2.imread(CameraImage)
    scanner = zbar.ImageScanner()                                        # create a reader
    scanner.parse_config('enable')                                       # configure Reader
    gray = cv2.cvtColor(imageRaw, cv2.COLOR_RGB2GRAY,dstCn=0)            # Obtain image data
    ret, gray = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)            # Threshold to convert image to binary

    #gray = cv2.adaptiveThreshold(gray, 255 , cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,17,2)          ## May need integrate this later. Using adaptive gaussian method. Useful for images with ranges of shading in image. Good lighting is probably a better implementation

    pil = Image.fromarray(gray)
    width, height = pil.size
    raw = pil.tobytes()
    image = zbar.Image(width,height,'Y800',raw)                          # wrap image data
    scanner.scan(image)


    for symbol in scanner.results:
        print(symbol.data)
        print(symbol.location)
        A=symbol.location
        y1a=A[0][1]+0.0                                                  # Corner 0 y point   points to form line a
        y2a=A[2][1]+0.0                                                  # Corner 2 y point
        x1a=A[0][0]+0.0                                                  # Corner 0 x point
        x2a=A[2][0]+0.0                                                  # Corner 2 x point

        ma = (y2a-y1a)/(x2a-x1a)                                         # Slope of line a
        ba = y1a - ma*x1a                                                # Intercept of line a

        y1b=A[1][1]+0.0                                                  # Corner 1 y point   points to form line b
        y2b=A[3][1]+0.0                                                  # Corner 3 y point
        x1b=A[1][0]+0.0                                                  # Corner 1 x point
        x2b=A[3][0]+0.0                                                  # Corner 3 x point

        mb = (y2b-y1b)/(x2b-x1b)                                         # Slope of line b
        bb = y1b - mb*x1b                                                # Intercept of line b

        xintersect = (bb-ba)/(ma-mb)                                     # x intersection point of lines a and b
        yintersect = ma*xintersect + ba                                  # y intersection point of lines a and b
        cv2.circle(imageRaw,(int(xintersect),int(yintersect)),30,(255,0,0),-1)      # draw circles on image for visualization

        if (symbol.data == 'CutterTopLeft'):
            CutterTopLeft = (xintersect, yintersect)                     # Save center points of cutter QR codes
        if (symbol.data == 'CutterTopRight'):
            CutterTopRight = (xintersect, yintersect)
        if (symbol.data == 'CutterBottomLeft'):
            CutterBottomLeft = (xintersect, yintersect)
        if (symbol.data == 'CutterBottomRight'):
            CutterBottomRight = (xintersect, yintersect)
        if (symbol.data == SKU+'topLeft'):
            SKUtopLeft = (xintersect, yintersect)                        # Save center points of media QR codes
        if (symbol.data == SKU+'topRight'):
            SKUtopRight = (xintersect, yintersect)
        if (symbol.data == SKU+'bottomLeft'):
            SKUbottomLeft = (xintersect, yintersect)
        if (symbol.data == SKU+'bottomRight'):
            SKUbottomRight = (xintersect, yintersect)



    ##### CUTTER TRANSLATION AND ROTATION CALCULATIONS ########

    ma = (CutterBottomRight[1] - CutterTopLeft[1] + 0.0)/(CutterBottomRight[0]-CutterTopLeft[0] + 0.0)     # Slope of line a
    ba = CutterTopLeft[1] - ma*CutterTopLeft[0] + 0.0                                                      # Intercept of line a

    mb = (CutterTopRight[1] - CutterBottomLeft[1] + 0.0)/(CutterTopRight[0] - CutterBottomLeft[0] + 0.0)   # Slope of line b
    bb = CutterBottomLeft[1] - mb*CutterBottomLeft[0] + 0.0                                                # Intercept of line b

    xintersect = (bb-ba)/(ma-mb)                                                                           # x intersection point of lines a and b
    yintersect = ma*xintersect + ba                                                                        # y intersection point of lines a and b

    CutterTranslation = (xintersect , yintersect)                                                          # Cutter Translation , # Let our rotation metric be the sum of slopes of QR code diagonals
    CutterRotation = (CutterBottomRight[1]-CutterTopLeft[1])/(CutterBottomRight[0]-CutterTopLeft[0]) + (CutterTopRight[1]-CutterBottomLeft[1])/(CutterTopRight[0]-CutterBottomLeft[0]) + 0.0

    cv2.line(imageRaw,(int(CutterTopLeft[0]),int(CutterTopLeft[1])),(int(CutterBottomRight[0]),int(CutterBottomRight[1])),(255,0,0),5)
    cv2.line(imageRaw,(int(CutterBottomLeft[0]),int(CutterBottomLeft[1])),(int(CutterTopRight[0]),int(CutterTopRight[1])),(255,0,0),5)

    cv2.line(imageRaw,(int(SKUtopLeft[0]),int(SKUtopLeft[1])),(int(SKUbottomRight[0]),int(SKUbottomRight[1])),(0,0,255),5)
    cv2.line(imageRaw,(int(SKUbottomLeft[0]),int(SKUbottomLeft[1])),(int(SKUtopRight[0]),int(SKUtopRight[1])),(0,0,255),5)



    ######### SKU TRANSLATION AND ROTATION CALCULATIONS #########

    ma = (SKUbottomRight[1] - SKUtopLeft[1] + 0.0)/(SKUbottomRight[0]-SKUtopLeft[0] + 0.0)                 # Slope of line a
    ba = SKUtopLeft[1] - ma*SKUtopLeft[0] + 0.0                                                            # Intercept of line a

    mb = (SKUtopRight[1] - SKUbottomLeft[1] + 0.0)/(SKUtopRight[0] - SKUbottomLeft[0] + 0.0)               # Slope of line b
    bb = SKUbottomLeft[1] - mb*SKUbottomLeft[0] + 0.0                                                      # Intercept of line b

    xintersect = (bb-ba)/(ma-mb)                                                                           # x intersection point of lines a and b
    yintersect = ma*xintersect + ba                                                                        # y intersection point of lines a and b

    SKUtranslation = (xintersect , yintersect)                                                             # Cutter Translation , # Let our rotation metric be the sum of slopes of QR code diagonals
    SKUrotation = (SKUbottomRight[1]-SKUtopLeft[1])/(SKUbottomRight[0]-SKUtopLeft[0]) + (SKUtopRight[1]-SKUbottomLeft[1])/(SKUtopRight[0]-SKUbottomLeft[0]) +0.0



    #### TODO: need someway of calibrating Cutter to Image ????????? J


    ## Matplot lib stuff for visualization  # TODO: replace matplotlib with light weight image viewer
    plt.imshow(imageRaw)
    plt.show()
    x=0                                     # TODO: Solve x translation
    y=0                                     # TODO: Solve y translation
    rotation=0                              # TODO: Solve rotation
    return (x, y, rotation)