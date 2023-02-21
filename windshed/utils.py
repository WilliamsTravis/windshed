# -*- coding: utf-8 -*-
"""Utilities for retrieving and modifying input datasets.

Created on Feb 20th 2022

@author: twillia2
"""
import json
import urllib

import ee
import zipfile

from windshed.main import OUTDIR

ee.Initialize()


CO_BBOX = [-105.2961,39.4645,-104.6023,40.01]
GLO30_PATH = "projects/sat-io/open-datasets/GLO-30"


def get_dsm():
    """Get the Copernicus 30m DSM for CONUS."""
    # Open the 
    glo30 = ee.ImageCollection(GLO30_PATH)
    xmin, ymin, xmax, ymax = CO_BBOX
    region = ee.Geometry.BBox(*CO_BBOX)

    # What's in here
    i1 = glo30.mosaic()

    # Information methods appear to be broken
    url = i1.getDownloadURL(
        {
            "name": "glo30_dsm_sample",
            "scale": 30,
            "region": region,
            "crs": "epsg:4326"
        }
    )

    # Download file
    dst = OUTDIR.joinpath("glo30_dsm_sample.zip")
    urllib.request.urlretrieve(url, dst)
    with zipfile.ZipFile(dst) as zfile:
        zfile.extractall()


if __name__ == "__main__":
    get_dsm()
