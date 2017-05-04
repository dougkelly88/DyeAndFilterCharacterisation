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
    
    with open(filename, 'r') as csvf:
        rdr = csv.reader(csvf, delimiter='\t')
        for row in rdr:
            if (row[0] == 'wavelength') or (row[0] == 'nm'):
                continue
            else:
                sp.append([float(x) for x in row])
            
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