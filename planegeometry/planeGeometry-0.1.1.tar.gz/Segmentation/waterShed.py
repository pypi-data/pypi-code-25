import cv2
import numpy as np


def waterShedByCv2(imageFileName, kernelSize = 3, iterations = 3):
	colorImage = cv2.imread(imageFileName)
	if len(colorImage.shape) > 2:
		grayImage = cv2.cvtColor(colorImage, cv2.COLOR_BGR2GRAY)
	else :
		grayImage = colorImage.copy()
	ret, thresh = cv2.threshold(grayImage,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
	#noise removal
	kernel = np.ones((kernelSize, kernelSize),np.uint8)
	opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)

	sure_bg = cv2.dilate(opening,kernel,iterations= iterations)
	sure_fg = cv2.erode(opening,kernel,iterations = iterations)

	unknown = cv2.subtract(sure_bg,sure_fg)
	# Marker labelling
	ret, markers = cv2.connectedComponents(sure_fg)
	markers = markers+1
	markers[unknown==255] = 0
	markers = cv2.watershed(colorImage,markers)
	colorImage[markers == -1] = [255,0,0]
	cv2.imwrite('marker.jpg', markers)
	cv2.imwrite('segments.jpg', colorImage)
	