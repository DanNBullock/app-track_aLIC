#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 14:57:13 2021

@author: dan
"""

import os
import sys

sys.path.append('wma_pyTools')
startDir=os.getcwd()
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


# load inputs from config.json
with open('config.json') as config_json:
	config = json.load(config_json)

outDir='output'
if not os.path.exists(outDir):
    os.makedirs(outDir)
if not os.path.exists(os.path.join(outDir,'ROIS')):
    os.makedirs(os.path.join(outDir,'ROIS'))
#set to freesurfer output path for this subject
fsPath=config['fsDir']
#you may need to convert the .mgz files to .nii.gz using the mr_convert command
#also, you may need to rename the subsequent aparcDk atlas file to it's standard name:
# aparc+aseg
try:
    inputAtlas=nib.load(os.path.join(fsPath,'mri','aparc.DKTatlas+aseg.nii.gz'))
except:
    #can nibael handle mgz?
    inputAtlas=nib.load(os.path.join(fsPath,'mri','aparc.DKTatlas+aseg.mgz'))
inputAtlas=wmaPyTools.roiTools.inflateAtlasIntoWMandBG(inputAtlas, 1)
# lookupTablePath=config['lookupTable']
# lookupTable=pd.read_csv(lookupTablePath)
#refAnatT1 = nib.nifti1.Nifti1Image(refAnatT1.get_data(), np.round(refAnatT1.affine,2), refAnatT1.header)

#go ahead and set bad labels, for areas that streamlines can't actually terminate
invalidLabels=[63,31,4,14,15,43,24,72]

# #performSegmentation
#extract whole brain segmentation
#set to path to target whole brain tractogram
#smaller = faster
tractogramPath=config['tractogram']
tractogramLoad=nib.streamlines.load(tractogramPath)
#is this creating inf values?
#streamlines=wmaPyTools.streamlineTools.orientAllStreamlines(tractogramLoad.streamlines)
streamlines=tractogramLoad.streamlines
sideList=['left','right']
for iIndex,iSide in enumerate(sideList):
    if iSide=='left':
        sideLabel=1000
        #extract spine ROI
    elif iSide=='right':
        sideLabel=2000
        #extract spine ROI
    
    
    
    
    #set name
    tractName='aLIC_'+iSide
    
    #PRIMARY ROI
    #get the caudate. This will serve as the 
    caudateLabels=[11,50]
    caudateROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,caudateLabels[iIndex])
    #get the putamen and globus palladus
    palPutLabels=[[12,13],[51,52]]
    palPutROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,palPutLabels[iIndex])
    #get the white matter labels as well
    wmLabels=[2,41]
    wmROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,wmLabels[iIndex])
    #intersect the inflated palPutROI with the inflated 
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
    #done?
    nib.save(nib.nifti1.Nifti1Image(fullCutIC.get_fdata(), fullCutIC.affine),os.path.join(outDir,'ROIS','fullCutIC_ROI11_'+iSide+'.nii.gz'))
   
    #create an exclusion for things that go between the amygdala and the pal/put
    amigLabels=[18,54]
    amigROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,amigLabels[iIndex])
    #intersect amyg and pal/put
    roiInflateIntersection=wmaPyTools.roiTools.findROISintersection([amigROI,palPutROI],inflateiter=7)
    #now intersect with wm
    infPalPutExclude=wmaPyTools.roiTools.findROISintersection([roiInflateIntersection,wmROI],inflateiter=0)
    #save this ROI as well
    #has to be fdata because these loaders are dumb
    nib.save(nib.nifti1.Nifti1Image(infPalPutExclude.get_fdata(), fullCutIC.affine),os.path.join(outDir,'ROIS','infPalPutNOT_ROI_'+iSide+'.nii.gz'))
   
    
    
    #ENDPONT ROIS
    #actually sidenum+, but for listing purposes...
    frontalROIS=[32,28,27,26,24,20,19,18,14,12,3,2]
    #LR spinothalROIS
    #OLD
    #spinoThalamicROIS=[[9,10,16,28],[48,49,16,60]]
    #subcortOverrideLabels=[17, 18, 15, 16, 14, 13, 20, 19, 30, 28, 29, 27, 31,32]
    spinoThalamicROIS=[[15027, 15031,15015,15017,15013,10,16],[15028, 15032,15016,15018,15014,49,16]]
    #also get contraWM for good measure
    contraWM=[41,2]
    
    #get the ROIS
    frontalROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,np.add(frontalROIS,sideLabel),inflateIter=2)
    spinoThalamicROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,spinoThalamicROIS[iIndex],inflateIter=2)
    contraWMROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,contraWM[iIndex])
    
    #establish some stuff for the diencephalon
    contraDELabel=[60,28]
    contraDEroi=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,contraDELabel[iIndex])
  
    #generate ROI for invalid endpoints
    badEndpointROI=wmaPyTools.roiTools.multiROIrequestToMask(inputAtlas,invalidLabels) 
    
  
    #create a plan to split the superior and inferior streamlines
    #top of th diencephalon, posterior to the medial orbitofrontal, lateral to medial border of putamen
    acumbensLabel=[26,58]
    globPalLabel=[13,52]
    ccLabel=255
    medialOrbFront=14+sideLabel
    #get the relevant planar borders
    infCCborder=wmaPyTools.roiTools.planarROIFromAtlasLabelBorder(inputAtlas,ccLabel, 'inferior')
    antGlobPalBorder=wmaPyTools.roiTools.planarROIFromAtlasLabelBorder(inputAtlas,globPalLabel[iIndex], 'anterior')
    medAcumbBorder=wmaPyTools.roiTools.planarROIFromAtlasLabelBorder(inputAtlas,acumbensLabel[iIndex], 'medial')
    #cut the post orb border with the sup de and keep the inferior half
    infCatchPlane=wmaPyTools.roiTools.sliceROIwithPlane(antGlobPalBorder,infCCborder,'inferior')
    #cut this to return the lateral component of this inferior planar border
    latInfCatchPlane=wmaPyTools.roiTools.sliceROIwithPlane(infCatchPlane,medAcumbBorder,'lateral')
    #save it for visualization
    nib.save(nib.nifti1.Nifti1Image(latInfCatchPlane.get_fdata(), latInfCatchPlane.affine),os.path.join(outDir,'ROIS','latInfCatchPlane_ROI_'+iSide+'.nii.gz'))
   
    
    
    #explore its connectivity
    comboROIBool=wmaPyTools.segmentationTools.segmentTractMultiROI(streamlines, [fullCutIC,frontalROI,spinoThalamicROI,contraWMROI,contraDEroi,badEndpointROI], [True,True,True,False,False,False], ['any',"either_end","either_end","any","any","either_end"])
   
    #instead lets inflate into the white matter next to the DC and pallidum to get thse inferior streamlines

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
    nib.save(nib.nifti1.Nifti1Image(ventAlicROI.get_fdata(), ventAlicROI.affine),os.path.join('ROIS','ventAlicROI'+iSide+'.nii.gz'))
   
    
    inferiorStreams=wmaPyTools.segmentationTools.segmentTractMultiROI_fast(streamlines, [ventAlicROI], [True], ['any'])
  
    
   
    #inferiorPlaneCatchBool=wmaPyTools.segmentationTools.segmentTractMultiROI(streamlines, [latInfCatchPlane], [True],['any'])
   
    
   
    superiorStreamsBool=np.logical_and(comboROIBool,np.logical_not(inferiorStreams))
    inferiorStreamsBool=np.logical_and(comboROIBool,inferiorStreams)
    
    #if the classification structure does not already exist
    if not 'classificationOut' in locals():
        #create it
        classificationOut=wmaPyTools.streamlineTools.updateClassification(superiorStreamsBool,'superior_'+tractName)
        classificationOut=wmaPyTools.streamlineTools.updateClassification(inferiorStreamsBool,'inferior_'+tractName,existingClassification=classificationOut)
    else:
        #otherwise, add the names to it
        classificationOut=wmaPyTools.streamlineTools.updateClassification(superiorStreamsBool,'superior_'+tractName,existingClassification=classificationOut)
        classificationOut=wmaPyTools.streamlineTools.updateClassification(inferiorStreamsBool,'inferior_'+tractName,existingClassification=classificationOut)

    
    wmaPyTools.streamlineTools.stubbornSaveTractogram(streamlines[superiorStreamsBool],os.path.join(outDir,'superior_'+tractName+'.tck'))
    wmaPyTools.streamlineTools.stubbornSaveTractogram(streamlines[inferiorStreamsBool],os.path.join(outDir,'inferior_'+tractName+'.tck'))

from scipy.io import savemat
#save down the classification structure
savemat(os.path.join(outDir,'wmc','classification.mat'),classificationOut)
 


    