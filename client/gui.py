#!/usr/bin/env python3

# Bancal Samuel

# Offers main GUI

import os
import sys
import pprint
from PyQt4 import QtGui, QtCore
from utility import CONST, Key_Chain, CancelOperationException, Output, validate_username
from cifs_mount import CIFS_Mount
import conf


class UI_Label_Entry(QtGui.QHBoxLayout):

    def __init__(self, label):
        super(UI_Label_Entry, self).__init__()
        self.label = QtGui.QLabel(label)
        self.addWidget(self.label)
        self.addStretch(1)


class UI_Username_Box(QtGui.QWidget):

    def __init__(self, ui, username=None):
        super(UI_Username_Box, self).__init__()
        
        self.ui = ui
        
        # Identified Layout
        identified_hlayout = QtGui.QHBoxLayout()
        self.identified_label = QtGui.QLabel()
        bt_change_username = QtGui.QPushButton("Change user")
        bt_change_username.clicked.connect(self._bt_change_username)
        identified_hlayout.addWidget(self.identified_label)
        identified_hlayout.addStretch(1)
        identified_hlayout.addWidget(bt_change_username)

        self.setLayout(identified_hlayout)
        
        self._set_username(username)
            
    def _set_username(self, username):
        if username is None:
            username = "..."
        self.identified_label.setText("Drives available for username <b>{}</b>".format(username))

    def _save_username(self, username):
        self.ui.switch_username(username)
        self._set_username(username)

    def _bt_change_username(self):
        msg = "Type your EPFL username :"
        while True:
            username, ok = QtGui.QInputDialog.getText(
                self,
                "Define your EPFL username",
                msg,
            )

            if ok:
                validation_answer = validate_username(username)
                if validation_answer == "ok":
                    self._save_username(username)
                    break
                else:
                    msg = "{}.\nType your EPFL username :".format(validation_answer)
            else:
                break


class HLine(QtGui.QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QtGui.QFrame.HLine)
        self.setFrameShadow(QtGui.QFrame.Sunken)


class UI_Mount_Entry(QtGui.QHBoxLayout):

    def __init__(self, ui, mount_instance):
        super(UI_Mount_Entry, self).__init__()

        self.ui = ui
        self.mount_instance = mount_instance

        self.bt_bookmark = QtGui.QPushButton()
        self.bt_bookmark.setGeometry(0, 0, 15, 15)
        self.bt_bookmark.clicked.connect(self.toggle_bookmark)
        self.update_bookmark()
        
        self.label_status = QtGui.QLabel()
        self.label_status.setGeometry(0, 0, 15, 15)

        self.label = QtGui.QLabel(self.mount_instance.settings["label"])
        
        self.win_letter = QtGui.QComboBox()
        self.win_letter.addItem("Z:")
        self.win_letter.addItem("U:")
        self.win_letter.addItem("V:")
        self.win_letter.addItem("R:")
        self.win_letter.addItem("Y:")
        self.win_letter.addItem("X:")
        self.win_letter.addItem("")
        
        self.bt_mount = QtGui.QPushButton("Mount", self.ui)
        self.bt_mount.clicked.connect(self.toggle_mount)
        self.bt_open = QtGui.QPushButton('Open', self.ui)
        self.bt_open.clicked.connect(self.mount_instance.open_file_manager)
        self.addWidget(self.bt_bookmark)
        self.addWidget(self.label_status)
        self.addWidget(self.label)
        self.addStretch(1)
        self.addWidget(self.win_letter)
        self.addWidget(self.bt_mount)
        self.addWidget(self.bt_open)
        self.update_status()

    def toggle_bookmark(self):
        self.mount_instance.settings["bookmark"] = not self.mount_instance.settings["bookmark"]
        conf.save_bookmark(self.mount_instance.settings["name"], self.mount_instance.settings["bookmark"])
        self.update_bookmark()
    
    def update_bookmark(self):
        if self.mount_instance.settings["bookmark"]:
            self.bt_bookmark.setIcon(QtGui.QIcon(CONST.BOOKMARK_ON_PNG))
        else:
            self.bt_bookmark.setIcon(QtGui.QIcon(CONST.BOOKMARK_OFF_PNG))
    
    def toggle_mount(self):
        if self.mount_instance.is_mounted():
            self.mount_instance.umount()
        else:
            self.mount_instance.mount()
        self.update_status()

    def update_status(self):
        if self.mount_instance.is_mounted():
            self.bt_mount.setText("Disconnect")
            self.label_status.setPixmap(QtGui.QPixmap(CONST.MOUNTED_PNG))
            self.bt_open.setEnabled(True)
        else:
            self.bt_mount.setText("Connect")
            self.label_status.setPixmap(QtGui.QPixmap(CONST.UMOUNTED_PNG))
            self.bt_open.setEnabled(False)
    
    def destroy(self):
        """
            This Mount_Entry has to be deleted.
            Happens when switching username.
        """
        self.bt_bookmark.setParent(None)
        self.label_status.setParent(None)
        self.label.setParent(None)
        self.win_letter.setParent(None)
        self.bt_mount.setParent(None)
        self.bt_open.setParent(None)
        self.setParent(None)


class GUI(QtGui.QWidget):

    def __init__(self):
        super(GUI, self).__init__()
        
        self.key_chain = Key_Chain(self)

        self.entries_layer = QtGui.QVBoxLayout()
        self.entries = []
        self.load_config()

        self.username_box = UI_Username_Box(self, self.cfg.get("global", {}).get("username"))
        
        self.bt_quit = QtGui.QPushButton('Quit', self)
        self.bt_quit.clicked.connect(QtGui.qApp.quit)

        self.hbox_bt_quit = QtGui.QHBoxLayout()
        self.hbox_bt_quit.addStretch(1)
        self.hbox_bt_quit.addWidget(self.bt_quit)

        self.vbox_layout = QtGui.QVBoxLayout()
        self.vbox_layout.addWidget(self.username_box)
        self.vbox_layout.addWidget(HLine())
        self.vbox_layout.addLayout(self.entries_layer)
        self.vbox_layout.addWidget(HLine())
        self.vbox_layout.addLayout(self.hbox_bt_quit)

        self.setLayout(self.vbox_layout)
        
        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.timeout.connect(self._refresh_entries)
        self.refresh_timer.start(5000)  # every 5s.

        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle("ENACdrives")
        self.setWindowIcon(QtGui.QIcon(os.path.join(CONST.RESOURCES_DIR, "enacdrives.png")))
        self.show()

    def notify_user(self, msg):
        msgBox = QtGui.QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()
        
    def get_password(self, realm, password_mistyped=False):
        if password_mistyped:
            msg = "Password was mistyped, try again.\nGive your " + realm + " password"
        else:
            msg = "Give your " + realm + " password"
        password, ok = QtGui.QInputDialog.getText(
            self,
            "Please enter a password",
            msg,
            QtGui.QLineEdit.Password,
        )

        if ok:
            return str(password)
        else:
            raise CancelOperationException("Button cancel pressed")

    def _refresh_entries(self):
        for entry in self.entries:
            entry.update_status()
    
    def switch_username(self, username):
        conf.save_username(username)
        self.key_chain.wipe_passwords()
        self.load_config()
    
    def load_config(self):
        self.cfg = conf.get_config()
        Output.write(pprint.pformat(self.cfg))
        
        # Delete previous config
        for entry in self.entries:
            entry.destroy()
        self.entries = []
        
        # Instanciate new config objects
        entries_added = []
        for entry_name in self.cfg["global"].get("entries_order", ()):
            if entry_name in self.cfg["CIFS_mount"]:
                entry = CIFS_Mount(self, self.cfg, entry_name, self.key_chain)
                self.entries.append(UI_Mount_Entry(self, entry))
                entries_added.append(entry_name)
            else:
                Output.write("Warning, Entry not found '{0}'.".format(entry_name))
        for entry_name in self.cfg.get("CIFS_mount", {}):
            if entry_name not in entries_added:
                entry = CIFS_Mount(self, self.cfg, entry_name, self.key_chain)
                self.entries.append(UI_Mount_Entry(self, entry))

        for entry in self.entries:
            self.entries_layer.addLayout(entry)


def main_GUI():
    app = QtGui.QApplication(sys.argv)
    ui = GUI()
    sys.exit(app.exec_())
