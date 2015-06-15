#!/usr/bin/env python3

# Bancal Samuel

# Offers main CLI

import sys
import pprint
import getpass
import datetime

import conf
from utility import Output, CONST, Key_Chain
from cifs_mount import CIFS_Mount


class CLI():
    def __init__(self, args):
        self.args = args
        self.key_chain = Key_Chain(self)
        self.cfg = conf.get_config()
        Output.verbose(pprint.pformat(self.cfg))
        
        self.entries = []
        entries_added = []
        for m_name in self.cfg["global"].get("entries_order", ()):
            if m_name in self.cfg["CIFS_mount"]:
                self.entries.append(CIFS_Mount(self, self.cfg, m_name, self.key_chain))
                entries_added.append(m_name)
            else:
                Output.warning("Entry not found '{0}'.".format(m_name))
        for m_name in self.cfg["CIFS_mount"]:
            if m_name not in entries_added:
                self.entries.append(CIFS_Mount(self, self.cfg, m_name, self.key_chain))

    def run(self):
        if self.args.add_bookmark is not None:
            for m_name in self.args.add_bookmark:
                if m_name in self.cfg["CIFS_mount"]:
                    conf.save_bookmark(m_name, True)
                else:
                    Output.warning("Skipping to add bookmark {}: Unknown entry.".format(m_name))

        if self.args.rm_bookmark is not None:
            for m_name in self.args.rm_bookmark:
                if m_name in self.cfg["CIFS_mount"]:
                    conf.save_bookmark(m_name, False)
                else:
                    Output.warning("Skipping to rm bookmark {}: Unknown entry.".format(m_name))

        if self.args.summary:
            self.show_summary()

    def show_summary(self):
        def is_bookmarked(entry):
            if entry.settings["bookmark"]:
                return "\033[01;33m\u272F\033[00m"
            else:
                return " "  # "\u274F"  # "\u274d"

        def is_mounted(entry):
            if entry.is_mounted():
                return "\033[01;32m\u2713\033[00m on {}".format(entry.settings["local_path"])
            else:
                return "\033[01;31m\u2717\033[00m"

        name_width = 1
        label_width = 1
        for entry in self.entries:
            name_width = max(name_width, len(entry.settings["name"]))
            label_width = max(label_width, len(entry.settings["label"]))
        for entry in self.entries:
            Output.cli("{}  \033[00;37m{:<{name_width}}\033[00m  \033[01;37m{:<{label_width}}\033[00m  {}".format(is_bookmarked(entry), entry.settings["name"], entry.settings["label"], is_mounted(entry), name_width=name_width, label_width=label_width))

    def get_password(self, realm, password_mistyped):
        # For Key_Chain
        if password_mistyped:
            Output.cli("Password mistyped. Please re-type '{}' password".format(realm))
        else:
            Output.cli("Please type '{}' password".format(realm))
        return getpass.getpass()
    
    def notify_user(self, msg):
        # For CIFS_Mount
        Output.cli("Notify_user: " + msg)


def main_CLI(args):
    Output.verbose("*"*10 + " " + str(datetime.datetime.now()) + " " + "*"*10)
    Output.verbose("ENACdrives " + CONST.FULL_VERSION)
    Output.verbose("Detected OS : " + CONST.OS_DISTRIB + " " + CONST.OS_SYS + " " + CONST.OS_VERSION + "\n")
    Output.debug("LOCAL_USERNAME:" + CONST.LOCAL_USERNAME)
    Output.debug("LOCAL_GROUPNAME:" + CONST.LOCAL_GROUPNAME)
    Output.debug("LOCAL_UID:" + str(CONST.LOCAL_UID))
    Output.debug("LOCAL_GID:" + str(CONST.LOCAL_GID))
    Output.debug("HOME_DIR:" + CONST.HOME_DIR)
    Output.debug("USER_CONF_FILE:" + CONST.USER_CONF_FILE)
    Output.debug("RESOURCES_DIR:" + CONST.RESOURCES_DIR + "\n")
    
    ui = CLI(args)
    sys.exit(ui.run())
    
