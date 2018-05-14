import numpy as np
import healpy as hp
from fitsfuncdrizzlib import read_map
from pympler.tracker import SummaryTracker
tracker = SummaryTracker()

#map = hp.read_map("/Users/pilot/Soft_Librairies/CADE/drizzlib-python/tests/VGPS_1_8192_nested.fits", nest=True)
healpix='/Users/pilot/Soft_Librairies/CADE/drizzlib-python/tests/VGPS_1_8192_nested.fits'
field=1
m, h = read_map(healpix, h=True, hdu=field)


tracker.print_diff()

#map_ring = hp.pixelfunc.reorder(map, inp='NEST', out='RING')


tracker.print_diff()

#ind=np.where(map_ring == -32768)
#map_ring[ind]=0.
map2 = hp.smoothing(m[0,:], fwhm=np.radians(0.997775))

tracker.print_diff()

map2[ind]=-32768
map3 = hp.ud_grade(map2,nside_out=2048, pess=True)

tracker.print_diff()

hp.write_map("/Users/pilot/Soft_Librairies/CADE/drizzlib-python/tests/VGPS_1_2048_nested.fits", map3)

tracker.print_diff()

