# Copyright (c) 2020 brainlife.io
#
# This file is a template for a python-based brainlife.io App
# brainlife stages this git repo, writes `config.json` and execute this script.
# this script reads the `config.json` and execute pynets container through singularity
#
# you can run this script(main) without any parameter to test how this App will run outside brainlife
# you will need to copy config.json.brainlife-sample to config.json before running `main` as `main`
# will read all parameters from config.json
#
# Author: Franco Pestilli
# The University of Texas at Austin

# set up environment
import json
import nibabel as nib
import dipy

from dipy.align.reslice import reslice
from dipy.data import get_fnames

# load inputs from config.json
with open('config.json') as config_json:
	config = json.load(config_json)

# Load into variables predefined code inputs
data_file = str(config['t1'])
 
# set the output resolution
out_res = [ int(v) for v in config['outres'].split(" ")]

# we load the input T1w that we would like to resample
img = nib.load(data_file)

# we get the data from the nifti file
input_data   = img.get_data()
input_affine = img.affine
input_zooms  = img.header.get_zooms()[:3]

# resample the data
out_data, out_affine = reslice(input_data, input_affine, input_zooms, out_res)

# create the new NIFTI file for the output
out_img = nib.Nifti1Image(out_data, out_affine)

# save the output file (with the new resolution) to disk
nib.save(out_img, 'out_dir/t1.nii.gz')

