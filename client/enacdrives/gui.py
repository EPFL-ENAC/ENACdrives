#!/usr/bin/env python3

# Bancal Samuel

# Offers main GUI

import sys
import pprint
import datetime
import webbrowser
from PyQt5 import QtGui, QtCore, QtWidgets
from utility import CONST, Key_Chain, CancelOperationException, Output, validate_username, validate_release_number, Networks_Check, enacit1logs_notify
from cifs_mount import CIFS_Mount
import conf
if CONST.OS_SYS == "Linux":
    from lin_stack import os_check
elif CONST.OS_SYS == "Windows":
    from win_stack import WindowsLettersManager, os_check
elif CONST.OS_SYS == "Darwin":
    from osx_stack import os_check


class Unsupported_OS(QtWidgets.QHBoxLayout):

    def __init__(self, os):
        super(Unsupported_OS, self).__init__()
        error_png = QtWidgets.QLabel()
        error_png.setGeometry(0, 0, 48, 48)
        error_png.setPixmap(QtGui.QPixmap(CONST.WARNING_PNG_48))
        label = QtWidgets.QLabel(
            "We're sorry but ENACdrives is not supported on {}. See <a href='{}'>full documentation</a>.".format(os, CONST.DOC_URL),
            openExternalLinks=True)
        self.addWidget(error_png)
        self.addWidget(label)
        self.addStretch(1)


class UI_Download_New_Release(QtWidgets.QWidget):

    def __init__(self):
        super(UI_Download_New_Release, self).__init__()

        hlayout = QtWidgets.QHBoxLayout()
        warning_png = QtWidgets.QLabel()
        warning_png.setGeometry(0, 0, 48, 48)
        warning_png.setPixmap(QtGui.QPixmap(CONST.WARNING_PNG_48))
        label = QtWidgets.QLabel(CONST.NEED_TO_UPDATE_MSG, openExternalLinks=True)
        # label.setStyleSheet("QLabel {color : red;}")
        hlayout.addWidget(warning_png)
        hlayout.addWidget(label)
        hlayout.addStretch(1)
        self.setLayout(hlayout)

class UI_Msg(QtWidgets.QWidget):

    ICONS = {
        "none": CONST.MSG_PNG_48,
        "info": CONST.INFO_PNG_48,
        "warning": CONST.WARNING_PNG_48,
        "critical": CONST.CRITICAL_PNG_48,
    }
    def __init__(self, text, icon):
        super(UI_Msg, self).__init__()

        self.hlayout = QtWidgets.QHBoxLayout()
        self.icon_png = QtWidgets.QLabel()
        self.icon_png.setGeometry(0, 0, 48, 48)
        self.icon_png.setPixmap(QtGui.QPixmap(UI_Msg.ICONS.get(icon, "transp")))
        self.label = QtWidgets.QLabel(text, openExternalLinks=True)
        self.hlayout.addWidget(self.icon_png)
        self.hlayout.addWidget(self.label)
        self.hlayout.addStretch(1)
        self.setLayout(self.hlayout)

    def destroy(self):
        """
            This Msg has to be deleted.
            Happens when switching username.
        """
        self.icon_png.setParent(None)
        self.label.setParent(None)
        self.hlayout.setParent(None)
        self.setParent(None)


class UI_Username_Box(QtWidgets.QWidget):

    def __init__(self, ui, username=None):
        super(UI_Username_Box, self).__init__()

        self.ui = ui

        # Identified Layout
        identified_hlayout = QtWidgets.QHBoxLayout()
        self.identified_label = QtWidgets.QLabel()
        self.bt_change_username = QtWidgets.QPushButton("Define user")
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
        else:
            self.bt_change_username.setText("Change user")
        self.identified_label.setText("Drives available for username <b>{}</b>".format(username))

    def _save_username(self, username):
        self.ui.switch_username(username)
        self._set_username(username)

    def _bt_change_username(self):
        msg = "Type your EPFL username :"
        while True:
            username, ok = QtWidgets.QInputDialog.getText(
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


class HLine(QtWidgets.QFrame):
    def __init__(self):
        super(HLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class UI_Mount_Entry(QtWidgets.QHBoxLayout):

    def __init__(self, ui, mount_instance):
        super(UI_Mount_Entry, self).__init__()

        self.ui = ui
        self.mount_instance = mount_instance
        self.settings = mount_instance.settings

        self.bt_bookmark = QtWidgets.QPushButton()
        self.bt_bookmark.setGeometry(0, 0, 15, 15)
        self.bt_bookmark.clicked.connect(self.toggle_bookmark)
        self.update_bookmark()

        self.label_status = QtWidgets.QLabel()
        self.label_status.setGeometry(0, 0, 15, 15)

        self.label = QtWidgets.QLabel(self.settings["label"])

        # Windows Letters : Z: -> A:
        if CONST.OS_SYS == "Windows":
            self.possible_win_letters = ["{}:".format(chr(i)) for i in range(90, 64, -1)]
            self.possible_win_letters.insert(0, "")
            self.win_letter = QtWidgets.QComboBox()
            for l in self.possible_win_letters:
                self.win_letter.addItem(l)
            self.win_letter.setCurrentIndex(self.possible_win_letters.index(self.settings.get("Windows_letter", "")))
            self.win_letter.currentIndexChanged.connect(self.win_letter_changed)
            self.ui.windows_letter_manager.add_mount_entry(self)

        self.bt_mount = QtWidgets.QPushButton("Mount", self.ui)
        self.bt_mount.clicked.connect(self.toggle_mount)
        if CONST.OS_SYS == "Windows" and self.win_letter.currentText() == "":
            self.bt_mount.setEnabled(False)
        self.bt_open = QtWidgets.QPushButton("Open", self.ui)
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
        def _cb(is_mounted):
            # Output.debug("gui._cb")
            if is_mounted:
                self.mount_instance.umount()
            else:
                self.mount_instance.mount()
            self.update_status()

        # Output.debug("gui.toggle_mount")
        self.mount_instance.is_mounted(_cb)

    def update_status(self):
        def _cb(is_mounted):
            if is_mounted:
                self.bt_mount.setText("Disconnect")
                self.label_status.setPixmap(QtGui.QPixmap(CONST.MOUNTED_PNG))
                self.label_status.setToolTip("Connected")
                self.label.setToolTip("Connected")
                self.bt_open.setEnabled(True)
                if CONST.OS_SYS == "Windows":
                    self.win_letter.setEnabled(False)
                    self.win_letter.setCurrentIndex(self.possible_win_letters.index(self.settings.get("Windows_letter", "")))
            else:
                self.bt_mount.setText("Connect")
                self.label_status.setPixmap(QtGui.QPixmap(CONST.UMOUNTED_PNG))
                self.label_status.setToolTip("Not connected")
                self.label.setToolTip("Not connected")
                self.bt_open.setEnabled(False)
                if CONST.OS_SYS == "Windows":
                    self.win_letter.setEnabled(True)

        network_present = True
        required_network = self.settings.get("require_network")
        if required_network is not None:
            status, msg = self.ui.networks_check.get_status(required_network)
            if status is False:
                self.label_status.setPixmap(QtGui.QPixmap(CONST.WARNING_PNG))
                self.label_status.setToolTip(msg)
                self.label.setToolTip(msg)
                network_present = False
                self.bt_mount.setEnabled(False)
                self.bt_open.setEnabled(False)

        if network_present:
            if CONST.OS_SYS != "Windows" or self.win_letter.currentText() != "":
                self.bt_mount.setEnabled(True)
            self.mount_instance.is_mounted(_cb)

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


class GUI(QtWidgets.QMainWindow):
    UI_TYPE = "GUI"

    def __init__(self):
        super(GUI, self).__init__()

        now = datetime.datetime.now()

        self.key_chain = Key_Chain(self)
        if CONST.OS_SYS == "Windows":
            self.windows_letter_manager = WindowsLettersManager()

        self.networks_check = None  # set in load_config
        self.cfg = None  # set in load_config
        self.entries_layer = QtWidgets.QVBoxLayout()
        self.entries = []
        self.msgs_layout = QtWidgets.QVBoxLayout()
        self.msgs = []
        self.load_config()

        self.username_box = UI_Username_Box(self, self.cfg.get("global", {}).get("username"))

        self.vbox_layout = QtWidgets.QVBoxLayout()
        if not validate_release_number():
            self.vbox_layout.addWidget(UI_Download_New_Release())
        self.vbox_layout.addLayout(self.msgs_layout)
        self.vbox_layout.addWidget(self.username_box)
        self.vbox_layout.addWidget(HLine())
        self.vbox_layout.addLayout(self.entries_layer)

        # File > Quit
        quit_action = QtWidgets.QAction("&Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.setStatusTip("Quit ENACdrives")
        quit_action.triggered.connect(QtWidgets.qApp.quit)
        # Help > About
        about_action = QtWidgets.QAction("&About", self)
        about_action.setShortcut("Ctrl+?")
        about_action.setStatusTip("About ENACdrives")
        about_action.triggered.connect(self.show_about)
        # Help > Documentation
        doc_action = QtWidgets.QAction("Web &documentation", self)
        # doc_action.setShortcut("Ctrl+?")
        doc_action.setStatusTip("ENACdrives web documentation")
        doc_action.triggered.connect(self.show_web_documentation)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(quit_action)
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(about_action)
        help_menu.addAction(doc_action)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(self.vbox_layout)
        self.setCentralWidget(central_widget)
        self.set_tab_order()

        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.timeout.connect(self._refresh_entries)
        self.regular_refresh_upto = now + CONST.GUI_FOCUS_LOST_STILL_FULL_REFRESH
        self.last_refresh_dt = now
        self.refresh_timer.start(CONST.GUI_FOCUS_REFRESH_INTERVAL.seconds * 1000)  # every 3s.

        os_check(self)

        if CONST.OS_SYS == "Darwin":
            self.setContentsMargins(2, 2, 2, 2)
            self.vbox_layout.setSpacing(0)
            self.vbox_layout.setContentsMargins(0, 0, 0, 0)
        self.setGeometry(300, 300, 200, 100)
        self.setWindowTitle("ENACdrives")
        self.setWindowIcon(QtGui.QIcon(CONST.ENACDRIVES_PNG))
        self.show()
        enacit1logs_notify(self)

    def notify_user(self, msg):
        Output.normal("Notified User: " + msg)
        msgBox = QtWidgets.QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()

    def get_password(self, realm, password_mistyped=False):
        if password_mistyped:
            msg = "Password was mistyped, try again.<br>Give your <b>{}</b> password".format(realm)
        else:
            msg = "Give your <b>{}</b> password".format(realm)
        password, ok = QtWidgets.QInputDialog.getText(
            self,
            "Please enter a password",
            msg,
            QtWidgets.QLineEdit.Password,
        )

        if ok:
            return str(password)
        else:
            raise CancelOperationException("Button cancel pressed")

    def _refresh_entries(self):
        now = datetime.datetime.now()
        if self.isActiveWindow():
            self.regular_refresh_upto = now + CONST.GUI_FOCUS_LOST_STILL_FULL_REFRESH
        elif (self.regular_refresh_upto < now and
              self.last_refresh_dt + CONST.GUI_NOFOCUS_REFRESH_INTERVAL > now):
            return
        self.last_refresh_dt = now
        self.networks_check.scan()
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
        self.networks_check = Networks_Check(self.cfg, self)
        Output.verbose(pprint.pformat(self.cfg))

        # Delete previous config
        for entry in self.entries:
            entry.destroy()
        self.entries = []

        for msg in self.msgs:
            msg.destroy()
        self.msgs = []

        # Instanciate new config objects
        entries_added = []
        for entry_name in self.cfg["global"].get("entries_order", ()):
            if entry_name in self.cfg["CIFS_mount"]:
                entry = CIFS_Mount(self, self.cfg, entry_name, self.key_chain)
                self.entries.append(UI_Mount_Entry(self, entry))
                entries_added.append(entry_name)
            else:
                Output.warning("Entry not found '{0}'.".format(entry_name))
        for entry_name in self.cfg.get("CIFS_mount", {}):
            if entry_name not in entries_added:
                entry = CIFS_Mount(self, self.cfg, entry_name, self.key_chain)
                self.entries.append(UI_Mount_Entry(self, entry))
        if CONST.OS_SYS == "Windows":
            self.windows_letter_manager.refresh_letters()

        for entry in self.entries:
            self.entries_layer.addLayout(entry)

        for msg in self.cfg["msg"]:
            msg_item = UI_Msg(self.cfg["msg"][msg]["text"], self.cfg["msg"][msg]["icon"])
            self.msgs.append(msg_item)
            self.msgs_layout.addWidget(msg_item)

    def set_tab_order(self):
        widgets_ordered = self.username_box.get_widgets_order()
        for entry in self.entries:
            widgets_ordered.extend(entry.get_widgets_order())

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

    def show_about(self):
        msg = """\
<h2> ENACdrives version : <b>{}</b> ({}) </h2>

<div>
A project developped and brought to you by ENAC-IT @ EPFL
</div>

<h3> Project team : </h3>
<ul>
    <li>Samuel Bancal</li>
    <li>Paulo De Jesus</li>
    <li>Nicolas Dubois</li>
</ul>

<h3> Fellow team members : </h3>
<ul>
    <li>Jean-Daniel Bonjour</li>
    <li>Stefano Nepa</li>
</ul>

<h3> Technologies used : </h3>
<ul>
<li>client side: Python3, PyQt5, pexpect</li>
<li>server side: Python3, Django</li>
</ul>

License : pending ...
""".format(CONST.VERSION, CONST.VERSION_DATE)
        about_box = QtWidgets.QMessageBox()
        about_box.setIconPixmap(QtGui.QPixmap(CONST.ENACDRIVES_PNG))
        about_box.setText(msg)
        about_box.setStyleSheet("width: 800px;")
        about_box.exec_()

    def show_web_documentation(self):
        webbrowser.open(CONST.DOC_URL)


def main_GUI():
    Output.verbose("*"*10 + " " + str(datetime.datetime.now()) + " " + "*"*10)
    Output.verbose("ENACdrives " + CONST.FULL_VERSION)
    Output.verbose("Detected OS : " + CONST.OS_DISTRIB + " " + CONST.OS_SYS + " " + CONST.OS_VERSION)
    Output.debug("LOCAL_USERNAME:" + CONST.LOCAL_USERNAME)
    Output.debug("LOCAL_GROUPNAME:" + CONST.LOCAL_GROUPNAME)
    Output.debug("LOCAL_UID:" + str(CONST.LOCAL_UID))
    Output.debug("LOCAL_GID:" + str(CONST.LOCAL_GID))
    Output.debug("HOME_DIR:" + CONST.HOME_DIR)
    Output.debug("USER_CONF_FILE:" + CONST.USER_CONF_FILE)
    Output.debug("RESOURCES_DIR:" + CONST.RESOURCES_DIR)
    Output.debug("IMAGES_DIR:" + CONST.IMAGES_DIR + "\n")
    Output.debug("DEFAULT_MNT_DIR:" + CONST.DEFAULT_MNT_DIR + "\n")
    Output.br()

    app = QtWidgets.QApplication(sys.argv)
    ui = GUI()
    sys.exit(app.exec_())
