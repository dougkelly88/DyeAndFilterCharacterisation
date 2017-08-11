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
                # test that [float...] is 2 elements; otherwise skip. Deals with odd numbers at bottom of some spectra files
                r = [float(x.rstrip()) for x in row]
                if len(r) == 2:
                    sp.append(r)
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
    """take input spectrum and interpolate to sample every dlambda - be careful of cases with spectra narrower than dlambda"""    
    
    wlIn = spectrum[:,0]
    wlInterp = dlambda * ( np.arange( np.floor(min(wlIn/dlambda)), 
                                                np.ceil(max(wlIn/dlambda))))
    spectrumIn = spectrum[:,1]                                                                                        
    
    interpSpectrum = np.column_stack((wlInterp, np.interp(wlInterp, wlIn, spectrumIn)))

    return interpSpectrum
    
def integrateSpectra(spectra, dlambda):
    """ take list of spectra, and return integral of their product over the largest possible range"""
    
    """
    spectra = list of Nx2 arrays describing filter or dye spectra, or laser wavelength profile
    dlambda = wavelength difference betweeen adjacent values in the spectra
    """

    lowerLimit = min( [min(spectrum[:,0]) for spectrum in spectra] )
    upperLimit = max( [max(spectrum[:,0]) for spectrum in spectra] )

    
    #trimmedSpectra = [spectrum[(spectrum[:,0] >= lowerLimit) & (spectrum[:,0] <= upperLimit)] for spectrum in spectra]
    trimmedSpectra = [padWithZeros(spectrum, lowerLimit, upperLimit) for spectrum in spectra]
#    for spectrum in trimmedSpectra:
#        plt.plot(spectrum[:,0], spectrum[:,1])
#    plt.title('Spectra for integration')
#    plt.show()
    
    product = trimmedSpectra[0][:,1]
    for idx in np.arange(1,len(spectra)):
        product = np.multiply(product, trimmedSpectra[idx][:,1])
        
        
    product = np.ones((trimmedSpectra[0][:,1].shape))
    for spectrum in trimmedSpectra:
        product = np.multiply(product, spectrum[:,1])
    
    
#    min_spectrum = min(np.asarray(trimmedSpectra), 1)
#    fig = plt.figure()        
#    lmbda = np.linspace(lowerLimit, upperLimit, num=1+(upperLimit-lowerLimit)/dlambda)    
#    print(lmbda.shape)    
#    print(product.shape)
#    
#    plt.plot(lmbda, product)
    
    integral = np.sum(product) * dlambda
#    print(product)
    
    return integral
    
def normaliseSpectrum(spectrum):
    """ Normalise maximum of spectrum to 1 """
    
    m = max(spectrum[:,1]);
    spectrum[:,1] = spectrum[:,1] / m;
    return spectrum;
    
def padWithZeros(spectrum, min_lambda, max_lambda):
    """ Pad spectra with zeros for undefined values between min and max """
    
    dl = np.diff(spectrum[:,0])[0]
    # TODO: check and throw error if dl isn't constant throughout spectrum
    min_included_l = min(spectrum[:,0])
    max_included_l = max(spectrum[:,0])
    l_low = np.linspace(min_lambda, (min_included_l - dl), int(((min_included_l - dl) - min_lambda)/dl + 1)).T
    l_high = np.linspace((max_included_l + dl), max_lambda, int((max_lambda - (max_included_l + dl))/dl + 1)).T
    pad_spectrum = np.concatenate([np.stack([l_low, np.zeros_like(l_low)], axis=1), 
                             spectrum, 
                             np.stack([l_high, np.zeros_like(l_high)], axis=1)])
                             
    return pad_spectrum 
    