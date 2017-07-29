# -*- coding: utf-8 -*-
"""
Created on Wed May  3 15:45:39 2017

@author: d.kelly

TODO: ERROR HANDLING!
"""

import numpy as np
import utils


class Dye(object):
    """ A class defining a general fluorescent dye. """
    
    """
    QY: fractional value for quantum yield. 
    epsilon: absorption coefficient at the longest wavelength absorption maximum in M^-1 cm^-1
    absorptionSpectrum: Nx2 array with wavelength in first column and absorption in the second. If a filename is passed, then absorption spectrum is read from this file. 
    emissionSpectrum: Nx2 array with wavelength in first column and emission in the second. If a filename is passed, then emission spectrum is read from this file. 
    """
    QY = 1
    epsilon = 120000
    absorptionSpectrum = utils.makeGaussian(1, 700, 5)
    emissionSpectrum = utils.makeGaussian(1, 720, 5)
    name = 'dummy700'


    def __init__(self, name = None, epsilon = None, qy = None, absSpectrum = None, emSpectrum = None):
        if epsilon is not None:
            self.epsilon = epsilon
        if qy is not None:
            self.QY = qy
        if absSpectrum is not None:
            self.setAbsorptionSpectrum(absSpectrum)
        if emSpectrum is not None:
            self.setEmissionSpectrum(emSpectrum)
        if name is not None:
            self.name = name
        
        
#    def readBothDyeSpectrumOneFile(self, filename):
#        exS = 1
#        emS = 1
#        return exS, emS
        
    def setName(self, name):
        self.name = name        
        
    def setQY(self, qy):
        qy = 0 if qy < 0 else 1 if qy > 1 else qy     # coerce qy to be 0<=qy<=1
        self.QY = qy
        
        
    def setEpsilon(self, epsilon):
        self.epsilon = epsilon
        

    def setEmissionSpectrum(self, emSpectrum):
        if isinstance(emSpectrum, np.ndarray):
                if emSpectrum.shape[1] == 2:
                    self.emissionSpectrum = emSpectrum
                else:
                    print('Error - wrong shape of spectrum array!')
                    # throw error - wrong shape of spectrum array!
        elif isinstance(emSpectrum, str):
            self.emissionSpectrum = utils.readSpectrumFile(emSpectrum)


    def setAbsorptionSpectrum(self, absSpectrum):
        if isinstance(absSpectrum, np.ndarray):
                if absSpectrum.shape[1] == 2:
                    self.absorptionSpectrum = absSpectrum
                else:
                    print('Error - wrong shape of spectrum array!')
                    # throw error - wrong shape of spectrum array!
        elif isinstance(absSpectrum, str):
            self.absorptionSpectrum = utils.readSpectrumFile(absSpectrum)
            
    def displaySpectra(self):
        utils.displaySpectra([utils.normaliseSpectrum(self.absorptionSpectrum), 
                              utils.normaliseSpectrum(self.emissionSpectrum)])