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
import sys
import getpass
import platform
from PyQt4 import QtGui
try:
    import grp
    import pwd
except ImportError: # for Windows
    pass

class CONST():
    
    OS_SYS = platform.system()
    if OS_SYS == "Linux":
        DISTRIB, OS_VERSION = platform.linux_distribution()[:2]
        OS_SYS = DISTRIB + " " + OS_SYS
    elif OS_SYS == "Darwin":
        OS_VERSION = platform.mac_ver()[0]
    elif OS_SYS == "Windows":
        OS_VERSION = platform.win32_ver()[0]
    else:
        OS_VERSION = "Error: OS not supported."

    LOCAL_USERNAME = getpass.getuser()
    HOME_DIR = os.path.expanduser("~")
    if OS_SYS != "Windows":
        LOCAL_GROUPNAME = grp.getgrgid(pwd.getpwnam(LOCAL_USERNAME).pw_gid).gr_name
        LOCAL_UID = pwd.getpwnam(LOCAL_USERNAME)[2]
        LOCAL_GID = pwd.getpwnam(LOCAL_USERNAME)[3]
    else:
        LOCAL_GROUPNAME = "Undefined"
        LOCAL_UID = -1
        LOCAL_GID = -1


class UI_Entry(QtGui.QHBoxLayout):

    def __init__(self, label, value):
        super(UI_Entry, self).__init__()
        self.label = QtGui.QLabel(label)
        self.value = QtGui.QLabel(value)
        self.addWidget(self.label)
        self.addWidget(self.value)
        self.addStretch(1)

class UI(QtGui.QWidget):
    
    def __init__(self):
        super(UI, self).__init__()

        self.entries = []
        
        self.entries.append(UI_Entry(
            "OS:",
            CONST.OS_SYS + " " + CONST.OS_VERSION
        ))
        
        self.entries.append(UI_Entry(
            "Local username:",
            CONST.LOCAL_USERNAME
        ))
        
        self.entries.append(UI_Entry(
            "Local groupname:",
            CONST.LOCAL_GROUPNAME
        ))
        
        self.entries.append(UI_Entry(
            "Local uid:",
            str(CONST.LOCAL_UID)
        ))
        
        self.entries.append(UI_Entry(
            "Local gid:",
            str(CONST.LOCAL_GID)
        ))
        
        self.entries.append(UI_Entry(
            "Home dir:",
            CONST.HOME_DIR
        ))
        
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

def main_GUI():
    app = QtGui.QApplication(sys.argv)
    ui = UI()
    sys.exit(app.exec_())

def main_CLI():
    print("Test app")
    print("Detected OS : " + CONST.OS_SYS + " " + CONST.OS_VERSION)
    print("Local username:", CONST.LOCAL_USERNAME)
    print("Local groupname:", CONST.LOCAL_GROUPNAME)
    print("Local uid:", str(CONST.LOCAL_UID))
    print("Local gid:", str(CONST.LOCAL_GID))
    print("Home dir:", CONST.HOME_DIR)

if __name__ == '__main__':
    main_CLI()
    main_GUI()