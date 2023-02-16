# -*- coding: utf-8 -*-
"""Viewshed Calculator

Created on Tue Feb 14 13:43:12 2023

@author: twillia2
"""
import multiprocessing as mp
import time

from pathlib import Path

import cupy
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio as rio
import rioxarray as xrio

from tqdm import tqdm
from xrspatial import viewshed

from windshed.paths import paths


DEM_FPATH = paths["srtm_16_05"]
OUTDIR = Path("~/scratch/viewshed/").expanduser() 
TDB_FPATH = paths["uswtdb_v5_3_20230113"]


def get_turbines(dem):
    """Get turbines within the dem tile."""
    # Get bounding box of dem
    minx = dem.x.min()
    maxx = dem.x.max()
    miny = dem.y.min()
    maxy = dem.y.max()
    bounds = [minx, miny, maxx, maxy]
    df = gpd.read_file(TDB_FPATH, bbox=bounds)
    return df


def get_dem():
    """Return subsetted data array and profile."""
    # Use rasterio for the profile
    with rio.open(DEM_FPATH) as r:    
        profile = r.profile

    # Use xrio for the data array
    dem = xrio.open_rasterio(DEM_FPATH)[0, :3_000, :3_000]
    dem.data = cupy.array(dem.data)
    profile["height"] = dem.shape[0]
    profile["width"] = dem.shape[1]

    return dem, profile


def get_view(args):
    """Return subsetted data array and profile."""
    # Unpack args
    dem, turbine = args

    # Pick a point within the dem
    tlon = turbine["xlong"]
    tlat = turbine["ylat"]
    coords = dem.sel(x=tlon, y=tlat, method="nearest")
    x = int(np.where(dem.x == coords.x)[0])
    y = int(np.where(dem.y == coords.y)[0])

    # Get hub height
    if not np.isnan(turbine["t_ttlh"]):
        th = turbine["t_ttlh"]
    else:
        th = 130

    # Calculate viewshed from coordinates
    vs = viewshed(
        dem,
        x=coords.x,
        y=coords.y,
        observer_elev=1.5,
        target_elev=th
    )
    im = vs.data

    # Create a nice block for the target elevation
    im[y-4:y+4, x-4:x+4] = -9999

    return im


def main():
    """Calculate viewshed with single core CPU."""
    # Timers!
    then = time.time()

    # Create temp dir
    OUTDIR.mkdir(exist_ok=True, parents=True)

    # Get dem subset
    dem, profile = get_dem()

    # Get turbines
    turbines = get_turbines(dem)
    turbines = turbines[:100]

    # Get viewshed array
    arg_list = [(dem, turbine) for _, turbine in turbines.iterrows()]
    # nturbines = turbines.shape[0]
    # views = []
    # with mp.Pool(mp.cpu_count() - 1) as pool:
    #     for view in tqdm(pool.imap(get_view, arg_list), total=nturbines):
    #         views.append(view)

    # Get viewshed array
    views = []
    for args in tqdm(arg_list):
        break
        view = get_view(args)
        views.append(view)

    # Build composite
    view = np.array(views).max(axis=0)

    # Save view
    dst = OUTDIR.joinpath("viewshed_test.tif")
    with rio.open(dst, "w", **profile) as file:
        file.write(view, 1)

    # Save specific turbines
    turbines.to_file(OUTDIR.joinpath("turbines_test.gpkg"), "GPKG")

    # Time it
    now = time.time()
    duration = now - then
    print(f"Finished in {round(duration / 60, 2)} minutes")


# if __name__ == "__main__":
#     main()
