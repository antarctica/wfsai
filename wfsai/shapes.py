#!/usr/bin/env python

# File Version: 2025-09-16: First version
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
import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt
from dask import delayed
from wfsai.configuration import _check_path_
from wfsai.setup_logging import logger

"""
This library is for handling shapes in vector shapefile format.
"""

class shapefile:

    """
    This class is specifically for operations when handling vector shapefiles.
    """

    def __init__(self):
        self.src = None
        self.erode_distance = None
        self.max_cull_area = None
        self.out = None
        self.opf = None


    def prunelines(self,
                   source_aoi_path: Union[str, Path],
                   *args, 
                   erode_distance: Optional[Union[float, int]] = 0.75,
                   max_cull_area: Optional[Union[float, int]] = 0.0,
                   output_path: Optional[Union[str, Path]] = None) -> Union[Path, None]:
        """
        Performs erosion of shapefile geometries of very small
        area and tiny width (i.e. lines with zero area).

        The erosion is performed to dispose of the tiny width
        lines and then the erosion is reversed to restore the
        approzimate original areas of the 'non-zero-area' shapes.

        Greater erode_distance values give stronger erosion. The
        default value is 0.75.

        The max_cull_area allows a threshold to be set for
        culling. All areas smaller that max_cull_area will be
        removed.

        If no output_path is specified, the output shapefile(s)
        will be alongside the original with '_prunelines'
        appended to the filename.

        Returns the path of the successfully pruned shapefile.
        Otherwise returns None.
        """
        return_value = None

        logger.info("Starting shapefile.prunelines: %s", 
                    str(source_aoi_path))

        ### STEP 1 - Input checking
        if _check_path_(source_aoi_path):
            self.src = Path(source_aoi_path).resolve()

        else:
            logger.error("source AOI does not exist!")
            self.src = None
            return return_value
        
        if (type(erode_distance) not in (float, int)):
            logger.error("erode_distance must be float or int")
            return return_value
        else:
            self.erode_distance = erode_distance

        if (type(max_cull_area) not in (float, int)):
            logger.error("max_cull_area must be float or int")
            return return_value
        else:
            self.max_cull_area = max_cull_area
        
        if (output_path is not None) and Path(output_path).is_dir():
            self.out = Path(output_path).resolve()
            self.opf = Path(self.src).name.replace(".shp", "_prunelines.shp")
        
        elif (output_path is not None) and not Path(output_path).is_dir():
            self.out = Path(output_path).resolve().parent
            self.opf = Path(output_path).resolve().name

        else:
            if output_path is None:
                self.out = Path(self.src).parent
                self.opf = Path(self.src).name.replace(".shp", "_prunelines.shp")
            else:
                logger.error("output path is not valid")
                self.out = None
                return return_value
        
        ### STEP 2 - Print inputs and outputs
        logger.info("source_aoi_path:              %s", str(self.src))
        logger.info("erode_distance:               %s", str(self.erode_distance))
        logger.info("max_cull_area:                %s", str(self.max_cull_area))
        logger.info("output_path:                  %s", str(self.out))
        logger.info("output_file:                  %s", str(self.opf))

        ### STEP 3 - Load the shapefile into GeoDataFrame
        geo_data_frame = gpd.read_file(self.src)


        ### STEP 4 - Create a list to hold the valid, separated polygons
        final_rows = []

        ### STEP 5 - Iterate through each row in the GeoDataFrame
        for index, row in geo_data_frame.iterrows():
            # a. Apply a negative buffer
            negative_buffer_result = row['geometry'].buffer(-self.erode_distance)

            # b. Apply a positive buffer to bring it back to the original size
            # This also converts it to a valid geometry.
            round_trip_result = negative_buffer_result.buffer(self.erode_distance)
            
            # Check the type of the result
            if round_trip_result.geom_type == 'MultiPolygon':
                # If it's a MultiPolygon, iterate through its parts
                for part in round_trip_result.geoms:
                    # Create a new row with the new geometry and original attributes
                    new_row = {'Location': row['Location'], 'geometry': part}
                    final_rows.append(new_row)
            elif round_trip_result.geom_type == 'Polygon':
                # If it's a single Polygon, just add it
                new_row = { 'Location': row['Location'], 'geometry': round_trip_result}
                final_rows.append(new_row)

        # Create a new GeoDataFrame from the list of rows
        final_gdf = gpd.GeoDataFrame(final_rows, crs=geo_data_frame.crs)

        # Remove any resulting zero-area geometries
        final_gdf = final_gdf[final_gdf.area > self.max_cull_area]

        # Save the corrected shapefile
        final_gdf.to_file(Path.joinpath(self.out, self.opf))

        logger.info("Created prunelines version of %s > %s", self.src.name, self.opf)

        # if pixel_size == None:
        #     gdal.UseExceptions()
        #     with gdal.Open(self.src) as tempds:
        #         geotransform = tempds.GetGeoTransform()
        #         logger.info("geotransform:                 %s", str(geotransform))
        #         self.xres = geotransform[1]
        #         self.yres = geotransform[5] * -1.0
        # else:
        #     pass
        # logger.info("pixel_resolutions:            x: %s , y: %s", str(self.xres), str(self.yres))

        # ### STEP 3.5 - Work out number of raster bands
        # if src_bands is None:
        #     gdal.UseExceptions()
        #     with gdal.Open(self.src) as dataset:
        #         numbands = dataset.RasterCount
        #         bandlist = [i for i in range(numbands)]
        #         bandlist = list(set([1 if i == 0 else i for i in bandlist]))
        #         src_bands = dst_bands = bandlist
        # elif src_bands is not None and dst_bands is None:
        #     dst_bands = src_bands
        # else:
        #     pass
        # logger.info("source bands:                 %s", str(src_bands))
        # logger.info("destination bands:            %s", str(dst_bands))

        # ### STEP 4 - Do the orthorectification
        # outpath = str(Path.joinpath(self.out, self.opf))
        # gdal.UseExceptions()
        # ds = gdal.Warp(outpath, self.src, 
        #     options=self._get_warp_options(self.typ, self.dem, src_bands, dst_bands, dstSRS))
        # if ds is not None:
        #     ds = None
        #     return_value = Path(outpath)

        return return_value
