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
from typing import Optional
from typing import Literal
from typing import Union
from osgeo import gdal
from wfsai.configuration import _check_path_
from wfsai.setup_logging import logger

"""
This library is for handling imagery for pre or post AI tasks.
"""

class maxar:

    """
    This class is specifically for operations when handling Maxar satellite imagery.
    """

    def __init__(self):
        self.src = None
        self.typ = None
        self.dem = None
        self.out = None
        self.opf = None

    def _get_warp_options(self, image_type: str, dem_path: Optional[Path] = None) -> object:
        warp_options = None

        if dem_path is not None:
            #dem_pan_warp_options
            if image_type == 'pan':
                ####taken from https://gdal.org/en/stable/api/python/utilities.html
                warp_options = gdal.WarpOptions(
                    rpc = True, # use rpc for georeferencing
                    dstSRS = 'EPSG:32724',# force output projection
                    transformerOptions = ['RPC_DEM={}'.format(dem_path)], #see https://gdal.org/en/stable/api/gdal_alg.html#_CPPv426GDALCreateRPCTransformerV2PK13GDALRPCInfoV2idPPc
                    outputBounds =  [681432, 3959152, 684529, 3963404], #coordinates in dstSRS to process image chip
                    xRes=0.5, yRes=0.5, # same as in metadata
                    srcNodata = 0,
                    dstNodata = 0)
            #dem_mul_warp_options
            if image_type == 'mul':
                ####taken from https://gdal.org/en/stable/api/python/utilities.html
                warp_options = gdal.WarpOptions(
                    rpc = True, # use rpc for georeferencing
                    srcBands=[1,2,3],
                    dstBands=[3,2,1],
                    dstSRS = 'EPSG:32724',# force output projection
                    transformerOptions = ['RPC_DEM={}'.format(dem_path)], #see https://gdal.org/en/stable/api/gdal_alg.html#_CPPv426GDALCreateRPCTransformerV2PK13GDALRPCInfoV2idPPc
                    outputBounds =  [681432, 3959152, 684529, 3963404], #coordinates in dstSRS to process image chip
                    xRes=1.2, yRes=1.2, # same as in metadata
                    srcNodata = 0,
                    dstNodata = 0)
        
        return warp_options

    def orthorectify(self,
                     source_image_path: Union[str, Path],
                     source_type: Literal['pan', 'mul'],
                     dem_path: Optional[Union[str, Path]] = None,
                     output_path: Optional[Union[str, Path]] = None) -> Union[Path, None]:
        """
        Performs orthorectification of either a panchromatic or
        multispectral maxar satellite image.
        A digital elevation model (dem) can be provided which
        must cover the area of the source imagery. If no dem is
        available then dem_path=None.

        If no output path is provided then the default output
        file is created in the current working directory.

        Returns the path of the successfully orthorectified
        output file. Otherwise returns None.
        """
        return_value = None

        ### STEP 1 - Input checking
        if _check_path_(source_image_path):
            self.src = Path(source_image_path).resolve()

        else:
            logger.error("source image does not exist!")
            self.src = None
            return return_value

        if str(source_type) in ('pan', 'mul'):
            self.typ = str(source_type)
        else:
            logger.error("source_type must be 'pan' or 'mul'!")
            return return_value
        
        if (dem_path is not None) and _check_path_(dem_path):
            self.dem = Path(dem_path).resolve()
        else:
            logger.error("no valid dem specified")
            self.dem = None
        
        if (output_path is not None) and Path(output_path).is_dir():
            self.out = Path(output_path).resolve()
        else:
            if output_path is None:
                self.out = Path.cwd().resolve()
            else:
                logger.error("output path is not valid")
                self.out = None
                return return_value
        
        self.opf = self.src.parts[-1].split(".")[:-1][0] + \
            "_ortho." + self.src.parts[-1].split(".")[-1].replace("TIL", "tif")
        
        ### STEP 2 - Print inputs and outputs
        logger.info("source_image_path:            %s", str(self.src))
        logger.info("source_type:                  %s", str(self.typ))
        logger.info("digital_elevation_model_path: %s", str(self.dem))
        logger.info("output_path:                  %s", str(self.out))
        logger.info("output_file:                  %s", str(self.opf))

        ### STEP 3 - Do the orthorectification
        outpath = str(Path.joinpath(self.out, self.opf))
        gdal.UseExceptions()
        ds = gdal.Warp(outpath, self.src, 
            options=self._get_warp_options(self.typ, self.dem))
        if ds is not None:
            ds = None
            return_value = Path(outpath)

        return return_value

    #TODO What do I want the maxar data handling to actually do?
    # 1. Take in a single satellite image and ortho-rectify.
    # 2. Take in both PAN and MUL ortho-rectified images and output
    #    a pan sharpened image.
    


"""
Dump from jupyter notebook
==========================

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