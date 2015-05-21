#!/usr/bin/env python3
# Bancal Samuel

import sys
import utility
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(
    packages=[],
    excludes=[],
    include_files=["enacdrives.png", "mounted.png", "umounted.png", "bookmark_on.png", "bookmark_off.png", "warning.png"],
    include_msvcr=True  # skip error msvcr100.dll missing
)


if sys.platform == "win32":
    # target_dir = "build_windows"
    base = "Win32GUI"  # Tells the build script to hide the console.
elif sys.platform in ("linux", "linux2", "linux3"):
    # target_dir = "build_linux"
    base = None
else:
    raise Exception("Not managed platform %s" % sys.platform)

setup(
    name='ENACdrives',
    version=utility.CONST.VERSION,
    description='Access your Network Drives easily.',
    options=dict(build_exe=buildOptions),
    executables=[Executable(
        script="enacdrives.py",
        # initScript = None,
        # targetDir = target_dir,
        # targetName = "enacdrives.exe",
        base=base,
        compress=True,
        icon="enacdrives.ico"
        # copyDependentFiles = False,
        # appendScriptToExe = False,
        # appendScriptToLibrary = False,
    )])
