# -*- coding: utf-8 -*-
"""Viewshed Calculator

Created on Tue Feb 14 13:43:12 2023

@author: twillia2
"""
from pathlib import Path

import matplotlib.pyplot as plt
import rasterio as rio
import rioxarray as xrio

from xrspatial import viewshed

from windshed.paths import paths


DEM = paths["srtm_16_05"]
OUTDIR = Path("~/scratch/viewshed/").expanduser() 


# Sample sizes and point position
SX = 2_000
SY = 2_000
PX = 499
PY = 250


# Target elevation
TARGET_ELEV = 120

def get_dem():
    """Return subsetted data array and profile."""
    # Use rasterio for the profile
    with rio.open(DEM) as r:    
        profile = r.profile

    # Use xrio for the data array
    dem = xrio.open_rasterio(DEM)[0, :SY, :SX]

    # update profile
    profile["height"] = dem.shape[0]
    profile["width"] = dem.shape[1]

    # If you don't start at the origin, you'll have to update the transform

    return dem, profile


def get_view(dem):
    """Return subsetted data array and profile."""
    # Pick a point within the dem
    x = float(dem.x[PX])
    y = float(dem.y[PY])

    # Calculate viewshed from coordinates
    vs = viewshed(dem, x=x, y=y, observer_elev=1.5, target_elev=TARGET_ELEV)
    im = vs.data

    # Create a nice block for the target elevation
    im[PY-4:PY+4, PX-4:PX+4] = -9999

    return im


def main():
    """Calculate viewshed with single core CPU."""
    # Create temp dir
    OUTDIR.mkdir(exist_ok=True, parents=True)

    # Get dem subset
    dem, profile = get_dem()

    # Get viewshed array
    view = get_view(dem)

    # Save dem
    dst = OUTDIR.joinpath("dem_test.tif")
    with rio.open(dst, "w", **profile) as file:
        file.write(dem.data, 1)

    # Save view
    dst = OUTDIR.joinpath("viewshed_test.tif")
    with rio.open(dst, "w", **profile) as file:
        file.write(view, 1)


if __name__ == "__main__":
    main()
