# -*- coding: utf-8 -*-
"""
Created on Wed May  3 16:00:21 2017

@author: d.kelly
"""

import numpy as np
import csv
import matplotlib.pyplot as plt

def makeGaussian(A, mu, sigma):
    """Generate a Gaussian profile. 
    
    Generate a Gaussian described in a 2X101 array with x values in column 1 
    and y values in column 2
    A = amplitude of Gaussian
    mu = centre of Gaussian
    sigma = spread of Gaussian
    """
        
    wavelengths = np.arange(mu - 4 * sigma, mu + 4 * sigma, (8 * sigma)/101)
    spectrum = ( A * np.exp(
            - np.power((wavelengths - mu),2)/(2 * np.power(sigma,2))))
    spectrum = np.column_stack((wavelengths, spectrum))
    
    return spectrum
    
def readSpectrumFile(filename):
    """read a spectrum from a csv/tab delimited txt file, returning an array"""    
    
    sp = []
    
    # use ValueError to deal with varied header length/format
    with open(filename, 'r') as csvf:
        rdr = csv.reader(csvf, delimiter='\t')
        for row in rdr:
            try:
                sp.append([float(x.rstrip()) for x in row])
            except ValueError:
                continue
          
    spectrum = np.array(sp)
    # check array is right shape and throw error if not
    return spectrum
    
def displaySpectra(spectra):
    """display spectra input as a list on shared axes"""
    
    colList = ['r', 'g', 'b', 'm', 'c', 'y', 'k']
    for idx, spectrum in enumerate(spectra):
        #assign color
        c = colList[idx % len(colList)]
        plt.plot(spectrum[:,0], spectrum[:,1], c)
        
    plt.show()
    
def interpolateSpectrum(spectrum, dlambda):
    
    wlIn = spectrum[:,0]
    wlInterp = dlambda * ( np.arange( np.round(min(wlIn/dlambda)), 
                                                np.round(max(wlIn/dlambda))))
    spectrumIn = spectrum[:,1]                                                                                        
    
    interpSpectrum = np.column_stack((wlInterp, np.interp(wlInterp, wlIn, spectrumIn)))
    return interpSpectrum
    
def integrateSpectra(spectra, dlambda):
    """ take list of spectra, and return integral of their product over the largest possible range"""
    
    """
    spectra = list of Nx2 arrays describing filter or dye spectra, or laser wavelength profile
    dlambda = wavelength difference betweeen adjacent values in the spectra
    """
        
    lowerLimit = max( [min(spectrum[:,0]) for spectrum in spectra] )
    upperLimit = min( [max(spectrum[:,0]) for spectrum in spectra] )
    
    trimmedSpectra = [spectrum[(spectrum[:,0] >= lowerLimit) & (spectrum[:,0] <= upperLimit)] for spectrum in spectra]
    
    product = trimmedSpectra[0][:,1]
    for idx in np.arange(1,len(spectra)):
        product = np.multiply(product, trimmedSpectra[idx][:,1])
    
    integral = np.sum(product) * dlambda
    
    return integral
    
