import numpy as np
def gaussianEllipticalFunction(x, y):
	return [1, x, y, x * y, x * x, y * y]

def gaussianEllipticalWeight():
	gaussinMaskIdx = 0;
	gaussinMask = np.zeros((9, 6));
	for x in [-1, 0, 1]:
		for y in [-1, 0, 1]:
			gaussinMask[gaussinMaskIdx, : ] = gaussianEllipticalFunction(x, y)
			gaussinMaskIdx = gaussinMaskIdx + 1
	gts = gaussinMask.T; #transpose
	weight = np.matmul(matrixInv(np.matmul(gts, gaussinMask)), gts);
	return weight;


def subPixelGaussianEllipitcalFit(img, gradientMagnitude, gradientDirection):
	gradientMagnitude[np.where(gradientMagnitude < 0.01)] = 0.01
	logGradMag = np.log(gradientMagnitude)
	edgeX, edgeY = np.where(img > 0)
	subPos = np.zeros((len(edgeX), 2));
	idx = 0;
	weight = gaussianEllipticalWeight();
	approximationVector = np.zeros((9, 1))
	rowLimit, colLimit = img.shape
	for i, j in zip(edgeX, edgeY) :
		
		gaussinMaskIdx = 0;
		if i > 0 and i < rowLimit - 1 and j < colLimit - 1 and j > 0:
			for x in [i - 1, i, i + 1]:
				for y in [j - 1, j, j + 1]:
					approximationVector[gaussinMaskIdx] = logGradMag[x, y]
					gaussinMaskIdx = gaussinMaskIdx + 1
		else :
			subPos[idx, : ] = (i, j)
			continue
		coef = np.matmul(weight, approximationVector);
		try:
			denominator = (4 * coef[5] * coef[4] - coef[3] ** 2)
			detaX = (coef[3] * coef[2]  - 2 * coef[1] * coef[5]) / denominator
			detaY = (coef[3] * coef[1]  - 2 * coef[2] * coef[4]) / denominator
		except Warning as e:
			print (coef)
		
		if detaX > 1 or detaX < -1 or detaY > 1 or detaY < -1:
			continue
		subPos[idx, : ] = (i + detaX, j + detaY)
		idx += 1
	subPos =subPos [0 : idx]
	return subPos

def main():
	pass

if __name__ == '__main__':
	main()