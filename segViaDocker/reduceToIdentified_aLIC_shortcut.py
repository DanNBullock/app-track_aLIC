#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 10:58:25 2022

@author: dan
"""

import nibabel as nib
import os
import sys

sys.path.append('wma_pyTools')
startDir=os.getcwd()
#some how set a path to wma pyTools repo directory
#wmaToolsDir='../wma_pyTools'
#wmaToolsDir='..'
import os
#os.chdir(wmaToolsDir)
print(os.getcwd())
print(os.listdir())
import wmaPyTools.roiTools
import wmaPyTools.analysisTools
import wmaPyTools.segmentationTools
import wmaPyTools.streamlineTools
import wmaPyTools.visTools
import numpy as np
from dipy.io.streamline import load_tractogram, save_tractogram
import dipy.tracking.utils as ut
#os.chdir(startDir)

import re
import subprocess
import os
import json
import pandas as pd
import nibabel as nib
from nilearn.image import resample_to_img
from glob import glob
import shutil


#  The aLIC segmentation code, by default, saves the sub tracts out.
#  by directly loading these we can avoid having to load the potentially massive 
#  track.tck

#we'll just comment out the unnecessary steps

#load tractogram
tractogramDir='output'
#tckPath=os.path.join(tractogramDir,'track.tck')
#inputTractogram=nib.streamlines.load(tckPath)

#load classification
#outputWMCDir='bigwmc'
#classificationPath=os.path.join(outputWMCDir,'classification.mat')

#load and parse classification.mat
#classificationDict= wmaPyTools.streamlineTools.matWMC2dict(classificationPath)

#identify and locate the individual tcks
tractogramDir='output'
tcksInOutDir=glob(os.path.join(tractogramDir,'*.tck'))
#but we don't want the big track.tck
tcksInOutDir.remove('output/track.tck')
#now we pass those to our desired output tcks dir.

#make a directory just for the output tracts
tcksDir=os.path.join('tcks')
if not os.path.exists(tcksDir):
    os.makedirs(tcksDir)
#copy the files over
[shutil.copyfile(iSubTck, os.path.join(tcksDir,os.path.split(iSubTck)[1])) for iSubTck in tcksInOutDir]
 
reducedTckDir=os.path.join('reduced_Tck')
if not os.path.exists(reducedTckDir):
    os.makedirs(reducedTckDir)
streamsOut,dictOut= wmaPyTools.streamlineTools.inputTcks_to_WMCandTCK(tcksDir)   
#save the tractogram
save_tractogram(streamsOut,os.path.join(reducedTckDir,'track.tck'), bbox_valid_check=False)
#save the wmc
from scipy.io import savemat
#save down the classification structure
reducedWMCDir=os.path.join('reduced_wmc')
if not os.path.exists(reducedWMCDir):
    os.makedirs(reducedWMCDir)
    #savemat acts weird
savemat(os.path.join('wmc','classification.mat'),{ "classification": {"names": np.array(dictOut['names'], dtype=np.object), "index": dictOut['index'] }})
 


    
