# Tutorial
  
These tutorials rely on the `wfsai` python package being installed in your environment. You will also need to install the **gdal** python implementation. For this please refer to the [Installation](installation.md) page.

---

- ## Ortho-rectification of MAXAR Worldview imagery

```python
from wfsai import imagery

# Set up maxar image processor
m = imagery.maxar()
DEM_FILE = 'path_to_digital_elevation_model/DEM_REMA_mosaic_2m.tif'
PAN_FILE = 'path_to_panchromatic_sat_image/24OCT21115056-P2AS-016418161040_01_P002.TIL'
MUL_FILE = 'path_to_multispectral_sat_image/24OCT21115057-M2AS-016418161040_01_P002.TIL'

# Orthorectify PAN file using Digital Elevation Model
m.orthorectify(PAN_FILE, source_type='pan', dem_path=DEM_FILE)

# Orthorectify PAN file without using Digital Elevation Model
m.orthorectify(PAN_FILE, source_type='pan')

# Orthorectify MUL file using Digital Elevation Model
m.orthorectify(MUL_FILE, source_type='mul', dem_path=DEM_FILE, pixel_size=(1.2, 1.2))

# Orthorectify MUL file without using Digital Elevation Model
m.orthorectify(MUL_FILE, source_type='mul', pixel_size=(1.2, 1.2))
```

---

- ## Pan-sharpening of ortho-rectified MAXAR Worldview imagery

```python
from wfsai import imagery

# Set up maxar image processor
m = imagery.maxar()

# Pan-Sharpen PAN & MUL using Digital Elevation Model
ORTHO_PAN_FILE = './24OCT21115056-P2AS-016418161040_01_P002_ortho.tif'
ORTHO_MUL_FILE = './24OCT21115057-M2AS-016418161040_01_P002_ortho.tif'
m.pansharpen(ORTHO_PAN_FILE, ORTHO_MUL_FILE)

# Pan-Sharpen PAN & MUL without using Digital Elevation Model
CONST_PAN_FILE = './24OCT21115056-P2AS-016418161040_01_P002_ortho_const.tif'
CONST_MUL_FILE = './24OCT21115057-M2AS-016418161040_01_P002_ortho_const.tif'
m.pansharpen(CONST_PAN_FILE, CONST_MUL_FILE)
```

---

- ## Mask processed image to Area-of-interest shapefile

```python
# TODO
```

---

- ## Tile a masked (or unmasked) image

```python
from wfsai import imagery

#            (bands, y_size, x_size)
CHUNK_SIZE = (4,     200,    200)

PANSHARPENED_FILE = './24OCT21115057-M2AS-016418161040_01_P002_ortho_psh.tif'

t = imagery.tiling()

t.tile(PANSHARPENED_FILE, CHUNK_SIZE, output_dir_path=output_tiles_dir)
```