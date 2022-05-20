[![Abcdspec-compliant](https://img.shields.io/badge/ABCD_Spec-v1.1-green.svg)](https://github.com/soichih/abcd-spec)
[![Run on Brainlife.io](https://img.shields.io/badge/Brainlife-bl.app.130-blue.svg)](https://doi.org/10.25663/bl.app.130)

# 
This app will perform ensemble tracking between 2 or more cortical regions of interest (ROIs) from  atlas parcellation. First, the ROIs are registered to diffusion space using Freesurfer's mri_label2vol, and a white matter mask is generated in diffusion space, by running the create_wm_mask script. Then, tracking will be performed using mrtrix/0.2.12 by running the trackROI2ROI script. Finally, a classification structure will be generated using Vistasoft's bsc_mergeFGandClass and bsc_makeFGsFromClassification functions by running the classificationGenerator script.

### Authors
- Brad Caron (bacaron@iu.edu)
- Ilaria Sani (isani01@rockefeller.edu)
- Dan Bullock (dnbulloc@iu.edu)

### Contributors
- Soichi Hayashi (hayashi@iu.edu)

### Funding
[![NSF-BCS-1734853](https://img.shields.io/badge/NSF_BCS-1734853-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1734853)
[![NSF-BCS-1636893](https://img.shields.io/badge/NSF_BCS-1636893-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1636893)

## Running the App 

### On Brainlife.io

You can submit this App online at [https://doi.org/10.25663/bl.app.34](https://doi.org/10.25663/bl.app.34) via the "Execute" tab.

### Running Locally (on your machine)

1. git clone this repo.
2. Inside the cloned directory, create `config.json` with something like the following content with paths to your input files.

```json
{
        "parcellation": "./input/parc/",
        "dtiinit": "./input/dtiinit/",
        "fsurfer": "./input/freesurfer/",
        "roiPair": "45,54",      
        "num_fibers": 500000,
        "max_num": 1000000,
        "stepsize": 0.2,
        "minlength": 10,
        "maxlength": 200,
        "num_repetitions": 1
}
```

### Sample Datasets

You can download sample datasets from Brainlife using [Brainlife CLI](https://github.com/brain-life/cli).

```
npm install -g brainlife
bl login
mkdir input
bl dataset download 5b96bc8b059cf900271924f4 && mv 5b96bc8b059cf900271924f4 input/parcellation
bl dataset download 5b96bc8d059cf900271924f5 && mv 5b96bc8d059cf900271924f5 input/dtiinit
bl dataset download 5b96bc8d059cf900271924f5 && mv 5b96bc8d059cf900271924f5 input/freesurfer

```


3. Launch the App by executing `main`

```bash
./main
```

## Output

The main outputs of this App is a 'track.tck' file, a folder called 'tracts' containing .json files for each tract, an 'output.mat' containing the classification structure, and a text file called 'output_fibercounts.txt' which contains information regarding the number of streamlines in each tract.

#### Product.json
The secondary output of this app is `product.json`. This file allows web interfaces, DB and API calls on the results of the processing. 

### Dependencies

This App requires the following libraries when run locally.

  - singularity: https://singularity.lbl.gov/
  - VISTASOFT: https://github.com/vistalab/vistasoft/
  - ENCODE: https://github.com/brain-life/encode
  - SPM 8 or 12: https://www.fil.ion.ucl.ac.uk/spm/software/spm8/
  - WMA: https://github.com/brain-life/wma
  - Freesurfer: https://hub.docker.com/r/brainlife/freesurfer/tags/6.0.0
  - mrtrix: https://hub.docker.com/r/brainlife/mrtrix_on_mcr/tags/1.0
  - jsonlab: https://github.com/fangq/jsonlab.git
