# -*- coding: utf-8 -*-
"""
Created on Thu May  4 06:34:36 2017

@author: d.kelly
"""

import numpy as np
import utils


class Laser(object):
    """ A class defining a general laser source"""
    
    """
    channel = string descrbing laser channel, for reference
    centreWavelength = nominal wavelength of laser, in nm
    fwhmNm = (nominal) FWHM of laser about central wavelength - NOT SIGMA
    laserOutputPowerMw = measured output power after laser - for now, also after 
    laserProfile = wavelength profile of the laser"""
    
    channel = 'L000nm'
    centreWavelengthNm = 532
    fwhmNm = 3
    laserOutputPowerMw = 10
    laserProfile = utils.makeGaussian(laserOutputPowerMw, centreWavelengthNm, 
                                      fwhmNm / (2 * np.sqrt(2 * np.log(2))))
    
    def __init__(self, channel = None, centreWavelengthNm = None, fwhmNm = None, 
                 laserOutputPowerMw = None, laserProfile = None):
        if channel is not None:
             self.channel = channel
        if centreWavelengthNm is not None:
            self.centreWavelengthNm = centreWavelengthNm
        if fwhmNm is not None:
            self.fwhmNm = fwhmNm
        if laserOutputPowerMw is not None:
            self.setLaserOutputPower(laserOutputPowerMw)
        if laserProfile is not None:
            self.setLaserProfile(laserProfile)
        
        
    def setCentreWavelength(self, wavelength):
        self.centreWavelengthNm = wavelength
        sigma = self.fwhmNm / (2 * np.sqrt(2 * np.log(2)))
        self.laserProfile = utils.makeGaussian(self.laserOutputPowerMw, self.centreWavelengthNm, sigma)
        
    def setFWHM(self, fwhm):
        self.fwhmNm = fwhm
        sigma = self.fwhmNm / (2 * np.sqrt(2 * np.log(2)))
        self.laserProfile = utils.makeGaussian(self.laserOutputPowerMw, self.centreWavelengthNm, sigma)
        
    def setLaserOutputPower(self, power):
        self.laserOutputPowerMw = power
        sigma = self.fwhmNm / (2 * np.sqrt(2 * np.log(2)))
        self.laserProfile = utils.makeGaussian(self.laserOutputPowerMw, self.centreWavelengthNm, sigma)
        
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
            
    def displayLaserProfile(self):
        utils.displaySpectra([self.laserProfile])
            
#            
#l = Laser()
#l.setCentreWavelength(594)
#l.setFWHM(1.01)
#l.setLaserOutputPower(101)