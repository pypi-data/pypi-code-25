# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

### imports from ##############################################################
from scipy.signal import bartlett, blackman

### relative imports ##########################################################
from .spectrum import Spectrum

###############################################################################
def pad(ifg, Nd, Np):
    ifg = np.pad(ifg, (Np - Nd, 0), 'constant', constant_values=(0, 0))
    return ifg


def ramp(Nd, Np):
    r = np.ones(Np)
    r[:Nd] = np.linspace(0, 1, Nd)
    
    return r


def triangle(Nd, Np):
    Nd2 = Nd // 2
    t = np.zeros(Np)
    N_right = Np - Nd2
    
    t[Nd2:] = np.linspace(1, 0, N_right)
    t[:Nd2] = t[Nd:Nd2:-1]
    
    return t

###############################################################################
class Interferogram:
    def __init__(self, I, **kwargs):
        self.dx_cm = 633E-9 * 100 / 2 # spatial step size [cm]
        self.window = None
        
        for key, value in kwargs.items():
            if key == 'dx_cm':
                self.dx_cm = value
            elif key == 'window':
                self.window = value
        
        self.I = np.copy(I)
        self.I0 = np.max(np.abs(I))
        self.Np = I.size
        self.dnu = 1 / self.Np / self.dx_cm
        self.zpd = np.argmax(np.abs(I))

    def apod(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'blackman':
                window = blackman(self.Np, sym=False)
            elif key == 'triangle':
                window = bartlett(self.Np, sym=False)

        I = self.I * window
        ifg = self.copy(I, window=window)
        
        return ifg
                

    def blackman(self):
        window = blackman(self.Np, sym=False)
        I = self.I * window
        ifg = self.copy(I, window=window)
        
        return ifg

    def copy(self, I, **kwargs):
        dx_cm = self.dx_cm
        window = self.window
        
        for key, value in kwargs.items():
            if key == 'window':
                window = value
        
        ifg = Interferogram(I, dx_cm=dx_cm, window=window)

        return ifg

    def fft(self):
        S = np.fft.fft(self.I)
        wn = np.fft.fftfreq(self.Np, d=self.dx_cm)
        spectrum = Spectrum(wn, S)
        
        return spectrum

    def pad(self):
        Nd = 2 * self.zpd
        I = pad(self.I, Nd, self.Np)
        ifg = self.copy(I)

        return ifg

    def ramp(self):
        Nd = 2 * self.zpd
        window = ramp(Nd, self.Np)
        I = 2 * self.I * window
        ifg = self.copy(I, window=window)
        
        return ifg

    def triangle(self):
        window = bartlett(self.Np, sym=False)
        I = self.I * window
        ifg = self.copy(I, window=window)
        
        return ifg

    def triangle_ss(self):
        Nd = 2 * self.zpd
        window = triangle(Nd, self.Np)
        I = self.I * window
        ifg = self.copy(I, window=window)
        
        return ifg


    def shift(self):
        I = np.fft.fftshift(self.I)

        window = None
        
        if self.window is not None:
            window = np.fft.fftshift(self.window)
        
        ifg = self.copy(I, window=window)
        return ifg

    def single_side(self, Nd):
        Nd2 = Nd // 2
        I = self.I[self.zpd-Nd2:]
        ifg = self.copy(I)
        
        return ifg

    def truncate(self, Nd):
        il = self.zpd - Nd // 2
        ir = self.zpd + Nd // 2
        I = self.I[il:ir]
        ifg = self.copy(I)
        
        return ifg
