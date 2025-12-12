# Installation

If not using a conda/mamba environment it is recommended to pip install the `wfsai` package inside a python virtual environment. e.g.
```bash
python -m venv <path-of-your-venv>
source activate <path-of-your-venv>   
```
> ## pip
> `pip install git+https://github.com/antarctica/wfsai.git@main`

> ## conda/mamba
> `conda/mamba create -n <environment-name> -c conda-forge git pip`  
> `conda/mamba activate <environment-name>`  
> `pip install git+https://github.com/antarctica/wfsai.git@main`  

## GDAL
The 'imagery' module within the `wfsai` package makes use of the **gdal** python implementation, including it's underlying dependencies. We found that the best way to handle **gdal** and it's dependencies is to use a mamba environment with the mamba dependency solver. If you are using a conda/mamba environment in your project then simply include **gdal** as a dependency in your environment.yaml or use the command:  
> `conda install -n <environment-name> -c conda-forge gdal`  

If not using the 'imagery' module then **gdal** installation is not required.  

## Environment Variables
If retrieving a configuration from a remote repository then specify the `REMOTE_CONFIG_REPO` environment variable.
```bash
REMOTE_CONFIG_REPO=<url>
```  
With either remote or local config files, you should specify the `CONFIG_FILE` environment variable.
```bash
CONFIG_FILE=<config filename>
```
