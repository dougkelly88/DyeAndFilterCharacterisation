# -*- coding: utf-8 -*-
"""
Created on Thu May  4 06:34:36 2017

@author: d.kelly
"""

import numpy as np
import utils


class Laser(object):
    """ A class defining a general laser source"""
    
    """channel = string descrbing laser channel, for reference
    centreWavelength = nominal wavelength of laser, in nm
    fwhmNm = (nominal) FWHM of laser about central wavelength - NOT SIGMA
    laserOutputPowerMw = measured output power after laser
    laserProfile = wavelength profile of the laser"""
    
    channel = 'L000nm'
    centreWavelengthNm = 532
    fwhmNm = 3
    laserOutputPowerMw = 10
    laserProfile = utils.makeGaussian(laserOutputPowerMw, centreWavelengthNm, 
                                      (1 / 2 * np.sqrt(2 * np.log(fwhmNm))))
    
    def __init__(self, channel = None, centreWavelengthNm = None, fwhmNm = None, 
                 laserOutputPowerMw = None, laserProfile = None):
        if channel is not None:
             self.channel = channel
        if centreWavelengthNm is not None:
            self.centreWavelengthNm = centreWavelengthNm
        if fwhmNm is not None:
            self.fwhmNm = fwhmNm
        if laserOutputPowerMw is not None:
            self.laserOutputPowerMw =laserOutputPowerMw
        if laserProfile is not None:
            self.setLaserProfile(laserProfile)
        
        
    def setCentreWavelength(self, wavelength):
        self.centreWavelengthNm = wavelength
        sigma = (1 / 2 * np.sqrt(2 * np.log(self.fwhm)))
        self.laserProfile = self.makeGaussian(self.laserOutputPowerMw, self.centreWavelenghNm, sigma)
        
    def setFWHM(self, fwhm):
        self.fwhmNm = fwhm
        sigma = (1 / 2 * np.sqrt(2 * np.log(self.fwhm)))
        self.laserProfile = self.makeGaussian(self.laserOutputPowerMw, self.centreWavelenghNm, sigma)
        
    def setChannel(self, channel):
        self.channel = channel
        
    def setLaserProfile(self, laserProfile):
        if isinstance(laserProfile, np.ndarray):
                if laserProfile.shape[1] == 2:
                    self.laserProfile = laserProfile
                else:
                    print('Error - wrong shape of spectrum array!')
                    # throw error - wrong shape of spectrum array!
        elif isinstance(laserProfile, str):
            self.laserProfile = utils.readSpectrumFile(laserProfile)
            
    
            