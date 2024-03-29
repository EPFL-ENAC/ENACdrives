#!/usr/bin/env python3

# Bancal Samuel

# Offers CIFS Mount for :
# + Windows
# + Linux
# + Mac OSX

import re
from enacdrives.utility import CONST, Output

if CONST.OS_SYS == "Linux":
    from enacdrives.lin_stack import (
        cifs_uncache_is_mounted,
        cifs_is_mounted,
        cifs_mount,
        cifs_post_mount,
        cifs_umount,
        cifs_post_umount,
        open_file_manager,
    )
elif CONST.OS_SYS == "Windows":
    from enacdrives.win_stack import (
        cifs_uncache_is_mounted,
        cifs_is_mounted,
        cifs_mount,
        cifs_post_mount,
        cifs_umount,
        cifs_post_umount,
        open_file_manager,
    )
elif CONST.OS_SYS == "Darwin":
    from enacdrives.osx_stack import (
        cifs_uncache_is_mounted,
        cifs_is_mounted,
        cifs_mount,
        cifs_post_mount,
        cifs_umount,
        cifs_post_umount,
        open_file_manager,
    )


class CIFS_Mount:

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
    * bookmark = boolean
        default : False
    * Linux_CIFS_method = default method used for CIFS on Linux
        * mount.cifs : Linux's mount.cifs (requires sudo ability)
        * gvfs : Linux's gvfs-mount
    * Linux_mountcifs_filemode = filemode setting to use with mount.cifs method
    * Linux_mountcifs_dirmode  = dirmode setting to use with mount.cifs method
    * Linux_mountcifs_options = options to use with mount.cifs method
    * Linux_gvfs_symlink = boolean
        Enables the creation of a symbolic link to "local_path" after mount with gvfs method.
        default : False
    * Windows_letter = letter
        Drive letter to use for the mount (only on Windows)
    """

    def __init__(self, ui, cfg, mount_name, key_chain):
        def _cf(option, default=None):
            try:
                if option == "realm_domain":
                    realm = _cf("realm")
                    return cfg["realm"][realm]["domain"]
                elif option == "realm_username":
                    realm = _cf("realm")
                    return cfg["realm"][realm]["username"]
                elif option in (
                    "Linux_CIFS_method",
                    "Linux_mountcifs_filemode",
                    "Linux_mountcifs_dirmode",
                    "Linux_mountcifs_options",
                    "Linux_gvfs_symlink",
                    "realm",
                    "require_network",
                ):
                    if option in cfg["CIFS_mount"][mount_name]:
                        return cfg["CIFS_mount"][mount_name][option]
                    else:
                        return cfg["global"][option]
                else:
                    return cfg["CIFS_mount"][mount_name][option]
            except KeyError:
                return default

        self.settings = {
            "name": mount_name,
            "label": _cf("label"),
            "require_network": _cf("require_network"),
            "realm": _cf("realm"),
            "realm_domain": _cf("realm_domain"),
            "realm_username": _cf("realm_username"),
            "server_name": _cf("server_name"),
            "server_path": _cf("server_path"),
            "local_path": _cf("local_path"),
            "bookmark": _cf("bookmark", False),
            "Linux_CIFS_method": _cf("Linux_CIFS_method"),
            "Linux_mountcifs_filemode": _cf("Linux_mountcifs_filemode"),
            "Linux_mountcifs_dirmode": _cf("Linux_mountcifs_dirmode"),
            "Linux_mountcifs_options": _cf("Linux_mountcifs_options"),
            "Linux_gvfs_symlink": _cf("Linux_gvfs_symlink"),
            "Windows_letter": _cf(
                "Windows_letter", ""
            ),  # may be overwritten in "is_mounted"
        }

        self.settings["local_path"] = self.settings["local_path"].format(
            MNT_DIR=CONST.DEFAULT_MNT_DIR,
            HOME_DIR=CONST.HOME_DIR,
            DESKTOP_DIR=CONST.DESKTOP_DIR,
            LOCAL_USERNAME=CONST.LOCAL_USERNAME,
            LOCAL_GROUPNAME=CONST.LOCAL_GROUPNAME,
        )
        self.settings["server_share"], self.settings["server_subdir"] = re.match(
            r"([^/]+)/?(.*)$", self.settings["server_path"]
        ).groups()
        if CONST.OS_SYS == "Windows":
            self.settings["server_path"] = self.settings["server_path"].replace(
                "/", "\\"
            )
            self.settings["local_path"] = self.settings["local_path"].replace("/", "\\")
        self.settings["local_uid"] = CONST.LOCAL_UID
        self.settings["local_gid"] = CONST.LOCAL_GID
        self._cache = {
            "is_mounted": None,
        }
        self.ui = ui
        self.key_chain = key_chain

    def uncache_is_mounted(self):
        cifs_uncache_is_mounted(self)

    def is_mounted(self, cb=None):
        """
        evaluate if this CIFS_mount is mounted
        if cb is None make it synchronously
        else make it asynchronously
        """

        def _cb(is_m):
            # Output.debug("cifs_mount._cb")
            if is_m != self._cache["is_mounted"]:
                Output.normal(
                    "--> CIFS_mount {} : {} -> {}".format(
                        self.settings["name"], self._cache["is_mounted"], is_m
                    )
                )
                if is_m:
                    cifs_post_mount(self)
                else:
                    cifs_post_umount(self)
                self._cache["is_mounted"] = is_m
            if cb is not None:
                cb(is_m)

        # Output.debug("cifs_mount.is_mounted")
        if cb is None:
            is_m = cifs_is_mounted(self)
            _cb(is_m)
            return is_m
        else:
            cifs_is_mounted(self, _cb)

    def mount(self):
        # Output.br()
        return cifs_mount(self)

    def umount(self):
        # Output.br()
        return cifs_umount(self)

    def open_file_manager(self):
        # Output.br()
        return open_file_manager(self)
