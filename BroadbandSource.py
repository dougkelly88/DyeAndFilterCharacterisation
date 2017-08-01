# -*- coding: utf-8 -*-
"""
Created on Tue Aug  1 18:35:15 2017

@author: d.kelly
"""

import numpy as np
import utils


class BroadbandSource(object):
    """ A class defining a general broadband light source"""
    
    """
    name = string descrbing the source, for reference
    integratedPowerW = power integrated across the spectrum at the coupled output
    spectrum = normalised wavelength profile of the source"""
    
    name = 'lamp'
    integratedPowerW = 1
    spectrum = utils.makeGaussian(1, 550, 
                                      200 / (2 * np.sqrt(2 * np.log(2))))
    
    def __init__(self, name = None, integratedPowerW = None, spectrum = None):
        if name is not None:
             self.name = name
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