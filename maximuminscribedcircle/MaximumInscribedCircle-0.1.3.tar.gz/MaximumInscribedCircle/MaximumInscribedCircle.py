import math
import random

import numpy as np
from numpy import linalg



epsilon = 1e-6
class Point():
	def __init__(self, x, y):
		self.x = x
		self.y = y

	@classmethod
	def fromList(cls, p) :
		return cls(p[0], p[1])

	def __cmp__(self, other):
		return cmp(self.x, other.x) and cmp(self.y, other.y)

	def __str__(self):
		return 'x : {}, y : {}'.format(self.x, self.y)

	def toTuple(self):
		return (self.x, self.y)

def listToPoint(p):
	return Point(p[0], p[1]);

class Vector():
	
	def __init__(self, p1, p2):
		self.__construtor(p1, p2)

	def __construtor(self, p1, p2):
		self.fromPoint = p1
		self.toPoint = p2
		self.diffPoint = Point(p2.x - p1.x, p2.y - p1.y)

	def __str__(self):
		return 'cor : {}'.format(self.diffPoint)

	def setToPoint(self, p):
		self.__construtor(self.fromPoint, p)

	def setNorm(self, newNorm):
		if abs(newNorm) < epsilon:
			self.__construtor(self.p1, self.p1)
		else :
			factor = newNorm / self.norm()
			x = self.diffPoint.x * factor
			y = self.diffPoint.y * factor
			self.diffPoint = Point(x, y)
			self.toPoint = Point(self.fromPoint.x + x,
				self.fromPoint.y + y)
		return self

	def norm(self):
		xsquare = self.diffPoint.x * self.diffPoint.x
		ysquare = self.diffPoint.y * self.diffPoint.y
		return math.sqrt(xsquare + ysquare)

	def dotProduct(self, other):
		return self.diffPoint.x * other.diffPoint.x + self.diffPoint.y * other.diffPoint.y

	def includedAngleIndegrees(self, other):
		rad = self.includedAngleRad(other)
		return math.degrees(rad)

	def includedAngle(self, other):
		return self.includedAngleIndegrees(other)

	def includedAngleCos(self, other):

		return self.dotProduct(other) / (self.norm() * other.norm())

	def includedAngleRad(self, other):
		return math.acos(self.includedAngleCos(other))

class MaximumInscribledCircle():
	"""docstring for MaximumInscribledCircle"""
	def __init__(self, points):

		if not isinstance(points[0], Point):
			xs, ys = np.mean(points, axis = 0)
			self.points = [listToPoint(p) for p in points]
		else :
			self.points = points
			xs = np.mean((p.x for p in points))
			ys = np.mean((p.y for p in points))
		self.center = Point(xs, ys)

	def __getNorms(self, tmpVector, p):
		other = Vector(tmpVector.fromPoint, p)
		if abs(other.norm()) < epsilon:

			return tmpVector.norm() / epsilon
		costheta = tmpVector.dotProduct(other) / (tmpVector.norm() * other.norm())
		if costheta < epsilon:
			return tmpVector.norm() / epsilon
		# print ('other norm', other.norm(), costheta, tmpVector.dotProduct(other))
		return other.norm() / costheta / 2

	def getIntersection(self, tmpVector, newNorm):
		newCenter = Vector(tmpVector.fromPoint, tmpVector.toPoint).setNorm(newNorm).toPoint
		return newCenter

	def getCenter(self):
		originalPoint = Point(0, 0)
		firstNorm = self.first.x * self.first.x + self.first.y * self.first.y
		secondNorm = self.second.x * self.second.x + self.second.y * self.second.y
		thirdNorm = self.third.x * self.third.x + self.third.y * self.third.y

		xdelta1 = 2 * (self.first.x - self.second.x)
		ydelta1 = 2 * (self.first.y - self.second.y)
		xdelta2 = 2 * (self.third.x - self.second.x)
		ydelta2 = 2 * (self.third.y - self.second.y)
		coefficient = np.array([[xdelta1, ydelta1], [xdelta2, ydelta2]])
		ordinate = np.array([firstNorm - secondNorm, thirdNorm - secondNorm]) 
		center = linalg.solve(coefficient, ordinate)

		return center
	def getThirdPoint(self, points):
		lineVector = Vector(self.first, self.second)
		lineVectorNorm = lineVector.norm() / 2
		def getCosTheta(p):
			other = Vector(self.directionVector.fromPoint, p)
			if other.norm() < epsilon:
				return -epsilon
			tmp = self.directionVector.includedAngleCos(other)
			return  - epsilon if tmp < epsilon else tmp
		def getSinTheta(p):
			tmpVector = Vector(p, self.first)
			other = Vector(p, self.second)
			x = tmpVector.includedAngleCos(other)
			return math.sqrt(1 - x * x)
			

		costhetas = [getCosTheta(p) for p in points]
		sinThetas = [epsilon] * len(costhetas)
		for i in range(len(sinThetas)):
			if costhetas[i] > epsilon:
				sinThetas[i] = getSinTheta(points[i])
		radiusApproximate = [lineVectorNorm / s for s in sinThetas]
		# print ('radius approximate', radiusApproximate, lineVectorNorm)
		pidx = np.argmin(radiusApproximate)
		self.third = points[pidx]
		self.final_radius = radiusApproximate[pidx]


	def getSecondPoint(self, points):

		norms = [self.__getNorms(self.directionVector, p) for p in points]
		pidx = np.argmin(norms)
		intersection = self.getIntersection(self.directionVector, norms[pidx])
		self.center = intersection
		# print (Vector(intersection, self.first).norm(), 'first to center')
		# print (Vector(intersection, points[pidx]).norm(), 'second to center')

		return points[pidx]

	def getMinimalDistancePoint(self):
		center = self.center
		points = self.points
		getDist = lambda p : np.sqrt((center.x - p.x) * (center.x - p.x) + 
			(center.y - p.y) * (center.y - p.y))
		dist = [getDist(p) for p in points]

		return points[np.argmin(dist)]

	def verifyAngle(self):
		if Vector(self.first, self.second).dotProduct(Vector(self.first, self.third)) < epsilon:
			return -1
		if Vector(self.second, self.first).dotProduct(Vector(self.second, self.third)) < epsilon :
			return -2
		return 0
		
	def getRadius(self):

		self.first = self.getMinimalDistancePoint()

		points = self.points
		self.directionVector = Vector(self.first, self.center)
		self.second = self.getSecondPoint(points)

		middle = Point((self.first.x + self.second.x) / 2, 
			(self.first.y + self.second.y) / 2)
		self.directionVector = Vector(middle, self.center)
		self.getThirdPoint(points)
		code = self.verifyAngle()
		while code != 0:
			self.center = self.getCenter()
			self.center = listToPoint(self.center)
			if code == -1:
				self.first = self.third
			else :
				self.second = self.third
			middle = Point((self.first.x + self.second.x) / 2, (self.first.y + self.second.y) / 2)
			self.directionVector = Vector(middle, self.center)
			self.getThirdPoint(points)
			code = self.verifyAngle()
		return self.final_radius
	

def PointsInCircum(r,n=100):
    data = [(math.cos(2*math.pi/n*x)*r,math.sin(2*math.pi/n*x)*r) for x in range(n+1)]
    data = [(p[0] + random.random(), p[1] + random.random()) for p in data]
    return data

def testFunc():
	points = PointsInCircum(200)
	circle = MaximumInscribledCircle(points)
	print (circle.getRadius(), 'max radius')
	# print (circle.first, circle.second, circle.third)



def main():
	testFunc()

if __name__ == '__main__':
	main()
	