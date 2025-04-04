# wfsai
Wildlife from Space AI  
A pip installable python package to help with the AI workflow stages of detecting Wildlife from Space.  

![Typical AI Image analysis workflow](https://osu-wams-blogs-uploads.s3.amazonaws.com/blogs.dir/2115/files/2024/12/A.I.-Model-768x432.png)  
(diagram courtesy of [this](https://blogs.oregonstate.edu/gemmlab/2024/12/23/demystifying-ai-a-brief-overview-of-image-pre-processing-and-a-machine-learning-workflow/) blogpost.)

## Installation
> ### pip
> `pip install git+https://github.com/antarctica/wfsai.git@main`

> ### conda/mamba
> `conda/mamba create -n <environment-name> -c conda-forge git pip`  
> `conda/mamba activate <environment-name>`  
> `pip install git+https://github.com/antarctica/wfsai.git@main`  

## Usage
From the diagram above, often the first step of AI workflow is to obtain a source dataset to answer a scientific question. Datasets may be remote or local to the working environment and it is helpful to set out a framework for how the data will be handled during the workflow.  
For example:
- `configuration files -> retrieving/linking of input files -> intermediate files -> outputs.`

### **--help**
*show the built-in help for the wfs-ai package*  
