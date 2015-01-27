#!/usr/bin/env python3
# Bancal Samuel

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [])


if sys.platform == "win32":
    # target_dir = "build_windows"
    base = "Win32GUI" # Tells the build script to hide the console.
elif sys.platform == "linux":
    # target_dir = "build_linux"
    base = None
else:
    raise Exception("Not managed platform %s" % sys.platform)

setup(
    name='Linux PyQt test',
    version = '0.1',
    description = 'Test ability to compile PyQt app',
    options = dict(build_exe = buildOptions),
    executables = [Executable(
        script="test_Qt.py",
        # initScript = None,
        # targetDir = target_dir,
        # targetName = "test_Qt.exe",
        base=base,
        compress=True,
        # icon = "mount_filers.ico"
        # copyDependentFiles = False,
        # appendScriptToExe = False,
        # appendScriptToLibrary = False,
    )])

