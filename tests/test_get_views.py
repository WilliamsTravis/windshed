# -*- coding: utf-8 -*-
"""Viewshed Calculator

Created on Tue Feb 14 13:43:12 2023

@author: twillia2
"""
import time
import warnings

import cupy
import numpy as np

from numba import NumbaPerformanceWarning

from windshed.main import (
    get_dem,
    get_position,
    get_turbines,
    get_view,
    get_view_gdal,
    OUTDIR
)

warnings.filterwarnings("ignore", category=NumbaPerformanceWarning)  # <------- Check this out later

DEM, _ = get_dem()
CDEM, _ = get_dem(cuda=True)
TURBINE = get_turbines(DEM, rows=1)


def test_cpu():
    """get_view without cuda."""
    print("Running viewshed with CPU...")
    then = time.perf_counter()
    _ = get_view(DEM, TURBINE)
    now = time.perf_counter()
    duration = now - then
    print(f"Finished in {round(duration / 60, 6)} minutes\n")


def test_gdal():
    """Test GDAL's method."""
    print("Running viewshed with CPU and GDAL...")
    then = time.perf_counter()
    _ = get_view_gdal(DEM, TURBINE)
    now = time.perf_counter()
    duration = now - then
    print(f"Finished in {round(duration / 60, 6)} minutes\n")


def test_gpu():
    """Test GPU/CUDA method."""
    print("Running viewshed with GPU...")
    then = time.perf_counter()
    _ = get_view(CDEM, TURBINE)
    now = time.perf_counter()
    cduration = now - then
    print(f"Finished in {round(cduration / 60, 6)} minutes\n")
