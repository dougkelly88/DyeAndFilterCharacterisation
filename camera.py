# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 19:17:38 2017

@author: d.kelly
"""

import numpy as np
import utils

class Camera(object):
    """A class describinig a camera or other detector"""

    def __init__(self, name = None, qeCurve = None, sensorSizeXYMm = None, 
                 sensorSizeXYPix = None, ADUperE = None):
        
        self.name = 'AndorZyla5.5'
        self.qeCurve = utils.makeGaussian(0.8, 555, 100)
        self.sensorSizeXYMm = (16.6, 14.0)
        self.sensorAreaM2 = 2.32E-4
        self.sensorSizeXYPix = (2560, 2160)
        self.ADUperE = 0.45

        if name is not None:
            self.name = name
        if qeCurve is not None:
            self.setQECurve(qeCurve)
        if sensorSizeXYMm is not None:
            self.sensorSizeXYMm = self.setSensorSize(sensorSizeXYMm)
        if sensorSizeXYPix is not None:
            self.sensorSizeXYPix = sensorSizeXYPix
        if ADUperE is not None:
            self.ADUperE = ADUperE
            
            
    def displayQECurve(self):
        utils.displaySpectra([self.qeCurve])
        
    def setQECurve(self, qeCurve):
        if isinstance(qeCurve, np.ndarray):
                if qeCurve.shape[1] == 2:
                    self.qeCurve = qeCurve
                else:
                    print('Error - wrong shape of spectrum array!')
                    # throw error - wrong shape of spectrum array!
        elif isinstance(qeCurve, str):
            self.qeCurve = utils.readSpectrumFile(qeCurve)
            
        elif qeCurve == 1:
            """ for perfect detector, qECurve argument can be passed as 1 """
            mx = 1000
            mn = 1
            dl = 1
            l = np.linspace(mn, mx, round(mx-mn)/dl + 1)
            t = np.ones(round((mx-mn)/dl + 1))
            self.qeCurve = np.vstack((l,t)).T
            
    def getQEValue(self, wavelength):
        """ Return the value read from the QE curve at a given wavelength """
        if ((wavelength < np.min(self.qeCurve[:,0])) | (wavelength > np.max(self.qeCurve[:,0]))): 
            print('Requested value outside range!')
            return 0;
        spectrum = utils.interpolateSpectrum(self.qeCurve, 0.5)
        return spectrum[np.argmin(abs(spectrum[:,0] - wavelength)), 1]
        
            
    def setSensorSize(self, sensorSizeXYMm):
        """ take tuple containing sensor dimensions in mm (X,Y) and set size """
        self.sensorSizeXYMm = sensorSizeXYMm
        self.sensorAreaM2 = (sensorSizeXYMm[0] * sensorSizeXYMm[1] * 1E-6) 
        
            