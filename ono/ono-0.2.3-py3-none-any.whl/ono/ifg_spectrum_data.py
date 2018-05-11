# -*- coding: utf-8 -*-

### imports ###################################################################
import logging
import numpy as np

### logging ###################################################################
logging.getLogger('ftir').addHandler(logging.NullHandler())

###############################################################################
class FTIRData(object):
    '''Abstract class to keep track modification history
    '''
    def __init__(self, **kwargs):
        self.logger = logging.getLogger('ftir')

        self.parent = None
        self.modifications = []
        
        for key, value in kwargs.items():
            if key == 'parent':
                self.parent = value

        # inherits modifications from parent object
        if self.parent:
            self.modifications = list(self.parent.modifications)

    def __str__(self):
        m_list = []
        
        for m in self.modifications:
            m_str = ''
            
            if m[0] == 'boxcar':
                m_str = 'boxcar(' + str(m[1]) + ', ' + str(m[2]) + ')'
            elif m[0] == 'phase shift':
                m_str ='$\epsilon$ = ' + str(m[1])
            elif m[0] == 'truncate':
                m_str = 'truncate(' + str(m[1]) + ', ' + str(m[2]) + ')'
            elif m[0].find('IFFT') > 0:
                m_str = m[0]
            elif m[0].find('FFT') > 0:
                m_str = m[0]

            if m_str:
                m_list.append(m_str)

        mod_str = ', '.join(m_list)
        
        return mod_str

###############################################################################
class Interferogram(FTIRData):
    def __init__(self, **kwargs):
        super(Interferogram, self).__init__(**kwargs)

        self.dx_cm = 1
        flip = True
        roll = True
        self.y = []

        for key, value in kwargs.items():
            if key == 'dx_cm':
                self.dx_cm = value
            if key == 'flip':
                flip = value
            elif key == 'lwn':
                # spatial resolution is half the laser wavelength [cm]
                self.lwn = value
                self.lambda_laser_cm = 1 / self.lwn
                self.lambda_laser = self.lambda_laser_cm / 100
                self.dx_cm = self.lambda_laser_cm / 2
            elif key == 'roll':
                roll = value
            elif key == 'y':
                self.y = value

        self.N = len(self.y)
        self.bit_length = self.N.bit_length()

        # scan length [cm]
        self.L_cm = self.N * self.dx_cm
        self.logger.debug('scan length: L = %4.2f cm', self.L_cm)

        # search interferogram absolute maximum
        self.i0 = np.argmax(np.abs(self.y))
        I0 = self.y[self.i0]

        # flip sign, so that I0 > 0
        if flip and np.sign(I0) < 0:
            self.y = -self.y

        if roll:
            self.roll()

    @property
    def I0(self):
        '''I0: interferogram absolute maximum'''
        return self.y[0]

    def boxcar(self, N1):
        y = np.copy(self.y)
        y[N1:-N1] = 0

        ifg = Interferogram(y=y, dx_cm=self.dx_cm, parent=self)
        ifg.modifications.append(('boxcar', N1, N1))

        return ifg

    def roll(self):
        imax = np.argmax(self.y)
        
        if imax > 0:
            self.y = np.roll(self.y, -imax)

    def truncate(self, N1):
        y_L1 = self.y[-N1:]
        y_L2 = self.y[:N1]
        y = np.concatenate((y_L2, y_L1))

        ifg = Interferogram(y=y, dx_cm=self.dx_cm, parent=self)
        ifg.modifications.append(('truncate', N1, N1))

        return ifg
