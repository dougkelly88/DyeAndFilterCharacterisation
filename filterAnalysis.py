# -*- coding: utf-8 -*-
"""
Created on Tue May  2 12:32:25 2017

@author: d.kelly
"""

import numpy as np

class Dye(object):
    """ A class defining a general fluorescent dye. 
    QY is a fractional value for quantum yield. 
    epsilon is absorption coefficient at the longest wavelength absorption maximum in M^-1 cm^-1
    absorptionSpectrum is a Nx2 array with wavelength in first column and absorption in the second. If a filename is passed to constructor, then absorption spectrum is read from this file. 
    emissionSpectrum is a Nx2 array with wavelength in first column and emission in the second. If a filename is passed to constructor, then emission spectrum is read from this file. 
    """
    QY = 1
    epsilon = 30000
    absorptionSpectrum = np.zeros((1,2))
    emissionSpectrum = np.zeros((1,2))


    def __init__(self, epsilon = None, qy = None, absSpectrum = None, emSpectrum = None):
        if epsilon is not None:
            self.epsilon = epsilon
        if qy is not None:
            self.QY = qy
        if absSpectrum is not None:
            
        if emSpectrum is not None:
            if isinstance(emSpectrum, numpy.ndarray):
                if emSpectrum.shape[1] == 2:
                    self.emissionSpectrum = emSpectrum
                else:
                    print('Error - wrong shape of spectrum array!')
                    # throw error - wrong shape of spectrum array!
                    
        
    def readSingleDyeSpectrumFile(self, filename):
        spectrum = np.zeros((5,2))
        return spectrum
        
        
    def readBothDyeSpectrumFile(self, filename):
        exS = self.readSingleDyeSpectrumFile(filename)
        emS = self.readSingleDyeSpectrumFile(filename)
        return exS, emS
        
        
    def setQY(self, qy):
        qy = 0 if qy < 0 else 1 if qy > 1 else qy     
        self.QY = qy
        
        
    def setEpsioln(self, epsilon):
        self.epsilon = epsilon
        

    def setEmissionSpectrum(self, emSpectrum):
        if isinstance(emSpectrum, numpy.ndarray):
                if emSpectrum.shape[1] == 2:
                    self.emissionSpectrum = emSpectrum
                else:
                    print('Error - wrong shape of spectrum array!')
                    # throw error - wrong shape of spectrum array!
            elif isinstance(emSpectrum, str):
                self.emissionSpectrum = readSingleDyeSpectrumFile(emSpectrum)


    def setAbsorptionSpectrum(self, absSpectrum):
        if isinstance(absSpectrum, numpy.ndarray):
                if absSpectrum.shape[1] == 2:
                    self.absorptionSpectrum = absSpectrum
                else:
                    print('Error - wrong shape of spectrum array!')
                    # throw error - wrong shape of spectrum array!
            elif isinstance(absSpectrum, str):
                self.absorptionSpectrum = readSingleDyeSpectrumFile(absSpectrum)

class InterferenceFilt(object):
    """ A class defining a general interference filter"""
    
    def __init__(self):
        self.name = 'FF01 532/30'
        self.spectrum = np.zeros((1,2))
        
    def readSpectrumFile(self, filename):
        self.spectrum = np.zeros((5,2))
        
    def setName(self, name):
        self.name = name
        
class FilterCube(object):
    """ A class defining a general microscope filter cube"""
    
    def __init__(self):
        self.excitationFilter = InterferenceFilt()
        self.dichroicFilter = InterferenceFilt()
        self.emissionFilter = InterferenceFilt()
        self.channel = 'Lxxxnm'
        
    def setExcitationFilter(self, exFilt):
        # check that exFilt is correct type, otherwise return error        
        self.excitationFilter = exFilt
        
    def setEmissionFilter(self, emFilt):
        # check that exFilt is correct type, otherwise return error        
        self.emissionFilter = emFilt
        
    def setDichroicFilter(self, diFilt):
        # check that exFilt is correct type, otherwise return error        
        self.dichroicFilter = diFilt
        
    def setChannel(self, channel):
        self.channel = channel
        
class Laser(object):
    """ A class defining a general laser source"""
    
    def __init__(self):
        self.channel = 'Lxxxnm'
        self.centreWavelenghNm = 532
        self.fwhmNm = 3
        self.powerBeforeFiltersMw = 10
        self.laserProfile = np.zeros((1,2))
        
    def setCentreWL(self, wavelength):
        self.centreWavelengthNm = wavelength
        sigma = (1 / 2 * np.sqrt(2 * np.log(self.fwhm)))
        self.laserProfile = self.makeGaussian(self.centreWavelenghNm, sigma)
        
    def setFWHM(self, fwhm):
        self.fwhmNm = fwhm
        sigma = (1 / 2 * np.sqrt(2 * np.log(self.fwhm)))
        self.laserProfile = self.makeGaussian(self.centreWavelenghNm, sigma)
        
    def setChannel(self, channel):
        self.channel = channel
        
