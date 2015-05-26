#!/usr/bin/env python3

# Bancal Samuel

# Offers general facility utilities

import os
import gc
import sys
import time
import socket
import getpass
import tempfile
import datetime
import platform
import subprocess
import urllib.error
import urllib.request
from PyQt4 import QtCore

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

    VERSION_DATE = "2015-05-26"
    VERSION = "0.2.6"
    FULL_VERSION = VERSION_DATE + " " + VERSION

    OS_SYS = platform.system()
    LOCAL_USERNAME = getpass.getuser()
    HOME_DIR = os.path.expanduser("~")

    URL_TIMEOUT = 2
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
        DOWNLOAD_NEW_RELEASE_URL = "http://enacsoft.epfl.ch/enacdrives/"
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
        DOWNLOAD_NEW_RELEASE_URL = "http://enacsoft.epfl.ch/enacdrives/"
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
        try:
            LOCAL_APPDATA = os.environ["LOCALAPPDATA"]
            USER_CACHE_DIR = LOCAL_APPDATA + "\\ENACdrives\\enacdrives.cache"
            USER_CONF_FILE = LOCAL_APPDATA + "\\ENACdrives\\enacdrives.conf"
        except KeyError:
            USER_CACHE_DIR = RESOURCES_DIR + "\\enacdrives.cache"
            USER_CONF_FILE = RESOURCES_DIR + "\\enacdrives.conf"
        SYSTEM_CONF_FILE = "C:\\enacdrives.conf"
        LATEST_RELEASE_NUMBER_URL = "http://enacdrives.epfl.ch/releases/api/latest_release_number?os=Windows"
        DOWNLOAD_NEW_RELEASE_URL = "http://enacsoft.epfl.ch/enacdrives/"
    else:
        OS_VERSION = "Error: OS not supported."

    # use full ABSOLUTE path to the image, not relative
    ENACDRIVES_PNG = RESOURCES_DIR + "/enacdrives.png"
    MOUNTED_PNG = RESOURCES_DIR + "/mounted.png"
    UMOUNTED_PNG = RESOURCES_DIR + "/umounted.png"
    BOOKMARK_ON_PNG = RESOURCES_DIR + "/bookmark_on.png"
    BOOKMARK_OFF_PNG = RESOURCES_DIR + "/bookmark_off.png"
    WARNING_PNG = RESOURCES_DIR + "/warning.png"


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
    def subprocess_check_output(cls, cmd, cb, env=None):
        def _cb(name, success, output, exit_code):
            # Output.write("utility._cb")
            if not success:
                Output.write("Error while running {}.\nOutput : {}".format(cmd, output))
            cls.cache[str_cmd]["expire_dt"] = datetime.datetime.now() + Live_Cache.CACHE_DURATION
            cls.cache[str_cmd]["value"] = output
            cls.cache[str_cmd]["exit_code"] = exit_code
            # Output.write("C cls.cache: {}".format(cls.cache))
            all_cb = cls.cache[str_cmd]["cb"]
            del(cls.cache[str_cmd]["proc"])
            del(cls.cache[str_cmd]["cb"])
            for cb_i in all_cb:
                cb_i(output, exit_code)

        # Output.write("utility.subprocess_check_output")
        str_cmd = " ".join(cmd)
        try:
            cached_entry = cls.cache[str_cmd]
            if cached_entry["expire_dt"] > datetime.datetime.now():
                cb(cached_entry["value"], cached_entry["exit_code"])
                return
        except AttributeError:
            cls.cache = {}
        except KeyError:
            pass
        # No valid cache entry found, creating one.

        cls.cache.setdefault(str_cmd, {})
        try:
            proc = NonBlockingProcess(".".join(cmd), _cb)
            cls.cache[str_cmd]["proc"] = proc
            cls.cache[str_cmd]["cb"] = [cb, ]
            # Output.write("A cls.cache: {}".format(cls.cache))
        except NonBlockingProcessException:
            # Output.write("Warning, skipping '{}', a process is already running.".format(" ".join(cmd)))
            cls.cache[str_cmd]["cb"].append(cb)
            # Output.write("B cls.cache: {}".format(cls.cache))
            return
        if env is not None:
            proc_env = QtCore.QProcessEnvironment()
            for k, v in env.items():
                proc_env.insert(k, v)
            proc.setProcessEnvironment(proc_env)
        proc.run(cmd)
        
    @classmethod
    def invalidate_cmd_cache(cls, cmd):
        str_cmd = " ".join(cmd)
        try:
            cls.cache[str_cmd]["expire_dt"] = datetime.datetime.now()
        except (AttributeError, KeyError):
            pass


class Networks_Check():
    def __init__(self, cfg):
        now = datetime.datetime.now()
        
        # Output.write("Networks_Check.__init__ {}".format(cfg))
        self.networks = {}
        self.hosts_status = {}
        
        for net in cfg.get("network", []):
            self.networks[net] = {
                "parent": cfg["network"][net].get("parent"),
                "ping": cfg["network"][net]["ping"],
                "error_msg": cfg["network"][net]["error_msg"],
            }
            for h in cfg["network"][net]["ping"]:
                self.hosts_status[h] = {
                        # "proc": proc,
                        "dt": now,
                        "status": True,
                    }
    
    def scan(self):
        """
            Scan all networks to check which are available and which are not.
        """
        for h in self.hosts_status:
            if CONST.OS_SYS == "Windows":
                cmd = ["ping", h, "-n", '1']
            if CONST.OS_SYS == "Linux":
                cmd = ["ping", "-c1", "-w1", h]
            if CONST.OS_SYS == "Darwin":
                cmd = ["ping", "-c1", "-W1", h]
            
            try:
                proc = NonBlockingProcess(h, self._scan_finished)
            except NonBlockingProcessException:
                Output.write("Warning, skipping ping of {}, a process is already running.".format(h))
                continue
            self.hosts_status[h]["proc"] = proc
            proc.run(cmd)

    def _scan_finished(self, h, status, output, exit_code):
        # print("ping {} : {}".format(h, output))
        self.hosts_status[h]["dt"] = datetime.datetime.now()
        self.hosts_status[h]["status"] = status
        del(self.hosts_status[h]["proc"])

    def get_status(self, net):
        """
            returns tuple status, error_msg
            if parent(s) are also of bad status, then returns error_msg from parent
        """
        dt_limit = datetime.datetime.now() - datetime.timedelta(seconds=45)
        try:
            for h in self.networks[net]["ping"]:
                if (self.hosts_status[h]["status"] and
                   self.hosts_status[h]["dt"] > dt_limit):
                    return (True, "")
        except KeyError:
            return (True, "")
        
        # this network is unreachable -> check parent
        if self.networks[net]["parent"] is not None:
            parent_status = self.get_status(self.networks[net]["parent"])
            if parent_status[0]:
                return (False, self.networks[net]["error_msg"])
            else:
                return parent_status
        else:
            return (False, self.networks[net]["error_msg"])


def validate_username(username):
    validate_url = CONST.VALIDATE_USERNAME_URL.format(username=username)
    try:
        with urllib.request.urlopen(validate_url, timeout=CONST.URL_TIMEOUT) as response:
            lines = [l.decode() for l in response.readlines()]
        return lines[0]
    except (socket.timeout, urllib.error.URLError):
        Output.write("Warning, could not load validate url. ({0})".format(validate_url))
        return "Error, could not contact config server."


def validate_release_number():
    try:
        with urllib.request.urlopen(CONST.LATEST_RELEASE_NUMBER_URL, timeout=CONST.URL_TIMEOUT) as response:
            latest_release = response.readline().decode()
            return latest_release == CONST.VERSION
    except (socket.timeout, urllib.error.URLError):
        Output.write("Warning, could not validate release number.")
        return True


class NonBlockingProcessException(Exception):
    pass


class NonBlockingProcess(QtCore.QProcess):
    def __init__(self, name, cb):
        super(NonBlockingProcess, self).__init__()
        NonBlockingProcess.register_process_name(name)
        self.name = name
        self.cb = cb
        
    def run(self, cmd):
        self.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.finished.connect(self._proc_finished)
        self.start(" ".join(cmd), QtCore.QIODevice.ReadOnly)

    def _proc_finished(self, exit_code, exit_status):
        NonBlockingProcess.unregister_process_name(self.name)
        success = (exit_status == 0 and exit_code == 0)
        output = bytes(self.readAll()).decode()
        self.cb(self.name, success, output, exit_code)
            
    @classmethod
    def register_process_name(cls, name):
        while True:
            try:
                if name in cls.process_names:
                    raise NonBlockingProcessException("Process named '{}' is already running.".format(name))
                cls.process_names.add(name)
                return
            except AttributeError:
                cls.process_names = set()

    @classmethod
    def unregister_process_name(cls, name):
        try:
            cls.process_names.remove(name)
        except AttributeError:
            cls.process_names = set()
        except KeyError:
            pass
