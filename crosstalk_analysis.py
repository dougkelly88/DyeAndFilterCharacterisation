# -*- coding: utf-8 -*-
"""
Created on Thu May  4 18:24:42 2017

@author: d.kelly

TODO: wavelength-dependent loss from other optics. Camera sensitivity?
TODO: error handling
"""

import os

from dye import Dye
from laser import Laser
from filterCube import FilterCube
import utils


def signalFromDyeXInChannelY(laser, filtercube, dye):
    
    # error checking - verify input types
    if (laser.channel is not filtercube.channel):
        return 0, 0, 0  # throw more informative error...
    
    dye_label = dye.name
    channel_label = laser.channel
    
    # interpolate spectra to 0.5 nm resolution so that all spectra can be easily overlapped
    dlambda = 0.5
    lsr = utils.interpolateSpectrum(laser.laserProfile, dlambda)
    exFilt = utils.interpolateSpectrum(filtercube.excitationFilter.transmissionSpectrum, dlambda)
    emFilt = utils.interpolateSpectrum(filtercube.emissionFilter.transmissionSpectrum, dlambda)
    diFilt = utils.interpolateSpectrum(filtercube.dichroicFilter.transmissionSpectrum, dlambda)
    absSpectrum = utils.interpolateSpectrum(dye.absorptionSpectrum, dlambda)
    emSpectrum = utils.interpolateSpectrum(dye.emissionSpectrum, dlambda)
    
    # normalise dye absorption;  multiply absorption by absorption coeff. 
    # deal with the fact that on the excitation path we are concerned with how much light is REFLECTED by the dichroic - assume zero absorption    
    diFiltIn = diFilt
    diFiltIn[:,1] = 1 - diFilt[:,1]
    absSpectrum[:,1] = absSpectrum[:,1] / max(absSpectrum[:,1]) * dye.epsilon
    
    # normalise dye emission; multiply by QY
    emSpectrum[:,1] = emSpectrum[:,1] / max(emSpectrum[:,1]) * dye.QY
    
    # multiply together including laser, integrate over wavelengths (0.5 nm d(lambda)) - PAY ATTENTION TO LIMITS!      
    exSpectraList = [lsr, exFilt, diFiltIn, absSpectrum]
    emSpectraList = [emSpectrum, diFilt, emFilt]
    
        
    exTerm = utils.integrateSpectra(exSpectraList, dlambda)
    emTerm = utils.integrateSpectra(emSpectraList, dlambda)

    signal = exTerm * emTerm
    
    return dye_label, channel_label, signal

def displayCrosstalkPlot(lsrList, filtercubeList, dyeList):

    signals = []
    ch_labels = [x.channel for x in filtercubeList]
    dye_labels = [x.name for x in dyeList]
    
    for chidx, lsr in enumerate(lsrList):
        fc = filtercubeList[chidx]
        
        for dye in dyeList:
            dum1, dum2, signal = signalFromDyeXInChannelY(lsr, fc, dye)
            signals.append(signal)
            
    print(ch_labels)
    print(dye_labels)        
    print(signals)

dyesPath = os.path.join((os.path.dirname(os.path.abspath(__file__)) ), 'Dye spectra')
filtersPath = os.path.join((os.path.dirname(os.path.abspath(__file__)) ), 'Filter spectra')


# seems a bit boilerplate-y? Work into a loop somehow?
dye633 = Dye(name = "Atto655", epsilon = 125000, qy = 0.3, 
          absSpectrum = os.path.join(dyesPath, 'ATTO655_PBS.abs.txt'), 
          emSpectrum = os.path.join(dyesPath, 'ATTO655_PBS.ems.txt') )        

dye700 = Dye(name = "Atto700", epsilon = 120000, qy = 0.25, 
          absSpectrum = os.path.join(dyesPath, 'ATTO700_PBS.abs.txt'), 
          emSpectrum = os.path.join(dyesPath, 'ATTO700_PBS.ems.txt') )         
          
l633 = Laser(channel = 'L633Nm', centreWavelengthNm = 640, fwhmNm = 3, 
             laserOutputPowerMw = 30)
          
l700 = Laser(channel = 'L700Nm', centreWavelengthNm = 701, fwhmNm = 3, 
             laserOutputPowerMw = 30)
             
fc633 = FilterCube(channel = 'L633Nm', 
                   excitationFilter = ( 'FF01-640_14', os.path.join(filtersPath, 'FF01-640_14_spectrum.txt') ), 
                   dichroicFilter = ( 'Di02-R635', os.path.join(filtersPath, 'Di02-R635_Spectrum.txt') ), 
                   emissionFilter = ( 'FF01-679_41', os.path.join(filtersPath, 'FF01-679_41_Spectrum.txt') ) )
                   
#oldFc700 = Fil

#newFc700 = 
          
print('Signal from 633 dye in 633 channel:')
d, ch, sig = signalFromDyeXInChannelY(l633, fc633, dye633)
print(sig)

print('Crosstalk from 700 dye in 633 channel:')
d, ch, ct = signalFromDyeXInChannelY(l633, fc633, dye700)
print(ct)

print('Crosstalk as a fraction of signal:')
print(ct/sig)

displayCrosstalkPlot([l633], [fc633], [dye633, dye700])