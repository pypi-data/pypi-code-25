# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

### imports from ##############################################################
from .interferogram import Interferogram

###############################################################################
class SingleChannel:
    def __init__(self, I, Nd):
        self.ifg = Interferogram(I)
        
        # low res spectrum
        ifg_low_res = self.ifg.truncate(Nd)
    
        # apodize and shift the low res spectrum
        ifg_low_res_apod = ifg_low_res.triangle().shift()
    
        # FT
        low_res_spectrum = ifg_low_res_apod.fft().shift()
    
        # full single-sided interferogram
        ifg_apod = self.ifg.triangle_ss()
        ifg_apod_ramp = ifg_apod.ramp()
        ifg_apod_pad_shift = ifg_apod_ramp.pad().shift()
    
        # FT and phase correction
        self.spectrum = ifg_apod_pad_shift.fft().shift()
        self.spectrum.mertz(low_res_spectrum)        

        imin = np.where(self.spectrum.wn > 560)[0][0]
        imax = np.where(self.spectrum.wn < 600)[0][-1]
        self.wn = self.spectrum.wn[imin:imax+1]
        self.S = self.spectrum.S_abs[imin:imax+1]