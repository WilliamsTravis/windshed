# -*- coding: utf-8 -*-
"""Viewshed Calculator

Created on Tue Feb 14 13:43:12 2023

@author: twillia2
"""
import time
import warnings

import cartopy.crs as ccrs
import cupy
import matplotlib.pyplot as plt
import numpy as np
import rasterio as rio

from numba import NumbaPerformanceWarning
from xrspatial import hillshade

from windshed.main import (
    get_dem,
    get_position,
    get_turbines,
    get_view,
    get_view_gdal,
    OUTDIR
)

plt.close("all")
warnings.filterwarnings("ignore", category=NumbaPerformanceWarning)  # <------- Check this out later


def single_map(dem, turbine, view, duration=None):
    """Map one viewshed."""
    # Convert the cupy array to a numpy array
    if isinstance(view, cupy.ndarray):
        view = view.get()
        device = "GPU"
        shadows = True
    else:
        device = "CPU"
        shadows = True

    # Set no values
    view[view == -1] = np.nan

    # Create a hillshade
    hs = hillshade(dem, shadows=shadows)
    hs = (hs - 1) * -1

    # Get x, y position of turbine
    x, y = get_position(dem, turbine)

    # Create figure
    fig, axis = plt.subplots(1, 1, figsize=(10, 10))

    # CPU Results 
    if duration:
        axis.set_title(f"{device} Viewshed - {duration:.3f} Seconds")
    else:
        axis.set_title(f"{device} Viewshed")
    axis.imshow(hs.data, cmap="gray")
    axis.imshow(view, cmap="Reds", alpha=0.5)
    axis.scatter(x, y, s=90, c="black")
    axis.scatter(x, y, s=40, c="red")
    axis.set_axis_off()


def sub_plot(ax, view, dem, hs, x, y, duration):
    """Build subplot of songle viewshed."""
    # Convert the cupy array to a numpy array
    if isinstance(view, cupy.ndarray):
        view = view.get()
        device = "GPU"
    else:
        device = "CPU"

    # Determine if this is from gdal (won't have -1)
    if -1 not in view:
        device += "(GDAL)"

    # Convert to float to hide nan values
    na = -1
    if "int" in str(view.dtype):
        view = view.astype("float16")
        na = 0

    # Set no values
    view[view == na] = np.nan

    # Plot
    ax.set_title(f"{device} Viewshed - {duration:.3f} Seconds")
    ax.imshow(dem.data, cmap="gray")
    ax.imshow(hs, cmap="gray", alpha=0.75)
    ax.imshow(view, cmap="Blues", alpha=0.85)
    ax.scatter(x, y, s=90, c="black")
    ax.scatter(x, y, s=40, c="red")
    ax.set_axis_off()


def comparison_map(dem, turbine, view1=None, view2=None, view3=None,
                   duration1=None, duration2=None, duration3=None):
    """Map multiple viewsheds."""
    # Create a hillshade
    hs = hillshade(dem)
    hs = (hs - 1) * -1

    # Get x, y position of turbine
    x, y = get_position(dem, turbine)

    # Collect views
    views = [view1, view2, view3]
    views = [view for view in views if view is not None]
    durations = [duration1, duration2, duration3]
    durations = [d for d in durations if d is not None]
    nplots = len(views)

    # Create figure
    fig, axes = plt.subplots(1, nplots, gridspec_kw=dict(left=0.1, right=0.9,
                             bottom=0.1, top=0.9), figsize=(10 * nplots, 10))
    if not isinstance(axes, np.ndarray):
        axes = [axes]

    for i, view in enumerate(views):
        duration = durations[i]
        sub_plot(axes[i], view, dem, hs, x, y, duration)

    # Tighten image
    dst = OUTDIR.joinpath("viewshed_comparison.png")
    plt.savefig(dst)


def main(cpu=False, gdal=False, gpu=False):
    """Calculate viewshed with single core CPU."""
    # Get a numpy and cupy DEM 
    dem, profile = get_dem()
    cdem, profile = get_dem(cuda=True)

    # Get turbine
    dst = OUTDIR.joinpath("test_turbine.gpkg")
    turbines = get_turbines(dem)
    wturbine = turbines[turbines["index"] == 124]
    turbine = turbines.iloc[124]  # One for now
    wturbine.to_file(dst, "GPKG")

    # I need these coordinates
    print(f"Running viewshed for {turbine.x}, {turbine.y}")

    # Set initial outputs to None
    view1 = None
    view2 = None
    view3 = None
    duration1 = None
    duration2 = None
    duration3 = None

    # Run get_view with cuda
    if gpu:
        print("Running viewshed with GPU...")
        then = time.perf_counter()
        view1 = get_view(cdem, turbine)
        now = time.perf_counter()
        duration1 = now - then
        print(f"Finished in {round(duration1 / 60, 6)} minutes\n")
    
        # Write to file
        profile["dtype"] = view1.dtype
        dst = OUTDIR.joinpath("viewshed_gpu_test.tif")
        array = view1.get()
        with rio.open(dst, "w", **profile) as file:
            file.write(array, 1)

    # Run get_view without cuda
    if cpu:
        print("Running viewshed with CPU...")
        then = time.perf_counter()
        view2 = get_view(dem, turbine)
        now = time.perf_counter()
        duration2 = now - then
        print(f"Finished in {round(duration2 / 60, 6)} minutes\n")

    if gdal:
        print("Running viewshed with CPU and GDAL...")
        then = time.perf_counter()
        view3 = get_view_gdal(turbine)
        now = time.perf_counter()
        duration3 = now - then
        print(f"Finished in {round(duration3 / 60, 6)} minutes\n")

    # Compare the outputs to make sure they match
    comparison_map(dem, turbine, view1, view2, view3, duration1, duration2,
                   duration3)


if __name__ == "__main__":
    cpu = False
    gdal = True
    gpu = True
    main(gpu=gpu, cpu=cpu, gdal=gdal)
