#!/usr/bin/env python

# File Version: 2025-05-14: First version
#               2025-08-04: Second version
#               2025-08-13: Added dynamic pansharpen bands
#
# Author: matsco@bas.ac.uk

import sys
import os
import shutil
import yaml
import glob
import dask
import rioxarray as rxr
from pathlib import Path
from typing import Optional
from typing import Literal
from typing import Union
from osgeo import gdal
from math import ceil
from numpy import zeros as np_zeros
import pandas as pd
from matplotlib import pyplot as plt
from dask import delayed
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
                            dst_bands: Union[list, None],
                            dSRS: str ) -> object:
        warp_options = None

        if dem_path is not None:
            #dem_pan_warp_options
            if image_type == 'pan':
                ####taken from https://gdal.org/en/stable/api/python/utilities.html
                warp_options = gdal.WarpOptions(
                    rpc = True, # use rpc for georeferencing
                    dstSRS = str(dSRS),
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
                    dstSRS = str(dSRS),
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
                    dstSRS = str(dSRS),
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
                    dstSRS = str(dSRS),
                    transformerOptions = ['RPC_HEIGHT=0'], # see https://gdal.org/en/stable/api/gdal_alg.html#_CPPv426GDALCreateRPCTransformerV2PK13GDALRPCInfoV2idPPc
                    #outputBounds =  [681432, 3959152, 684529, 3963404], #coordinates in dstSRS to process image chip
                    xRes=self.xres, yRes=self.yres, # same as in metadata
                    # srcNodata = 0,
                    # dstNodata = 0
                )
        
        return warp_options

    
    def _get_virtual_raster_format(self, number_of_bands: int) -> str:
        """
        Returns the specific virtual raster bands configuration
        in XML format.
        """
        virt_raster_format =       '<VRTDataset subClass="VRTPansharpenedDataset">\n'+ \
                                   '    <PansharpeningOptions>\n'+ \
                                   '        <PanchroBand>\n'+ \
                                   '            <SourceFilename relativeToVRT="1">'+ \
                                        f'{str(self.src[0])}'+'</SourceFilename>\n'+ \
                                   '            <OpenOptions>\n'+ \
                                   '                <OOI key="NUM_THREADS">ALL_CPUS</OOI>\n'+ \
                                   '            </OpenOptions>\n'+ \
                                   '            <SourceBand>1</SourceBand>\n'+ \
                                   '        </PanchroBand>\n'

        for band in range(1, number_of_bands+1):
            virt_raster_format += f'        <SpectralBand dstBand="{str(band)}">\n'+ \
                                   '            <SourceFilename relativeToVRT="1">'+ \
                                            f'{str(self.src[1])}</SourceFilename>\n'+ \
                                   '            <OpenOptions>\n'+ \
                                   '                <OOI key="NUM_THREADS">ALL_CPUS</OOI>\n'+ \
                                   '            </OpenOptions>\n'+ \
                                  f'            <SourceBand>{str(band)}</SourceBand>\n'+ \
                                   '        </SpectralBand>\n'

        virt_raster_format +=      '    </PansharpeningOptions>\n'+ \
                                   '</VRTDataset>\n'

        return virt_raster_format


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
        
        with rxr.open_rasterio(self.src, masked=True) as im:
            dstSRS = str(im.rio.crs)
        
        ortho_tag = "_ortho_const." if self.dem == None else "_ortho."
        self.opf = self.src.parts[-1].split(".")[:-1][0] + \
            ortho_tag + self.src.parts[-1].split(".")[-1].replace("TIL", "tif")
        
        ### STEP 2 - Print inputs and outputs
        logger.info("source_image_path:            %s", str(self.src))
        logger.info("source_type:                  %s", str(self.typ))
        logger.info("source crs:                   %s", dstSRS)
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
            options=self._get_warp_options(self.typ, self.dem, src_bands, dst_bands, dstSRS))
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
        virtual_raster_format_xml = self._get_virtual_raster_format(num_spectral_bands)
#         virtual_raster_format_xml = f'''
# <VRTDataset subClass="VRTPansharpenedDataset">
#     <PansharpeningOptions>
#         <PanchroBand>
#             <SourceFilename relativeToVRT="1">{str(self.src[0])}</SourceFilename>
#             <OpenOptions>
#                 <OOI key="NUM_THREADS">ALL_CPUS</OOI>
#             </OpenOptions>
#             <SourceBand>1</SourceBand>
#         </PanchroBand>
#         <SpectralBand dstBand="1">
#             <SourceFilename relativeToVRT="1">{str(self.src[1])}</SourceFilename>
#             <OpenOptions>
#                 <OOI key="NUM_THREADS">ALL_CPUS</OOI>
#             </OpenOptions>
#             <SourceBand>1</SourceBand>
#         </SpectralBand>
#         <SpectralBand dstBand="2">
#             <SourceFilename relativeToVRT="1">{str(self.src[1])}</SourceFilename>
#             <OpenOptions>
#                 <OOI key="NUM_THREADS">ALL_CPUS</OOI>
#             </OpenOptions>
#             <SourceBand>2</SourceBand>
#         </SpectralBand>
#         <SpectralBand dstBand="3">
#             <SourceFilename relativeToVRT="1">{str(self.src[1])}</SourceFilename>
#             <OpenOptions>
#                 <OOI key="NUM_THREADS">ALL_CPUS</OOI>
#             </OpenOptions>
#             <SourceBand>3</SourceBand>
#         </SpectralBand>
#     </PansharpeningOptions>
# </VRTDataset>
# '''
        
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
        self.output_dir_path = None
        self.chunk_dimensions = None
        self.yx_px_step = None
        self.bands = None
        self.png_dir_path = None
    
    ######################################################
# [3.0] Method for processing each chunk
    def _process_chunk(self,
                       x_idx,
                       y_idx,
                       chunk_data,
                       output_dir,
                       pngs_dir,
                       rgb_bands,
                       tiff_ref):
        """Save scene as tiles using dask chunks, 
        export to geotiff and png."""

        # If chunk is empty don't save
        if bool(chunk_data.isnull().all()):
            return None # Skip saving empty chunks  

        else:
            # Save raster tile
            tile_filename = f"{tiff_ref}_tile_{x_idx}_{y_idx}.tif"
            png_filename = f"{tiff_ref}_tile_{x_idx}_{y_idx}.png"
            tile_raster_path = Path.joinpath(output_dir, tile_filename)

            size_string = "("+str(chunk_data.sizes["y"])+","+str(chunk_data.sizes["x"])+")"
            logger.info("Saving raster: %s %s", str(Path(tile_raster_path).name), size_string)
            chunk_data.rio.to_raster(tile_raster_path, driver="GTiff", compress='lzw')

            if pngs_dir is not None:
                # Save png file
                plt.rcParams['figure.max_open_warning'] = 500
                tile_png_path = Path.joinpath(pngs_dir, png_filename)
                logger.info("Saving png: %s", str(Path(tile_png_path).name))
                chunk_data.sel(band=rgb_bands).plot.imshow(robust=True, size=6)
                fig = plt.gcf()
                fig.savefig(Path(tile_png_path), bbox_inches="tight")
                plt.close(fig)

            return tile_raster_path




    def tile(self,
             source_image_path: Union[str, Path],
             chunk_dimensions: Union[tuple, list],
             *args, 
             yx_px_step: Optional[Union[tuple, list]] = None,
             png_dir_path: Optional[Union[str, Path]] = None,
             bands: Optional[list] = None,
             backstep: Optional[bool] = False,
             pad_for_uniform: Optional[bool] = True,
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
        
        The optional png_dir_path will produce summary pngs for
        all tiles in the directory specified. If no directory is
        specified then no pngs are created. PNG creation is slow.

        The optional bands allows specific bands to be selected
        for the output tiles (this also determines the band
        order). If bands is not specified, the original image
        bands and order are used.

        The optional backstep refers to how the far right and far
        bottom edges are tiled if the chunk dimensions are not a
        whole multiple of the original image size. By default the
        backstep is disabled. Enabling would force uniform chunk
        sizes for the edges by backstepping. pad_for_uniform must
        be disbaled for this to work.

        The optional pad_for_uniform will add 'edge' padding to the
        source imagery to allow uniform output tile dimensions
        without using backstepping. This is enabled by default and
        overrides any enabled backstepping.

        If no output_dir_path is provided then the default output
        directory for the tiles is the same as the input file's
        directory.

        A reference CSV file is created in the output directory
        showing all tiles created and their image reference.

        Returns None.
        """
        return_value = None

        # check the source image path
        if _check_path_(source_image_path):
            self.src = Path(source_image_path).resolve()
        
        # check the chunk dimensions
        if type(chunk_dimensions) in [tuple, list]:
            if len(chunk_dimensions) == len([0,0,0]):
                self.chunk_dimensions = chunk_dimensions
            else:
                logger.error("Chunk dimensions size NOT equal to 3!")
        else:
            logger.error("Chunk dimensions not of correct type!")

        # check the bands
        if bands is not None:
            self.bands = bands
        else:
            raster = rxr.open_rasterio(Path(source_image_path), masked=True)
            self.bands = raster.band.to_dict()['data']

        # check the output_dir
        if output_dir_path is not None:
            if Path(Path(output_dir_path).resolve()).is_dir():
                self.output_dir_path = Path(output_dir_path).resolve()
            else:
                logger.error("output_dir_path is not a directory!")
                self.output_dir_path = None
        else:
            self.output_dir_path = \
              Path(source_image_path).resolve().parent

        # check yx_px_step
        if yx_px_step is not None:
            if type(yx_px_step) in [tuple, list]:
                if len(yx_px_step) == len([0,0]):
                    self.yx_px_step = yx_px_step
                else:
                    logger.error("yx_px_step NOT of length 2")
                    self.yx_px_step = None
            else:
                logger.error("yx_px_step is NOT tuple or list")
                self.yx_px_step = None
        else:
            self.yx_px_step = self.chunk_dimensions[1:]

        # check backstep
        if type(backstep) is not type(False):
            logger.error("backstep is NOT of type bool")
            backstep = False
        if pad_for_uniform == True:
            backstep = False
        
        # check pad_for_uniform
        if type(pad_for_uniform) is not type(False):
            logger.error("pad_for_uniform is NOT of type bool")
            pad_for_uniform = True

        # check for pngs_dir
        if png_dir_path is not None:
            if Path(Path(png_dir_path).resolve()).is_dir():
                self.png_dir_path = Path(png_dir_path).resolve()
            else:
                logger.error("png_dir_path is not a directory!")
                self.png_dir_path = None
        else:
            self.png_dir_path = None
        

        tiff_ref = os.path.basename(self.src).split(".")[0]
        logger.info("Starting tiling of image:     %s", str(Path(self.src).name))
        logger.info("Image tiff ref:               %s", str(tiff_ref))
        logger.info("output_dir_path:              %s", str(self.output_dir_path))
        logger.info("chunk_dimensions:             %s", str(self.chunk_dimensions))
        logger.info("bands:                        %s", str(self.bands))
        logger.info("yx_px_step:                   %s", str(self.yx_px_step))
        logger.info("backstep_enabled:             %s", str(backstep))
        logger.info("pad_for_uniform enabled:      %s", str(pad_for_uniform))
        logger.info("png_dir_path:                 %s", str(self.png_dir_path))

        raster = rxr.open_rasterio(Path(self.src),
                    chunks=self.chunk_dimensions,
                    masked=True)

        # Here the original raster may need to be padded with nans
        # for uniform tile output.
        if pad_for_uniform:
            if (raster.chunks[1:][0][-1], {raster.chunks[1:][1][-1]}) != self.yx_px_step:
                logger.info("Padding enabled and required: (%s, %s)",
                                raster.chunks[1:][0][-1], raster.chunks[1:][1][-1])

                pad_rows = (self.yx_px_step[0] - (raster.shape[1] % self.yx_px_step[0])) % self.yx_px_step[0]
                pad_cols = (self.yx_px_step[1] - (raster.shape[2] % self.yx_px_step[1])) % self.yx_px_step[1]
                logger.info(f"Padding (rows, cols):         (+{pad_rows}, +{pad_cols})")

                padded_raster = raster.pad(
                    pad_width={ "y": (0, pad_rows), "x": (0, pad_cols) },
                    mode='edge')

                raster = padded_raster.chunk({"x": self.chunk_dimensions[2], "y": self.chunk_dimensions[1]})

        # Create Dask delayed tasks for each chunk
        delayed_tasks = []

        for y_idx in range(ceil(raster.sizes["y"] / self.yx_px_step[0])):
            
            for x_idx in range(ceil(raster.sizes["x"] / self.yx_px_step[1])):

                if backstep:
                    # Account for not slicing over the right and bottom edges
                    ydim = raster.sizes["y"] - ((y_idx * self.yx_px_step[0]) + self.chunk_dimensions[1])
                    xdim = raster.sizes["x"] - ((x_idx * self.yx_px_step[1]) + self.chunk_dimensions[2])
                    ybackstep = ydim if ydim < 0 else 0
                    xbackstep = xdim if xdim < 0 else 0
                else:
                    ybackstep = xbackstep = 0

                # Select chunk
                chunk = raster.isel(
                    y=slice((y_idx * self.yx_px_step[0]) + ybackstep, (y_idx * self.yx_px_step[0]) + self.chunk_dimensions[1] + ybackstep),
                    x=slice((x_idx * self.yx_px_step[1]) + xbackstep, (x_idx * self.yx_px_step[1]) + self.chunk_dimensions[2] + xbackstep)
                )

                # Add to delayed task with explicit arguments
                delayed_tasks.append(
                    delayed(self._process_chunk)(x_idx, y_idx, chunk,
                                                self.output_dir_path,
                                                self.png_dir_path,
                                                self.bands, tiff_ref))

        # Compute all tasks in parallel
        img_refs = dask.compute(*delayed_tasks)
        tile_df = pd.DataFrame(img_refs, columns=["im_ref"])
        tile_df.to_csv(Path.joinpath(self.output_dir_path, str(tiff_ref)+"_tile_list.csv" ))

        return return_value