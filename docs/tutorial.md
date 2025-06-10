# Tutorial
  
These tutorials rely on the `wfsai` python package being installed in your environment. You will also need to install the **gdal** python implementation. For this please refer to the [Installation](installation.md) page.

---

- ## Ortho-rectification of MAXAR Worldview imagery

```python
from wfsai import imagery

# Set up maxar image processor
m = imagery.maxar()
DEM_FILE = '/data/magic_remotesensing/rema/rema_v2/rema_v2_2m/v2_tiles/SouthGeorgia_REMA_mosaic_2m.tif'

# Orthorectify PAN file
PAN_FILE = '/data/magic_remotesensing/vhr/DPLUS214_Elephant_Seals/dg_10300101070A4E00_SG_Hound_Bay/016418161040_01_P002_PAN/24OCT21115056-P2AS-016418161040_01_P002.TIL'
print(m.orthorectify(PAN_FILE, source_type='pan', dem_path=DEM_FILE))

# Orthorectify MUL file
MUL_FILE = '/data/magic_remotesensing/vhr/DPLUS214_Elephant_Seals/dg_10300101070A4E00_SG_Hound_Bay/016418161040_01_P002_MUL/24OCT21115057-M2AS-016418161040_01_P002.TIL'
print(m.orthorectify(MUL_FILE, source_type='mul', dem_path=DEM_FILE, pixel_size=(1.2, 1.2)))
```