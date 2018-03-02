# -*- coding: utf-8 -*-
"""
Created on Thu May  4 11:15:42 2017

@author: d.kelly
"""

import utils
from interferenceFilter import InterferenceFilter

class FilterCube(object):
    """ A class defining a general microscope filter cube"""
    
    """
    excitationFilter = (name, spectrum) tuple defining the excitation filter. Spectrum may be a Nx2 array or a path to the filter spectrum. 
    dichroicFilter = (name, spectrum) tuple defining the dichroic filter. Spectrum may be a Nx2 array or a path to the filter spectrum. 
    emissionFilter = (name, spectrum) tuple defining the emission filter. Spectrum may be a Nx2 array or a path to the filter spectrum. 
    channel = string desctbing the imaging channel corresponding to this cube in format "L<wavelength>Nm" for compatibility with instrument control. 
    """     
    
    def __init__(self, channel = None, excitationFilter = None, 
                 dichroicFilter = None, emissionFilter = None, 
                 doubleStackEmission = None):
                     
        self.excitationFilter = InterferenceFilter()
        self.dichroicFilter = InterferenceFilter()
        self.emissionFilter = InterferenceFilter()
        self.channel = 'Lxxxnm'   
        self.doubleStackEmission = False;
    
        if excitationFilter is not None:
            self.setExcitationFilter(excitationFilter)
        if dichroicFilter is not None:
            self.setDichroicFilter(dichroicFilter)
        if emissionFilter is not None:
            if doubleStackEmission is None:
                self.setEmissionFilter(emissionFilter)
            else:
                self.setEmissionFilter(emissionFilter, doubleStackEmission)
        if channel is not None:
            self.channel = channel

        
            
        
        
    def setExcitationFilter(self, exFilt):
        if isinstance(exFilt, InterferenceFilter):
            self.excitationFilter = exFilt
        else:
            self.excitationFilter = InterferenceFilter(exFilt[0], exFilt[1])
        
        
    def setEmissionFilter(self, emFilt, doubleStack): 
        if isinstance(emFilt, InterferenceFilter):
            self.emissionFilter = emFilt
        else:
            self.emissionFilter = InterferenceFilter(emFilt[0], emFilt[1],
                                                     doubleStack)
        
        
    def setDichroicFilter(self, diFilt):   
        if isinstance(diFilt, InterferenceFilter):
            self.dichroicFilter = diFilt
        else:
            self.dichroicFilter = InterferenceFilter(diFilt[0], diFilt[1])
        
        
    def setChannel(self, channel):
        self.channel = channel
        
    
    def displaySpectra(self):
        utils.displaySpectra([self.excitationFilter.getSpectrum(), self.dichroicFilter.getSpectrum(), self.emissionFilter.getSpectrum()])