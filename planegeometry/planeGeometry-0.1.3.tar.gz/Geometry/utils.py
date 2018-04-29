from numpy import linalg
import numpy as np

def getCenter(p1, p2, p3):
		firstNorm = p1[0] * p1[0] + p1[1] * p1[1]
		secondNorm = p2[0] * p2[0] + p2[1] * p2[1]
		thirdNorm = p3[0] * p3[0] + p3[1] * p3[1]

		xdelta1 = 2 * (p1[0] - p2[0])
		ydelta1 = 2 * (p1[1] - p2[1])
		xdelta2 = 2 * (p3[0] - p2[0])
		ydelta2 = 2 * (p3[1] - p2[1])
		coefficient = np.array([[xdelta1, ydelta1], [xdelta2, ydelta2]])
		ordinate = np.array([firstNorm - secondNorm, thirdNorm - secondNorm])
		center = linalg.solve(coefficient, ordinate)
		return center



def randomCircle(points, iterations = 100):
	def dist(p1, p2):
		return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
	finalCenter = None
	curVar = 0
	for i in range(iterations):
		ctlPoints = [points[j] for j in np.random.choice(range(len(points)), 3)]
		try:
			center = getCenter(ctlPoints[0], ctlPoints[1], ctlPoints[2])
			distances = [dist(center, p) for p in points]
			if finalCenter is None or curVar < np.var(distances):
				curVar = np.var(distances)
				finalCenter = center
		except Exception as e:
			pass
	return center

def leastSquareCircle(x, y):
	#! python
	# == METHOD 1 ==
	method_1 = 'algebraic'

	# coordinates of the barycenter
	x_m = np.mean(x)
	y_m = np.mean(y)

	# calculation of the reduced coordinates
	u = x - x_m
	v = y - y_m

	# linear system defining the center (uc, vc) in reduced coordinates:
	#    Suu * uc +  Suv * vc = (Suuu + Suvv)/2
	#    Suv * uc +  Svv * vc = (Suuv + Svvv)/2
	Suv  = np.sum(u*v)
	Suu  = np.sum(u**2)
	Svv  = np.sum(v**2)
	Suuv = np.sum(u**2 * v)
	Suvv = np.sum(u * v**2)
	Suuu = np.sum(u**3)
	Svvv = np.sum(v**3)

	# Solving the linear system
	A = np.array([ [ Suu, Suv ], [Suv, Svv]])
	B = np.array([ Suuu + Suvv, Svvv + Suuv ])/2.0
	uc, vc = linalg.solve(A, B)

	xc_1 = x_m + uc
	yc_1 = y_m + vc

	# Calcul des distances au centre (xc_1, yc_1)
	Ri_1     = np.sqrt((x-xc_1)**2 + (y-yc_1)**2)
	print (Ri_1, 'ris one')
	R_1      = np.mean(Ri_1)
	residu_1 = np.sum((Ri_1-R_1)**2)
	return (xc_1, yc_1), R_1

def lineIntersection(line1, line2):
	xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
	ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]) #Typo was here

	def det(a, b):
		return a[0] * b[1] - a[1] * b[0]

	div = det(xdiff, ydiff)
	if div == 0:
	   raise Exception('lines do not intersect')

	d = (det(*line1), det(*line2))
	x = det(d, xdiff) / div
	y = det(d, ydiff) / div
	return x, y

def main():
	xs, ys = np.loadtxt('data.txt')
	points = [(x, y) for x, y in zip(xs, ys)]
	randomCircle(points)

if __name__ == '__main__':
	main()
