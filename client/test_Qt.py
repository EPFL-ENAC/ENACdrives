#!/usr/bin/env python3

# Bancal Samuel

# Constraints :
#
# + Windows :
#   + WinPython-32bit-3.4.2.4 comes with PyQt4 (not PyQt5)
#
# + Linux :
#   + . activate
#   + export PYTHONPATH=/usr/lib/python3/dist-packages
#
# + MacOSX :
#

import os
import re
import gc
import sys
import time
import getpass
import tempfile
import platform
import datetime
import subprocess
from PyQt4 import QtGui
try:
    import grp
    import pwd
    import pexpect
except ImportError:  # for Windows
    pass
    # import winpexpect


# ENACIT1LOGS
# used to repatriate test cases
# + NET USE stdout and stderr (might encounter different one from different OS/Languages :( )
import enacit1logs


def debug_send(msg, additional_tags=None):
    if additional_tags is None:
        additional_tags = []
    my_print("GONNA SEND MSG TO ENACIT1LOGS : " + msg)
    enacit1logs.send(
        message=str(msg),
        tags=["dev_mountfilers2015", "notify_bancal", CONST.VERSION] + additional_tags
    )

# /ENACIT1LOGS


# Tools

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


class Output_Destination():
    def __init__(self):
        if (CONST.OS_SYS == "Windows" and
           getattr(sys, 'frozen', False)):
            # Windows frozen application
            self.output = open(CONST.RESOURCES_DIR + "/execution_output.txt", "a")
        else:
            self.output = sys.stdout

    def write(self, msg):
        self.output.write(msg)


def my_print(msg="", end="\n", flush=True, dest=Output_Destination()):
    """
        sends output to file if this is compiled on Windows
        sends output to stdou otherwise
        
        Note : flush has no effect.
    """
    dest.write(msg + end)


class CancelOperationException(Exception):
    """
        Raised when user want to abort an operation
    """
    pass


class UI_Label_Entry(QtGui.QHBoxLayout):

    def __init__(self, label):
        super(UI_Label_Entry, self).__init__()
        self.label = QtGui.QLabel(label)
        self.addWidget(self.label)
        self.addStretch(1)


class UI_Mount_Entry(QtGui.QHBoxLayout):

    def __init__(self, ui, mount_instance):
        super(UI_Mount_Entry, self).__init__()

        self.ui = ui
        self.mount_instance = mount_instance

        self.label = QtGui.QLabel(self.mount_instance.settings["label"])
        self.bt_mount = QtGui.QPushButton("Mount", self.ui)
        self.bt_mount.clicked.connect(self.toggle_mount)
        self.bt_open = QtGui.QPushButton('Open', self.ui)
        self.bt_open.clicked.connect(self.mount_instance.open)
        self.addWidget(self.label)
        self.addStretch(1)
        self.addWidget(self.bt_mount)
        self.addWidget(self.bt_open)
        self.update_status()

    def toggle_mount(self):
        if self.mount_instance.is_mounted():
            self.mount_instance.umount()
        else:
            self.mount_instance.mount()
        self.update_status()

    def update_status(self):
        if self.mount_instance.is_mounted():
            self.bt_mount.setText("unMount")
            self.label.setText(self.mount_instance.settings["label"] + "[mounted]")
        else:
            self.bt_mount.setText("Mount")
            self.label.setText(self.mount_instance.settings["label"] + "[not mounted]")


class UI(QtGui.QWidget):

    def __init__(self):
        super(UI, self).__init__()

        self.key_chain = Key_Chain(self)

        self.entries = []

        mount_bancal = CIFS_Mount(self, self.key_chain)
        self.entries.append(UI_Mount_Entry(self, mount_bancal))

        self.bt_quit = QtGui.QPushButton('Quit', self)
        self.bt_quit.clicked.connect(QtGui.qApp.quit)

        self.hbox_bt_quit = QtGui.QHBoxLayout()
        self.hbox_bt_quit.addStretch(1)
        self.hbox_bt_quit.addWidget(self.bt_quit)

        self.vbox_layout = QtGui.QVBoxLayout()
        for entry in self.entries:
            self.vbox_layout.addLayout(entry)
        self.vbox_layout.addStretch(1)
        self.vbox_layout.addLayout(self.hbox_bt_quit)

        self.setLayout(self.vbox_layout)

        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle("Test compiled Python (Win/Lin/OSX)")
        self.setWindowIcon(QtGui.QIcon(os.path.join(CONST.RESOURCES_DIR, "mount_filers.png")))
        self.show()

    def get_password(self, realm):
        password, ok = QtGui.QInputDialog.getText(
            self,
            "Please enter a password",
            "Give your " + realm + " password",
            QtGui.QLineEdit.Password,
        )

        if ok:
            return str(password)
        else:
            raise CancelOperationException("Button cancel pressed")


class Key_Chain():
    """
        Holds the passwords entered diring the execution time.
    """

    def __init__(self, ui):
        self.ui = ui
        self.keys = {}

    def get_password(self, realm):
        my_print("Asking password for {0}".format(realm))
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
            "Linux_CIFS_method": "mount.cifs",
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
        if CONST.OS_SYS == "Linux":
            if self.settings["Linux_CIFS_method"] == "gvfs":
                cmd = [CONST.CMD_GVFS_MOUNT, "-l"]
                # my_print(" ".join(cmd))
                lines = Live_Cache.subprocess_check_output(cmd)
                i_search = r"{server_share} .+ {server_name} -> smb://{realm_domain};{realm_username}@{server_name}/{server_share}".format(**self.settings)
                for l in lines.split("\n"):
                    if re.search(i_search, l):
                        # my_print(l)
                        return True
            else:  # "mount.cifs"
                return os.path.ismount(self.settings["local_path"])

        elif CONST.OS_SYS == "Windows":
            cmd = ["wmic", "logicaldisk"]  # List all Logical Disks
            lines = Live_Cache.subprocess_check_output(cmd)
            lines = lines.split("\n")
            caption_index = lines[0].index("Caption")
            providername_index = lines[0].index("ProviderName")
            i_search = r"^\\{server_name}\{server_path}$".format(**self.settings)
            i_search = i_search.replace("\\", "\\\\")
            # my_print("i_search='{0}'".format(i_search))
            for l in lines[1:]:
                try:
                    drive_letter = re.findall(r"^(\S+)", l[caption_index:])[0]
                    try:
                        provider = re.findall(r"^(\S+)", l[providername_index:])[0]
                        if re.search(i_search, provider):
                            self.settings["Windows_letter"] = drive_letter
                            return True
                    except IndexError:
                        provider = ""
                    # my_print("{0} : '{1}'".format(drive_letter, provider))
                except IndexError:
                    pass
            return False

        elif CONST.OS_SYS == "Darwin":
            return os.path.ismount(self.settings["local_path"])

        else:
            raise Exception("Unknown System " + CONST.OS_SYS)
        return False

    def mount(self):
        my_print()
        if CONST.OS_SYS == "Linux":
            if self.settings["Linux_CIFS_method"] == "gvfs":
                # 1) Remove broken symlink or empty dir
                if self.settings["Linux_gvfs_symlink"]:
                    if (os.path.lexists(self.settings["local_path"]) and
                       not os.path.exists(self.settings["local_path"])):
                        os.unlink(self.settings["local_path"])
                    if (os.path.isdir(self.settings["local_path"]) and
                       os.listdir(self.settings["local_path"]) == []):
                        os.rmdir(self.settings["local_path"])
                    if os.path.exists(self.settings["local_path"]):
                        raise Exception("Error : Path %s already exists" % self.settings["local_path"])

                # 2) Mount
                cmd = [CONST.CMD_GVFS_MOUNT, r"smb://{realm_domain}\;{realm_username}@{server_name}/{server_share}".format(**self.settings)]
                my_print(" ".join(cmd))
                process_meta = {
                    "was_cancelled": False,
                }
                try:
                    (output, exit_status) = pexpect.runu(
                        command=" ".join(cmd),
                        events={
                            'Password:': pexpect_ask_password,
                        },
                        extra_args={
                            "auth_realms": [
                                (r'Password:', self.settings["realm"])
                            ],
                            "key_chain": self.key_chain,
                            "process_meta": process_meta,
                            # "context" : "gvfs_mount_%s" % self.settings["name"]
                        },
                        withexitstatus=True,
                        timeout=5,
                    )
                except pexpect.ExceptionPexpect as exc:
                    raise Exception("Error while mounting : %s" % exc.value)
                if exit_status == 0:
                    self.key_chain.ack_password(self.settings["realm"])
                elif process_meta["was_cancelled"]:
                    pass
                elif exit_status != 0:
                    raise Exception("Error while mounting : %d %s" % (exit_status, output))
                Live_Cache.invalidate_cmd_cache([CONST.CMD_GVFS_MOUNT, "-l"])

                # 3) Symlink
                if self.settings["Linux_gvfs_symlink"]:
                    mount_point = None
                    for f in os.listdir(CONST.GVFS_DIR):
                        if CONST.GVFS_GENERATION == 1:
                            if re.match(r'{server_share} \S+ {server_name}'.format(**self.settings), f):
                                mount_point = os.path.join(CONST.GVFS_DIR, f)
                        else:
                            if (re.match(r'^smb-share:', f) and
                               re.search(r'domain={realm_domain}(,|$)'.format(**self.settings), f, flags=re.IGNORECASE) and
                               re.search(r'server={server_name}(,|$)'.format(**self.settings), f) and
                               re.search(r'share={server_share}(,|$)'.format(**self.settings), f) and
                               re.search(r'user={realm_username}(,|$)'.format(**self.settings), f)):
                                mount_point = os.path.join(CONST.GVFS_DIR, f)

                    if mount_point is None:
                        raise Exception("Error: Could not find the GVFS mountpoint.")

                    target = os.path.join(mount_point, self.settings["server_subdir"])
                    try:
                        os.symlink(target, self.settings["local_path"])
                    except OSError as e:
                        raise Exception("Could not create symbolic link : %s" % e.args[1])
                    if not os.path.islink(self.settings["local_path"]):
                        raise Exception("Could not create symbolic link : %s <- %s" % (target, self.settings["local_path"]))

            else:  # "mount.cifs"
                # 1) Make mount dir
                if not os.path.exists(self.settings["local_path"]):
                    try:
                        os.makedirs(self.settings["local_path"])
                    except OSError:
                        pass
                if not os.path.isdir(self.settings["local_path"]):
                    raise Exception("Error while creating dir : %s" % self.settings["local_path"])

                # 2) Mount
                cmd = [
                    "sudo", CONST.CMD_MOUNT_CIFS,
                    "//{server_name}/{server_path}",
                    "{local_path}",
                    "-o",
                    "user={realm_username},domain={realm_domain},"
                    "uid={local_uid},gid={local_gid},"
                    "file_mode={Linux_mountcifs_filemode},"
                    "dir_mode={Linux_mountcifs_filemode},"
                    "{Linux_mountcifs_options}"
                ]
                cmd = [s.format(**self.settings) for s in cmd]
                my_print(" ".join(cmd))
                # for i in xrange(3): # 3 attempts (for passwords mistyped)
                process_meta = {
                    "was_cancelled": False,
                }
                (output, exit_status) = pexpect.runu(
                    command=" ".join(cmd),
                    events={
                        '(?i)password': pexpect_ask_password,
                    },
                    extra_args={
                        "auth_realms": [
                            (r'\[sudo\] password', "sudo"),
                            (r'Password', self.settings["realm"])
                        ],
                        "key_chain": self.key_chain,
                        "process_meta": process_meta,
                    },
                    withexitstatus=True,
                    timeout=5,
                )
                if exit_status == 0:
                    self.key_chain.ack_password("sudo")
                    self.key_chain.ack_password(self.settings["realm"])
                    # break
                elif process_meta["was_cancelled"]:
                    pass
                elif exit_status != 0:
                    raise Exception("Error while mounting : %d %s" % (exit_status, output))

        elif CONST.OS_SYS == "Windows":
            # Couldn't make this work : TODO
            # cmd = [
            #     "NET", "USE", "{Windows_letter}",
            #     r"\\{server_name}\{server_path}", "*",
            #     r"/USER:{realm_domain}\{realm_username}", "/PERSISTENT:no"
            # ]
            # cmd = [s.format(**self.settings) for s in cmd]
            # my_print(" ".join(cmd))
            # child = winpexpect.winspawn(cmd[0], cmd[1:])
            # child.expect("password")
            # child.sendline("BLABLAPWD")
            # ... terminate
            
            # STARTUPINFO : Prevents cmd to be opened when subprocess.Popen is called.
            # http://stackoverflow.com/a/24171096/446302
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            # 1) First attempt without password
            cmd = [
                "NET",
                "USE", "{Windows_letter}",
                r"\\{server_name}\{server_path}", 
                r"/USER:{realm_domain}\{realm_username}", "/PERSISTENT:no"
            ]
            cmd = [s.format(**self.settings) for s in cmd]
            s_cmd = " ".join(cmd)
            my_print("Running : {0}".format(s_cmd))
            p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, startupinfo=startupinfo)
            while True:
                try:
                    stdout, stderr = p.communicate(timeout=1)
                    stdout = "\n".join([l.strip() for l in stdout.decode("UTF-8").split("\n") if l.strip() != ""])
                    stderr = "\n".join([l.strip() for l in stderr.decode("UTF-8").split("\n") if l.strip() != ""])
                    if stdout != "":
                        my_print("out:{0}".format(stdout))
                    if stderr != "":
                        my_print("err:{0}".format(stderr))
                    if stdout == "" and stderr == "":
                        my_print("<no output>")
                    if "Enter the password" in stdout:
                        p.kill()
                        break
                    if stderr != "":
                        debug_send("{0}\nout: {1}\nerr: {2}".format(s_cmd, stdout, stderr))
                    if p.returncode == 0:
                        Live_Cache.invalidate_cmd_cache(["wmic", "logicaldisk"])
                        return True
                    if p.returncode is not None:
                        debug_send("{0}\nout: {1}\nerr: {2}\nreturncode: {3}".format(s_cmd, stdout, stderr, p.returncode))
                        break
                except subprocess.TimeoutExpired:
                    my_print(".", end="", flush=True)
            
            if p.returncode != 0:
                # 2) Second attempt with password
                for _ in range(3):
                    cmd = [
                        "NET",
                        "USE", "{Windows_letter}",
                        r"\\{server_name}\{server_path}", "***",
                        r"/USER:{realm_domain}\{realm_username}", "/PERSISTENT:no"
                    ]
                    cmd = [s.format(**self.settings) for s in cmd]
                    s_cmd = " ".join(cmd)
                    try:
                        cmd[4] = self.key_chain.get_password(self.settings["realm"])
                    except CancelOperationException:
                        my_print("Operation cancelled.")
                        break
                    my_print("Running : {0}".format(s_cmd))
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, startupinfo=startupinfo)
                    while True:
                        try:
                            stdout, stderr = p.communicate(timeout=1)
                            stdout = "\n".join([l.strip() for l in stdout.decode("UTF-8").split("\n") if l.strip() != ""])
                            stderr = "\n".join([l.strip() for l in stderr.decode("UTF-8").split("\n") if l.strip() != ""])
                            if stdout != "":
                                my_print("out:{0}".format(stdout))
                            if stderr != "":
                                my_print("err:{0}".format(stderr))
                            if stdout == "" and stderr == "":
                                my_print("<no output>")
                            if "password is not correct" in stderr:
                                p.kill()
                                break
                            if "bad password" in stderr:
                                p.kill()
                                break
                            if stderr != "":
                                debug_send("{0}\nout: {1}\nerr: {2}".format(s_cmd, stdout, stderr))
                            if p.returncode == 0:
                                Live_Cache.invalidate_cmd_cache(["wmic", "logicaldisk"])
                                self.key_chain.ack_password(self.settings["realm"])
                                return True
                            if p.returncode is not None:
                                debug_send("{0}\nout: {1}\nerr: {2}\nreturncode: {3}".format(s_cmd, stdout, stderr, p.returncode))
                                break
                        except subprocess.TimeoutExpired:
                            my_print(".", end="", flush=True)
                        except Exception as e:
                            my_print("Exception : {0}".format(e))
                            debug_send("{0}\nException: {1}\n".format(s_cmd, e))

        elif CONST.OS_SYS == "Darwin":
            pass  # TO DO
        else:
            raise Exception("Unknown System " + CONST.OS_SYS)
        return False

    def umount(self):
        my_print()
        if CONST.OS_SYS == "Linux":
            if self.settings["Linux_CIFS_method"] == "gvfs":
                # 1) Umount
                cmd = [CONST.CMD_GVFS_MOUNT, "-u", r"smb://{realm_domain};{realm_username}@{server_name}/{server_share}".format(**self.settings)]
                my_print(" ".join(cmd))
                try:
                    output = subprocess.check_output(cmd)
                except subprocess.CalledProcessError as e:
                    raise Exception("Error (%s) while umounting : %s" % (e.returncode, e.output.decode()))
                Live_Cache.invalidate_cmd_cache([CONST.CMD_GVFS_MOUNT, "-l"])

                # 2) Remove symlink
                if self.settings["Linux_gvfs_symlink"]:
                    if (os.path.lexists(self.settings["local_path"]) and
                       not os.path.exists(self.settings["local_path"])):
                        os.unlink(self.settings["local_path"])

            else:  # "mount.cifs"
                # 1) uMount
                cmd = ["sudo", CONST.CMD_UMOUNT, "{local_path}"]
                cmd = [s.format(**self.settings) for s in cmd]
                my_print(" ".join(cmd))
                # for i in xrange(3): # 3 attempts (for passwords mistyped)
                process_meta = {
                    "was_cancelled": False,
                }
                (output, exit_status) = pexpect.runu(
                    command=" ".join(cmd),
                    events={
                        '(?i)password': pexpect_ask_password,
                    },
                    extra_args={
                        "auth_realms": [
                            (r'\[sudo\] password', "sudo"),
                        ],
                        "key_chain": self.key_chain,
                        "process_meta": process_meta,
                    },
                    withexitstatus=True,
                    timeout=5,
                )
                if exit_status == 0:
                    self.key_chain.ack_password("sudo")
                    # break
                elif process_meta["was_cancelled"]:
                    pass
                elif exit_status != 0:
                    raise Exception("Error while umounting : %d %s" % (exit_status, output))

                # 2) Remove mount dir
                if (os.path.exists(self.settings["local_path"]) and
                   os.listdir(self.settings["local_path"]) == []):
                    try:
                        os.rmdir(self.settings["local_path"])
                    except OSError:
                        pass

        elif CONST.OS_SYS == "Windows":
            # TODO : manage this message ... (cross languages!)
            # There are open files and/or incomplete directory searches pending on the connect
            # ion to Z:.
            #
            # Is it OK to continue disconnecting and force them closed? (Y/N) [N]:
            cmd = ["NET", "USE", self.settings["Windows_letter"], "/delete"]
            my_print(" ".join(cmd))
            try:
                # STARTUPINFO : Prevents cmd to be opened when subprocess.Popen is called.
                # http://stackoverflow.com/a/24171096/446302
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                output = subprocess.check_output(cmd, shell=False, startupinfo=startupinfo)
            except subprocess.CalledProcessError as e:
                raise Exception("Error (%s) while umounting : %s" % (e.returncode, e.output.decode()))
            Live_Cache.invalidate_cmd_cache(["wmic", "logicaldisk"])

        elif CONST.OS_SYS == "Darwin":
            pass  # TO DO
        else:
            raise Exception("Unknown System " + CONST.OS_SYS)
        return False

    def open(self):
        my_print()
        # TO DO : if Windows (drive or path)
        if (CONST.OS_SYS == "Linux" and
           self.settings["Linux_CIFS_method"] == "gvfs" and
           not self.settings["Linux_gvfs_symlink"]):
            path = None
            for f in os.listdir(CONST.GVFS_DIR):
                if CONST.GVFS_GENERATION == 1:
                    if re.match(r'{server_share} \S+ {server_name}'.format(**self.settings), f):
                        path = os.path.join(CONST.GVFS_DIR, f, self.settings["server_subdir"])
                else:
                    if (re.match(r'^smb-share:', f) and
                       re.search(r'domain={realm_domain}(,|$)'.format(**self.settings), f, flags=re.IGNORECASE) and
                       re.search(r'server={server_name}(,|$)'.format(**self.settings), f) and
                       re.search(r'share={server_share}(,|$)'.format(**self.settings), f) and
                       re.search(r'user={realm_username}(,|$)'.format(**self.settings), f)):
                        path = os.path.join(CONST.GVFS_DIR, f, self.settings["server_subdir"])
            if path is None:
                raise Exception("Error: Could not find the GVFS mountpoint.")
        elif CONST.OS_SYS == "Windows":
            path = self.settings["Windows_letter"]
        else:
            path = self.settings["local_path"]

        cmd = [s.format(path=path) for s in CONST.CMD_OPEN.split(" ")]
        my_print("cmd : %s" % cmd)
        subprocess.call(cmd)


def pexpect_ask_password(values):
    process_question = values["child_result_list"][-1]
    try:
        for pattern, auth_realm in values["extra_args"]["auth_realms"]:
            if re.search(pattern, process_question):
                return values["extra_args"]["key_chain"].get_password(auth_realm) + "\n"
    except CancelOperationException:
        my_print("Operation cancelled.")
        values["extra_args"]["process_meta"]["was_cancelled"] = True
        # Stop current process
        return True


def main_GUI():
    app = QtGui.QApplication(sys.argv)
    ui = UI()
    sys.exit(app.exec_())


def main_CLI():
    my_print("Test app")
    my_print("Detected OS : " + CONST.OS_DISTRIB + " " + CONST.OS_SYS + " " + CONST.OS_VERSION)
    my_print("Local username:" + CONST.LOCAL_USERNAME)
    my_print("Local groupname:" + CONST.LOCAL_GROUPNAME)
    my_print("Local uid:" + str(CONST.LOCAL_UID))
    my_print("Local gid:" + str(CONST.LOCAL_GID))
    my_print("Home dir:" + CONST.HOME_DIR)


if __name__ == '__main__':
    my_print()
    my_print("*"*10 + " " + str(datetime.datetime.now()) + " " + "*"*10)
    main_CLI()
    main_GUI()
