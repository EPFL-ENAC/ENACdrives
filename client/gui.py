#!/usr/bin/env python3

# Bancal Samuel

# Offers main GUI

import os
import sys
from PyQt4 import QtGui
from utility import CONST, Key_Chain, CancelOperationException
from cifs_mount import CIFS_Mount


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
        self.bt_open.clicked.connect(self.mount_instance.open_file_manager)
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


class GUI(QtGui.QWidget):

    def __init__(self):
        super(GUI, self).__init__()

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


def main_GUI():
    app = QtGui.QApplication(sys.argv)
    ui = GUI()
    sys.exit(app.exec_())
