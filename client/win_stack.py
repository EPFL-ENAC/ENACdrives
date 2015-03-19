#!/usr/bin/env python3

# Bancal Samuel

# Offers Windows stack for :
# + cifs_is_mount
# + cifs_mount
# + cifs_umount
# + open_file_manager

import win32net
import win32wnet
import win32netcon
import pywintypes
import subprocess
from utility import CONST, Output, CancelOperationException, debug_send


def cifs_is_mounted(mount):
    current_mounts = win32net.NetUseEnum(None, 0, 0)[0]
    # ([{'local': 'Z:', 'remote': '\\\\files9.epfl.ch\\data\\bancal'}], 1, 0)
    for m in current_mounts:
        Output.write("{0} : {1}".format(m["local"], m["remote"]))
        if m["remote"] == r"\\{server_name}\{server_path}".format(**mount.settings):
            Output.write("MATCH!")
            mount.settings["Windows_letter"] = m["local"]
            return True
    Output.write("NO-MATCH.")
    return False
    

def cifs_mount(mount):
    remote = r"\\{server_name}\{server_path}".format(**mount.settings)
    local = mount.settings["Windows_letter"]
    Output.write("remote={0}\nlocal={1}".format(remote, local))
    
    # 1st attempt without password
    try:
        Output.write("1st attempt without password")
        win32wnet.WNetAddConnection2(
            win32netcon.RESOURCETYPE_DISK,
            local,
            remote,
        )
        Output.write("succeeded")
        return True
    except pywintypes.error as e:
        if e.winerror == 86:  # (86, 'WNetAddConnection2', 'The specified network password is not correct.')
            pass
        elif e.winerror == 1326:  # (1326, 'WNetAddConnection2', 'Logon failure: unknown user name or bad password.')
            pass
        else:
            Output.write("failed : {0}".format(e))
            debug_send("mount without password:\n{0}".format(e))
    
    # 2nd attempt with password
    wrong_password = False
    for _ in range(3):
        try:
            pw = mount.key_chain.get_password(mount.settings["realm"], wrong_password)
            wrong_password = False
            Output.write("New attempt with password")
            win32wnet.WNetAddConnection2(
                win32netcon.RESOURCETYPE_DISK,
                local,
                remote,
                None,
                r'{0}\{1}'.format(mount.settings["realm_domain"], mount.settings["realm_username"]),
                pw,
                0
            )
            mount.key_chain.ack_password(mount.settings["realm"])
            Output.write("succeeded")
            return True
        except pywintypes.error as e:
            if e.winerror == 86:  # (86, 'WNetAddConnection2', 'The specified network password is not correct.')
                mount.key_chain.invalidate_if_no_ack_password(mount.settings["realm"])
                wrong_password = True
            elif e.winerror == 1326:  # (1326, 'WNetAddConnection2', 'Logon failure: unknown user name or bad password.')
                mount.key_chain.invalidate_if_no_ack_password(mount.settings["realm"])
                wrong_password = True
            else:
                Output.write("failed : {0}".format(e))
                debug_send("mount with password:\n{0}".format(e))
        except CancelOperationException:
            Output.write("Operation cancelled.")
            return False
    return False


def cifs_umount(mount):
    try:
        Output.write("Doing umount of {0}".format(mount.settings["Windows_letter"]))
        win32wnet.WNetCancelConnection2(mount.settings["Windows_letter"], 0, False)
    except pywintypes.error as e:
        if e.winerror == 2401:  # (2401, 'WNetCancelConnection2', 'There are open files on the connection.')
            mount.ui.notify_user(e.strerror)
        else:
            Output.write("failed : {0}".format(e))
            debug_send("umount:\n{0}".format(e))


def open_file_manager(mount):
    path = mount.settings["Windows_letter"]
    cmd = [s.format(path=path) for s in CONST.CMD_OPEN.split(" ")]
    Output.write("cmd : %s" % cmd)
    subprocess.call(cmd)
