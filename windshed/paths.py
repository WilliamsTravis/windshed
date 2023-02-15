# -*- coding: utf-8 -*-
"""Package Data Helpers.

Created on Mon May 23 20:31:32 2022

@author: twillia2
"""
import os

from importlib import resources

import windshed


contents = resources.files(windshed.__name__)
data = [file for file in contents.iterdir() if file.name == "data"][0]
paths = {}
for folder in data.iterdir():
    name = os.path.splitext(folder.name)[0].lower()
    paths[name] = folder

