# -*- coding: utf-8 -*-
"""
Created on Thu May  4 18:24:42 2017

@author: d.kelly

Tools to investigate the suitability of optics to detect fluorescent signals 
in multiple channels. Crucially, we want to minimise crosstalk from other
fluorescent species than the one being interrogated. 


TODO: wavelength-dependent loss from other optics. Camera sensitivity?
TODO: error handling - suppress divide by zero warning for log10 step?
TODO: scrape all Semrock/Chroma spectra from the web? Would allow for optimisation of filterset...?
"""

import os
import numpy as np
import matplotlib.pyplot as plt

from dye import Dye
from laser import Laser
from filterCube import FilterCube
from camera import Camera
from objective import Objective
from broadbandSource import BroadbandSource
import utils

def signalFromDyeXInChannelY(source, filtercube, dye, objective, camera):    
    
    # interpolate spectra to 0.5 nm resolution so that all spectra can be easily overlapped
    dlambda = 0.5
    dye_label = dye.name
    if isinstance(source, BroadbandSource):
        channel_label = source.name
        lsr = utils.interpolateSpectrum(source.spectrum, dlambda)
    else:
        channel_label = source.channel
        lsr = utils.interpolateSpectrum(source.laserProfile, dlambda)

    exFilt = utils.interpolateSpectrum(filtercube.excitationFilter.getSpectrum(), dlambda)
    emFilt = utils.interpolateSpectrum(filtercube.emissionFilter.getSpectrum(), dlambda)
    diFilt = utils.interpolateSpectrum(filtercube.dichroicFilter.getSpectrum(), dlambda)
    absSpectrum = utils.interpolateSpectrum(dye.absorptionSpectrum, dlambda)
    emSpectrum = utils.interpolateSpectrum(dye.emissionSpectrum, dlambda)
    objSpectrum = utils.interpolateSpectrum(objective.transmissionCurve, dlambda)
    camQE = utils.interpolateSpectrum(camera.qeCurve, dlambda)
    
    # normalise dye absorption
    # deal with the fact that on the excitation path we are concerned with how much light is REFLECTED by the dichroic - assume zero absorption    
    diFiltIn = np.zeros(diFilt.shape)
    diFiltIn[:,0] = diFilt[:,0]
    diFiltIn[:,1] = 1 - diFilt[:,1]
    absSpectrum[:,1] = absSpectrum[:,1] / max(absSpectrum[:,1]) 
    
    # normalise dye emission
    emSpectrum[:,1] = emSpectrum[:,1] / max(emSpectrum[:,1])
    
    # multiply together including laser, integrate over wavelengths (0.5 nm d(lambda)) - PAY ATTENTION TO LIMITS!      
    exSpectraList = [lsr, exFilt, diFiltIn, absSpectrum, objSpectrum]
    emSpectraList = [emSpectrum, diFilt, emFilt, camQE, objSpectrum]
    
        
    # integrate spectra and multiply by absorption coeff and QY respectively
    exTerm = utils.integrateSpectra(exSpectraList, dlambda) * dye.epsilon
    emTerm = utils.integrateSpectra(emSpectraList, dlambda) * dye.QY

    signal = exTerm * emTerm
    
    return dye_label, channel_label, signal

def displayCrosstalkPlot(lsrList, filtercubeList, dyeList, objective, camera, log_colour=True, title='Crosstalk'):
    """ display a heatmap showing the log10 of crosstalk contribution from each fluorescent species to total signal in each detection channel"""

    signals = []
    ch_labels = [x.channel for x in filtercubeList]
    dye_labels = [x.name for x in dyeList]

    
    for chidx, lsr in enumerate(lsrList):
        fc = filtercubeList[chidx]
        
        for dye in dyeList:
            dum1, dum2, signal = signalFromDyeXInChannelY(lsr, fc, dye, 
                                                          objective, camera)
            signals.append(signal)
            
               
    sigArray = np.array(signals).reshape([len(filtercubeList), len(dyeList)])
    totalSigs = np.sum(sigArray, 1)
    crosstalkMatrix = sigArray / totalSigs[:, None]
#    plt.rc('text', usetex=True)
    hfig = plt.figure();
    plt.rc('font', family='serif')
    if log_colour:
        plt.imshow(np.log10(crosstalkMatrix), cmap = 'Reds', interpolation='none')
        clbl = 'log_10 of crosstalk as fraction of signal'
    else:
        plt.imshow(crosstalkMatrix, cmap = 'Reds', interpolation='none')
        clbl = 'crosstalk as fraction of signal'
    plt.title(title)
    hax = hfig.gca()
    hcbar = plt.colorbar()
    hcbar.ax.get_yaxis().labelpad = 15    
    hcbar.ax.set_ylabel(clbl, rotation=90)
    hax.set_xlabel('Detection channel')
    hax.set_ylabel('Dye contributing to signal')
    ch_labels.insert(0, '')   # hacky solution...
    dye_labels.insert(0, '')
    hax.set_xticklabels(ch_labels, rotation=90)
    hax.set_yticklabels(dye_labels)
    
    # add data labels
    for x in range(len(ch_labels) - 1):
        for y in range(len(dye_labels) - 1):
            plt.text(x,y,'{:0.2f}'.format(crosstalkMatrix[x,y]), 
                     horizontalalignment='center', 
                     verticalalignment='center', 
                     color = 'c')
    
    # handles maximising the image
#    try:
#        figManager = plt.get_current_fig_manager()
#        figManager.window.showMaximized()   
#    except:
#        print('backend doesn''t support maximised screen in this implementation!')
#   
    
    plt.show()
    
    return crosstalkMatrix
         

def showDyeEmissionEnclosedByFilters(dye, filtercube, objective, camera, title='dummy title'):
    """Given dye and filtercube, give visual indication of overlap"""
    
    dlambda = 0.5
    dem = utils.interpolateSpectrum(dye.emissionSpectrum, dlambda)
    fem = utils.interpolateSpectrum(filtercube.emissionFilter.getSpectrum(), dlambda)
    fdiem = utils.interpolateSpectrum(filtercube.dichroicFilter.getSpectrum(), dlambda)
    spectra = [dem, fem, fdiem]
    
    lowerLimit = max( [min(spectrum[:,0]) for spectrum in spectra] )
    upperLimit = min( [max(spectrum[:,0]) for spectrum in spectra] )
    
    trimmedSpectra = [spectrum[(spectrum[:,0] >= lowerLimit) & (spectrum[:,0] <= upperLimit)] for spectrum in spectra]

    ovrlp = np.ones((trimmedSpectra[0][:,1].shape))
    
    for spectrum in trimmedSpectra:
        ovrlp = np.multiply(ovrlp, spectrum[:,1])
    
    hfig = plt.figure()
    plt.title(filtercube.channel + ' ' + title)
    plt.ylabel('Transmission (or normalised emission)')
    plt.xlabel('Wavelength, nm')
    utils.displaySpectra(trimmedSpectra)
    plt.fill_between(trimmedSpectra[0][:,0], ovrlp)
    plt.legend(['Dye emission', 'Emission filter', 'Dichroic filter'], loc='upper right')
        
    return np.sum(ovrlp)*dlambda

def calcLeakage(source, filtercube, obj):
    """Given a set of filters in a cube and a source spectrum, how excitation light is detected by the camera? """
    
    dl = 0.5
    if isinstance(source, BroadbandSource):
        s = utils.interpolateSpectrum(source.spectrum, dl)
    else:
        s = utils.interpolateSpectrum(source.laserProfile, dl)
    ex = utils.interpolateSpectrum(filtercube.excitationFilter.getSpectrum(), dl)
    di = utils.interpolateSpectrum(filtercube.dichroicFilter.getSpectrum(), dl)
    em = utils.interpolateSpectrum(filtercube.emissionFilter.getSpectrum(), dl)
    o = utils.interpolateSpectrum(obj.transmissionCurve, dl)
    diIn = np.zeros_like(di)
    diIn[:,0] = di[:,0]
    diIn[:,1] = 1 - di[:,1]
    
    spList = [s, ex, diIn, o, o, di, em]
    
    leakage = utils.integrateSpectra(spList, dl)
    
    return leakage

dyesPath = os.path.join((os.path.dirname(os.path.abspath(__file__)) ), 'Dye spectra')
filtersPath = os.path.join((os.path.dirname(os.path.abspath(__file__)) ), 'Filter spectra')
opticsPath = os.path.join((os.path.dirname(os.path.abspath(__file__)) ), 'Optics spectra')
cameraPath = os.path.join((os.path.dirname(os.path.abspath(__file__)) ), 'Camera spectra')
sourcesPath = 'Source spectra/'
#
#
## seems a bit boilerplate-y? Work into a loop somehow?
#""" 
#Sources for dye data:
#Atto general properties: https://www.atto-tec.com/fileadmin/user_upload/Katalog_Flyer_Support/Dye_Properties_01.pdf
#Atto spectra: https://www.atto-tec.com/attotecshop/product_info.php?language=en&info=p117_ATTO-700.html
#Alexa 405 absorption coefficient: http://www.atdbio.com/content/34/Alexa-dyes
#Alexa 405 QY: http://confocal-microscopy-list.588098.n2.nabble.com/alexa-405-QY-td6913848.html
#Alexa 405 spectra: https://www.chroma.com/spectra-viewer?fluorochromes=10533
#
#Sources for filter spectra:
#Semrock filters: http://www.laser2000.co.uk
#Chroma 700 dichroics: emailed from Chroma
#"""
#
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
             
bb = BroadbandSource(name='Thorlabs HPLS343, 3mm LLG',  
                      integratedPowermW=4000.0, 
                      spectrum=os.path.join(sourcesPath, 'Thorlabs Plasma Source.txt'))
             
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
                   
fc405multi = FilterCube(channel = 'L405Nm', 
                   excitationFilter = ( 'FF01-390_40', os.path.join(filtersPath, 'FF01-390_40_Spectrum.txt') ), 
                   dichroicFilter = ( 'Chroma multiedge', os.path.join(filtersPath, 'Chroma ZT405-532-594-640-701rpc.txt') ), 
                   emissionFilter = ( 'FF01-452_45', os.path.join(filtersPath, 'FF01-452_45_Spectrum.txt') ) )
                   
fc532multi = FilterCube(channel = 'L532Nm', 
                   excitationFilter = ( 'FF01-532_3', os.path.join(filtersPath, 'FF01-532_3_spectrum.txt') ), 
                   dichroicFilter = ( 'Chroma multiedge', os.path.join(filtersPath, 'Chroma ZT405-532-594-640-701rpc.txt') ), 
                   emissionFilter = ( 'FF01-562_40', os.path.join(filtersPath, 'FF01-562_40_spectrum.txt') ) )
                   
fc594multi = FilterCube(channel = 'L594Nm', 
                   excitationFilter = ( 'FF01-591_6', os.path.join(filtersPath, 'FF01-591_6_Spectrum.txt') ), 
                   dichroicFilter = ( 'Chroma multiedge', os.path.join(filtersPath, 'Chroma ZT405-532-594-640-701rpc.txt') ), 
                   emissionFilter = ( 'FF01-647_57', os.path.join(filtersPath, 'FF01-647_57_Spectrum.txt') ) )
             
fc633multi = FilterCube(channel = 'L633Nm', 
                   excitationFilter = ( 'FF01-640_14', os.path.join(filtersPath, 'FF01-640_14_spectrum.txt') ), 
                   dichroicFilter = ( 'Chroma multiedge', os.path.join(filtersPath, 'Chroma ZT405-532-594-640-701rpc.txt') ), 
                   emissionFilter = ( 'FF01-679_41', os.path.join(filtersPath, 'FF01-679_41_Spectrum.txt') ) )
                   
fc700multi = FilterCube(channel = 'L700Nm', 
                   excitationFilter = ( 'FF01-692_40', os.path.join(filtersPath, 'FF01-692_40_Spectrum.txt') ), 
                   dichroicFilter = ( 'Chroma multiedge', os.path.join(filtersPath, 'Chroma ZT405-532-594-640-701rpc.txt') ), 
                   emissionFilter = ( 'FF01-747_33', os.path.join(filtersPath, 'FF01-747_33_Spectrum.txt') ) )


#
#laser_list = [l405, l532, l594, l633, l700]
#fc_list = [fc405, fc532, fc594, fc633, fc700new]
#dye_list = [dye405, dye532, dye594, dye633, dye700]
#multi_fc_list = [fc405multi, fc532multi, fc594multi, fc633multi, fc700multi]

                   
                   
camera = Camera(name = 'Andor Zyla 5.5', qeCurve = 1)

objective = Objective(name = 'Olympus UPLANSAPO20x 0.75NA', 
                      transmissionCurve = os.path.join(opticsPath, 'Olympus UPLANSAPO20x.txt'))

nobj = Objective(name = 'Nikon CFISuperFluor 0.5NA', 
                      transmissionCurve = os.path.join(opticsPath, 'Nikon CFISuperFluor10x.txt'))

#ratios = []
#ch_labels = []
#
#laser_list = [l405, l532, l594, l633, l700]
#fc_list = [fc405, fc532, fc594, fc633, fc700new]
#dye_list = [dye405, dye532, dye594, dye633, dye700]
#source_list = [bb, bb, bb, bb, bb]
#
#for l, bbb, fc, dy in zip(laser_list, source_list, fc_list, dye_list):
#    d, ch, sig_new = signalFromDyeXInChannelY(bbb, fc, dy, objective, camera)
#    print(ch)
#    print('broadband signal = {:0.3f}'.format(sig_new))
#    d, ch, sig_old = signalFromDyeXInChannelY(l, fc, dy, objective, camera)
#    print('laser signal = {:0.3f}'.format(sig_old))
#    
#    ratios.append(sig_new/sig_old)
#    ch_labels.append(ch)
#    
#fig3 = plt.figure();
#plt.bar([1, 2, 3, 4, 5], 
#        ratios, 
#        tick_label=ch_labels, 
#        align='center')
#plt.ylabel('Fractional signal')
#plt.show()

                           
#
#d, ch, sig = signalFromDyeXInChannelY(l700, fc700old, dye700)
#d, ch, ct = signalFromDyeXInChannelY(l700, fc700old, dye633)
#
#print('Crosstalk from 633 in old 700 channel as a fraction of signal:')
#print(100*ct/sig)
#
#
#d, ch, sig = signalFromDyeXInChannelY(l700, fc700new, dye700)
#d, ch, ct = signalFromDyeXInChannelY(l700, fc700new, dye633)
#
#print('Crosstalk from 633 in new 700 channel as a fraction of signal:')
#print(100*ct/sig)
#
### debug
###d, ch, sig = signalFromDyeXInChannelY(l405, fc405, dye405)
###print('{} dye, detection channel {}, signal = {}'.format(d,ch,sig))
##
##out = displayCrosstalkPlot([l405, l532, l594, l633, l700], [fc405, fc532, fc594, fc633, fc700new], [dye405, dye532, dye594, dye633, dye700])

#zip()
#signalFromDyeXInChannelY(l405, fc405, dye405, objective, camera)
#
#ratios = []
#ch_labels = []
#
#for l, f_old, f_new, dy in zip(laser_list, fc_list, multi_fc_list, dye_list):
#    d, ch, sig_new, prodex1, prodem1 = signalFromDyeXInChannelY(l, f_new, dy, objective, camera)
#    d, ch, sig_old, prodex2, prodem2 = signalFromDyeXInChannelY(l, f_old, dy, objective, camera)
#    ol1, dum1em = show_dye_emission_enclosed_by_filters(dy, f_old, objective, camera)
#    ol2, dum2em = show_dye_emission_enclosed_by_filters(dy, f_new, objective, camera)
#    print(ch)
#    print(sig_new/sig_old)
#    print('ol1 = {:0.3f}'.format(ol1 * dy.QY))
#    print('ol2 = {:0.3f}'.format(ol2 * dy.QY))
#    print('Ratio of new:old emission overlaps = {}\n\n'.format(ol2/ol1))
#    ratios.append(ol2/ol1)