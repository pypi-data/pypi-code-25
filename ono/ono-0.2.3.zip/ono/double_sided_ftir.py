# -*- coding: utf-8 -*-

### imports ###################################################################
import numpy as np

### imports from ##############################################################
from ono.bruker_opus_filereader import OpusReader

###############################################################################
class Spectrum:
    def __init__(self, nu, y):
        self.nu = nu
        self.y = y

###############################################################################
class SingleChannel:
    def __init__(self, filename, block='IgSm'):
        sample = OpusReader(filename)
        sample.readDataBlocks()
        
        if block in ('AB', 'ScRf', 'ScSm'):
            self.y = sample[block]
            
            key = ' '.join((block, 'Data Parameter'))
            data_params = sample[key]
            fxv = data_params['FXV']
            lxv = data_params['LXV']
            NPT = data_params['NPT']
            self.nu = np.linspace(fxv, lxv, NPT)
        else:
            self.lwn = sample['Instrument']['LWN']
            self.dx_cm = 1 / self.lwn / 2
    
            ifg_fwd_bwd = sample[block]
            N_fwd_bwd = ifg_fwd_bwd.size
            self.N = N_fwd_bwd // 2
    
            ifg = ifg_fwd_bwd[:self.N]
            
            i0 = np.argmax(ifg)
            ifg = np.roll(ifg, -i0)
            
            self.y = np.real(np.fft.fft(ifg))
            self.nu = np.fft.fftfreq(self.N, self.dx_cm)
        

###############################################################################
class Sample:
    def __init__(self, **kwargs):
        self.absorption = None
        self.alpha = None
        self.R = 0.276
        self.scrf = None
        self.scsm = None
        self.thickness_cm = None
        
        for key, value in kwargs.items():
            if key == 'thickness_mm':
                self.thickness_cm = value / 10

    def setBackground(self, filename, block='IgRf'):
        self.scrf = SingleChannel(filename, block)
        return self.scrf.nu, self.scrf.y

    def setDifference(self, filename, block='AB'):
        self.diff = SingleChannel(filename, block)
        return self.diff.nu, self.diff.y

    def setSample(self, filename, block='IgSm'):
        self.scsm = SingleChannel(filename, block)
        return self.scsm.nu, self.scsm.y

    def calcAbsorptionCoeff(self):
        T = self.scsm.y / self.scrf.y
        T[T<0] = 1E-16
        self.transmission = Spectrum(self.scsm.nu, T)
        
        alpha = 1 / self.thickness_cm * np.log((1 - self.R)**2 / T)
        self.absorption = Spectrum(self.scsm.nu, alpha)
        
        return self.scsm.nu, alpha
    
    def calcDiff(self, ref):
        nu = self.absorption.nu
        alpha = self.absorption.y
        alpha_ref = ref.absorption.y
        diff = alpha - alpha_ref
        self.diff = Spectrum(nu, diff)
        
        return nu, diff
