#!/usr/bin/env python3

# Bancal Samuel

# Offers CIFS Mount for :
# + Windows
# + Linux
# + Mac OSX

import re
from utility import CONST, Output

if CONST.OS_SYS == "Linux":
    from lin_stack import cifs_is_mounted, cifs_mount, cifs_umount, open_file_manager
elif CONST.OS_SYS == "Windows":
    from win_stack import cifs_is_mounted, cifs_mount, cifs_umount, open_file_manager
elif CONST.OS_SYS == "Darwin":
    from osx_stack import cifs_is_mounted, cifs_mount, cifs_umount, open_file_manager
    

class CIFS_Mount():

    """
        * name = mount's name
        * label = Label displayed
        * realm = CIFS_realm used
        * server_name = server name
        * server_path = path to be mounted (uncludes share and may include subdir)
        * local_path = path where to mount. Substitutions available :
            * {MNT_DIR}
            * {HOME_DIR}
            * {DESKTOP_DIR}
            * {LOCAL_USERNAME}
            * {LOCAL_GROUPNAME}
        * stared = boolean
            default : False
        * Linux_CIFS_method = default method used for CIFS on Linux
            * mount.cifs : Linux's mount.cifs (requires sudo ability)
            * gvfs : Linux's gvfs-mount
        * Linux_mountcifs_filemode = filemode setting to use with mount.cifs method
        * Linux_mountcifs_dirmode  = dirmode setting to use with mount.cifs method
        * Linux_mountcifs_options = options to use with mount.cifs method
        * Linux_gvfs_symlink = boolean
            Enables the creation of a symbolic link to "local_path" after mount with gvfs method.
            default : True
        * Windows_letter = letter
            Drive letter to use for the mount (only on Windows)
    """

    def __init__(self, ui, key_chain):
        self.settings = {
            "name": "private",
            "label": "bancal@files9 (individuel)",
            "realm": "EPFL",
            "server_name": "files9.epfl.ch",
            "server_path": "data/bancal",
            "local_path": "{MNT_DIR}/bancal_on_files9",
            "stared": False,
            "Linux_CIFS_method": "gvfs",  # "mount.cifs",
            "Linux_mountcifs_filemode": "0770",
            "Linux_mountcifs_dirmode": "0770",
            "Linux_mountcifs_options": "rw,nobrl,noserverino,iocharset=utf8,sec=ntlm",
            "Linux_gvfs_symlink": True,
            "Windows_letter": "Z:",  # may be overwritten in "is_mounted"
        }
        self.settings["local_path"] = self.settings["local_path"].format(
            MNT_DIR=CONST.DEFAULT_MNT_DIR,
            HOME_DIR=CONST.HOME_DIR,
            DESKTOP_DIR=CONST.DESKTOP_DIR,
            LOCAL_USERNAME=CONST.LOCAL_USERNAME,
            LOCAL_GROUPNAME=CONST.LOCAL_GROUPNAME,
        )
        self.settings["server_share"], self.settings["server_subdir"] = re.match(r"([^/]+)/?(.*)$", self.settings["server_path"]).groups()
        if CONST.OS_SYS == "Windows":
            self.settings["server_path"] = self.settings["server_path"].replace("/", "\\")
            self.settings["local_path"] = self.settings["local_path"].replace("/", "\\")
        self.settings["realm_domain"] = "INTRANET"
        self.settings["realm_username"] = "bancal"
        self.settings["local_uid"] = CONST.LOCAL_UID
        self.settings["local_gid"] = CONST.LOCAL_GID
        self.ui = ui
        self.key_chain = key_chain

    def is_mounted(self):
        return cifs_is_mounted(self)

    def mount(self):
        Output.write()
        return cifs_mount(self)

    def umount(self):
        Output.write()
        return cifs_umount(self)

    def open_file_manager(self):
        Output.write()
        return open_file_manager(self)
