# Tutorial
  
These tutorials rely on the `wfsai` python package being installed in your environment. You will also need to install the **gdal** python implementation. For this please refer to the [Installation](installation.md) page.

---

- ## Ortho-rectification of MAXAR Worldview imagery

```python
from wfsai import imagery

# Set up maxar image processor
m = imagery.maxar()
DEM_FILE = '/data/magic_remotesensing/rema/rema_v2/rema_v2_2m/v2_tiles/SouthGeorgia_REMA_mosaic_2m.tif'
PAN_FILE = '/data/magic_remotesensing/vhr/DPLUS214_Elephant_Seals/dg_10300101070A4E00_SG_Hound_Bay/016418161040_01_P002_PAN/24OCT21115056-P2AS-016418161040_01_P002.TIL'
MUL_FILE = '/data/magic_remotesensing/vhr/DPLUS214_Elephant_Seals/dg_10300101070A4E00_SG_Hound_Bay/016418161040_01_P002_MUL/24OCT21115057-M2AS-016418161040_01_P002.TIL'

# Orthorectify PAN file using Digital Elevation Model
print(m.orthorectify(PAN_FILE, source_type='pan', dem_path=DEM_FILE))

# Orthorectify PAN file without using Digital Elevation Model
print(m.orthorectify(PAN_FILE, source_type='pan'))

# Orthorectify MUL file using Digital Elevation Model
print(m.orthorectify(MUL_FILE, source_type='mul', dem_path=DEM_FILE, pixel_size=(1.2, 1.2)))

# Orthorectify MUL file without using Digital Elevation Model
print(m.orthorectify(MUL_FILE, source_type='mul', pixel_size=(1.2, 1.2)))

# Pan-Sharpen PAN & MUL using Digital Elevation Model
ORTHO_PAN_FILE = './24OCT21115056-P2AS-016418161040_01_P002_ortho.tif'
ORTHO_MUL_FILE = './24OCT21115057-M2AS-016418161040_01_P002_ortho.tif'
print(m.pansharpen(ORTHO_PAN_FILE, ORTHO_MUL_FILE))

# Pan-Sharpen PAN & MUL without using Digital Elevation Model
CONST_PAN_FILE = './24OCT21115056-P2AS-016418161040_01_P002_ortho_const.tif'
CONST_MUL_FILE = './24OCT21115057-M2AS-016418161040_01_P002_ortho_const.tif'
print(m.pansharpen(CONST_PAN_FILE, CONST_MUL_FILE))
```