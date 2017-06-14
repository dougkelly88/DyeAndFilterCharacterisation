# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 19:30:13 2017

@author: d.kelly
"""

import numpy as np
import utils

class Objective(object):
    """A class describinig an objective or other lossy optical component"""
    
    """THIS MODEL IGNORES ANY ANGLE DEPENDENT CHANGES TO TRANSMISSION SPECTRUM"""
    
    name = 'UPLSAPO20x'
    transmissionCurve = utils.makeGaussian(0.8, 555, 100)
    
    def __init__(self, name = None, transmissionCurve = None):
        if name is not None:
            self.name = name
        if transmissionCurve is not None:
            self.settransmissionCurve(transmissionCurve)
            
    def displaytransmissionCurve(self):
        utils.displaySpectra([self.transmissionCurve])
        
    def settransmissionCurve(self, transmissionCurve):
        if isinstance(transmissionCurve, np.ndarray):
                if transmissionCurve.shape[1] == 2:
                    self.transmissionCurve = transmissionCurve
                else:
                    print('Error - wrong shape of spectrum array!')
                    # throw error - wrong shape of spectrum array!
        elif isinstance(transmissionCurve, str):
            self.transmissionCurve = utils.readSpectrumFile(transmissionCurve)
            
        elif transmissionCurve == 1:
            """ for non-lossy objective, transmissionCurve argument can be passed as 1 """
            mx = 1000
            mn = 1
            dl = 1
            l = np.linspace(mn, mx, round(mx-mn)/dl + 1)
            t = np.ones(round((mx-mn)/dl + 1))
            self.transmissionCurve = np.vstack((l,t)).T
            