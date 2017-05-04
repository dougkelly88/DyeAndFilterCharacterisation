# -*- coding: utf-8 -*-
"""
Created on Thu May  4 18:24:42 2017

@author: d.kelly

TODO: wavelength-dependent loss from other optics. Camera sensitivity?
"""

import numpy as np

from dye import Dye
from interferenceFilter import interferenceFilter
from laser import Laser
from filterCube import FilterCube
import utils


def signalFromDyeXInChannelY(laser, filtercube, dye):
    
    # error checking - verify input types
    if (laser.channel is not filtercube.channel):
        return 0, 0, 0
    
    dye_label = dye.name
    channel_label = laser.channel
    
    # interpolate spectra to 0.5 nm resolution
    dlambda = 0.5
    lsr = utils.interpolateSpectrum(laser.laserProfile, dlambda)
    exFilt = utils.interpolateSpectrum(filtercube.excitationFilter, dlambda)
    emFilt = utils.interpolateSpectrum(filtercube.emissionFilter, dlambda)
    diFilt = utils.interpolateSpectrum(filtercube.dichroicFilter, dlambda)
    absSpectrum = utils.interpolateSpectrum(dye.absorptionSpectrum, dlambda)
    emSpectrum = utils.interpolateSpectrum(dye.emissionSpectrum, dlambda)
    
    # normalise excitation and dichroic filters and dye absorption;  multiply absorption by absorption coeff. 
    exFilt[:,2] = exFilt[:,2] / max(exFilt[:,2])
    diFilt[:,2] = diFilt[:,2] / max(diFilt[:,2])
    # deal with the fact that on the excitation path we are concerned with how much light is REFLECTED by the dichroic - assume zero absorption    
    diFiltIn = diFilt
    diFiltIn[:,1] = 1 - diFilt[:,1]
    absSpectrum[:,2] = absSpectrum[:,2] / max(absSpectrum[:,2]) * dye.epsilon
    
    # normalise dichroic and emission filters and dye emission; multiply by QY
    emFilt[:,2] = emFilt[:,2] / max(emFilt[:,2])
    emSpectrum[:,2] = emSpectrum[:,2] / max(emSpectrum[:,2]) * dye.QY
    
    # multiply together including laser, integrate over wavelengths (0.5 nm d(lambda)) - PAY ATTENTION TO LIMITS!
#    exTermLimits = ( max( [ min(exFilt[:,0]), min(diFilt[:,0]), min(absSpectrum[:,0]), min(lsr[:,0]) ] ), 
#                          min( [ max(exFilt[:,0]), max(diFilt[:,0]), max(absSpectrum[:,0]), max(lsr[:,0]) ] ) )
#   
#    exTermIntegrand = ( lsr[((lsr[:,0] >= exTermLimits[0]) & (lsr[:,0] <= exTermLimits[1])), 1] * 
#        exFilt[((exFilt[:,0] >= exTermLimits[0]) & (exFilt[:,0] <= exTermLimits[1])), 1] * 
#        diFilt[((diFilt[:,0] >= exTermLimits[0]) & (diFilt[:,0] <= exTermLimits[1])), 1] * 
#        absSpectrum[((absSpectrum[:,0] >= exTermLimits[0]) & (absSpectrum[:,0] <= exTermLimits[1])), 1]
        
    exSpectraList = [lsr, exFilt, diFiltIn, absSpectrum]
    emSpectraList = [emSpectrum, diFilt, emFilt]
    
        
    exTerm = utils.integrateSpectra(exSpectraList, dlambda)
    emTerm = utils.integrateSpectra(emSpectraList, dlambda)

    signal = exTerm * emTerm
    
    return dye_label, channel_label, signal


