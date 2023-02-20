# -*- coding: utf-8 -*-
"""Utilities for retrieving and modifying input datasets.

Created on Feb 20th 2022

@author: twillia2
"""
import ee

from windshed.main import OUTDIR

ee.Initialize()


def get_dsm():
    """Get the Copernicus 30m DSM for CONUS."""

