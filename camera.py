# -*- coding: utf-8 -*-
"""
Created on Thu Jun  1 19:17:38 2017

@author: d.kelly
"""

import numpy as np
import utils

class Camera(object):
    """A class describinig a camera or other detector"""

    def __init__(self, name = None, qeCurve = None):
        
        self.name = 'AndorZyla5.5'
        self.qeCurve = utils.makeGaussian(0.8, 555, 100)
    
        if name is not None:
            self.name = name
        if qeCurve is not None:
            self.setQECurve(qeCurve)
            
    def displayQECurve(self):
        utils.displaySpectra([self.qeCurve])
        
    def setQECurve(self, qeCurve):
        if isinstance(qeCurve, np.ndarray):
                if qeCurve.shape[1] == 2:
                    self.qeCurve = qeCurve
                else:
                    print('Error - wrong shape of spectrum array!')
                    # throw error - wrong shape of spectrum array!
        elif isinstance(qeCurve, str):
            self.qeCurve = utils.readSpectrumFile(qeCurve)
            
        elif qeCurve == 1:
            """ for perfect detector, qECurve argument can be passed as 1 """
            mx = 1000
            mn = 1
            dl = 1
            l = np.linspace(mn, mx, round(mx-mn)/dl + 1)
            t = np.ones(round((mx-mn)/dl + 1))
            self.qeCurve = np.vstack((l,t)).T
            