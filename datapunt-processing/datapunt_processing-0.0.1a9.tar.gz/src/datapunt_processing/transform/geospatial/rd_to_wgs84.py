def rd_to_wgs84(X, Y):
	"""
		Quick reprojection method, does result in 1m max offset difference.
		Use Postgres ST_Transform method if you want a better reprojection.
		Example downloaded from http://forum.geocaching.nl/index.php?showtopic=7886
	"""
	dX = (X - 155000) * 10 ** -5
	dY = (Y - 463000) * 10 ** -5
	
	SomN = (3235.65389 * dY) + (-32.58297 * dX ** 2) + (-0.2475 * dY ** 2) + (-0.84978 * dX ** 2 * dY) + (-0.0655 * dY ** 3) + (-0.01709 * dX ** 2 * dY ** 2) + (-0.00738 * dX) + (0.0053 * dX ** 4) + (-0.00039 * dX ** 2 * dY ** 3) + (0.00033 * dX ** 4 * dY) + (-0.00012 * dX * dY)
	SomE = (5260.52916 * dX) + (105.94684 * dX * dY) + (2.45656 * dX * dY ** 2) + (-0.81885 * dX ** 3) + (0.05594 * dX * dY ** 3) + (-0.05607 * dX ** 3 * dY) + (0.01199 * dY) + (-0.00256 * dX ** 3 * dY ** 2) + (0.00128 * dX * dY ** 4) + (0.00022 * dY ** 2) + (-0.00022 * dX ** 2) + (0.00026 * dX ** 5)

	Latitude = 52.15517 + (SomN / 3600)
	Longitude = 5.387206 + (SomE / 3600)

	LatitudeGraden = Latitude
	LongitudeGraden = Longitude

	LatitudeMinuten = (Latitude - LatitudeGraden) * 60.0
	LongitudeMinuten = (Longitude - LongitudeGraden) * 60.0

	Latitude = '%s' % (LatitudeGraden)
	Longitude = '%s' % (LongitudeGraden)

	return Latitude, Longitude
