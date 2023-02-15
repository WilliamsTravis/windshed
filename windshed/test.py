# -*- coding: utf-8 -*-
"""Viewshed Calculator

Created on Tue Feb 14 13:43:12 2023

@author: twillia2
"""
from pathlib import Path

import matplotlib.pyplot as plt
import rasterio as rio

from xrspatial import viewshed


DEM = Path("data/srtm_16_05.tif")
OUTDIR = Path("~/scratch/viewshed/").expanduser() 


def main():
    """Calculate viewshed with single core CPU."""
    # Open dem and data array
    r = rio.open(DEM)
    profile = 
    dem = r[0][:500, :500]

    # Pick a point within the dem
    x = float(dem.x[499])
    y = float(dem.y[250])

    # Calculate viewshed from coordinates
    vs = viewshed(dem, x=x, y=y, observer_elev=1.5, target_elev=120)
    im = vs.data
    dim = dem.data
    plt.imshow(dem)
    plt.imshow(im)


if __name__ == "__main__":
    main()
