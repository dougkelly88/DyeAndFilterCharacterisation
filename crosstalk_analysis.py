# -*- coding: utf-8 -*-
"""
Created on Thu May  4 18:24:42 2017

@author: d.kelly

Tools to investigate the suitability of optics to detect fluorescent signals 
in multiple channels. Crucially, we want to minimise crosstalk from other
fluorescent species than the one being interrogated. 


TODO: wavelength-dependent loss from other optics. Camera sensitivity?
TODO: error handling - suppress divide by zero warning for log10 step?
"""

import os
import numpy as np
import matplotlib.pyplot as plt

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
    """ display a heatmap showing the log10 of crosstalk contribution from each fluorescent species to total signal in each detection channel"""

    signals = []
    ch_labels = [x.channel for x in filtercubeList]
    dye_labels = [x.name for x in dyeList]

    
    for chidx, lsr in enumerate(lsrList):
        fc = filtercubeList[chidx]
        
        for dye in dyeList:
            dum1, dum2, signal = signalFromDyeXInChannelY(lsr, fc, dye)
#            dye_labels.append(dye.name)
#            ch_labels.append(lsr.channel)
            signals.append(signal)
            
    print(ch_labels)
    print(dye_labels)        
    print(signals)
    
    sigArray = np.array(signals).reshape([len(filtercubeList), len(dyeList)])
    totalSigs = np.sum(sigArray, 0)
    crosstalkMatrix = sigArray / totalSigs[:, None]
#    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.imshow(np.log10(crosstalkMatrix), cmap = 'Reds', interpolation='none')
    hax = plt.gca()
    hcbar = plt.colorbar()
    hcbar.ax.get_yaxis().labelpad = 15    
    hcbar.ax.set_ylabel('log_10 of crosstalk as fraction of signal', rotation=90)
    hax.set_xlabel('Detection channel')
    hax.set_ylabel('Dye contributing to signal')
    ch_labels.insert(0, '')   # hacky solution...
    dye_labels.insert(0, '')
    hax.set_xticklabels(ch_labels, rotation=90)
    hax.set_yticklabels(dye_labels)
    
    # handles maximising the image
    try:
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()   
    except:
        print('backend doesn''t support maximised screen in this implementation!')
    
    plt.show()
    
    return crosstalkMatrix
    

dyesPath = os.path.join((os.path.dirname(os.path.abspath(__file__)) ), 'Dye spectra')
filtersPath = os.path.join((os.path.dirname(os.path.abspath(__file__)) ), 'Filter spectra')


# seems a bit boilerplate-y? Work into a loop somehow?
""" 
Sources for dye data:
Atto general properties: https://www.atto-tec.com/fileadmin/user_upload/Katalog_Flyer_Support/Dye_Properties_01.pdf
Atto spectra: https://www.atto-tec.com/attotecshop/product_info.php?language=en&info=p117_ATTO-700.html
Alexa 405 absorption coefficient: http://www.atdbio.com/content/34/Alexa-dyes
Alexa 405 QY: http://confocal-microscopy-list.588098.n2.nabble.com/alexa-405-QY-td6913848.html
Alexa 405 spectra: https://www.chroma.com/spectra-viewer?fluorochromes=10533

Sources for filter spectra:
Semrock filters: http://www.laser2000.co.uk
Chroma 700 dichroics: emailed from Chroma
"""

dye405 = Dye(name = 'Alexa405', epsilon = 35000, qy = 0.54, 
             absSpectrum = os.path.join(dyesPath, 'Alexa405abs.txt'), 
             emSpectrum = os.path.join(dyesPath, 'Alexa405em.txt'))
          
dye532 = Dye(name = 'Atto532', epsilon = 115000, qy = 0.9, 
             absSpectrum = os.path.join(dyesPath, 'ATTO532_PBS.abs.txt'), 
             emSpectrum = os.path.join(dyesPath, 'ATTO532_PBS.ems.txt'))

dye594 = Dye(name = 'Atto594', epsilon = 120000, qy = 0.85, 
             absSpectrum = os.path.join(dyesPath, 'ATTO594_PBS.abs.txt'), 
             emSpectrum = os.path.join(dyesPath, 'ATTO594_PBS.ems.txt'))

dye633 = Dye(name = "Atto655", epsilon = 125000, qy = 0.3, 
          absSpectrum = os.path.join(dyesPath, 'ATTO655_PBS.abs.txt'), 
          emSpectrum = os.path.join(dyesPath, 'ATTO655_PBS.ems.txt') )        

dye700 = Dye(name = "Atto700", epsilon = 120000, qy = 0.25, 
          absSpectrum = os.path.join(dyesPath, 'ATTO700_PBS.abs.txt'), 
          emSpectrum = os.path.join(dyesPath, 'ATTO700_PBS.ems.txt') )         
          
l405 = Laser(channel = 'L405Nm', centreWavelengthNm = 405, fwhmNm = 0.01, 
             laserOutputPowerMw = 3)
             
l532 = Laser(channel = 'L532Nm', centreWavelengthNm = 532, fwhmNm = 0.01, 
             laserOutputPowerMw = 18)
             
l594 = Laser(channel = 'L594Nm', centreWavelengthNm = 594, fwhmNm = 0.01, 
             laserOutputPowerMw = 25)             
          
l633 = Laser(channel = 'L633Nm', centreWavelengthNm = 640, fwhmNm = 0.01, 
             laserOutputPowerMw = 30)
          
l700 = Laser(channel = 'L700Nm', centreWavelengthNm = 701, fwhmNm = 0.01, 
             laserOutputPowerMw = 30)
             
fc405 = FilterCube(channel = 'L405Nm', 
                   excitationFilter = ( 'FF01-390_40', os.path.join(filtersPath, 'FF01-390_40_Spectrum.txt') ), 
                   dichroicFilter = ( 'Di02-R405', os.path.join(filtersPath, 'Di02-R405_Spectrum.txt') ), 
                   emissionFilter = ( 'FF01-452_45', os.path.join(filtersPath, 'FF01-452_45_Spectrum.txt') ) )
                   
fc532 = FilterCube(channel = 'L532Nm', 
                   excitationFilter = ( 'FF01-532_3', os.path.join(filtersPath, 'FF01-532_3_spectrum.txt') ), 
                   dichroicFilter = ( 'Di02-R532', os.path.join(filtersPath, 'Di02-R532_Spectrum.txt') ), 
                   emissionFilter = ( 'FF01-562_40', os.path.join(filtersPath, 'FF01-562_40_spectrum.txt') ) )
                   
fc594 = FilterCube(channel = 'L594Nm', 
                   excitationFilter = ( 'FF01-591_6', os.path.join(filtersPath, 'FF01-591_6_Spectrum.txt') ), 
                   dichroicFilter = ( 'Di02-R594', os.path.join(filtersPath, 'Di02-R594_Spectrum.txt') ), 
                   emissionFilter = ( 'FF01-647_57', os.path.join(filtersPath, 'FF01-647_57_Spectrum.txt') ) )
             
fc633 = FilterCube(channel = 'L633Nm', 
                   excitationFilter = ( 'FF01-640_14', os.path.join(filtersPath, 'FF01-640_14_spectrum.txt') ), 
                   dichroicFilter = ( 'Di02-R635', os.path.join(filtersPath, 'Di02-R635_Spectrum.txt') ), 
                   emissionFilter = ( 'FF01-679_41', os.path.join(filtersPath, 'FF01-679_41_Spectrum.txt') ) )
                   
fc700old = FilterCube(channel = 'L700Nm', 
                   excitationFilter = ( 'FF01-692_40', os.path.join(filtersPath, 'FF01-692_40_Spectrum.txt') ), 
                   dichroicFilter = ( '725dcxxr', os.path.join(filtersPath, 'Chroma 725dcxxr.txt') ), 
                   emissionFilter = ( 'FF01-795_150', os.path.join(filtersPath, 'FF01-795_150_Spectrum.txt') ) )
                   
fc700new = FilterCube(channel = 'L700Nm', 
                   excitationFilter = ( 'FF01-692_40', os.path.join(filtersPath, 'FF01-692_40_Spectrum.txt') ), 
                   dichroicFilter = ( '725lpxr', os.path.join(filtersPath, 'Chroma 725lpxr.txt') ), 
                   emissionFilter = ( 'FF01-747_33', os.path.join(filtersPath, 'FF01-747_33_Spectrum.txt') ) )
                           

d, ch, sig = signalFromDyeXInChannelY(l700, fc700old, dye700)
d, ch, ct = signalFromDyeXInChannelY(l700, fc700old, dye633)

print('Crosstalk from 633 in old 700 channel as a fraction of signal:')
print(ct/sig)


d, ch, sig = signalFromDyeXInChannelY(l700, fc700new, dye700)
d, ch, ct = signalFromDyeXInChannelY(l700, fc700new, dye633)

print('Crosstalk from 633 in new 700 channel as a fraction of signal:')
print(ct/sig)

## debug
#d, ch, sig = signalFromDyeXInChannelY(l405, fc405, dye405)
#print('{} dye, detection channel {}, signal = {}'.format(d,ch,sig))

out = displayCrosstalkPlot([l405, l532, l594, l633, l700], [fc405, fc532, fc594, fc633, fc700old], [dye405, dye532, dye594, dye633, dye700])