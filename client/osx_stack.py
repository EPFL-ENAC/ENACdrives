#!/usr/bin/env python3

# Bancal Samuel

# Offers Mac OSX stack for :
# + CIFS (is_mount, mount, umount)
# + open_file_manager

import os
import subprocess
from utility import CONST, Output


def cifs_is_mounted(mount):
    return os.path.ismount(mount.settings["local_path"])


def cifs_mount(mount):
    pass
    

def cifs_umount(mount):
    pass


def open_file_manager(mount):
    path = mount.settings["local_path"]

    cmd = [s.format(path=path) for s in CONST.CMD_OPEN.split(" ")]
    Output.write("cmd : %s" % cmd)
    subprocess.call(cmd)
