#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 16 11:34:47 2022

@author: dan
"""


import os
import sys

sys.path.append('wma_pyTools')
#startDir=os.getcwd()
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

#os.chdir(startDir)

import os
import json
import numpy as np
import nibabel as nib


# load inputs from config.json
with open('config.json') as config_json:
	config = json.load(config_json)

outDir='output/'
if not os.path.exists(outDir):
    os.makedirs(outDir)
if not os.path.exists(outDir+'/ROIS'):
    os.makedirs(outDir+'/ROIS')
#set to freesurfer output path for this subject
fsPath=config['freesurfer']
#you may need to convert the .mgz files to .nii.gz using the mr_convert command
#also, you may need to rename the subsequent aparcDk atlas file to it's standard name:
atlasName='aparc+aseg'
try:
    inputAtlas=nib.load(os.path.join(fsPath,'mri/'+atlasName+'.nii.gz'))
except:
    #can nibael handle mgz?
    inputAtlas=nib.load(os.path.join(fsPath,'mri/'+atlasName+'.mgz'))
inputAtlas=wmaPyTools.roiTools.inflateAtlasIntoWMandBG(inputAtlas, 1)
# lookupTablePath=config['lookupTable']
# lookupTable=pd.read_csv(lookupTablePath)

#set this to the path of the t1 for 
# refT1Path=config['T1']
# refAnatT1=nib.load(refT1Path)
# #for high res unaligned?
# refAnatT1 = nib.nifti1.Nifti1Image(refAnatT1.get_data(), np.round(refAnatT1.affine,2), refAnatT1.header)

sideList=['left','right']
for iIndex,iSide in enumerate(sideList):
    if iSide=='left':
        sideLabel=1000
        #extract spine ROI
    elif iSide=='right':
        sideLabel=2000
        #extract spine ROI
    
    #Endpoint ROIs
    #these have to be labeled ROI_1, ROI_2, etc for the segmentation code
    
    #Frontal ROIs
    frontalLabels=np.add([32, 28, 27, 26, 24, 20, 19, 18, 14, 12, 3, 2],sideLabel)
    frontalROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,frontalLabels)
    nib.save(nib.nifti1.Nifti1Image(frontalROI.get_fdata(), frontalROI.affine),outDir+'/ROIS/ROI_'+str(((iIndex+1)*2)-1) +'.nii.gz')
   
    spinoThalLabels=[[9, 10, 16, 28],[48, 49, 16, 60]]
    spinoThalROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,spinoThalLabels[iIndex])
    nib.save(nib.nifti1.Nifti1Image(spinoThalROI.get_fdata(), spinoThalROI.affine),outDir+'/ROIS/ROI_'+str((iIndex+1)*2) +'.nii.gz')
   
    #PRIMARY ROI
    #get the caudate. This will serve as the medial influence
    caudateLabels=[11,50]
    caudateROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,caudateLabels[iIndex])
    #get the putamen and globus palladus, these will be the lateral influences
    palPutLabels=[[12,13],[51,52]]
    palPutROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,palPutLabels[iIndex])
    #get the white matter labels as well
    wmLabels=[2,41]
    wmROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,wmLabels[iIndex])
    #intersect the inflated palPutROI with the inflated caudate
    roiInflateIntersection=wmaPyTools.roiTools.findROISintersection([caudateROI,palPutROI],inflateiter=11)
    #find the intersection of this with the white matter
    putativeRoughIC=wmaPyTools.roiTools.findROISintersection([roiInflateIntersection,wmROI],inflateiter=0)
    #apply anterior and posterior constraints
    #was the anterior the putamen or the caudate
    anteriorPutBorder=wmaPyTools.roiTools.planarROIFromAtlasLabelBorder(inputAtlas,palPutLabels[iIndex], 'anterior')
    #anterior of the brainstem border
    anteriorBrainstemBorder=wmaPyTools.roiTools.planarROIFromAtlasLabelBorder(inputAtlas,16, 'anterior')
    #cut the roi to return the constrained version of the IC
    #using the anterior border
    anteriorCutIC=wmaPyTools.roiTools.sliceROIwithPlane(putativeRoughIC,anteriorPutBorder,'posterior')
    #using the posterior border
    fullCutIC=wmaPyTools.roiTools.sliceROIwithPlane(anteriorCutIC,anteriorBrainstemBorder,'anterior')
    nib.save(nib.nifti1.Nifti1Image(fullCutIC.get_fdata(), fullCutIC.affine),outDir+'/ROIS/fullCutIC11_ROI_'+iSide+'.nii.gz')
   
    #get the DE. This will medialROI 
    deLabels=[28,60]
    deROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,deLabels[iIndex])
    #get the putamen and globus palladus
    palPutLabels=[[12,13],[51,52]]
    palPutROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,palPutLabels[iIndex])
    #get the white matter labels as well
    wmLabels=[2,41]
    wmROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,wmLabels[iIndex])
    #intersect the inflated palPutROI with the inflated 
    roiInflateIntersection=wmaPyTools.roiTools.findROISintersection([deROI,palPutROI],inflateiter=12)
    #find the intersection of this with the white matter
    ventAlicROI=wmaPyTools.roiTools.findROISintersection([roiInflateIntersection,wmROI],inflateiter=0)
    nib.save(nib.nifti1.Nifti1Image(ventAlicROI.get_fdata(), ventAlicROI.affine),outDir+'/ROIS/ventAlicROI'+iSide+'.nii.gz')
   
