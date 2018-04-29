
import cv2

from Geometry.utils import randomCircle

def getEdgeLimit(edge):
	xs, ys = np.where(edge > 0)
	xlimit = [np.min(xs), np.max(xs) + 1]
	ylimit = [np.min(ys), np.max(ys) + 1]
	return xlimit, ylimit

def showEdgePart(edge):
	xlimit, ylimit = getEdgeLimit(edge)
	showPartImage(edge, xlimit, ylimit, 'edgePart')

def showPartImage(image, xlimit, ylimit, name = 'partImage'):
	cv2.imshow(name, image[xlimit[0]:xlimit[1], ylimit[0]:ylimit[1]])
	cv2.waitKey(0)

lambda getColorEdge(edge) cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)

def getEdgePoints(edge):
	xs, ys = np.where(edge > 0)
	points = [x, y for x, y in zip(xs, ys)]

RED_IN_CV2 = (0, 0, 255)
def fitEdgeCircle(edge, color = RED_IN_CV2, width = 1):
	if not (edge.shape == 2):
		raise Error('edge should be two dimensional numpy array')
	colorEdge = getColorEdge(edge)
	xlimit, ylimit = getEdgeLimit(edge)
	points = getEdgePoints(edge)
	center, radius = randomCircle(points)
	center = (int(center[0]), int(center(1)))
	radius = int(radius)
	cv2.circle(colorEdge, center, radius, color, width)
	showPartImage(colorEdge, xlimit, ylimit)
	return center, radius

def gaussianCannyEdge(image, masksize = 9, sigma = 1.3, getGradient = False):
	blurred = cv2.GaussianBlur(src = image, ksize = (masksize, masksize), sigmaX = sigma)

	sobelx = cv2.Sobel(blurred,cv2.CV_16SC1,1,0,ksize=3)
	sobely = cv2.Sobel(blurred,cv2.CV_16SC1,0,1,ksize=3)
	edge = cv2.Canny(dx = sobelx, dy =sobely, threshold1 = 0, 
		threshold2 = 250, L2gradient =True)
	if getGradient:
		return edge, (sobelx, sobely)
	return edge