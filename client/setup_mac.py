#!/usr/bin/env python3
# Bancal Samuel

"""
Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ["test_Qt.py"]
DATA_FILES = []
OPTIONS = {"iconfile":"mount_filers.png",}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app":OPTIONS},
    setup_requires=["py2app"],
)