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
    integratedPowermW = 1000
    spectrum = utils.makeGaussian(1, 550, 
                                      200 / (2 * np.sqrt(2 * np.log(2))))
    
    def __init__(self, name = None, integratedPowermW = None, spectrum = None):
        if name is not None:
             self.name = name
        if integratedPowermW is not None:
            self.integratedPowemrW = integratedPowermW
        if spectrum is not None:
            self.setSpectrum(spectrum)
        else:
            self.setSpectrum(self.spectrum)
        
    def setSpectrum(self, spectrum):
        if isinstance(spectrum, np.ndarray):
                if spectrum.shape[1] == 2:
                    dl = 0.5
                    norm_spectrum = utils.normaliseSpectrum(spectrum)
                    interp_spectrum = utils.interpolateSpectrum(norm_spectrum, dl)
                    integrated_spectrum = utils.integrateSpectra([interp_spectrum], dl)
                    out_spectrum = np.ones(interp_spectrum.shape)
                    out_spectrum[:,0] = interp_spectrum[:,0]
                    out_spectrum[:,1] = (self.integratedPowermW / integrated_spectrum) * interp_spectrum[:,1]
                    self.spectrum = out_spectrum
                else:
                    print('Error - wrong shape of spectrum array!')
                    # throw error - wrong shape of spectrum array!
        elif isinstance(spectrum, str):
            self.spectrum = utils.readSpectrumFile(spectrum)
            self.setSpectrum(self.spectrum)
            
    def displaySpectrum(self):
        utils.displaySpectra([self.spectrum])

    