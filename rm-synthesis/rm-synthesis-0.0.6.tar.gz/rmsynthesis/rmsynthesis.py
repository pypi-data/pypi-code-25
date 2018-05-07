## Lerato Sebokolodi <mll.sebokolodi@gmail.com>

import numpy
import astropy.io.fits as pyfits
import time
import sys
from multiprocessing import Pool
import argparse
import os


_path = os.path.realpath(__file__)
_path = os.path.dirname(_path)
execfile("%s/__init__.py"%_path)


def read_data(image, freq=True):
                                                                              
    """ Read and return image data: ra, dec and freq only"""
    try:
        with pyfits.open(image) as hdu:
            imagedata = hdu[0].data
            header = hdu[0].header
        imslice = numpy.zeros(imagedata.ndim, dtype=int).tolist()
        imslice[-1] = slice(None)
        imslice[-2] = slice(None)
        if freq:
            imslice[-3] = slice(None)
        print('>>> Image %s loaded sucessfully. '%image)
        return imagedata[imslice], header
    except OSError:
        sys.exit('>>> could not load %s. Aborting...'%image)
        


def check_shape(qfits, ufits, frequencies):
    """
    Checks the shape of the cubes and frequency file
    """
    qhdr =  pyfits.getheader(qfits)
    uhdr =  pyfits.getheader(ufits)
    
    errors = []
    axis = ['naxis1', 'naxis2', 'naxis3']
    if qhdr['naxis'] < 3 or uhdr['naxis'] < 3:
        errors.append('The dimensions of Q = %d and U = %d, not >=3.' %(
               qhdr['naxis'], uhdr['naxis']))
    if qhdr['naxis'] != uhdr['naxis']:
        if qhdr['naxis'] >= 3 and uhdr['naxis'] >=3:
             for ax in axis:
                 if qhdr[ax] != uhdr[ax]:
                      errors.append('%s for Q is != %d of U.' %(ax, qhdr[ax], uhdr[ax]))
    if qhdr[axis[2]] != len(frequencies) or uhdr[axis[2]] != len(frequencies):
        errors.append('Freq-axis of the cubes differ from that of the '
           'frequency file provided.')
            
    return errors

 

def faraday_phase(phi_sample, wavelengths):       
    
    """return phase term of the Faraday spectrum """
    phase = numpy.zeros([len(phi_sample), len(wavelengths)], dtype=numpy.complex64)  
    derotated_wavelength = wavelengths - wavelengths.mean()
    for i, phi in enumerate(phi_sample):                  
        phase[i, :] = numpy.exp(-2 * 1j * phi * derotated_wavelength )
                              
    return phase



def add_RM_to_fits_header(header, pol, phi_sample=None):

    """
    Adds RM axis to the data in place of frequency.

    NB:Knicked and modified from Brentjens RM Synthesis code     
    """
    hdr = header.copy()
    if len(phi_sample) >= 2:
        # if it is a cube then do this:
        new_hdr = {'naxis3': len(phi_sample), 'crpix3':1.0,
                  'cdelt3': phi_sample[1]-phi_sample[0], 
                  'crval3': phi_sample[0], 'ctype3':'RM',
                  'cunit3': 'rad/m^2', 'POL': '%s'%pol}
                  
    else:
        new_hdr = {'naxis': 3, 'naxis3': 1, 'cunit3': 'rad/m^2', 
                   'ctype3':'RM', 'POL': '%s'%pol}

    hdr.update(new_hdr) 
    return hdr


def faraday_depth_interval(wavelengths, phi_max=None,  
                       phi_min=None, dphi=None):

    """Computes the RM interval and resolution"""
    #TODO: optimize this better booboo
    if phi_max is None:
        phi_max = (1.9/abs(numpy.diff(wavelengths)).max())

    if phi_min is None:
       phi_min = -phi_max

    if dphi is None:
       dphi = (3.8/abs(wavelengths[0] - wavelengths[-1]))/3.0

    return phi_max, phi_min, dphi



def compute_dispersion(x, y):
   
    """Computes Faraday Dispersion of a pixel in question"""

    start = time.time()
    P = qdata[:, x, y] + 1j * udata[:, x, y]
    dispersion = numpy.sum(P * phase, axis=1)/N_wave
    end = time.time()
    print('Time %.6f secs for (%d, %d)'%(end-start, x, y))
    return dispersion


def read_mask(fits):
    """get pixel coordinates for a mask"""
    maskdata = read_data(fits, freq=False)
    xpix, ypix = numpy.where(mask > 0)
    return xpix, ypix


def main():

    parser = argparse.ArgumentParser(description='Performs 1-D RM Synthesis. '
             'It requires Stokes Q and U image cubes as well as a frequency '
             'in text format. These cubes should be (312), freq, ra, dec. '
             'There is an option for multi-processing, see numProcessor. '
             'The outputs are the Q and U  of Faraday dispersion (FD) cube, '
             'RM map derived from peak in FD spectrum. The RMSF amplitude and '
             'the RM range in a text file.')
    add = parser.add_argument
    add("-v","--version", action="version",version=
        "{:s} version {:s}".format(parser.prog, __version__))
    add('-q', '--qcube', dest='qfits', help='Stokes Q cube (fits)')
    add('-u', '--ucube', dest='ufits', help='Stokes U cube (fits)')
    add('-f', '--freq', dest='freq', help='Frequency file (text)')  
    add('-ncore', '--numpr', dest='numProcessor', help='number of cores to use. Default 1.', 
        default=1, type=int)
    add('-rmin', '--rm-min', dest='phi_min', help='Minimum Faraday depth. Default None. '
       'If not specified will be determined internally. See Brentjens (2005) paper.',
       type=float, default=None)
    add('-rmax', '--rm-max', dest='phi_max', help='Maximum Faraday depth. See -rn.',
       type=float, default=None)
    add('-rstep', '--rm-sample', dest='dphi', help='The sampling width in Faraday-space.',
        type=float, default=None)
    add('-mask', '--maskfits', dest='maskfits', help='A mask image (fits). This package '
        'comes with a tool called cleanmask to allow the user to create a mask, for more info '
        'cleanmask -h', default=None)
    add('-o', '--prefix', dest='prefix', help='This is a prefix for output files.')
    
    
    #TODO: 1) RM cleaning, '
    #TODO: 2) derotate the observed PA by RM_peak *wavelengths^2
    #TODO: 4) add log file.

    args = parser.parse_args()

    try:
        frequencies = numpy.loadtxt(args.freq)
    except ValueError:
        sys.exit(">>> Problem found with frequency file. It should be a text file")
    
    
    errors = check_shape(args.qfits, args.ufits, frequencies)
    if len(errors) > 0:
        print(errors)
        sys.exit()
    global qdata, udata, phase, N_wave

    wavelengths =  (299792458.0/frequencies)**2 
    qdata, qhdr = read_data(args.qfits) # run Q-cube 
    udata, uhdr = read_data(args.ufits) # run U-cube

    
    phi_max, phi_min, dphi = faraday_depth_interval(wavelengths, args.phi_max, 
                         args.phi_min, args.dphi)
    phi_sample =  numpy.arange(phi_min, phi_max, dphi)
    print('>>> Maximum RM = %.2f, minimum RM =%.2f, in steps of %.2f rad/m^2'\
          %(phi_max, phi_min, dphi))

    phase = faraday_phase(phi_sample, wavelengths)
    N_wave, N_x, N_y = qdata.shape
    N_phi = len(phi_sample)
    
    # use mask or all pixels
    if args.maskfits:
        x, y = read_mask(args.maskfits)
    
    else:
        x, y = numpy.indices((N_x, N_y))
        x = x.flatten()
        y = y.flatten()

    # compute the Faraday dispersion via multi-processing
    Faraday_Dispersion = numpy.zeros([N_phi, N_x, N_y ], dtype=numpy.complex64)
    start_all = time.time()
    pool = Pool(args.numProcessor)  
    for (xx, yy) in zip(x, y):  
       Faraday_Dispersion[:, xx, yy] = pool.apply(compute_dispersion, args=(xx, yy))
    end_all = time.time()
    print('>>> The total time for multiprocessing is %.6f'%(end_all-start_all))
   
    print('>>> Extracting peaks in the Faraday spectrum, amplitude and angle...')
    # get peak in the Faraday dispersion function, angle and RM
    Faraday_amp = numpy.absolute(Faraday_Dispersion)
    peaks = numpy.argmax(Faraday_amp, axis=0)
    RM_peak = phi_sample[peaks]
    FDispersion = numpy.take(Faraday_Dispersion, peaks)
    FDangle = numpy.angle(FDispersion) - RM_peak * wavelengths.mean()
    FDpeak = numpy.absolute(FDispersion)
    phase_amp = numpy.absolute(numpy.sum(phase, axis=1) )/N_wave
    # get headers
    rmhdr = add_RM_to_fits_header(qhdr, pol='RM', phi_sample=[1])
    fhdr  = add_RM_to_fits_header(qhdr, pol='Q', phi_sample=phi_sample)
    print('>>> Saving outputs...')
    # save the data
    args.prefix = args.prefix or args.qfits.split('.')[0]
    numpy.savetxt(args.prefix  + '-RMSF.txt', numpy.vstack((phi_sample, phase_amp)) )
    pyfits.writeto(args.prefix + '-RM.FITS', RM_peak, rmhdr, clobber=True)
    pyfits.writeto(args.prefix + '-FDAMP.FITS', FDpeak,
           rmhdr.update('POL', 'FPEAK'), clobber=True)
    pyfits.writeto(args.prefix + '-FDANG.FITS', FDangle, 
           rmhdr.update('POL', 'FANG'), clobber=True)
    pyfits.writeto(args.prefix + '-QRM.FITS', Faraday_Dispersion.real, 
           fhdr, clobber=True)
    pyfits.writeto(args.prefix + '-URM.FITS', Faraday_Dispersion.imag,
           fhdr.update('POL', 'U'), clobber=True)
    print('>>> Done!')


