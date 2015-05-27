#!/usr/bin/env python3

# Bancal Samuel

# Offers Windows stack for :
# + cifs_is_mount
# + cifs_mount
# + cifs_post_mount
# + cifs_umount
# + cifs_post_umount
# + open_file_manager

import re
import win32api
import win32wnet
import win32netcon
import pywintypes
import subprocess
from utility import Output, CancelOperationException, debug_send, NonBlockingProcess


class WIN_CONST():
    CMD_OPEN = "explorer {path}"


def cifs_is_mounted(mount, cb):
    def _cb(success, output, exit_code):
        lines = output.split("\n")
        caption_index = lines[0].index("Caption")
        providername_index = lines[0].index("ProviderName")
        i_search = r"^\\{server_name}\{server_path}$".format(**mount.settings)
        i_search = i_search.replace("\\", "\\\\")
        # Output.write("i_search='{0}'".format(i_search))
        for l in lines[1:]:
            try:
                drive_letter = re.findall(r"^(\S+)", l[caption_index:])[0]
                try:
                    provider = re.findall(r"^(\S+)", l[providername_index:])[0]
                    if re.search(i_search, provider):
                        mount.settings["Windows_letter"] = drive_letter
                        cb(True)
                        return
                except IndexError:
                    provider = ""
                # Output.write("{0} : '{1}'".format(drive_letter, provider))
            except IndexError:
                pass
        cb(False)
        
    cmd = ["wmic", "logicaldisk"]  # List all Logical Disks
    NonBlockingProcess(cmd, _cb, cache=True)


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
        NonBlockingProcess.invalidate_cmd_cache(["wmic", "logicaldisk"])
        return True
    except pywintypes.error as e:
        if e.winerror == 86:  # (86, "WNetAddConnection2", "The specified network password is not correct.")
            pass
        elif e.winerror == 1326:  # (1326, "WNetAddConnection2", "Logon failure: unknown user name or bad password.")
            pass
        elif e.winerror == 1202:  # (1202, 'WNetAddConnection2', 'The local device name has a remembered connection to another network resource.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 85:  # (85, 'WNetAddConnection2', 'The local device name is already in use.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 67:  # (67, 'WNetAddConnection2', 'The network name cannot be found.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 5:  # (5, 'WNetAddConnection2', 'Access is denied.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 53:  # (53, 'WNetAddConnection2', 'The network path was not found.')
            mount.ui.notify_user(e.strerror)
            return False
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
                r"{0}\{1}".format(mount.settings["realm_domain"], mount.settings["realm_username"]),
                pw,
                0
            )
            mount.key_chain.ack_password(mount.settings["realm"])
            Output.write("succeeded")
            NonBlockingProcess.invalidate_cmd_cache(["wmic", "logicaldisk"])
            return True
        except pywintypes.error as e:
            if e.winerror == 86:  # (86, "WNetAddConnection2", "The specified network password is not correct.")
                mount.key_chain.invalidate_if_no_ack_password(mount.settings["realm"])
                wrong_password = True
            elif e.winerror == 1326:  # (1326, "WNetAddConnection2", "Logon failure: unknown user name or bad password.")
                mount.key_chain.invalidate_if_no_ack_password(mount.settings["realm"])
                wrong_password = True
            elif e.winerror == 1202:  # (1202, 'WNetAddConnection2', 'The local device name has a remembered connection to another network resource.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 85:  # (85, 'WNetAddConnection2', 'The local device name is already in use.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 67:  # (67, 'WNetAddConnection2', 'The network name cannot be found.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 5:  # (5, 'WNetAddConnection2', 'Access is denied.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 53:  # (53, 'WNetAddConnection2', 'The network path was not found.')
                mount.ui.notify_user(e.strerror)
                return False
            else:
                Output.write("failed : {0}".format(e))
                debug_send("mount with password:\n{0}".format(e))
        except CancelOperationException:
            Output.write("Operation cancelled.")
            return False
    return False


def cifs_post_mount(mount):
    """
    Performs tasks when mount is done.
    May happen some seconds after cifs_mount is completed (OS)
    """
    pass


def cifs_umount(mount):
    try:
        Output.write("Doing umount of {0}".format(mount.settings["Windows_letter"]))
        win32wnet.WNetCancelConnection2(mount.settings["Windows_letter"], 0, False)
        NonBlockingProcess.invalidate_cmd_cache(["wmic", "logicaldisk"])
    except pywintypes.error as e:
        if e.winerror == 2401:  # (2401, "WNetCancelConnection2", "There are open files on the connection.")
            mount.ui.notify_user(e.strerror)
        else:
            Output.write("failed : {0}".format(e))
            debug_send("umount:\n{0}".format(e))


def cifs_post_umount(mount):
    """
    Performs tasks when umount is done.
    May happen some seconds after cifs_umount is completed (OS)
    """
    pass


def open_file_manager(mount):
    def _cb(success, output, exit_code):
        pass

    path = mount.settings["Windows_letter"]
    cmd = [s.format(path=path) for s in WIN_CONST.CMD_OPEN.split(" ")]
    Output.write("cmd : %s" % cmd)
    NonBlockingProcess(
        cmd,
        _cb
    )


class WindowsLettersManager():
    """
    Manages booking of letters by
    + Windows (read its state)
    + All CIFS_mount entries (read their state + disable already booked letters)
    """
    def __init__(self):
        self.entries = []

    def add_mount_entry(self, entry):
        self.entries.append(entry)

    def clear_entries(self):
        self.entries = []

    def refresh_letters(self):
        # 1) read state
        letter_booking = {}

        # 1.1) Windows letters
        letters_string = win32api.GetLogicalDriveStrings()  # 'C:\\\x00D:\\\x00'
        for letter in letters_string.split('\x00'):
            if letter != "":
                letter_booking[letter[:2]] = None

        # 1.2) ENACdrives letters
        for e in self.entries:
            letter = e.settings.get("Windows_letter", "")
            if letter != "":
                letter_booking[letter] = e

        # 2) notify entries
        for e in self.entries:
            disabled_letters = []
            for letter in letter_booking:
                if letter_booking[letter] != e:
                    disabled_letters.append(letter)
            e.set_disabled_windows_letters(disabled_letters)
