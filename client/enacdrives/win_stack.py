#!/usr/bin/env python3

# Bancal Samuel

# Offers Windows stack for :
# + os_check
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
from enacdrives.utility import CONST, Output, CancelOperationException, debug_send, NonBlockingQtProcess


class WIN_CONST():
    CMD_OPEN = "explorer {path}"


def os_check(ui):
    """
    Check that OS has all pre-requisite functionalities
    """
    if (CONST.OS_DISTRIB == "Microsoft" and
            CONST.OS_SYS == "Windows" and
            CONST.OS_VERSION == "XP"):
        ui.notify_user("We're sorry but ENACdrives is not supported on Windows XP. See <a href='{}'>full documentation</a>.".format(CONST.DOC_URL))


def cifs_uncache_is_mounted(mount):
    NonBlockingQtProcess.invalidate_cmd_cache(["wmic", "logicaldisk"])


def cifs_is_mounted(mount, cb):
    def _cb(success, output, exit_code):
        lines = output.split("\n")
        items = re.findall(r"(\S+)", lines[0])
        caption = "Caption"
        after_caption = items[items.index("Caption")+1]
        providername = "ProviderName"
        after_providername = items[items.index("ProviderName")+1]
        caption_start = lines[0].index(caption)
        caption_end = lines[0].index(after_caption)
        providername_start = lines[0].index(providername)
        providername_end = lines[0].index(after_providername)

        i_search = r"^\\{server_name}\{server_path}".format(**mount.settings)
        i_search = i_search.replace("\\", "\\\\")
        i_search = i_search.replace("$", r"\$")
        i_search += "$"
        # Output.debug("i_search='{0}'".format(i_search))
        for l in lines[1:]:
            try:
                drive_letter = l[caption_start:caption_end].strip()
                provider = l[providername_start:providername_end].strip()
                # Output.debug("{} <- {}".format(drive_letter, provider))
                if re.search(i_search, provider, flags=re.IGNORECASE):
                    mount.settings["Windows_letter"] = drive_letter
                    # Output.debug("MATCH!")
                    cb(True)
                    return
            except IndexError:
                pass
        cb(False)

    cmd = ["wmic", "logicaldisk"]  # List all Logical Disks
    NonBlockingQtProcess(cmd, _cb, cache=True)


def cifs_mount(mount):
    remote = r"\\{server_name}\{server_path}".format(**mount.settings)
    local = mount.settings["Windows_letter"]
    Output.normal("remote={}\nlocal={}".format(remote, local))

    # 1st attempt without password
    try:
        Output.verbose("1st attempt without password")
        win32wnet.WNetAddConnection2(
            win32netcon.RESOURCETYPE_DISK,
            local,
            remote,
        )
        Output.verbose("succeeded")
        cifs_uncache_is_mounted(mount)
        return True
    except pywintypes.error as e:
        if e.winerror == 5:  # (5, 'WNetAddConnection2', 'Access is denied.')
            pass
        elif e.winerror == 86:  # (86, "WNetAddConnection2", "The specified network password is not correct.")
            pass
        elif e.winerror == 1326:  # (1326, "WNetAddConnection2", "Logon failure: unknown user name or bad password.")
            pass
        elif e.winerror == 31:  # (31, 'WNetAddConnection2', 'A device attached to the system is not functioning.')
            pass
        elif e.winerror == 53:  # (53, 'WNetAddConnection2', 'The network path was not found.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 55:  # (55, 'WNetAddConnection2', 'The specified network resource or device is no longer available.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 64:  # (64, 'WNetAddConnection2', 'Le nom réseau spécifié n’est plus disponible.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 67:  # (67, 'WNetAddConnection2', 'The network name cannot be found.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 71:  # (71, 'WNetAddConnection2', 'No more connections can be made to this remote computer at this time because there are already as many connections as the computer can accept.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 85:  # (85, 'WNetAddConnection2', 'The local device name is already in use.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 121:  # (121, 'WNetAddConnection2', 'The semaphore timeout period has expired.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 1202:  # (1202, 'WNetAddConnection2', 'The local device name has a remembered connection to another network resource.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 1208:  # (1208, 'WNetAddConnection2', 'An extended error has occurred.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 1219:  # (1219, 'WNetAddConnection2', 'Multiple connections to a server or shared resource by the same user, using more than one user name, are not allowed. Disconnect all previous connections to the server or shared resource and try again.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 1222:  # (1222, 'WNetAddConnection2', 'The network is not present or not started.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 1265:  # (1265, 'WNetAddConnection2', 'The system detected a possible attempt to compromise security. Please ensure that you can contact the server that authenticated you.')
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 1272:  # (1272, 'WNetAddConnection2', "You can't access this shared folder because your organization's security policies block unauthenticated guest access. These policies help protect your PC from unsafe or malicious devices on the network.")
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 1311:  # (1311, 'WNetAddConnection2', 'There are currently no logon servers available to service the logon request.')
                                  # (1311, 'WNetAddConnection2', "We can't sign you in with this credential because your domain isn't available. Make sure your device is connected to your organization's network and try again. If you previously signed in on this device with another credential, you can sign in with that credential.")
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 1331:  # (1331, 'WNetAddConnection2', "This user can't sign in because this account is currently disabled.")
            mount.ui.notify_user(e.strerror)
            return False
        elif e.winerror == 1907:  # (1907, 'WNetAddConnection2', "The user's password must be changed before signing in.")
            pass
        else:
            Output.error("failed : {0}".format(e))
            debug_send("mount without password:\n{0}".format(e))

    # 2nd attempt with password
    wrong_password = False
    for _ in range(3):
        try:
            pw = mount.key_chain.get_password(mount.settings["realm"], wrong_password)
            wrong_password = False
            Output.verbose("New attempt with password")
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
            Output.verbose("succeeded")
            cifs_uncache_is_mounted(mount)
            return True
        except pywintypes.error as e:
            if e.winerror == 86:  # (86, "WNetAddConnection2", "The specified network password is not correct.")
                mount.key_chain.invalidate_if_no_ack_password(mount.settings["realm"])
                wrong_password = True
            elif e.winerror == 1326:  # (1326, "WNetAddConnection2", "Logon failure: unknown user name or bad password.")
                mount.key_chain.invalidate_if_no_ack_password(mount.settings["realm"])
                wrong_password = True
            elif e.winerror == 5:  # (5, 'WNetAddConnection2', 'Access is denied.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 31:  # (31, 'WNetAddConnection2', 'A device attached to the system is not functioning.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 53:  # (53, 'WNetAddConnection2', 'The network path was not found.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 55:  # (55, 'WNetAddConnection2', 'The specified network resource or device is no longer available.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 64:  # (64, 'WNetAddConnection2', 'Le nom réseau spécifié n’est plus disponible.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 67:  # (67, 'WNetAddConnection2', 'The network name cannot be found.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 71:  # (71, 'WNetAddConnection2', 'No more connections can be made to this remote computer at this time because there are already as many connections as the computer can accept.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 85:  # (85, 'WNetAddConnection2', 'The local device name is already in use.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 121:  # (121, 'WNetAddConnection2', 'The semaphore timeout period has expired.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 1202:  # (1202, 'WNetAddConnection2', 'The local device name has a remembered connection to another network resource.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 1208:  # (1208, 'WNetAddConnection2', 'An extended error has occurred.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 1219:  # (1219, 'WNetAddConnection2', 'Multiple connections to a server or shared resource by the same user, using more than one user name, are not allowed. Disconnect all previous connections to the server or shared resource and try again.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 1222:  # (1222, 'WNetAddConnection2', 'The network is not present or not started.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 1265:  # (1265, 'WNetAddConnection2', 'The system detected a possible attempt to compromise security. Please ensure that you can contact the server that authenticated you.')
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 1272:  # (1272, 'WNetAddConnection2', "You can't access this shared folder because your organization's security policies block unauthenticated guest access. These policies help protect your PC from unsafe or malicious devices on the network.")
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 1311:  # (1311, 'WNetAddConnection2', 'There are currently no logon servers available to service the logon request.')
                                      # (1311, 'WNetAddConnection2', "We can't sign you in with this credential because your domain isn't available. Make sure your device is connected to your organization's network and try again. If you previously signed in on this device with another credential, you can sign in with that credential.")
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 1331:  # (1331, 'WNetAddConnection2', "This user can't sign in because this account is currently disabled.")
                mount.ui.notify_user(e.strerror)
                return False
            elif e.winerror == 1907:  # (1907, 'WNetAddConnection2', "The user's password must be changed before signing in.")
                mount.ui.notify_user(e.strerror)
                return False
            else:
                Output.error("failed : {0}".format(e))
                debug_send("mount with password:\n{0}".format(e))
                mount.ui.notify_user(e.strerror)
        except CancelOperationException:
            Output.verbose("Operation cancelled.")
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
        Output.verbose("Doing umount of {0}".format(mount.settings["Windows_letter"]))
        win32wnet.WNetCancelConnection2(mount.settings["Windows_letter"], 0, False)
        cifs_uncache_is_mounted(mount)
    except pywintypes.error as e:
        if e.winerror == 2401:  # (2401, "WNetCancelConnection2", "There are open files on the connection.")
            mount.ui.notify_user(e.strerror)
        elif e.winerror == 2250:  # (2250, 'WNetCancelConnection2', 'This network connection does not exist.')
            mount.ui.notify_user(e.strerror)
        else:
            Output.error("failed : {0}".format(e))
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
    Output.verbose("cmd: " + " ".join(cmd))
    NonBlockingQtProcess(
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
