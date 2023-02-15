#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Created on Sun Mar  8 16:58:59 2020.

@author: travis
"""
import os

from setuptools import setup


REPO_DIR = os.path.abspath(os.path.dirname(__file__))
VERSION_FILE = os.path.join(REPO_DIR, "windshed", "version.py")
DESCRIPTION = "Methods for calculating viewsheds for wind turbines."


with open(os.path.join(REPO_DIR, "README.md"), encoding="utf-8") as f:
    README = f.read()

# with open("requirements.txt") as f:
#     INSTALL_REQUIREMENTS = f.read().splitlines()


setup(
    name="windshed",
    version="0.0.1",
    description=DESCRIPTION,
    long_description=README,
    author="Travis Williams",
    author_email="Travis.Williams@nrel.gov",
    packages=["windshed"],
    zip_safe=False,
    keywords="windshed",
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.11",
        "Framework :: Dash",
    ],
    test_suite="tests",
    include_package_data=True,
    package_data={"data": ["*"]},
    # install_requires=INSTALL_REQUIREMENTS
)
