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
import urllib.error
import urllib.request

try:
    import grp
    import pwd
except ImportError:  # Windows
    pass

# ENACIT1LOGS
import enacit1logs
# /ENACIT1LOGS


FileNotFoundException = getattr(__builtins__, 'FileNotFoundError', IOError)


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

    VERSION = "0.1.17"  # Note : always copy this to PACKAGE_SIGNATURE_VERSION
    PACKAGE_SIGNATURE_VERSION = "ABCXYZ_0.1.17_ZYXCBA"  # This is used to auto-recognize software version inside a package
    PACKAGE_SIGNATURE_VERSION2 = "ABCDEF_" + VERSION + "_FEDCBA"  # This is used to auto-recognize software version inside a package
    FULL_VERSION = "2015-05-12 " + VERSION

    OS_SYS = platform.system()
    LOCAL_USERNAME = getpass.getuser()
    HOME_DIR = os.path.expanduser("~")
    
    CONFIG_URL = "http://enacdrives.epfl.ch/config/get?username={username}&version=" + VERSION
    VALIDATE_USERNAME_URL = "http://enacdrives.epfl.ch/config/validate_username?username={username}&version=" + VERSION

    # RESOURCES_DIR is used to get files like app's icon
    if getattr(sys, 'frozen', False):
        # The application is frozen (applies to Linux and Windows)
        RESOURCES_DIR = os.path.dirname(os.path.realpath(sys.executable))
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
        except FileNotFoundException:
            DESKTOP_DIR = HOME_DIR + "/Desktop"
        DEFAULT_MNT_DIR = DESKTOP_DIR  # Should be overwritten from conf file
        USER_CACHE_DIR = HOME_DIR + "/.enacdrives.cache"
        USER_CONF_FILE = HOME_DIR + "/.enacdrives.conf"
        SYSTEM_CONF_FILE = "/etc/enacdrives.conf"
        LATEST_RELEASE_NUMBER_URL = "http://enacdrives.epfl.ch/releases/api/latest_release_number?os=Linux"
        DOWNLOAD_NEW_RELEASE_URL = "http://enacdrives.epfl.ch/"
    elif OS_SYS == "Darwin":
        OS_DISTRIB = "Apple"
        OS_VERSION = platform.mac_ver()[0]
        LOCAL_GROUPNAME = grp.getgrgid(pwd.getpwnam(LOCAL_USERNAME).pw_gid).gr_name
        LOCAL_UID = pwd.getpwnam(LOCAL_USERNAME)[2]
        LOCAL_GID = pwd.getpwnam(LOCAL_USERNAME)[3]
        DESKTOP_DIR = HOME_DIR + "/Desktop"
        DEFAULT_MNT_DIR = DESKTOP_DIR
        USER_CACHE_DIR = HOME_DIR + "/.enacdrives.cache"
        USER_CONF_FILE = HOME_DIR + "/.enacdrives.conf"
        SYSTEM_CONF_FILE = "/etc/enacdrives.conf"
        LATEST_RELEASE_NUMBER_URL = "http://enacdrives.epfl.ch/releases/api/latest_release_number?os=MacOSX"
        DOWNLOAD_NEW_RELEASE_URL = "http://enacdrives.epfl.ch/"
        if getattr(sys, 'frozen', False):
            RESOURCES_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.executable), os.pardir, "Resources"))
    elif OS_SYS == "Windows":
        OS_DISTRIB = "Microsoft"
        OS_VERSION = platform.win32_ver()[0]
        LOCAL_GROUPNAME = "Undefined"
        LOCAL_UID = -1
        LOCAL_GID = -1
        DESKTOP_DIR = HOME_DIR + "/Desktop"  # TO DO
        DEFAULT_MNT_DIR = DESKTOP_DIR  # TO DO
        USER_CACHE_DIR = RESOURCES_DIR + "\\enacdrives.cache"
        USER_CONF_FILE = RESOURCES_DIR + "\\enacdrives.conf"
        SYSTEM_CONF_FILE = "C:\\enacdrives.conf"
        LATEST_RELEASE_NUMBER_URL = "http://enacdrives.epfl.ch/releases/api/latest_release_number?os=Windows"
        DOWNLOAD_NEW_RELEASE_URL = "http://enacdrives.epfl.ch/"
    else:
        OS_VERSION = "Error: OS not supported."
    
    # use full ABSOLUTE path to the image, not relative
    ENACDRIVES_PNG = RESOURCES_DIR + "/enacdrives.png"
    MOUNTED_PNG = RESOURCES_DIR + "/mounted.png"
    UMOUNTED_PNG = RESOURCES_DIR + "/umounted.png"
    BOOKMARK_ON_PNG = RESOURCES_DIR + "/bookmark_on.png"
    BOOKMARK_OFF_PNG = RESOURCES_DIR + "/bookmark_off.png"


class Output():
    def __init__(self, dest=None):
        if dest is not None:
            self.output = dest
        else:
            self.output = sys.stdout

    def __enter__(self):
        Output.set_instance(self)
        if (CONST.OS_SYS == "Windows" and
           getattr(sys, 'frozen', False)):
            # Windows frozen application
            self.output = open(CONST.RESOURCES_DIR + "/execution_output.txt", "w")

    def __exit__(self, typ, value, traceback):
        Output.del_instance()
        if (CONST.OS_SYS == "Windows" and
           getattr(sys, 'frozen', False)):
            # Windows frozen application
            self.output.close()

    def do_write(self, msg):
        self.output.write(msg)

    @classmethod
    def set_instance(cls, instance):
        cls.instance = instance

    @classmethod
    def del_instance(cls):
        cls.instance = None
    
    @classmethod
    def write(cls, msg="", end="\n"):
        cls.instance.do_write(msg + end)


# ENACIT1LOGS
# used to repatriate test cases
# + NET USE stdout and stderr (might encounter different one from different OS/Languages :( )
def debug_send(msg, additional_tags=None):
    if additional_tags is None:
        additional_tags = []
    Output.write("GONNA SEND MSG TO ENACIT1LOGS : " + msg)
    enacit1logs.send(
        message=str(msg),
        tags=["ENACdrives_debug", "notify_bancal", CONST.VERSION] + additional_tags
    )

# /ENACIT1LOGS


class Key_Chain():
    """
        Holds the passwords entered diring the execution time.
    """

    def __init__(self, ui):
        self.ui = ui
        self.keys = {}

    def get_password(self, realm, password_mistyped=False):
        if realm in self.keys:
            for _ in range(3):
                if self.keys[realm]["ack"]:
                    Output.write("Getting password for {0}".format(realm))
                    return self.keys[realm]["pw"]
                time.sleep(0.1)
        if password_mistyped:
            Output.write("Asking password for {0} (previously mistyped)".format(realm))
        else:
            Output.write("Asking password for {0}".format(realm))
        password = self.ui.get_password(realm, password_mistyped)
        self.keys[realm] = {
            "ack": False,
            "pw": password,
        }
        return self.keys[realm]["pw"]

    def ack_password(self, realm):
        if realm in self.keys:
            self.keys[realm]["ack"] = True
    
    def invalidate_if_no_ack_password(self, realm):
        if realm in self.keys:
            if not self.keys[realm]["ack"]:
                del(self.keys[realm])
                gc.collect()

    def invalidate_password(self, realm):
        if realm in self.keys:
            del(self.keys[realm])
            gc.collect()

    def wipe_passwords(self):
        del(self.keys)
        self.keys = {}
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
    def subprocess_check_output(cls, cmd, env=None):
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
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=stdout_file,
                stderr=subprocess.PIPE,
                shell=False,
                env=env,
                startupinfo=startupinfo
            )
            return_code = process.wait()
            if return_code != 0:
                raise Exception("Error while running %s. Returncode : %d" % (cmd, return_code))
            stdout_file.flush()
            stdout_file.seek(0)
            output = stdout_file.read()
            stdout_file.close()
        else:
            output = subprocess.check_output(
                cmd,
                env=env
            ).decode()

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


def validate_username(username):
    validate_url = CONST.VALIDATE_USERNAME_URL.format(username=username)
    try:
        with urllib.request.urlopen(validate_url) as response:
            lines = [l.decode() for l in response.readlines()]
        return lines[0]
    except urllib.error.URLError:
        Output.write("Warning, could not load validate url. ({0})".format(validate_url))
        return "Error, could not contact config server."
        

def validate_release_number():
    with urllib.request.urlopen(CONST.LATEST_RELEASE_NUMBER_URL) as response:
        latest_release = response.readline().decode()
        return latest_release == CONST.VERSION
