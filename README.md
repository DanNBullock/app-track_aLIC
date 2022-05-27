[![Abcdspec-compliant](https://img.shields.io/badge/ABCD_Spec-v1.1-green.svg)](https://github.com/brain-life/abcd-spec)
[![Run on Brainlife.io](https://img.shields.io/badge/Brainlife-bl.app.###-blue.svg)](https://doi.org/10.25663/brainlife.app.630)

# app-track_aLIC

Track the [anterior limb of the internal capsule](https://doi.org/10.1523/JNEUROSCI.2335-17.2017) using [ensemble tractography](https://doi.org/10.1371/journal.pcbi.1004692) (i.e. via parameter sweep)

## Overview of app-track_aLIC

This application produces a streamline-based model of the anterior limb of the internal capsule.  It further divides its output into a superior (canonical) and inferior (non-canonical) components. 

### App use case

The resultant streamline-based model of the anterior limb of the internal capsule can be used to assess the morphology, trajectory, spatial occupancy, and connectivity of this structure.

### Overly simplified algorithm/metholodology

There are three primary steps in this methodlology

- 1.  Identification of the anterior limb white matter volume. This is acheived by identifying anatomical landmarks withing the subject's brain (using the [freesurfer](https://surfer.nmr.mgh.harvard.edu/) [Desikan-Killiany](10.1016/j.neuroimage.2006.01.021) parcellation).  This is performed by the _app-track-between-multiple-regions/produce\_aLIC\_ROIs.py_ script.
- 2.  Performance of targeted, [ensemble tractography](https://doi.org/10.1371/journal.pcbi.1004692).  This algorithm iterates across parameter settings to create a broadly sampled tractogram.  The current implementation is essentialy a copy of [an existing app/resource (currently entitled "RACE-Track")](https://doi.org/10.25663/bl.app.101) developed and maintaned by [Brent McPherson](https://github.com/bcmcpher).  This is performed by the _app-track-between-multiple-regions/mrtrix3\_tracking.sh_ script.
- 3.  Segmentation of the resultant tractogram, to produce a curated model of the anterior limb of the internal capsule.  Although [MRtrix3](https://www.mrtrix.org/) and [RACE-Track](https://doi.org/10.25663/bl.app.101) produce quality tractography models, further curation is needed to ensure adherence to constraints of biological plausibility and contemporary understanding of the structure's morphology.  This is acheived via a [White Matter Query Language (WMQL)](https://doi.org/10.1007/s00429-015-1179-4)-like method that has been [used in previous publications](https://doi.org/10.1007/s00429-019-01907-8) and has been comprehensively described in the [White Matter Segentation Education (WIMSE) resource](https://github.com/DanNBullock/WiMSE) (website [here](https://dannbullock.github.io/WiMSE/landingPage.html)).  It is performed by the _segViaDocker/seg\_aLIC\_connections.py_ script.

### Necessary inputs and outputs

#### Inputs

##### Data

This application requres the following input files/datatypes:

- A preprocessed [DWI image](https://brainlife.io/datatype/58c33c5fe13a50849b25879b/readme) (config.json key: "diff")
    - Associated bvec and bval files (config.json keys: "bvec" and "bval")
- A preprocessed [T1 anatomical image](https://brainlife.io/datatype/58c33bcee13a50849b25879a/readme) (config.json key: "anat")
- A [freesurfer output directory](https://brainlife.io/datatype/58cb22c8e13a50849b25882e/readme) (config.json key for "output" dir: "freesurfer")

NOTE: All of these should be in the same "reference space" and aligned to one another

#### Parameters

This application has the following options for input parameters (listed names = config.json key):

- tensor_fit (type: number): If multi-shell data is passed, this selects the bval shell that will be extracted for application of a tensor fit.  Otherwise, if single-shell data is passed, this is ignored.
- norm (type: boolean):  Perform log-domain normalization of CSD data before tracking (multi-shell data only).
- min_length (type: number): The minimum length a streamline may be (in mm).
- max_length (type: number): The maximum length a streamline may be (in mm).
- ens_lmax (type: boolean):  Whether to perform [ensemble tracking](https://doi.org/10.1371/journal.pcbi.1004692) on every lmax up to the maximum value passed.
- curvs (type: multiple numbers):  The maximum curvature angle streamline can take during tracking.  Multiple values results in iteration across these parameters.
- num\_fibers (type: int):  The number of streamlines to produce _per parameter combination_ (thus the total number returned will be some substantial **multiple** of this).
- do_dtdt (type: boolean):  Whether to perform tensor-based deterministic tractography.
- do_dtpb (type: boolean):  Whether to perform tensor-based probabilistic tractography.
- do_detr (type: boolean):  Whether to perform deterministic tractography.
- do_prb1 (type: boolean):  Whether to perform mrtrix2 probabilistic tractography.
- do_prb2 (type: boolean):  Whether to perform mrtrix3 probabilistic tractography
- do_fact (type: boolean):  Whether to perform FACT tracking.
- fact_dirs (type: int): The number of directions to perform [FACT tracking](https://radiopaedia.org/articles/fiber-assignment-by-continuous-tracking-algorithm-fact?lang=us) on (if requested).
- fact_fibs (type: number): The number of FACT fibers to track per lmax (if requested).
- premask (type: boolean):  If the input anatomical T1s have already been skull stripped, check this to prevent 5ttgen from cutting off a portion of the brain. (This sets -premasked option for 5ttgens)  (WARNING: current implementation does not handle this well; recomended to leave this as FALSE)
- step (type: number): Streamline internode distance
- imaxs (type: int(s)): The lmax(s) or (alternatively) maximum value to fit and create tractography data for. If not provided, the App will find the maximum possible lmax within the data and use that.

#### Outputs
_Check out the [brainlife datatypes webpage](https://brainlife.io/datatypes) for a cataloguing of relevant datatypes._

- This application outputs a [.tck file](https://brainlife.io/datatype/5907d922436ee50ffde9c549/readme) corresponding to the output of the _mrtrix3\_tracking.sh_ script.

- This application also outputs a ["White Matter Classification" (WMC)](https://brainlife.io/datatype/5cc1d64c44947d8aea6b2d8b/readme).  It contains two fields: _names_ which corresponds to the names of the white matter structures identified, and _index_, which corresponds to the identity of each streamline in the associated tck file, with respect to the _name_ vector. To illustrate it's meaning: a 1 at _index_ location 4 indicates that streamline 4 in the associated tractogram is associated with the first structure listed in the _name_ vector.  More can be found on this in the earlier "WMC" link. This file is stored as a [.mat (matlab)](https://www.mathworks.com/help/matlab/ref/matlab.io.matfile.html) file.  However, it can also be straightforwardly converted (with the inclusion of it's associated tck file) into a set of tck files (e.g. using [this app](https://doi.org/10.25663/brainlife.app.251) or [this code](https://github.com/DanNBullock/wma_pyTools/blob/13be3f4c6e509760022919d223fd8cd102cf8020/wmaPyTools/streamlineTools.py#L815-L873) or a [python dictionary object](https://github.com/DanNBullock/wma_pyTools/blob/13be3f4c6e509760022919d223fd8cd102cf8020/wmaPyTools/streamlineTools.py#L875-L929).

### Other usage notes

NOTE:  Runtime for this application will vary in accordance with the number of streamlines requested.  As more streamlines are requeseted, it may be necessary to change the _TCKGEN__TIMEOUT_ parameter in the mrtrix3_tracking.sh scirpt.

## Author, funding sources, references, & license info

### Authors
- [Dan Bullock](https://github.com/DanNBullock/) ([bullo092@umn.edu](mailto:bullo092@umn.edu))

### PI
- [Sarah Heilbronner](https://med.umn.edu/bio/department-of-neuroscience/sarah-heilbronner) ([heilb028@umn.edu](mailto:heilb028@umn.edu))

### Funding
[![NIH-NIBIB-1T32EB031512-01](https://img.shields.io/badge/NIH_NIBIB-1T32EB031512--01-blue.svg)](https://reporter.nih.gov/project-details/10205698)
[![NIMH-5P50MH119569-02](https://img.shields.io/badge/NIMH-5P50MH119569--02-blue.svg)](https://reporter.nih.gov/project-details/10123009)
[![NIMH-5R01MH118257-04](https://img.shields.io/badge/NIMH-5R01MH118257--04-blue.svg)](https://reporter.nih.gov/project-details/10122991)
[![NIDA-1P30DA048742-01A1](https://img.shields.io/badge/NIDA-1P30DA048742--01A1-blue.svg)](https://reporter.nih.gov/project-details/10025457)

* [Dan Bullock](https://github.com/DanNBullock/)'s work is supported by the following sources:
    - The University of Minnesota’s Neuroimaging Postdoctoral Fellowship Program, College of Science and Engineering's, and the Medical School's NIH funded T32 Neuroimaging Training Grant. NOGA: [1T32EB031512-01](https://reporter.nih.gov/project-details/10205698) 

- [Sarah Heilbronner](https://med.umn.edu/bio/department-of-neuroscience/sarah-heilbronner)'s work is supported by the following sources:
    - The University of Minnesota’s Neurosciences' and Medical School's NIMH grant for the investigation of "Neural Basis of Psychopathology, Addictions and Sleep Disorders Study Section[NPAS]". NOGA: [5P50MH119569-02-04](https://reporter.nih.gov/project-details/10123009) 
    - The University of Minnesota’s Neurosciences' Translational Neurophysiology grant. NOGA: [5R01MH118257-04](https://reporter.nih.gov/project-details/10122991)
    - The University of Minnesota’s Neurosciences' Addiction Connectome grant. NOGA: [1P30DA048742-01A1](https://reporter.nih.gov/project-details/10025457)
    
### Citations

#### Directly relevant citations

(Provide citations that are _directly_ relevant to this code implementation here)

#### Indirectly relevant citations

(Provide citations that are _indirectly_ relevant to this code implementation here)

### License info

GNU License

## Nuts and bolts -- Using this app
Below  a description of how to use this code repository on the Brainlife platform, with docker/singularity, or simply in your local compute environment.

### Omnibus usage notes
One characteristic that can apply across all of these use contexts is the config.json file.

#### The config.json 

The [config.json file](https://brainlife.io/docs/apps/helloworld/#configjson) is a [standard component of application functionality on the brainlife.io platform](https://brainlife.io/docs/apps/introduction/).  However, even outside of the brainlife.io context (running this code in your local python environment), the config.json file is a clean and effective way of managing file and parameter inputs for this code.  Typically, the "main" python file/script (main.py, is the default case) reads the .json file (using the [json](https://docs.python.org/3/library/json.html) module) into a _config_ [dictionary object](https://docs.python.org/3/tutorial/datastructures.html#dictionaries) thusly:

```
with open('config.json') as config_json:
	config = json.load(config_json)
```

Variables and parameters can then be read in from the dictionary using the relevant _keys_.  An example config.json setup might look something like this:

```
{
    "inputFile_1": "local/path/to/inputFile_1",
    "inputFile_2": "local/path/to/inputFile_2",
    "inputFile_3": "local/path/to/inputFile_3",
    "parameter_1": parameter_1_value,
    "parameter_2": parameter_2_value,
    "parameter_3": parameter_3_value
}
```
Consider reviewing the [json standard overview](https://www.json.org/json-en.html) for help formatting this object.

The config.json file can provide a standard interface for controlling execution of the code, whether using [brainlife.io](https://brainlife.io/), [docker](https://docs.docker.com/)/[singularity](https://sylabs.io/guides/2.6/user-guide/index.html), or a local python environment.

####  The config.json for *this* app

Below you will find an example config.json for this app.

```
{
    "tensor_fit": 1,
    "norm": false,
    "min_length": 10,
    "max_length": 250,
    "ens_lmax": true,
    "curvs": "5 10 20 40 80",
    "num_fibers": 2000,
    "do_dtdt": false,
    "do_dtpb": false,
    "do_detr": false,
    "do_prb1": false,
    "do_prb2": true,
    "do_fact": false,
    "fact_dirs": 3,
    "fact_fibs": 0,
    "premask": false,
    "step": 0.5,
    "imaxs": 8,
    "diff": "testdata/dwi.nii.gz",
    "bvec": "testdata/dwi.bvecs",
    "bval": "testdata/dwi.bvals",
    "freesurfer": "testdata/output",
    "anat": "testdata/t1.nii.gz"
}
```

###  Using this app on [Brainlife.io](https://brainlife.io/)

NOTE: for any given app on Brainlife.io, a link to the corresponding github repository (containing the code used to run the app) can be found just below the app name (in gray text) on the Apps "homepage".

#### Input datatypes


This application requres the following input files/datatypes from the [Brainlife.io platform](https://brainlife.io/datatypes):

- A preprocessed [DWI image](https://brainlife.io/datatype/58c33c5fe13a50849b25879b/readme) (config.json key: "diff")
    - Associated bvec and bval files (config.json keys: "bvec" and "bval")
- A preprocessed [T1 anatomical image](https://brainlife.io/datatype/58c33bcee13a50849b25879a/readme) (config.json key: "anat")
- A [freesurfer output directory](https://brainlife.io/datatype/58cb22c8e13a50849b25882e/readme) (config.json key for "output" dir: "freesurfer")

NOTE: All of these should be in the same "reference space" and aligned to one another

#### Parameter settings

(parameter settings, including default/typical inputs/values, should be documented and provided on the [brainlife App user interface page](https://doi.org/10.25663/brainlife.app.630).  However, use this section to also duplicate   )

SEE "Necessary inputs and outputs" above.

#### Single execution notes

(notes pertinent/specific to usage via the **Execute** interface)

#### Rule/Pipeline usage notes

(notes pertinent/specific to usage via the **Pipeline/Rule** interface)

### LOCAL usage via [docker](https://docs.docker.com/)/[singularity](https://sylabs.io/guides/2.6/user-guide/index.html)

Although excution of python code/apps (under the current developmental framework) is typically controlled by the _main.py_ file, for the purposes of portability and standardization, the execution of of this file is acheived via a bash script that sets up some environmental variables for local / HPC usage and then runs the python script in the relevant docker environment (using "[singularity exec](https://sylabs.io/guides/3.1/user-guide/cli/singularity_exec.html)") in (roughly) the following fashion:

```
#!/bin/bash
#PBS -l nodes=1:ppn=16
#PBS -l walltime=02:00:00

# run the actual python code
singularity exec docker://organization/container:version python3 main.py
```

#### Installation
Local use of [docker images/containers](https://www.techtarget.com/searchitoperations/definition/Docker-image) using [singularity](https://sylabs.io/guides/2.6/user-guide/index.html) requires local installation of singularity (a non-trivial matter).  The [Sylabs Singularity documentation page](https://sylabs.io/guides/3.0/user-guide/quick_start.html#quick-installation-steps) provides an overview of installation processes, however, this may not cover all installation cases.  For example [a debian package](https://neuro.debian.net/install_pkg.html?p=singularity-container) has been provided by the [neurodebian group](https://neuro.debian.net/).  Additionally, [Brainlife documention](https://brainlife.io/docs/) provides a [guide to singularity installation/usage as well](https://brainlife.io/docs/apps/container/).

#### Settings & setup

There are two major singularity properties to keep in mind when considering local Singularity configuration: the [cache directory](https://sylabs.io/guides/3.3/user-guide/build_env.html) and the [bind path](https://sylabs.io/guides/3.3/user-guide/bind_paths_and_mounts.html)

##### Singularity cache directory
Docker images that are pulled from repositories like [dockerhub](https://hub.docker.com/) are stored and "built" locally.  Usage of a wide range of docker images can quite easily lead to a significant buildup of files in this directory, which can quickly occupy a great deal of harddrive.  As such it is important to be mindful of where (e.g. which disk resource) this environmental variable points to.

##### Singularity bind path
The virtual environments instantiated when a docker image is run (via singularity) **do not** have full access to your local file system.  Instead, only [a narrow set of paths](https://sylabs.io/guides/2.6/user-guide/bind_paths_and_mounts.html#system-defined-bind-points) are made available by default.  As such, **any functions or files called by the code that ARE NOT on these paths will not be found, resulting in an error**.  There are two approaches to dealing with this:

- 1.  Ensure that all requisite files & functions are accessible on these paths.  For requisite files (e.g. input data) in particular, this may mean storing these in a subdirectory of the directory from which the "main" bash script (e.g. where the singularity call is executed).
- 2.  [Manual specification of additional bindpaths using the --bind option](https://sylabs.io/guides/3.1/user-guide/bind_paths_and_mounts.html#user-defined-bind-paths)

### Local usage
With the appropriate modules installed in your local os and python environment it is also possible to run this code.  Ensure that the required modules (see below) are installed, that the config.json file is pointing to the correct files, and you should be ready to go.

#### Required packages / modules

- MRtrix3
- Dipy
- wmaPyTools (included as submodule)
- numpy
- nibabel
- nilearn (?)

(consider https://docs.python.org/3/library/modulefinder.html run on main)

## Followup 

NOTE: for any given app on Brainlife.io, a link to the corresponding github repository (containing the code used to run the app) can be found just below the app name (in gray text) on the Apps "homepage".

### Converting to tck files

- [Extract multi-tcks from wmc + wbfg or composite tck](https://doi.org/10.25663/brainlife.app.251) 

As noted earlier, the output of this application/code (a [WMC/classification.mat](https://brainlife.io/datatype/5cc1d64c44947d8aea6b2d8b/readme) file) can be converted to a collection of .tck files using [this app](https://doi.org/10.25663/brainlife.app.251) or [this code](https://github.com/DanNBullock/wma_pyTools/blob/13be3f4c6e509760022919d223fd8cd102cf8020/wmaPyTools/streamlineTools.py#L815-L873) (with the additional provision of the source .tck file--"track.tck" in this case.

### Converting to density NIFTIs

The following app can be used to obtain a density NIFTI for each of the white matter structures identified:

- [Track Density Masks](https://doi.org/10.25663/brainlife.app.498)

### Visualization

These apps can be used to provide visualizations for this output:

- [Generate tract figures (wma_pyTools)](https://doi.org/10.25663/brainlife.app.638) 
- [Generate figures of white matter tracts overlaid on anatomical image](https://doi.org/10.25663/brainlife.app.607) 
- [WMC Figures (AFQ or WMA)](https://doi.org/10.25663/brainlife.app.145) (depricated)

### Quantification and analysis

These apps can be used to provide quantative analyses:

-  [Tractography quality check](https://doi.org/10.25663/brainlife.app.189)

## Development note

Work to better structure and document this code/application.  Please feel free to create issues [using the "issues" tab above] to help foster clarity in documentation, or to suggest alterations to documentation/code more directly. Furthermore, it is _acutely_ understood that many of the functionalities in this package may be redundant implementations of (likely more robust and reliable) functionalities from other packages. The identification of such instances (and their other-package correspondances) would be **greatly appreciated**. Feel free to create branches which implement these alternatives.  Be sure to update the documentation as well to describe your changes and to ensure that your contributions are appropriately credited.
