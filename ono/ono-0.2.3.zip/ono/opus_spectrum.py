# -*- coding: utf-8 -*-

### imports from ##############################################################
from .bruker_opus_filereader import OpusReader

###############################################################################
class OpusSpectrum:
    def __init__(self, filename):
        self.sample = OpusReader(filename)
        self.sample.readDataBlocks()

        # spectra
        self.ab = self.scrf = self.scsm = None

        # first and last wavenumber
        self.fxv = self.lxv = None

        for key, value in self.sample.items():
            if key == 'AB':
                self.ab = value

                self.fxv = self.sample['AB Data Parameter']['FXV']
                self.lxv = self.sample['AB Data Parameter']['LXV']

            elif key == 'ScRf':
                self.scrf = value

                if not self.fxv:
                    self.fxv = self.sample['ScRf Data Parameter']['FXV']
                    self.lxv = self.sample['ScRf Data Parameter']['LXV']

            elif key == 'ScSm':
                self.scsm = value

                if not self.fxv:
                    self.fxv = self.sample['ScSm Data Parameter']['FXV']
                    self.lxv = self.sample['ScSm Data Parameter']['LXV']

        # wavenumbers
        self.wavenumbers = self.sample['WN']
