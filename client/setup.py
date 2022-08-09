#!/usr/bin/env python3
# Bancal Samuel

from enacdrives import utility
from distutils.core import setup

setup(
    name="ENACdrives",
    version=utility.CONST.VERSION,
    description="Access your Network Drives easily.",
    long_description="Access your Network Drives easily.",
    author="Samuel Bancal",
    author_email="Samuel.Bancal@epfl.ch",
    url="https://enacit.epfl.ch/enacdrives/",
    packages=["enacdrives"],
    scripts=[
        "bin/enacdrives",
    ],
    data_files=[
        ("/etc", ["etc/enacdrives.conf"]),
        ("share/applications", ["meta/enacdrives.desktop"]),
        (
            "share/pixmaps/enacdrives",
            [
                "share/pixmaps/enacdrives/bookmark_off.png",
                "share/pixmaps/enacdrives/bookmark_on.png",
                "share/pixmaps/enacdrives/critical_48.png",
                "share/pixmaps/enacdrives/enacdrives.icns",
                "share/pixmaps/enacdrives/enacdrives.ico",
                "share/pixmaps/enacdrives/enacdrives.png",
                "share/pixmaps/enacdrives/enacdrives.svg",
                "share/pixmaps/enacdrives/info_48.png",
                "share/pixmaps/enacdrives/mounted.png",
                "share/pixmaps/enacdrives/msg_48.png",
                "share/pixmaps/enacdrives/umounted.png",
                "share/pixmaps/enacdrives/warning_48.png",
                "share/pixmaps/enacdrives/warning.png",
            ],
        ),
        # ('share/man/man1', ['man/hello.1']),
    ],
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "License :: Free To Use But Restricted",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
    platforms="POSIX",
    license="MIT License",
)
