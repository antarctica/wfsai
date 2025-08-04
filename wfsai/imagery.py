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
        self.xres = None
        self.yres = None
        self.dem = None
        self.out = None
        self.opf = None

    def _get_warp_options(self, image_type: str, 
                            dem_path: Union[Path, None],
                            src_bands: Union[list, None],
                            dst_bands: Union[list, None] ) -> object:
        warp_options = None

        if dem_path is not None:
            #dem_pan_warp_options
            if image_type == 'pan':
                ####taken from https://gdal.org/en/stable/api/python/utilities.html
                warp_options = gdal.WarpOptions(
                    rpc = True, # use rpc for georeferencing
                    dstSRS = 'EPSG:32724',# force output projection
                    transformerOptions = ['RPC_DEM={}'.format(dem_path)], #see https://gdal.org/en/stable/api/gdal_alg.html#_CPPv426GDALCreateRPCTransformerV2PK13GDALRPCInfoV2idPPc
                    #outputBounds =  [681432, 3959152, 684529, 3963404], #coordinates in dstSRS to process image chip
                    xRes=self.xres, yRes=self.yres, # same as in metadata
                    srcNodata = 0,
                    dstNodata = 0)
            #dem_mul_warp_options
            if image_type == 'mul':
                ####taken from https://gdal.org/en/stable/api/python/utilities.html
                warp_options = gdal.WarpOptions(
                    rpc = True, # use rpc for georeferencing
                    srcBands=src_bands,
                    dstBands=dst_bands,
                    dstSRS = 'EPSG:32724',# force output projection
                    transformerOptions = ['RPC_DEM={}'.format(dem_path)], #see https://gdal.org/en/stable/api/gdal_alg.html#_CPPv426GDALCreateRPCTransformerV2PK13GDALRPCInfoV2idPPc
                    #outputBounds =  [681432, 3959152, 684529, 3963404], #coordinates in dstSRS to process image chip
                    xRes=self.xres, yRes=self.yres, # same as in metadata
                    srcNodata = 0,
                    dstNodata = 0)
        
        else:
            #without_dem_pan_warp_options
            if image_type == 'pan':
                #### taken from https://gdal.org/en/stable/api/python/utilities.html
                warp_options = gdal.WarpOptions(
                    rpc = True, # use rpc for georeferencing
                    dstSRS = 'EPSG:32724',# force output projection
                    transformerOptions = ['RPC_HEIGHT=0'], # see https://gdal.org/en/stable/api/gdal_alg.html#_CPPv426GDALCreateRPCTransformerV2PK13GDALRPCInfoV2idPPc
                    #outputBounds =  [681432, 3959152, 684529, 3963404], #coordinates in dstSRS to process image chip
                    xRes=self.xres, yRes=self.yres, # same as in metadata
                    # srcNodata = 0,
                    # dstNodata = 0
                )
            #without_dem_mul_warp_options
            if image_type == 'mul':
                #### taken from https://gdal.org/en/stable/api/python/utilities.html
                warp_options = gdal.WarpOptions(
                    rpc = True, # use rpc for georeferencing
                    srcBands=src_bands,
                    dstBands=dst_bands,
                    dstSRS = 'EPSG:32724',# force output projection
                    transformerOptions = ['RPC_HEIGHT=0'], # see https://gdal.org/en/stable/api/gdal_alg.html#_CPPv426GDALCreateRPCTransformerV2PK13GDALRPCInfoV2idPPc
                    #outputBounds =  [681432, 3959152, 684529, 3963404], #coordinates in dstSRS to process image chip
                    xRes=self.xres, yRes=self.yres, # same as in metadata
                    # srcNodata = 0,
                    # dstNodata = 0
                )
        
        return warp_options

    def orthorectify(self,
                     source_image_path: Union[str, Path],
                     *args, 
                     source_type: Literal['pan', 'mul'],
                     pixel_size: Optional[Union[tuple, list]] = None,
                     src_bands: Optional[list] = None,
                     dst_bands: Optional[list] = None,
                     dem_path: Optional[Union[str, Path]] = None,
                     output_path: Optional[Union[str, Path]] = None) -> Union[Path, None]:
        """
        Performs orthorectification of either a panchromatic or
        multispectral maxar satellite image.

        If no pixel size (x_meters, y_meters) is provided, the
        pixel size of the source image will be used.

        A digital elevation model (dem) can be provided which
        must cover the area of the source imagery. If no dem is
        available then dem_path=None.

        If no output path is provided then the default output
        file is created in the current working directory.

        If no xxx_bands are provided then orthorectification will
        be performed on all bands in the original order.

        Returns the path of the successfully orthorectified
        output file. Otherwise returns None.
        """
        return_value = None

        logger.info("Starting ortho-rectification: %s, %s", 
                    str(source_image_path), str(source_type))

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
        
        if (pixel_size is not None):
            if type(pixel_size) in (tuple, list):
                if len(pixel_size) == 1:
                    self.xres = self.yres = float(pixel_size)
                elif len(pixel_size) == 2:
                    self.xres, self.yres = [float(xy) for xy in pixel_size]
                else:
                    logger.error("unexpected length of pixel size(s)")
                    return return_value

        if (dem_path is not None) and _check_path_(dem_path):
            self.dem = Path(dem_path).resolve()
        else:
            logger.warning("no valid dem specified, continuing without dem")
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
        
        if src_bands is None and dst_bands is not None:
            logger.error("dst_bands cannot be specified without src_bands")
            self.out = None
            return return_value
        
        ortho_tag = "_ortho_const." if self.dem == None else "_ortho."
        self.opf = self.src.parts[-1].split(".")[:-1][0] + \
            ortho_tag + self.src.parts[-1].split(".")[-1].replace("TIL", "tif")
        
        ### STEP 2 - Print inputs and outputs
        logger.info("source_image_path:            %s", str(self.src))
        logger.info("source_type:                  %s", str(self.typ))
        logger.info("digital_elevation_model_path: %s", str(self.dem))
        logger.info("output_path:                  %s", str(self.out))
        logger.info("output_file:                  %s", str(self.opf))

        ### STEP 3 - Get the x and y pixel resolution
        if pixel_size == None:
            gdal.UseExceptions()
            with gdal.Open(self.src) as tempds:
                geotransform = tempds.GetGeoTransform()
                logger.info("geotransform:                 %s", str(geotransform))
                self.xres = geotransform[1]
                self.yres = geotransform[5] * -1.0
        else:
            pass
        logger.info("pixel_resolutions:            x: %s , y: %s", str(self.xres), str(self.yres))

        ### STEP 3.5 - Work out number of raster bands
        if src_bands is None:
            gdal.UseExceptions()
            with gdal.Open(self.src) as dataset:
                numbands = dataset.RasterCount
                bandlist = [i for i in range(numbands)]
                bandlist = list(set([1 if i == 0 else i for i in bandlist]))
                src_bands = dst_bands = bandlist
        elif src_bands is not None and dst_bands is None:
            dst_bands = src_bands
        else:
            pass
        logger.info("source bands:                 %s", str(src_bands))
        logger.info("destination bands:            %s", str(dst_bands))

        ### STEP 4 - Do the orthorectification
        outpath = str(Path.joinpath(self.out, self.opf))
        gdal.UseExceptions()
        ds = gdal.Warp(outpath, self.src, 
            options=self._get_warp_options(self.typ, self.dem, src_bands, dst_bands))
        if ds is not None:
            ds = None
            return_value = Path(outpath)

        return return_value


    def pansharpen(self,
                   pan_image_path: Union[str, Path],
                   mul_image_path: Union[str, Path],
                   *args,
                   output_path: Optional[Union[str, Path]] = None) -> Union[Path, None]:
        """
        Performs orthorectification of either a panchromatic or
        multispectral maxar satellite image.

        If no pixel size (x_meters, y_meters) is provided, the
        pixel size of the source image will be used.

        A digital elevation model (dem) can be provided which
        must cover the area of the source imagery. If no dem is
        available then dem_path=None.

        If no output path is provided then the default output
        file is created in the current working directory.

        Returns the path of the successfully orthorectified
        output file. Otherwise returns None.
        """
        return_value = None

        # Currently the only supported pansharpening algorithm is a "weighted" Brovey algorithm. 
        # https://gdal.org/en/stable/drivers/raster/vrt.html#gdal-vrttut-pansharpen

        logger.info("Starting pan-sharpening: %s, %s", 
                    str(pan_image_path), str(mul_image_path))

        self.src = [None, None]

        ### STEP 1 - Input checking
        if _check_path_(pan_image_path):
            self.src[0] = Path(pan_image_path).resolve()

        else:
            logger.error("pan source image does not exist!")
            self.src = None
            return return_value
        
        if _check_path_(mul_image_path):
            self.src[1] = Path(mul_image_path).resolve()

        else:
            logger.error("mul source image does not exist!")
            self.src = None
            return return_value
        
        if (output_path is not None) and Path(output_path).is_dir():
            self.out = Path(output_path).resolve()
        else:
            if output_path is None:
                self.out = Path.cwd().resolve()
            else:
                logger.error("output path is not valid")
                self.out = None
                return return_value

        # Use the MUL filename as output from pan-sharpening
        sharp_tag = "_psh."
        self.opf = self.src[1].parts[-1].split(".")[:-1][0] + sharp_tag + "tif"

        ### STEP 2 - Print inputs and outputs
        logger.info("pan_image_path:               %s", str(self.src[0]))
        logger.info("mul_image_path:               %s", str(self.src[1]))
        logger.info("output_path:                  %s", str(self.out))
        logger.info("output_file:                  %s", str(self.opf))

        ### STEP 3 - load the imagery PAN & MUL
        gdal.UseExceptions()
        pan_dataset = gdal.Open(self.src[0])
        pan_band = pan_dataset.GetRasterBand(1)

        mul_dataset = gdal.Open(self.src[1])
        num_spectral_bands = mul_dataset.RasterCount
        spectral_bands = [mul_dataset.GetRasterBand(i + 1) for i in range(num_spectral_bands)]
        logger.info("panchromatic bands:           %s", str(1))
        logger.info("multispectral bands:          %s", str(num_spectral_bands))

        ### STEP 4 - define the XML pansharpening config
        #### xml format https://gdal.org/en/stable/drivers/raster/vrt.html#gdal-vrttut-pansharpen
        virtual_raster_format_xml = f'''
<VRTDataset subClass="VRTPansharpenedDataset">
    <PansharpeningOptions>
        <PanchroBand>
            <SourceFilename relativeToVRT="1">{str(self.src[0])}</SourceFilename>
            <OpenOptions>
                <OOI key="NUM_THREADS">ALL_CPUS</OOI>
            </OpenOptions>
            <SourceBand>1</SourceBand>
        </PanchroBand>
        <SpectralBand dstBand="1">
            <SourceFilename relativeToVRT="1">{str(self.src[1])}</SourceFilename>
            <OpenOptions>
                <OOI key="NUM_THREADS">ALL_CPUS</OOI>
            </OpenOptions>
            <SourceBand>1</SourceBand>
        </SpectralBand>
        <SpectralBand dstBand="2">
            <SourceFilename relativeToVRT="1">{str(self.src[1])}</SourceFilename>
            <OpenOptions>
                <OOI key="NUM_THREADS">ALL_CPUS</OOI>
            </OpenOptions>
            <SourceBand>2</SourceBand>
        </SpectralBand>
        <SpectralBand dstBand="3">
            <SourceFilename relativeToVRT="1">{str(self.src[1])}</SourceFilename>
            <OpenOptions>
                <OOI key="NUM_THREADS">ALL_CPUS</OOI>
            </OpenOptions>
            <SourceBand>3</SourceBand>
        </SpectralBand>
    </PansharpeningOptions>
</VRTDataset>
'''
        
        ### STEP 5 - Do the pan-sharpening
        outpath = str(Path.joinpath(self.out, self.opf))
        gdal.UseExceptions()

        vrt_ds = gdal.CreatePansharpenedVRT(virtual_raster_format_xml, pan_band, spectral_bands) 
        psh_ds = gdal.Translate(outpath, vrt_ds, noData=0, creationOptions=['COMPRESS=LZW', 'BIGTIFF=YES'])

        if psh_ds is not None:
            psh_ds = None
            return_value = Path(outpath)

        return return_value


class tiling:

    """
    This class is specifically for tiling operations on satellite imagery.
    """

    def __init__(self):
        self.src = None
    
    def tile(self,
             source_image_path: Union[str, Path],
             chunk_dimensions: Union[tuple, list],
             *args, 
             yx_px_step: Optional[Union[tuple, list]] = (0,0),
             output_dir_path: Optional[Union[str, Path]] = None) -> None:
        """
        Performs tiling of a geotiff satellite image. Given the
        source_image_path and chunk_dimensions.

        The chunk_dimensions should be a three element tuple or
        list with the first element being the number of
        spectral_bands, then the chunk_height followed by
        chunk_width, both in pixels. i.e:
          (spectral_bands, chunk_height, chunk_width)

        The optional yx_px_step parameter can be provided if
        stepped offset tiles are required (tiles will overlap).
        i.e:
          (y_pixel_step, x_pixel_step)

        If no output_dir_path is provided then the default output
        directory for the tiles is the same as the input file's
        directory.

        Returns None.
        """
        return_value = None