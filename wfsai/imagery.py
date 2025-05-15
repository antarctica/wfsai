#!/usr/bin/env python

# File Version: 2025-05-14: First version
#
# Author: matsco@bas.ac.uk

import sys
import os
import shutil
import yaml
import glob
from pathlib import Path
from wfsai.configuration import _check_config_path_
from wfsai.configuration import _load_

"""
This library is for handling imagery for pre or post AI tasks.
"""

class maxar:

    """
    This class is specifically for operations when handling Maxar satellite imagery.
    """

    def __init__():
        pass

    def basic_test(test_string: str) -> str:
        ret_string = "The test string provided was: '"+test_string+"'"
        return ret_string

    #TODO What do I want the maxar data handling to actually do?
    # 1. Take in a single satellite image and ortho-rectify.
    # 2. Take in both PAN and MUL ortho-rectified images and output
    #    a pan sharpened image.
    


"""
Dump from jupyter notebook
==========================

from osgeo import gdal

PAN_FILE = '/data/magic_remotesensing/vhr/DPLUS214_Elephant_Seals/dg_10300101070A4E00_SG_Hound_Bay/016418161040_01_P002_PAN/24OCT21115056-P2AS-016418161040_01_P002.TIL'
MUL_FILE = '/data/magic_remotesensing/vhr/DPLUS214_Elephant_Seals/dg_10300101070A4E00_SG_Hound_Bay/016418161040_01_P002_MUL/24OCT21115057-M2AS-016418161040_01_P002.TIL'

DEM_FILE = '/data/magic_remotesensing/rema/rema_v2/rema_v2_2m/v2_tiles/SouthGeorgia_REMA_mosaic_2m.tif'

#ORTHO

PAN_ORTHO_FILE = '/data/wfs/darwin-elephant-seal/matsco/wfsai/python_pan_ortho_dem.tif'
MUL_ORTHO_FILE = '/data/wfs/darwin-elephant-seal/matsco/wfsai/python_mul_ortho_dem.tif'

#### taken from https://gdal.org/en/stable/api/python/utilities.html
pan_warp_options = gdal.WarpOptions(
    rpc = True, # use rpc for georeferencing
    dstSRS = 'EPSG:32724',# force output projection
    transformerOptions = ['RPC_DEM={}'.format(DEM_FILE)], # see https://gdal.org/en/stable/api/gdal_alg.html#_CPPv426GDALCreateRPCTransformerV2PK13GDALRPCInfoV2idPPc
    outputBounds =  [681432, 3959152, 684529, 3963404], #coordinates in dstSRS to process image chip
    xRes=0.5, yRes=0.5, # same as in metadata
    srcNodata = 0,
    dstNodata = 0
)
mul_warp_options = gdal.WarpOptions(
    rpc = True, # use rpc for georeferencing
    srcBands=[1,2,3],
    dstBands=[3,2,1],
    dstSRS = 'EPSG:32724',# force output projection
    transformerOptions = ['RPC_DEM={}'.format(DEM_FILE)], # see https://gdal.org/en/stable/api/gdal_alg.html#_CPPv426GDALCreateRPCTransformerV2PK13GDALRPCInfoV2idPPc
    outputBounds =  [681432, 3959152, 684529, 3963404], #coordinates in dstSRS to process image chip
    xRes=1.2, yRes=1.2, # same as in metadata
    srcNodata = 0,
    dstNodata = 0
)

ds = gdal.Warp(PAN_ORTHO_FILE, PAN_FILE, options=pan_warp_options)
ds = None
ds = gdal.Warp(MUL_ORTHO_FILE, MUL_FILE, options=mul_warp_options)
ds = None

# ORTHO WITHOUT DEM

PAN_ORTHO_FILE = '/data/wfs/darwin-elephant-seal/matsco/wfsai/python_pan_ortho_const.tif'
MUL_ORTHO_FILE = '/data/wfs/darwin-elephant-seal/matsco/wfsai/python_mul_ortho_const.tif'

#### taken from https://gdal.org/en/stable/api/python/utilities.html

pan_warp_options = gdal.WarpOptions(
    rpc = True, # use rpc for georeferencing
    dstSRS = 'EPSG:32724',# force output projection
    transformerOptions = ['RPC_HEIGHT=0'], # see https://gdal.org/en/stable/api/gdal_alg.html#_CPPv426GDALCreateRPCTransformerV2PK13GDALRPCInfoV2idPPc
    outputBounds =  [681432, 3959152, 684529, 3963404], #coordinates in dstSRS to process image chip
    xRes=0.5, yRes=0.5, # same as in metadata
    # srcNodata = 0,
    # dstNodata = 0
)
mul_warp_options = gdal.WarpOptions(
    rpc = True, # use rpc for georeferencing
    srcBands=[1,2,3],
    dstBands=[3,2,1],
    dstSRS = 'EPSG:32724',# force output projection
    transformerOptions = ['RPC_HEIGHT=0'], # see https://gdal.org/en/stable/api/gdal_alg.html#_CPPv426GDALCreateRPCTransformerV2PK13GDALRPCInfoV2idPPc
    outputBounds =  [681432, 3959152, 684529, 3963404], #coordinates in dstSRS to process image chip
    xRes=1.2, yRes=1.2, # same as in metadata
    # srcNodata = 0,
    # dstNodata = 0
)

ds = gdal.Warp(PAN_ORTHO_FILE, PAN_FILE, options=pan_warp_options)
ds = None
ds = gdal.Warp(MUL_ORTHO_FILE, MUL_FILE, options=mul_warp_options)
ds = None

# Pansharpening

### Currently the only supported pansharpening algorithm is a "weighted" Brovey algorithm.  https://gdal.org/en/stable/drivers/raster/vrt.html#gdal-vrttut-pansharpen

PAN_ORTHO_FILE = '/data/wfs/darwin-elephant-seal/matsco/wfsai/python_pan_ortho_const.tif'
MUL_ORTHO_FILE = '/data/wfs/darwin-elephant-seal/matsco/wfsai/python_mul_ortho_const.tif'

PSH_FILE = '/data/wfs/darwin-elephant-seal/matsco/wfsai/python_psh_ortho_const.tif'

pan_ds = gdal.Open(PAN_ORTHO_FILE)
pan_band = pan_ds.GetRasterBand(1)

mul_ds = gdal.Open(MUL_ORTHO_FILE)
num_spectral_bands = mul_ds.RasterCount
spectral_bands = [mul_ds.GetRasterBand(i + 1) for i in range(num_spectral_bands)]

#### xml format https://gdal.org/en/stable/drivers/raster/vrt.html#gdal-vrttut-pansharpen
vrt_xml = f'''
<VRTDataset subClass="VRTPansharpenedDataset">
    <PansharpeningOptions>
        <PanchroBand>
            <SourceFilename relativeToVRT="1">{PAN_ORTHO_FILE}</SourceFilename>
            <OpenOptions>
                <OOI key="NUM_THREADS">ALL_CPUS</OOI>
            </OpenOptions>
            <SourceBand>1</SourceBand>
        </PanchroBand>
        <SpectralBand dstBand="1">
            <SourceFilename relativeToVRT="1">{MUL_ORTHO_FILE}</SourceFilename>
            <OpenOptions>
                <OOI key="NUM_THREADS">ALL_CPUS</OOI>
            </OpenOptions>
            <SourceBand>1</SourceBand>
        </SpectralBand>
        <SpectralBand dstBand="2">
            <SourceFilename relativeToVRT="1">{MUL_ORTHO_FILE}</SourceFilename>
            <OpenOptions>
                <OOI key="NUM_THREADS">ALL_CPUS</OOI>
            </OpenOptions>
            <SourceBand>2</SourceBand>
        </SpectralBand>
        <SpectralBand dstBand="3">
            <SourceFilename relativeToVRT="1">{MUL_ORTHO_FILE}</SourceFilename>
            <OpenOptions>
                <OOI key="NUM_THREADS">ALL_CPUS</OOI>
            </OpenOptions>
            <SourceBand>3</SourceBand>
        </SpectralBand>
    </PansharpeningOptions>
</VRTDataset>
'''

vrt_ds = gdal.CreatePansharpenedVRT(vrt_xml, pan_band, spectral_bands) 
psh_ds = gdal.Translate(PSH_FILE, vrt_ds, noData=0, creationOptions=['COMPRESS=LZW', 'BIGTIFF=YES'])
psh_ds = None

"""