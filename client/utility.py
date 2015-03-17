#!/usr/bin/env python3

# Bancal Samuel

# Offers Windows stack for :
# + CIFS (is_mount, mount, umount)

import os
import gc
import sys
import time
import getpass
import tempfile
import datetime
import platform
import subprocess

try:
    import grp
    import pwd
except ImportError:  # Windows
    pass

# ENACIT1LOGS
import enacit1logs
# /ENACIT1LOGS


class CancelOperationException(Exception):
    """
        Raised when user want to abort an operation
    """
    pass


def which(program):
    """
        from http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/377028#377028
    """
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


class CONST():

    VERSION = "2015-03-06"

    OS_SYS = platform.system()
    LOCAL_USERNAME = getpass.getuser()
    HOME_DIR = os.path.expanduser("~")

    # RESOURCES_DIR is used to get files like app's icon
    if getattr(sys, 'frozen', False):
        # The application is frozen
        RESOURCES_DIR = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        RESOURCES_DIR = os.path.dirname(__file__)

    if OS_SYS == "Linux":
        OS_DISTRIB, OS_VERSION = platform.linux_distribution()[:2]
        LOCAL_GROUPNAME = grp.getgrgid(pwd.getpwnam(LOCAL_USERNAME).pw_gid).gr_name
        LOCAL_UID = pwd.getpwnam(LOCAL_USERNAME)[2]
        LOCAL_GID = pwd.getpwnam(LOCAL_USERNAME)[3]
        try:
            DESKTOP_DIR = subprocess.check_output(["xdg-user-dir", "DESKTOP"]).decode().strip()
        except FileNotFoundError:
            DESKTOP_DIR = HOME_DIR + "/Desktop"
        DEFAULT_MNT_DIR = DESKTOP_DIR  # Should be overwritten from conf file
        CMD_OPEN = which("xdg-open") + " {path}"
        CMD_GVFS_MOUNT = which("gvfs-mount")
        CMD_MOUNT_CIFS = which("mount.cifs")
        CMD_UMOUNT = which("umount")
        if OS_VERSION in ("10.04", "10.10", "11.04", "11.10", "12.04"):
            GVFS_GENERATION = 1
            GVFS_DIR = os.path.join(HOME_DIR, ".gvfs")
        elif OS_VERSION in ("12.10", "13.04"):
            GVFS_GENERATION = 2
            GVFS_DIR = "/run/user/{0}/gvfs".format(LOCAL_USERNAME)
        else:
            GVFS_GENERATION = 3
            GVFS_DIR = "/run/user/{0}/gvfs".format(LOCAL_UID)
    elif OS_SYS == "Darwin":
        OS_DISTRIB = "Apple"
        OS_VERSION = platform.mac_ver()[0]
        LOCAL_GROUPNAME = grp.getgrgid(pwd.getpwnam(LOCAL_USERNAME).pw_gid).gr_name
        LOCAL_UID = pwd.getpwnam(LOCAL_USERNAME)[2]
        LOCAL_GID = pwd.getpwnam(LOCAL_USERNAME)[3]
        DESKTOP_DIR = HOME_DIR + "/Desktop"
        DEFAULT_MNT_DIR = DESKTOP_DIR
        CMD_OPEN = which("open") + " -a Finder {path}"
    elif OS_SYS == "Windows":
        OS_DISTRIB = "Microsoft"
        OS_VERSION = platform.win32_ver()[0]
        LOCAL_GROUPNAME = "Undefined"
        LOCAL_UID = -1
        LOCAL_GID = -1
        DESKTOP_DIR = HOME_DIR + "/Desktop"  # TO DO
        DEFAULT_MNT_DIR = DESKTOP_DIR  # TO DO
        CMD_OPEN = "explorer {path}"
    else:
        OS_VERSION = "Error: OS not supported."


class Output():
    def __init__(self):
        if (CONST.OS_SYS == "Windows" and
           getattr(sys, 'frozen', False)):
            # Windows frozen application
            self.output = open(CONST.RESOURCES_DIR + "/execution_output.txt", "a")
        else:
            self.output = sys.stdout
    
    def __del__(self):
        if (CONST.OS_SYS == "Windows" and
           getattr(sys, 'frozen', False)):
            # Windows frozen application
            try:
                self.output.close()
            except AttributeError:
                pass

    def do_write(self, msg):
        self.output.write(msg)

    @classmethod
    def write(cls, msg="", end="\n"):
        """
            sends output to file if this is compiled on Windows
            sends output to stdou otherwise
        """
        try:
            cls.dest
        except AttributeError:
            cls.dest = Output()
        cls.dest.do_write(msg + end)


# ENACIT1LOGS
# used to repatriate test cases
# + NET USE stdout and stderr (might encounter different one from different OS/Languages :( )
def debug_send(msg, additional_tags=None):
    if additional_tags is None:
        additional_tags = []
    Output.write("GONNA SEND MSG TO ENACIT1LOGS : " + msg)
    enacit1logs.send(
        message=str(msg),
        tags=["dev_mountfilers2015", "notify_bancal", CONST.VERSION] + additional_tags
    )

# /ENACIT1LOGS


class Key_Chain():
    """
        Holds the passwords entered diring the execution time.
    """

    def __init__(self, ui):
        self.ui = ui
        self.keys = {}

    def get_password(self, realm):
        Output.write("Asking password for {0}".format(realm))
        if realm in self.keys:
            for _ in range(3):
                if self.keys[realm]["ack"]:
                    return self.keys[realm]["pw"]
                time.sleep(1)
        password = self.ui.get_password(realm)
        self.keys[realm] = {
            "ack": False,
            "pw": password,
        }
        return self.keys[realm]["pw"]

    def ack_password(self, realm):
        if realm in self.keys:
            self.keys[realm]["ack"] = True

    def invalidate_password(self, realm):
        del(self.keys[realm])
        gc.collect()

    def wipe_passwords(self):
        for realm in self.keys:
            del(self.keys[realm])
        gc.collect()


class Live_Cache():

    """
        Used to cache low latency commands (mostly for "gvfs-mount -l" which takes 0.5 sec!)

        cls.cache{
            "command line being cached":{
                "expire_dt":request_datetime_now + deltatime,
                "value":"output",
            }
        }
    """

    CACHE_DURATION = datetime.timedelta(seconds=1)

    @classmethod
    def subprocess_check_output(cls, cmd):
        str_cmd = " ".join(cmd)
        try:
            cached_entry = cls.cache[str_cmd]
            if cached_entry["expire_dt"] > datetime.datetime.now():
                return cached_entry["value"]
        except AttributeError:
            cls.cache = {}
        except KeyError:
            pass
        # No valid cache entry found, creating one.

        if CONST.OS_SYS == "Windows":
            # STARTUPINFO : Prevents cmd to be opened when subprocess.Popen is called.
            # http://stackoverflow.com/a/24171096/446302
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            stdout_file = tempfile.NamedTemporaryFile(mode="r+", delete=False, encoding="UTF-16")
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=stdout_file, stderr=subprocess.PIPE, shell=False, startupinfo=startupinfo)
            return_code = process.wait()
            if return_code != 0:
                raise Exception("Error while running %s. Returncode : %d" % (cmd, return_code))
            stdout_file.flush()
            stdout_file.seek(0)
            output = stdout_file.read()
            stdout_file.close()
        else:
            output = subprocess.check_output(cmd).decode()

        cls.cache[str_cmd] = {
            "expire_dt": datetime.datetime.now() + Live_Cache.CACHE_DURATION,
            "value": output,
        }
        return output

    @classmethod
    def invalidate_cmd_cache(cls, cmd):
        str_cmd = " ".join(cmd)
        try:
            cls.cache.pop(str_cmd)
        except (AttributeError, KeyError):
            pass
