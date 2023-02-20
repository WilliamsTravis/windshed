# -*- coding: utf-8 -*-
"""Viewshed Calculator

Created on Tue Feb 14 13:43:12 2023

@author: twillia2
"""
import os

from pathlib import Path

import cupy
import geopandas as gpd
import numpy as np
import rasterio as rio
import rioxarray as xrio

from osgeo import gdal
from xrspatial import viewshed

from windshed.paths import paths


DEM_FPATH = paths["srtm_16_05_soco"]
OUTDIR = Path("~/scratch/viewshed/").expanduser() 
TURBINE_FPATH = paths["uswtdb_v5_3_20230113_soco"]
M_TO_FT = 3.28084


def get_dem(cuda=False):
    """Return subsetted data array and profile."""
    # Use rasterio for the profile
    with rio.open(DEM_FPATH) as r:    
        profile = r.profile

    # Use xrio for the data array
    dem = xrio.open_rasterio(DEM_FPATH)[0]
    if cuda:
        dem.data = cupy.array(dem.data)
    profile["height"] = dem.shape[0]
    profile["width"] = dem.shape[1]

    return dem, profile


def get_position(dem, turbine):
    """Get x, y position of turbine in DEM."""
    # Pick a point within the dem
    x = turbine["x"]
    y = turbine["y"]
    coords = dem.sel(x=x, y=y, method="nearest")
    xi = int(np.where(dem.x == coords.x)[0])
    yi = int(np.where(dem.y == coords.y)[0])
    return xi, yi


def get_turbines(dem):
    """Get turbines within the dem tile."""
    # Get bounding box of dem
    minx = dem.x.min()
    maxx = dem.x.max()
    miny = dem.y.min()
    maxy = dem.y.max()
    bounds = [minx, miny, maxx, maxy]

    # Read in data within bounding box
    df = gpd.read_file(TURBINE_FPATH, bbox=bounds)
    df["index"] = df.index

    # Assign x and y coordinates for convenience later
    df["x"] = df["geometry"].x
    df["y"] = df["geometry"].y

    return df


def get_view(dem, turbine, save=False):
    """Return subsetted data array and profile."""
    # Pick a point within the dem
    x = turbine["x"]
    y = turbine["y"]

    # Get hub height
    if not np.isnan(turbine["t_ttlh"]):
        th = turbine["t_ttlh"]
    else:
        th = 130

    # Convert to feet
    th *= M_TO_FT

    # Calculate viewshed from coordinates
    vs = viewshed(
        dem,
        x=x,
        y=y,
        observer_elev=6,
        target_elev=th
    )
    im = vs.data

    return im


def get_view_gdal(turbine):
    """Return subsetted data array and profile from GDAL's viewshed."""
    # Get DEM subset
    dem, profile = get_dem()

    # Set Curve/refraction coefficient ( Set to 1 for no refraction)
    cc = 1 - (1 / 7)

    # Pick a point within the dem
    x = turbine["x"]
    y = turbine["y"]

    # Get hub height
    if not np.isnan(turbine["t_ttlh"]):
        th = turbine["t_ttlh"]
    else:
        th = 130

    # Convert to feet
    th *= M_TO_FT

    # Get source band
    band = gdal.Open(str(DEM_FPATH)).GetRasterBand(1)
    dst = str(OUTDIR.joinpath("viewshed_gdal_test.tif"))

    # Calculate viewshed from coordinates using Python bindings
    # out = gdal.ViewshedGenerate(
    #     srcBand=band,
    #     driverName="GTiff",
    #     creationOptions="compress=lzw",
    #     targetRasterName=dst,
    #     observerX=x,
    #     observerY=y,
    #     observerHeight=1.5,
    #     targetHeight=th,
    #     noDataVal=-1,
    #     mode=1,
    #     visibleVal=1,
    #     invisibleVal=0,
    #     outOfRangeVal=0,
    #     dfCurvCoeff=cc,
    #     maxDistance=2_000
    # )

    # del out

    # CLI utility command
    cmd  = (f"gdal_viewshed -b 1 -a_nodata -1 -f GTiff -tz {th} -oz 6 "
            f"-ox {x} -oy {y} -om NORMAL {str(DEM_FPATH)} {dst}") 
    os.system(cmd)

    # Read in and return array
    with rio.open(dst) as file:
        view = file.read(1)

    return view
    