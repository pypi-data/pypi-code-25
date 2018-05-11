# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

###############################################################################
class Spectrum:
    def __init__(self, wn, S):
        self.S = S
        self.wn = wn
        
        self.Re = np.real(S)
        self.Im = np.imag(S)
        self.theta = np.arctan2(self.Im, self.Re)

    def mertz(self, low_res_spectrum):
        # interpolate theta to full resolution
        self.theta_smooth = np.interp(
                self.wn,
                low_res_spectrum.wn,
                low_res_spectrum.theta)
        
        cos_theta = np.cos(self.theta_smooth)
        sin_theta = np.sin(self.theta_smooth)
        
        self.S_abs = self.Re * cos_theta + self.Im * sin_theta

        return self.S_abs
        
    def shift(self):
        wn = np.fft.fftshift(self.wn)
        S = np.fft.fftshift(self.S)
        spectrum = Spectrum(wn, S)

        return spectrum