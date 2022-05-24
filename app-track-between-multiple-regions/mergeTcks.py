#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 17 13:31:27 2022

@author: dan
"""

import os
import sys

sys.path.append('wma_pyTools')
#startDir=os.getcwd()
#some how set a path to wma pyTools repo directory
#wmaToolsDir='wma_pyTools'
#wmaToolsDir='..'
#os.chdir(wmaToolsDir)
print(os.getcwd())
print(os.listdir())
import wmaPyTools.roiTools
import wmaPyTools.analysisTools
import wmaPyTools.segmentationTools
import wmaPyTools.streamlineTools
import wmaPyTools.visTools

#os.chdir(startDir)

import os
import json
import numpy as np
import nibabel as nib
from glob import glob
from dipy.io.streamline import load_tractogram, save_tractogram

#tcksORPaths=os.path.join('output')

#currently just being output to the app directory

tckFilePaths=glob(os.path.join('*.tck'))

outStatefulTractogram, wmc_Dict=wmaPyTools.streamlineTools.inputTcks_to_WMCandTCK(tckFilePaths,names=None)

save_tractogram(outStatefulTractogram, os.path.join('track.tck'))