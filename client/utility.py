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
import threading
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


def bytes_decode(b):
    for encoding in ("utf-8", "iso8859_15"):
        try:
            return b.decode(encoding)
        except UnicodeDecodeError:
            pass
    return b.decode("utf-8", "replace")


class CONST():

    VERSION_DATE = "2018-04-13"
    VERSION = "1.1.11"
    FULL_VERSION = VERSION_DATE + " " + VERSION

    DOC_URL = "https://enacit.epfl.ch/enacdrives"

    OS_SYS = platform.system()
    if sys.maxsize > 2**64:
        ARCH_BITS = "128bit"
    elif sys.maxsize > 2**32:
        ARCH_BITS = "64bit"
    elif sys.maxsize > 2**16:
        ARCH_BITS = "32bit"
    elif sys.maxsize > 2**8:
        ARCH_BITS = "16bit"
    else:
        ARCH_BITS = "8bit"
    LOCAL_USERNAME = getpass.getuser()
    HOME_DIR = os.path.expanduser("~")

    URL_TIMEOUT = 2
    PROC_TIMEOUT = 2
    CIFS_TIMEOUT = 1

    GUI_FOCUS_REFRESH_INTERVAL = datetime.timedelta(seconds=3)
    GUI_FOCUS_LOST_STILL_FULL_REFRESH = datetime.timedelta(seconds=30)
    GUI_NOFOCUS_REFRESH_INTERVAL = datetime.timedelta(seconds=30)

    # RESOURCES_DIR is used to get files like app's icon
    if getattr(sys, 'frozen', False):
        # The application is frozen (applies to Linux and Windows)
        RESOURCES_DIR = os.path.dirname(os.path.realpath(sys.executable))
    else:
        # The application is not frozen
        RESOURCES_DIR = os.path.dirname(__file__)

    if OS_SYS == "Linux":
        OS_DISTRIB, OS_VERSION = platform.linux_distribution()[:2]
        try:
            LOCAL_GROUPNAME = grp.getgrgid(pwd.getpwnam(LOCAL_USERNAME).pw_gid).gr_name
        except KeyError:
            LOCAL_GROUPNAME = "Unknown"
        LOCAL_UID = pwd.getpwnam(LOCAL_USERNAME)[2]
        LOCAL_GID = pwd.getpwnam(LOCAL_USERNAME)[3]
        AD_DOMAIN = None
        AD_USERNAME = None
        try:
            DESKTOP_DIR = bytes_decode(subprocess.check_output(["xdg-user-dir", "DESKTOP"])).strip()
        except FileNotFoundException:
            DESKTOP_DIR = HOME_DIR + "/Desktop"
        DEFAULT_MNT_DIR = DESKTOP_DIR  # Should be overwritten from conf file
        USER_CACHE_DIR = HOME_DIR + "/.enacdrives.cache"
        USER_CONF_FILE = HOME_DIR + "/.enacdrives.conf"
        SYSTEM_CONF_FILE = "/etc/enacdrives.conf"
        LATEST_RELEASE_NUMBER_URL = "http://enacdrives.epfl.ch/releases/api/latest_release_number?os=Linux"
        DOWNLOAD_NEW_RELEASE_URL = "http://enacsoft.epfl.ch/enacdrives/"
        NEED_TO_UPDATE_MSG = "You are not running the latest release.<br>Please upgrade the package enacdrives."
    elif OS_SYS == "Darwin":
        OS_DISTRIB = "Apple"
        OS_VERSION = platform.mac_ver()[0]
        try:
            LOCAL_GROUPNAME = grp.getgrgid(pwd.getpwnam(LOCAL_USERNAME).pw_gid).gr_name
        except KeyError:
            LOCAL_GROUPNAME = "Unknown"
        LOCAL_UID = pwd.getpwnam(LOCAL_USERNAME)[2]
        LOCAL_GID = pwd.getpwnam(LOCAL_USERNAME)[3]
        if "LDAPv3" in bytes_decode(subprocess.check_output(["dscl"], input=b"ls\n")).strip():
            AD_DOMAIN = "Found LDAPv3"
            AD_USERNAME = os.environ.get("USER")
        else:
            AD_DOMAIN = None
            AD_USERNAME = None
        DESKTOP_DIR = HOME_DIR + "/Desktop"
        DEFAULT_MNT_DIR = DESKTOP_DIR
        USER_CACHE_DIR = HOME_DIR + "/.enacdrives.cache"
        USER_CONF_FILE = HOME_DIR + "/.enacdrives.conf"
        SYSTEM_CONF_FILE = "/etc/enacdrives.conf"
        LATEST_RELEASE_NUMBER_URL = "http://enacdrives.epfl.ch/releases/api/latest_release_number?os=MacOSX"
        DOWNLOAD_NEW_RELEASE_URL = "http://enacsoft.epfl.ch/enacdrives/"
        if getattr(sys, 'frozen', False):
            RESOURCES_DIR = os.path.abspath(os.path.join(os.path.dirname(sys.executable), os.pardir, "Resources"))
        NEED_TO_UPDATE_MSG = ("You are not running the latest release.<br>"
            "Please download it from <a href='{}'>here</a>.".format(DOWNLOAD_NEW_RELEASE_URL))
    elif OS_SYS == "Windows":
        OS_DISTRIB = "Microsoft"
        OS_VERSION = platform.win32_ver()[0]
        LOCAL_GROUPNAME = "Undefined"
        LOCAL_UID = -1
        LOCAL_GID = -1
        AD_DOMAIN = os.environ.get("USERDNSDOMAIN")
        if AD_DOMAIN is None:
            AD_USERNAME = None
        else:
            AD_USERNAME = os.environ.get("USERNAME")
        DESKTOP_DIR = HOME_DIR + "/Desktop"  # TO DO
        DEFAULT_MNT_DIR = DESKTOP_DIR  # TO DO
        try:
            APPDATA = os.environ["APPDATA"]  # Goes to AppData\Roaming like : C:\Users\<username>\AppData\Roaming
            USER_CACHE_DIR = APPDATA + "\\ENACdrives\\enacdrives.cache"
            USER_CONF_FILE = APPDATA + "\\ENACdrives\\enacdrives.conf"
        except KeyError:
            USER_CACHE_DIR = RESOURCES_DIR + "\\enacdrives.cache"
            USER_CONF_FILE = RESOURCES_DIR + "\\enacdrives.conf"
        SYSTEM_CONF_FILE = "C:\\ProgramData\\ENACdrives\\enacdrives.conf"
        LATEST_RELEASE_NUMBER_URL = "http://enacdrives.epfl.ch/releases/api/latest_release_number?os=Windows"
        DOWNLOAD_NEW_RELEASE_URL = "http://enacsoft.epfl.ch/enacdrives/"
        NEED_TO_UPDATE_MSG = ("You are not running the latest release.<br>"
            "Please download it from <a href='{}'>here</a>.".format(DOWNLOAD_NEW_RELEASE_URL))
    else:
        OS_VERSION = "Error: OS not supported."

    CONFIG_URL = "http://enacdrives.epfl.ch/config/get?username={username}&version={version}&os={os}&os_version={os_version}".format(
        username="{username}",
        version=VERSION,
        os=OS_DISTRIB + "-" + OS_SYS,
        os_version=OS_VERSION,
    )
    VALIDATE_USERNAME_URL = "http://enacdrives.epfl.ch/config/validate_username?username={username}&version=" + VERSION

    # use full ABSOLUTE path to the image, not relative
    ENACDRIVES_PNG = RESOURCES_DIR + "/enacdrives.png"
    MOUNTED_PNG = RESOURCES_DIR + "/mounted.png"
    UMOUNTED_PNG = RESOURCES_DIR + "/umounted.png"
    BOOKMARK_ON_PNG = RESOURCES_DIR + "/bookmark_on.png"
    BOOKMARK_OFF_PNG = RESOURCES_DIR + "/bookmark_off.png"
    WARNING_PNG = RESOURCES_DIR + "/warning.png"
    MSG_PNG_48 = RESOURCES_DIR + "/msg_48.png"
    INFO_PNG_48 = RESOURCES_DIR + "/info_48.png"
    WARNING_PNG_48 = RESOURCES_DIR + "/warning_48.png"
    CRITICAL_PNG_48 = RESOURCES_DIR + "/critical_48.png"


class Output():
    LEVELS = {
        "debug": {"prefix": "DEBUG: ", "rank": 5},  # -vv default for Windows & OSX
        "verbose": {"prefix": "", "rank": 4},  # -v
        "normal": {"prefix": "", "rank": 3},  # default for Linux GUI
        "cli": {"prefix": "", "rank": 2},  # default for Linux CLI
        "warning": {"prefix": "WARNING: ", "rank": 1},
        "error": {"prefix": "ERROR: ", "rank": 0},
    }

    def __init__(self, dest=None, level="normal"):
        self.level = level
        self.level_rank = Output.LEVELS[level]["rank"]
        if dest is not None:
            self.output = dest
        else:
            self.output = sys.stdout

    def __enter__(self):
        Output.set_instance(self)
        if (CONST.OS_SYS == "Windows" and
           getattr(sys, 'frozen', False)):
            # Windows frozen application
            locations = [CONST.RESOURCES_DIR + "\\execution_output.txt",]
            for env_var in ("LOCALAPPDATA", "APPDATA", "TEMP"):
                # os.environ["LOCALAPPDATA"]  Goes to AppData\Local
                # os.environ["APPDATA"]  Goes to AppData\Roaming
                # os.environ["TEMP"]  Goes to AppData\Local\Temp
                try:
                    locations.append(os.environ[env_var] + "\\ENACdrives\\execution_output.txt")
                except KeyError:
                    # LOCALAPPDATA doesn't exist on Win XP
                    pass
            for f_name in locations:
                try:
                    parent = os.path.dirname(f_name)
                    if not os.path.exists(parent):
                        os.makedirs(parent)
                    self.output = open(f_name, "w")
                    break
                except IOError:
                    pass
        return self

    def __exit__(self, typ, value, traceback):
        Output.del_instance()
        if (CONST.OS_SYS == "Windows" and
           getattr(sys, 'frozen', False)):
            # Windows frozen application
            self.output.close()

    def do_write(self, msg, level):
        msg = msg.replace("<br>", "\n")
        msg = msg.replace("<b>", "\033[01;37m")
        msg = msg.replace("</b>", "\033[00m")
        msg = msg.replace("<i>", "\033[00;37m")
        msg = msg.replace("</i>", "\033[00m")
        if level is None:
            self.output.write(msg)
        elif Output.LEVELS[level]["rank"] <= self.level_rank:
            self.output.write("{}{}".format(Output.LEVELS[level]["prefix"], msg))

    @classmethod
    def set_instance(cls, instance):
        cls.instance = instance

    @classmethod
    def del_instance(cls):
        cls.instance = None

    @classmethod
    def br(cls):
        cls.instance.do_write("\n", None)

    @classmethod
    def error(cls, msg="", end="\n"):
        cls.instance.do_write(msg + end, "error")

    @classmethod
    def warning(cls, msg="", end="\n"):
        cls.instance.do_write(msg + end, "warning")

    @classmethod
    def cli(cls, msg="", end="\n"):
        cls.instance.do_write(msg + end, "cli")

    @classmethod
    def normal(cls, msg="", end="\n"):
        cls.instance.do_write(msg + end, "normal")

    @classmethod
    def verbose(cls, msg="", end="\n"):
        cls.instance.do_write(msg + end, "verbose")

    @classmethod
    def debug(cls, msg="", end="\n"):
        cls.instance.do_write(msg + end, "debug")


# ENACIT1LOGS
# used to know what version are used
def enacit1logs_notify(ui):
    def _target():
        try:
            if ui.UI_TYPE == "GUI":
                msg = "run ENACdrives GUI"
            else:
                msg = "run ENACdrives CLI"
            enacit1logs.send(
                message=msg,
                tags=["ENACdrives-{}".format(CONST.VERSION), "{}-{}-{}-{}".format(CONST.OS_DISTRIB, CONST.OS_SYS, CONST.OS_VERSION, CONST.ARCH_BITS)]
            )
        except enacit1logs.SendLogException as e:
            Output.warning("Could not notify enacit1logs")

    def _finished(answer):
        pass

    if ui.UI_TYPE == "GUI":
        NonBlockingQtThread(
            "enacit1logs_notify",
            _target,
            _finished,
        )
    else:
        NonBlockingThread(
            "enacit1logs_notify",
            _target,
            _finished,
        )


# used to repatriate test cases
# + NET USE stdout and stderr (might encounter different one from different OS/Languages :( )
def debug_send(msg, additional_tags=None):
    if additional_tags is None:
        additional_tags = []
    Output.debug("GONNA SEND MSG TO ENACIT1LOGS : " + msg)
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
                    Output.verbose("Getting password for {0}".format(realm))
                    return self.keys[realm]["pw"]
                time.sleep(0.1)
        if password_mistyped:
            Output.normal("Asking password for {0} (previously mistyped)".format(realm))
        else:
            Output.normal("Asking password for {0}".format(realm))
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


class Networks_Check():
    MAX_NO_PING_SECONDS = datetime.timedelta(seconds=45)

    def __init__(self, cfg, ui):
        now = datetime.datetime.now()

        self.ui = ui
        if self.ui.UI_TYPE == "GUI":
            default_status = True
        else:
            default_status = None

        # Output.debug("Networks_Check.__init__ {}".format(cfg))
        self.networks = {}
        self.hosts_status = {
            "ping": {},
            "cifs": {},
        }

        for net in cfg.get("network", []):
            self.networks[net] = {
                "parent": cfg["network"][net].get("parent"),
                "ping": cfg["network"][net].get("ping", []),
                "cifs": cfg["network"][net].get("cifs", []),
                "error_msg": cfg["network"][net]["error_msg"],
                "last_state": None,
            }
            for h in cfg["network"][net].get("ping", []):
                self.hosts_status["ping"][h] = {
                        "dt": now,
                        "status": default_status,
                    }
            for h in cfg["network"][net].get("cifs", []):
                self.hosts_status["cifs"][h] = {
                        "dt": now,
                        "status": default_status,
                    }

    def scan(self):
        """
            Scan all networks to check which are available and which are not.
        """
        def _ping_finished(status, output, exit_code, host):
            # print("ping {} : {}".format(host, status))
            self.hosts_status["ping"][host]["dt"] = datetime.datetime.now()
            self.hosts_status["ping"][host]["status"] = status

        def _ping_target(host):
            if CONST.OS_SYS == "Windows":
                cmd = ["ping", host, "-n", '1']
            elif CONST.OS_SYS == "Linux":
                cmd = ["ping", "-c1", "-w1", host]
            elif CONST.OS_SYS == "Darwin":
                cmd = ["ping", "-c1", "-W1", host]
            else:
                raise Exception("Unknown OS {}".format(CONST.OS_SYS))
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except FileNotFoundError:  #  FileNotFoundError: [Errno 2] No such file or directory: 'ping'
                Output.error("Could not find 'ping' utility. Skipping and considering ping {} is ok.".format(host))
                return True
            try:
                outs, errs = proc.communicate(timeout = CONST.PROC_TIMEOUT)
                success = True
            except subprocess.TimeoutExpired:
                proc.kill()
                outs, errs = proc.communicate()
                success = False
            return success and (proc.returncode == 0)

        def _ping_target_finished(answer, host):
            # print("ping {} : {}".format(host, answer))
            self.hosts_status["ping"][host]["dt"] = datetime.datetime.now()
            self.hosts_status["ping"][host]["status"] = answer


        def _cifs_target(host):
            port = 139
            try:
                sock = socket.create_connection((host, port), CONST.CIFS_TIMEOUT)
                sock.close()
            except:
                return False
            return True

        def _cifs_target_finished(answer, host):
            # print("cifs {} : {}".format(host, answer))
            self.hosts_status["cifs"][host]["dt"] = datetime.datetime.now()
            self.hosts_status["cifs"][host]["status"] = answer

        for h in self.hosts_status["ping"]:
            if CONST.OS_SYS == "Windows":
                cmd = ["ping", h, "-n", '1']
            if CONST.OS_SYS == "Linux":
                cmd = ["ping", "-c1", "-w1", h]
            if CONST.OS_SYS == "Darwin":
                cmd = ["ping", "-c1", "-W1", h]

            if self.ui.UI_TYPE == "GUI":
                # print("NonBlockingQtProcess {}".format(cmd))
                NonBlockingQtProcess(
                    cmd,
                    _ping_finished,
                    cb_extra_args={"host": h},
                    cache=True,
                )
            else:
                # print("NonBlockingThread ping.{}".format(h))
                NonBlockingThread(
                    "ping.{}".format(h),
                    _ping_target,
                    _ping_target_finished,
                    target_extra_args={"host": h},
                    cb_extra_args={"host": h},
                )
        for h in self.hosts_status["cifs"]:
            if self.ui.UI_TYPE == "GUI":
                # print("NonBlockingQtThread ping.cifs.{}".format(h))
                NonBlockingQtThread(
                    "ping.cifs.{}".format(h),
                    _cifs_target,
                    _cifs_target_finished,
                    target_extra_args={"host": h},
                    cb_extra_args={"host": h},
                )
            else:
                # print("NonBlockingThread ping.cifs.{}".format(h))
                NonBlockingThread(
                    "ping.cifs.{}".format(h),
                    _cifs_target,
                    _cifs_target_finished,
                    target_extra_args={"host": h},
                    cb_extra_args={"host": h},
                )

    def get_status(self, net):
        """
            returns tuple status, error_msg
            if parent(s) are also of bad status, then returns error_msg from parent
        """
        dt_limit = datetime.datetime.now() - Networks_Check.MAX_NO_PING_SECONDS
        try:
            while True:
                wait_for_answer = False
                for h in self.networks[net]["cifs"]:
                    if self.hosts_status["cifs"][h]["status"] is None:
                        wait_for_answer = True
                        continue
                    if (self.hosts_status["cifs"][h]["status"] and
                       self.hosts_status["cifs"][h]["dt"] > dt_limit):
                        if self.networks[net]["last_state"] is not True:
                            Output.normal("==> network {} : {} -> True".format(net, self.networks[net]["last_state"]))
                            self.networks[net]["last_state"] = True
                        return (True, "")
                for h in self.networks[net]["ping"]:
                    if self.hosts_status["ping"][h]["status"] is None:
                        wait_for_answer = True
                        continue
                    if (self.hosts_status["ping"][h]["status"] and
                       self.hosts_status["ping"][h]["dt"] > dt_limit):
                        if self.networks[net]["last_state"] is not True:
                            Output.normal("==> network {} : {} -> True".format(net, self.networks[net]["last_state"]))
                            self.networks[net]["last_state"] = True
                        return (True, "")
                if wait_for_answer:
                    # print("wait_for_answer")
                    time.sleep(0.1)
                else:
                    break
        except KeyError:
            return (True, "")

        if self.networks[net]["last_state"] is not False:
            Output.normal("==> network {} : {} -> False ({})".format(net, self.networks[net]["last_state"], self.networks[net]["error_msg"]))
            self.networks[net]["last_state"] = False

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
            lines = [bytes_decode(l) for l in response.readlines()]
            Output.debug("validate_username {} : {}".format(validate_url, lines))
            return lines[0]
    except (socket.timeout, urllib.error.URLError) as e:
        Output.warning("Could not load validate url. ({})".format(validate_url))
        Output.warning("Got error : {}".format(e))
        return "Error, could not contact config server."


def validate_release_number():
    try:
        with urllib.request.urlopen(CONST.LATEST_RELEASE_NUMBER_URL, timeout=CONST.URL_TIMEOUT) as response:
            lines = [bytes_decode(l) for l in response.readlines()]
            Output.debug("validate_release_number {} : {}".format(CONST.LATEST_RELEASE_NUMBER_URL, lines))
            return CONST.VERSION == lines[0]
    except (socket.timeout, urllib.error.URLError) as e:
        Output.warning("Could not validate release number. ({})".format(CONST.LATEST_RELEASE_NUMBER_URL))
        Output.warning("Got error : {}".format(e))
        return True


class BlockingProcess():
    CACHE_DURATION = datetime.timedelta(seconds=1)

    @classmethod
    def run(cls, cmd, env=None, cache=False):
        name = ".".join(cmd)
        if cache:
            cached = BlockingProcess.check_in_cache(name)
            if cached["found"]:
                return cached["answer"]

        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            outs, errs = proc.communicate(timeout = CONST.PROC_TIMEOUT)
            success = True
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
            success = False
        answer = {
            "success": success and (proc.returncode == 0),
            "output": bytes_decode(outs),
            "exit_code": proc.returncode,
        }
        if cache:
            BlockingProcess.save_in_cache(name, answer)
        return answer


    @classmethod
    def check_in_cache(cls, name):
        try:
            cls.cache
        except AttributeError:
            cls.cache = {}
        if cls.cache.get(name) and cls.cache[name]["expire_dt"] > datetime.datetime.now():
            return {
                "found": True,
                "answer": cls.cache[name]["answer"],
            }
        return {
            "found": False,
        }

    @classmethod
    def save_in_cache(cls, name, answer):
        try:
            cls.cache
        except AttributeError:
            cls.cache = {}
        cls.cache[name] = {
            "expire_dt": datetime.datetime.now() + BlockingProcess.CACHE_DURATION,
            "answer": answer,
        }

    @classmethod
    def invalidate_cmd_cache(cls, cmd):
        try:
            cls.cache
        except AttributeError:
            cls.cache = {}
        name = ".".join(cmd)
        try:
            del(cls.cache[name])
        except (KeyError, AttributeError):
            pass



class NonBlockingQtProcess(QtCore.QProcess):
    CACHE_DURATION = datetime.timedelta(seconds=1)

    def __init__(self, cmd, cb, env=None, cb_extra_args=None, cache=False):
        super(NonBlockingQtProcess, self).__init__()
        name = ".".join(cmd)
        self.name = name
        self.cmd = cmd
        self.cb_extra_args = cb_extra_args
        self.cache = cache
        self.output = ""

        if cache:
            if NonBlockingQtProcess.answer_if_in_cache(name, self, cb):
                return

        if not NonBlockingQtProcess.register_process(name, self, cb):
            return  # A process is already running. cb will be called
        self.finished.connect(self._finished)
        self.readyReadStandardOutput.connect(self._readyReadStandardOutput)

        if env is not None:
            proc_env = QtCore.QProcessEnvironment()
            for k, v in env.items():
                proc_env.insert(k, v)
            self.setProcessEnvironment(proc_env)

        self.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.start(" ".join(self.cmd), QtCore.QIODevice.ReadOnly)

    def _readyReadStandardOutput(self):
        out = self.readAll()
        out = bytes_decode(bytes(out))
        self.output += out

    def _finished(self, exit_code, exit_status):
        success = (exit_status == 0 and exit_code == 0)
        out = self.readAll()
        out = bytes_decode(bytes(out))
        self.output += out
        NonBlockingQtProcess.notify_answer(self.name, success, self.output, exit_code)

    @classmethod
    def register_process(cls, name, instance, cb):
        try:
            cls.process_names
        except AttributeError:
            cls.process_names = {}
            cls.lock = threading.Lock()
            cls.cache = {}

        with cls.lock:
            if name in cls.process_names:
                cls.process_names[name]["cb"].append(cb)
                return False
            else:
                cls.process_names[name] = {
                    "instance": instance,
                    "cb": [cb, ],
                    "launch_dt": datetime.datetime.now(),
                }
                return True

    @classmethod
    def notify_answer(cls, name, success, output, exit_code):
        try:
            cls.process_names
        except AttributeError:
            cls.process_names = {}
            cls.lock = threading.Lock()
            cls.cache = {}

        with cls.lock:
            # Output.debug("NonBlockingQtProcess.notify_answer '{}' took: {}.".format(name, datetime.datetime.now()-cls.process_names[name]["launch_dt"]))
            try:
                all_cb = cls.process_names[name]["cb"]
                cb_extra_args = cls.process_names[name]["instance"].cb_extra_args
                if cls.process_names[name]["instance"].cache:
                    cls.cache[name] = {
                        "expire_dt": datetime.datetime.now() + NonBlockingQtProcess.CACHE_DURATION,
                        "success": success,
                        "output": output,
                        "exit_code": exit_code,
                    }
                del(cls.process_names[name])
            except KeyError:
                all_cb = ()
        for cb in all_cb:
            if cb_extra_args is None:
                cb(success, output, exit_code)
            else:
                cb(success, output, exit_code, **cb_extra_args)

    @classmethod
    def answer_if_in_cache(cls, name, instance, cb):
        try:
            cls.process_names
        except AttributeError:
            cls.process_names = {}
            cls.lock = threading.Lock()
            cls.cache = {}

        try:
            found = False
            with cls.lock:
                cached = cls.cache[name]
                if cached["expire_dt"] >= datetime.datetime.now():
                    found = True
                    success = cached["success"]
                    output = cached["output"]
                    exit_code = cached["exit_code"]
            if found:
                # print("answer_if_in_cache {} : found valid cache".format(name))
                if instance.cb_extra_args is None:
                    cb(success, output, exit_code)
                else:
                    cb(success, output, exit_code, **instance.cb_extra_args)
                return True
        except KeyError:
            pass
        # print("answer_if_in_cache {} : not found".format(name))
        return False

    @classmethod
    def invalidate_cmd_cache(cls, cmd):
        name = ".".join(cmd)
        with cls.lock:
            try:
                del(cls.cache[name])
            except (KeyError, AttributeError):
                pass


class NonBlockingQtThread(QtCore.QThread):
    def __init__(self, name, target, cb, target_extra_args=None, cb_extra_args=None):
        super(NonBlockingQtThread, self).__init__()
        self.name = name
        self.target = target
        self.target_extra_args = target_extra_args
        if not NonBlockingQtThread.register_thread(name, self, cb, cb_extra_args):
            return  # A thread is already running. cb will be called
        self.finished.connect(self._finished)
        self.start()

    def run(self):
        # time.sleep(6)  # Make heavy delay tests
        if self.target_extra_args is None:
            answer = self.target()
        else:
            answer = self.target(**self.target_extra_args)
        NonBlockingQtThread.save_answer(self.name, answer)

    def _finished(self):
        NonBlockingQtThread.notify_cb(self.name)

    @classmethod
    def register_thread(cls, name, instance, cb, cb_extra_args):
        try:
            cls.thread_names
        except AttributeError:
            cls.thread_names = {}
            cls.lock = threading.Lock()

        with cls.lock:
            if name in cls.thread_names:
                cls.thread_names[name]["cb"].append((cb, cb_extra_args))
                return False
            else:
                cls.thread_names[name] = {
                    "instance": instance,
                    "cb": [(cb, cb_extra_args), ],
                }
                return True

    @classmethod
    def save_answer(cls, name, answer):
        try:
            cls.thread_names
        except AttributeError:
            cls.thread_names = {}
            cls.lock = threading.Lock()

        with cls.lock:
            try:
                cls.thread_names[name]["answer"] = answer
            except KeyError:
                pass

    @classmethod
    def notify_cb(cls, name):
        try:
            cls.thread_names
        except AttributeError:
            cls.thread_names = {}
            cls.lock = threading.Lock()

        with cls.lock:
            try:
                answer = cls.thread_names[name]["answer"]
                all_cb = cls.thread_names[name]["cb"]
                del(cls.thread_names[name])
            except KeyError:
                all_cb = ()
        for cb, cb_extra_args in all_cb:
            if cb_extra_args is None:
                cb(answer)
            else:
                cb(answer, **cb_extra_args)


class NonBlockingThread(threading.Thread):
    def __init__(self, name, target, cb, target_extra_args=None, cb_extra_args=None):
        super(NonBlockingThread, self).__init__()
        self.name = name
        self.target = target
        self.target_extra_args = target_extra_args
        if not NonBlockingThread.register_thread(name, self, cb, cb_extra_args):
            return  # A thread is already running. cb will be called
        self.start()

    def run(self):
        # time.sleep(6)  # Make heavy delay tests
        if self.target_extra_args is None:
            answer = self.target()
        else:
            answer = self.target(**self.target_extra_args)
        NonBlockingThread.save_answer(self.name, answer)
        NonBlockingThread.notify_cb(self.name)

    @classmethod
    def register_thread(cls, name, instance, cb, cb_extra_args):
        try:
            cls.thread_names
        except AttributeError:
            cls.thread_names = {}
            cls.lock = threading.Lock()

        with cls.lock:
            if name in cls.thread_names:
                cls.thread_names[name]["cb"].append((cb, cb_extra_args))
                return False
            else:
                cls.thread_names[name] = {
                    "instance": instance,
                    "cb": [(cb, cb_extra_args), ],
                }
                return True

    @classmethod
    def save_answer(cls, name, answer):
        try:
            cls.thread_names
        except AttributeError:
            cls.thread_names = {}
            cls.lock = threading.Lock()

        with cls.lock:
            try:
                cls.thread_names[name]["answer"] = answer
            except KeyError:
                pass

    @classmethod
    def notify_cb(cls, name):
        try:
            cls.thread_names
        except AttributeError:
            cls.thread_names = {}
            cls.lock = threading.Lock()

        with cls.lock:
            try:
                answer = cls.thread_names[name]["answer"]
                all_cb = cls.thread_names[name]["cb"]
                del(cls.thread_names[name])
            except KeyError:
                all_cb = ()
        for cb, cb_extra_args in all_cb:
            if cb_extra_args is None:
                cb(answer)
            else:
                cb(answer, **cb_extra_args)
