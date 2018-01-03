# -*- coding: utf-8 -*-
"""
Created on Thu May  4 07:59:37 2017

@author: d.kelly

TODO: support "compound" filters, e.g. in 532 emission
"""

import numpy as np
import utils


class InterferenceFilter(object):
    """ A ckass describing a spectral filter component of an optical system"""
    
    """ 
    name = description/part number of a particular filter
    transmissionSpectrum = Nx2 array describing the spectral response of the filter. If a path is passed, the spectum is read from a file
    """
    
    name = 'FF01-000/00'
    transmissionSpectrum = np.array([[x+500 for x in range(100)], 
                                     [1 * (x>50) for x in range(100)]]).T
    
    def __init__(self, name = None, spectrum = None):

        self.name = 'FF01-000/00'
        self.transmissionSpectrum = np.array([[x+500 for x in range(100)], 
                                     [1 * (x>50) for x in range(100)]]).T
                                     
        if name is not None:
            self.name = name
        if spectrum is not None:
            self.setTransmissionSpectrum(spectrum)
        
        
    def setName(self, name):
        self.name = name
        
    def getSpectrum(self):
        return self.transmissionSpectrum
        
    def setTransmissionSpectrum(self, spectrum):
        if isinstance(spectrum, np.ndarray):
                if spectrum.shape[1] == 2:
                    self.transmissionSpectrum = spectrum
                else:
                    print('Error - wrong shape of spectrum array!')
                    # throw error - wrong shape of spectrum array!
        elif isinstance(spectrum, str):
            self.transmissionSpectrum = utils.readSpectrumFile(spectrum)