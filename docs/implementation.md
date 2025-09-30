# Implementation

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