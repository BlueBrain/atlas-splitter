#!/usr/bin/env python

import importlib

from setuptools import find_packages, setup

VERSION = importlib.import_module("atlas_splitter.version").__version__

setup(
    name="atlas-splitter",
    author="BlueBrain NSE",
    author_email="bbp-ou-nse@groupes.epfl.ch",
    version=VERSION,
    description="CLI to split atlas regions and modify annotations accordingly",
    url="https://bbpgitlab.epfl.ch/nse/atlas-splitter",
    download_url="git@bbpgitlab.epfl.ch:nse/atlas-splitter.git",
    license="BBP-internal-confidential",
    python_requires=">=3.6.0",
    install_requires=[
        "atlas-commons>=0.1.3.dev0",
        "click>=7.0",
        "cgal-pybind>=0.1.3",
        "numpy>=1.15.0",
        "voxcell>=3.0.0",
    ],
    extras_require={
        "tests": [
            "pytest>=4.4.0",
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["atlas-splitter=atlas_splitter.app.cli:cli"]},
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
)
