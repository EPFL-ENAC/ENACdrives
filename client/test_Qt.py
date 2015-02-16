#!/usr/bin/env python3

# Bancal Samuel

# Constraints :

# + Windows :
#   + WinPython-32bit-3.4.2.4 comes with PyQt4 (not PyQt5)
# 
# + Linux :
#   + . venv_py3/bin/activate
#   + export PYTHONPATH=/usr/lib/python3/dist-packages
# 
# + MacOSX :
# 

import os
import re
import gc
import sys
import time
import pexpect
import getpass
import platform
import datetime
import subprocess
from PyQt4 import QtGui
try:
    import grp
    import pwd
except ImportError: # for Windows
    pass


# Tools

def which(program):
    """
        from http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/377028#377028
    """
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
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
    
    OS_SYS = platform.system()
    LOCAL_USERNAME = getpass.getuser()
    HOME_DIR = os.path.expanduser("~")
    if OS_SYS == "Linux":
        OS_DISTRIB, OS_VERSION = platform.linux_distribution()[:2]
        LOCAL_GROUPNAME = grp.getgrgid(pwd.getpwnam(LOCAL_USERNAME).pw_gid).gr_name
        LOCAL_UID = pwd.getpwnam(LOCAL_USERNAME)[2]
        LOCAL_GID = pwd.getpwnam(LOCAL_USERNAME)[3]
        try:
            DESKTOP_DIR = subprocess.check_output(["xdg-user-dir", "DESKTOP"]).decode().strip()
        except FileNotFoundError:
            DESKTOP_DIR = HOME_DIR + "/Desktop"
        DEFAULT_MNT_DIR = DESKTOP_DIR # Should be overwritten from conf file
        DEFAULT_OPEN_CMD = which("xdg-open") + " {path}"
        GVFS_MOUNT = which("gvfs-mount")
    elif OS_SYS == "Darwin":
        OS_DISTRIB = "Apple"
        OS_VERSION = platform.mac_ver()[0]
        LOCAL_GROUPNAME = grp.getgrgid(pwd.getpwnam(LOCAL_USERNAME).pw_gid).gr_name
        LOCAL_UID = pwd.getpwnam(LOCAL_USERNAME)[2]
        LOCAL_GID = pwd.getpwnam(LOCAL_USERNAME)[3]
        DESKTOP_DIR = HOME_DIR + "/Desktop"
        DEFAULT_MNT_DIR = DESKTOP_DIR
        DEFAULT_OPEN_CMD = which("open") + " -a Finder {path}"
    elif OS_SYS == "Windows":
        OS_DISTRIB = "Microsoft"
        OS_VERSION = platform.win32_ver()[0]
        LOCAL_GROUPNAME = "Undefined"
        LOCAL_UID = -1
        LOCAL_GID = -1
        DESKTOP_DIR = HOME_DIR + "/Desktop" # TO DO
        DEFAULT_MNT_DIR = DESKTOP_DIR # TO DO
        DEFAULT_OPEN_CMD = which("TO DO") + " {path}"
    else:
        OS_VERSION = "Error: OS not supported."
    

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
        
        self.entries.append(UI_Label_Entry(
            "OS:" + CONST.OS_DISTRIB + " " + CONST.OS_SYS + " " + CONST.OS_VERSION
        ))
        
        self.entries.append(UI_Label_Entry(
            "Local username:" + CONST.LOCAL_USERNAME
        ))
        
        self.entries.append(UI_Label_Entry(
            "Local groupname:" + CONST.LOCAL_GROUPNAME
        ))
        
        self.entries.append(UI_Label_Entry(
            "Local uid:" + str(CONST.LOCAL_UID)
        ))
        
        self.entries.append(UI_Label_Entry(
            "Local gid:" + str(CONST.LOCAL_GID)
        ))
        
        self.entries.append(UI_Label_Entry(
            "Home dir:" + CONST.HOME_DIR
        ))
        
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
        self.setWindowIcon(QtGui.QIcon("mount_filers.png"))
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


class Key_Chain():
    """
        Holds the passwords entered diring the execution time.
    """

    def __init__(self, ui):
        self.ui = ui
        self.keys = {}

    def get_password(self, realm):
        import pprint
        print(type(realm))
        pprint.pprint(realm)
        if realm in self.keys:
            for _ in range(3):
                if self.keys[realm]["ack"]:
                    return self.keys[realm]["pw"]
                time.sleep(1)
        password = self.ui.get_password(realm)
        self.keys[realm] = {
            "ack":False,
            "pw":password,
        }
        return self.keys[realm]["pw"]

    def ack_password(self, realm):
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
        # No valid entry found, creating one.
        output = subprocess.check_output(cmd).decode()
        cls.cache[str_cmd] = {
            "expire_dt":datetime.datetime.now() + Live_Cache.CACHE_DURATION,
            "value":output,
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
        * Linux_mount.cifs_filemode = filemode setting to use with mount.cifs method
        * Linux_mount.cifs_dirmode  = dirmode setting to use with mount.cifs method
        * Linux_mount.cifs_options = options to use with mount.cifs method
        * Linux_gvfs_symlink = boolean
            Enables the creation of a symbolic link to "local_path" after mount with gvfs method.
            default : True
        * Windows_letter = letter
            Drive letter to use for the mount (only on Windows)
    """

    def __init__(self, ui, key_chain):
        self.settings = {
            "name":"private",
            "label":"bancal@files9 (individuel)",
            "realm":"EPFL",
            "server_name":"files9.epfl.ch",
            "server_path":"data/bancal",
            "local_path":"{MNT_DIR}/bancal_on_files9",
            "stared":False,
            "Linux_CIFS_method":"gvfs",
            "Linux_mount.cifs_filemode":"0770",
            "Linux_mount.cifs_dirmode":"0770",
            "Linux_mount.cifs_options":"rw,nobrl,noserverino,iocharset=utf8,sec=ntlm",
            "Linux_gvfs_symlink":True,
            "Windows_letter":"Z:",
        }
        self.settings["local_path"] = self.settings["local_path"].format(
            MNT_DIR=CONST.DEFAULT_MNT_DIR,
            HOME_DIR=CONST.HOME_DIR,
            DESKTOP_DIR=CONST.DESKTOP_DIR,
            LOCAL_USERNAME=CONST.LOCAL_USERNAME,
            LOCAL_GROUPNAME=CONST.LOCAL_GROUPNAME,
        )
        self.settings["server_share"], self.settings["server_subdir"] = re.match(r"([^/]+)/?(.*)$", self.settings["server_path"]).groups()
        self.settings["realm_domain"] = "INTRANET"
        self.settings["realm_username"] = "bancal"
        self.ui = ui
        self.key_chain = key_chain
    
    def is_mounted(self):
        if CONST.OS_SYS == "Linux":
            if self.settings["Linux_CIFS_method"] == "gvfs":
                cmd = [CONST.GVFS_MOUNT, "-l"]
                print(" ".join(cmd))
                lines = Live_Cache.subprocess_check_output(cmd)
                i_search = r"{server_share} .+ {server_name} -> smb://{realm_domain};{realm_username}@{server_name}/{server_share}".format(**self.settings)
                for l in lines.split("\n"):
                    if re.search(i_search, l):
                        print(l)
                        return True
            else: # "mount.cifs"
                return os.path.ismount(self.settings["local_path"])
        elif CONST.OS_SYS == "Windows":
            return os.path.ismount(self.settings["Windows_letter"])
        elif CONST.OS_SYS == "Darwin":
            return os.path.ismount(self.settings["local_path"])
        else:
            raise Exception("Unknown System " + CONST.OS_SYS)
        return False

    def mount(self):
        if CONST.OS_SYS == "Linux":
            if self.settings["Linux_CIFS_method"] == "gvfs":
                cmd = [CONST.GVFS_MOUNT, r"smb://{realm_domain}\;{realm_username}@{server_name}/{server_share}".format(**self.settings)]
                print(" ".join(cmd))
                # print(type(self.pexpect_ask_password))
                # import types
                # print(isinstance(self.pexpect_ask_password, types.FunctionType))
                # sys.exit(0)
                try:
                    (output, exit_status) = pexpect.runu(
                        command=" ".join(cmd),
                        events={
                            'Password:':pexpect_ask_password,
                        },
                        extra_args={
                            "auth_realms":[
                                (r'Password:', self.settings["realm"])
                            ],
                            "key_chain":self.key_chain,
                            # "context" : "gvfs_mount_%s" % self.settings["name"]
                        },
                        withexitstatus=True,
                        timeout=5,
                    )
                except pexpect.ExceptionPexpect as exc:
                    raise Exception("Error while mounting : %s" % exc.value)
                if exit_status == 0:
                    self.key_chain.ack_password(self.settings["realm"])
                else:
                    raise Exception("Error while mounting : %s" % output)
                Live_Cache.invalidate_cmd_cache([CONST.GVFS_MOUNT, "-l"])

            else: # "mount.cifs"
                pass # TO DO
        elif CONST.OS_SYS == "Windows":
            pass # TO DO
        elif CONST.OS_SYS == "Darwin":
            pass # TO DO
        else:
            raise Exception("Unknown System " + CONST.OS_SYS)
        return False

    def umount(self):
        if CONST.OS_SYS == "Linux":
            if self.settings["Linux_CIFS_method"] == "gvfs":
                cmd = [CONST.GVFS_MOUNT, "-u", r"smb://{realm_domain};{realm_username}@{server_name}/{server_share}".format(**self.settings)]
                print(" ".join(cmd))
                try:
                    output = subprocess.check_output(cmd)
                except subprocess.CalledProcessError as e:
                    raise Exception("Error (%s) while umounting : %s" % (e.returncode, e.output.decode()))
                Live_Cache.invalidate_cmd_cache([CONST.GVFS_MOUNT, "-l"])
            else: # "mount.cifs"
                pass # TO DO
        elif CONST.OS_SYS == "Windows":
            pass # TO DO
        elif CONST.OS_SYS == "Darwin":
            pass # TO DO
        else:
            raise Exception("Unknown System " + CONST.OS_SYS)
        return False

    def open(self):
        # TO DO : if gvfs and no symlink
        # TO DO : if Windows (drive or path)
        subprocess.call(CONST.DEFAULT_OPEN_CMD.format(
            path=self.settings["local_path"]
        ))
        
def pexpect_ask_password(values):
    # print("pexpect_ask_password")
    process_question = values["child_result_list"][-1]
    # print(" process_question=" + process_question)
    for pattern, auth_realm in values["extra_args"]["auth_realms"]:
        if re.search(pattern, process_question):
            # print(" pattern=" + pattern + " auth_realm=" + auth_realm + " MATCHED!")
            return values["extra_args"]["key_chain"].get_password(auth_realm) + "\n"
        # else:
        #     print(" pattern=" + pattern + " auth_realm=" + auth_realm + " not matched!")

def main_GUI():
    app = QtGui.QApplication(sys.argv)
    ui = UI()
    sys.exit(app.exec_())

def main_CLI():
    print("Test app")
    print("Detected OS : " + CONST.OS_DISTRIB + " " + CONST.OS_SYS + " " + CONST.OS_VERSION)
    print("Local username:", CONST.LOCAL_USERNAME)
    print("Local groupname:", CONST.LOCAL_GROUPNAME)
    print("Local uid:", str(CONST.LOCAL_UID))
    print("Local gid:", str(CONST.LOCAL_GID))
    print("Home dir:", CONST.HOME_DIR)

if __name__ == '__main__':
    main_CLI()
    main_GUI()