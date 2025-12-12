# Implementation

## Python package
`wfsai` is implemented as a pip installable python package. Using python version 3.8 or higher.  

The use of the package is documented in the [Tutorial](tutorial.md) and [API REFERENCE](../autoapi/wfsai/) sections.  

---  

Most python modules are implemented as simple methods with arguments. Although the 'imagery' and 'shape' modules implement object classes as indicated below:  

```python
from wfsai import imagery
from wfsai import shapes

# Set up maxar image processor
m = imagery.maxar()

help(m)

# Set up the image tile processor
t = imagery.tiling()

help(t)

# Set up the shapefile processor
s = shapes.shapefile()

help(s)

```  

---  

## Command-Line Interface
A basic shell command line interface has been implemented.

**`wfsai`** `--help`
```bash
usage: wfsai [-h] [-v] [-d DISPLAY] [--remote_config]

Command Line interface for Wildlife from Space AI tools

options:
  -h, --help                         show this help message and exit
  -v, --version                      show this package version and exit
  -d CONF_FILE, --display CONF_FILE  display configuration
  --remote_config                    retrieve the remote configuration file

```  

From the command-line you can:  

- check the version of the wfsai package  
- display the formatted contents of a yaml config file  
- retrieve a remote config file (provided the 'REMOTE_CONFIG_REPO' and 'CONFIG_FILE' environment variables are set).