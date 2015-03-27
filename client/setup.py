#!/usr/bin/env python3
# Bancal Samuel

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(
    packages=[],
    excludes=[],
    include_files=["mount_filers.png"]
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
    name='MultiOS PyQt mount_filers',
    version='0.1',
    description='Test ability to compile PyQt app on 3 OS',
    options=dict(build_exe=buildOptions),
    executables=[Executable(
        script="mount_filers.py",
        # initScript = None,
        # targetDir = target_dir,
        # targetName = "mount_filers.exe",
        base=base,
        compress=True,
        icon="mount_filers.ico"
        # copyDependentFiles = False,
        # appendScriptToExe = False,
        # appendScriptToLibrary = False,
    )])
