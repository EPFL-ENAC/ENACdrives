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
if CONST.OS_SYS == "Windows":
    from win_stack import WindowsLettersManager


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
        self.bt_change_username = QtGui.QPushButton("Change user")
        self.bt_change_username.clicked.connect(self._bt_change_username)
        identified_hlayout.addWidget(self.identified_label)
        identified_hlayout.addStretch(1)
        identified_hlayout.addWidget(self.bt_change_username)

        self.setLayout(identified_hlayout)
        
        self._set_username(username)
    
    def get_widgets_order(self):
        return [self.bt_change_username, ]
            
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
        self.settings = mount_instance.settings

        self.bt_bookmark = QtGui.QPushButton()
        self.bt_bookmark.setGeometry(0, 0, 15, 15)
        self.bt_bookmark.clicked.connect(self.toggle_bookmark)
        self.update_bookmark()
        
        self.label_status = QtGui.QLabel()
        self.label_status.setGeometry(0, 0, 15, 15)

        self.label = QtGui.QLabel(self.settings["label"])
        
        # Windows Letters : Z: -> A:
        if CONST.OS_SYS == "Windows":
            self.possible_win_letters = ["{}:".format(chr(i)) for i in range(90, 64, -1)]
            self.possible_win_letters.insert(0, "")
            self.win_letter = QtGui.QComboBox()
            for l in self.possible_win_letters:
                self.win_letter.addItem(l)
            self.win_letter.setCurrentIndex(self.possible_win_letters.index(self.settings.get("Windows_letter", "")))
            self.win_letter.currentIndexChanged.connect(self.win_letter_changed)
            self.ui.windows_letter_manager.add_mount_entry(self)
        
        self.bt_mount = QtGui.QPushButton("Mount", self.ui)
        self.bt_mount.clicked.connect(self.toggle_mount)
        if CONST.OS_SYS == "Windows" and self.win_letter.currentText() == "":
            self.bt_mount.setEnabled(False)
        self.bt_open = QtGui.QPushButton('Open', self.ui)
        self.bt_open.clicked.connect(self.mount_instance.open_file_manager)
        self.addWidget(self.bt_bookmark)
        self.addWidget(self.label_status)
        self.addWidget(self.label)
        self.addStretch(1)
        if CONST.OS_SYS == "Windows":
            self.addWidget(self.win_letter)
        self.addWidget(self.bt_mount)
        self.addWidget(self.bt_open)
        self.update_status()
    
    def get_widgets_order(self):
        if CONST.OS_SYS == "Windows":
            return [self.bt_bookmark, self.win_letter, self.bt_mount, self.bt_open]
        else:
            return [self.bt_bookmark, self.bt_mount, self.bt_open]

    def win_letter_changed(self):
        self.settings["Windows_letter"] = self.win_letter.currentText()
        conf.save_windows_letter(self.settings["name"], self.win_letter.currentText())
        self.ui.windows_letter_manager.refresh_letters()
        if self.win_letter.currentText() == "":
            self.bt_mount.setEnabled(False)
        else:
            self.bt_mount.setEnabled(True)
    
    def set_disabled_windows_letters(self, l_letters):
        for i, letter in enumerate(self.possible_win_letters):
            if letter in l_letters:
                self.win_letter.model().item(i).setEnabled(False)
            else:
                self.win_letter.model().item(i).setEnabled(True)
            
    def toggle_bookmark(self):
        self.settings["bookmark"] = not self.settings["bookmark"]
        conf.save_bookmark(self.settings["name"], self.settings["bookmark"])
        self.update_bookmark()
    
    def update_bookmark(self):
        if self.settings["bookmark"]:
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
            if CONST.OS_SYS == "Windows":
                self.win_letter.setEnabled(False)
        else:
            self.bt_mount.setText("Connect")
            self.label_status.setPixmap(QtGui.QPixmap(CONST.UMOUNTED_PNG))
            self.bt_open.setEnabled(False)
            if CONST.OS_SYS == "Windows":
                self.win_letter.setEnabled(True)
    
    def destroy(self):
        """
            This Mount_Entry has to be deleted.
            Happens when switching username.
        """
        self.bt_bookmark.setParent(None)
        self.label_status.setParent(None)
        self.label.setParent(None)
        if CONST.OS_SYS == "Windows":
            self.win_letter.setParent(None)
        self.bt_mount.setParent(None)
        self.bt_open.setParent(None)
        self.setParent(None)


class GUI(QtGui.QWidget):

    def __init__(self):
        super(GUI, self).__init__()
        
        self.key_chain = Key_Chain(self)
        if CONST.OS_SYS == "Windows":
            self.windows_letter_manager = WindowsLettersManager()

        self.cfg = None  # set in load_config
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
        self.set_tab_order()
        
        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.timeout.connect(self._refresh_entries)
        self.refresh_timer.start(5000)  # every 5s.

        if CONST.OS_SYS == "Darwin":
            self.setContentsMargins(2, 2, 2, 2)
            self.vbox_layout.setSpacing(0)
            self.vbox_layout.setContentsMargins(0, 0, 0, 0)
        self.setGeometry(300, 300, 200, 100)
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
        if CONST.OS_SYS == "Windows":
            self.windows_letter_manager.refresh_letters()
    
    def switch_username(self, username):
        if CONST.OS_SYS == "Windows":
            self.windows_letter_manager.clear_entries()
        conf.save_username(username)
        self.key_chain.wipe_passwords()
        self.load_config()
        self.set_tab_order()
        self.resize_window_to_minimum()
    
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
        if CONST.OS_SYS == "Windows":
            self.windows_letter_manager.refresh_letters()

        for entry in self.entries:
            self.entries_layer.addLayout(entry)
        
    def set_tab_order(self):
        widgets_ordered = self.username_box.get_widgets_order()
        for entry in self.entries:
            widgets_ordered.extend(entry.get_widgets_order())
        widgets_ordered.append(self.bt_quit)
        
        prev_wid = None
        for wid in widgets_ordered:
            if prev_wid is not None:
                self.setTabOrder(prev_wid, wid)
            prev_wid = wid
    
    def resize_window_to_minimum(self):
        # http://stackoverflow.com/a/28667119/446302
        def _func_to_call():
            self.resize(self.minimumSizeHint())
        QtCore.QTimer.singleShot(500, _func_to_call)


def main_GUI():
    app = QtGui.QApplication(sys.argv)
    ui = GUI()
    sys.exit(app.exec_())
