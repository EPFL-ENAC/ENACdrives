#!/usr/bin/env python3

# Bancal Samuel

# Offers main CLI

import sys
import pprint
import getpass
import datetime

import conf
from utility import Output, CONST, Key_Chain, validate_username
from cifs_mount import CIFS_Mount


class CLI():
    UI_TYPE = "CLI"

    def __init__(self, args):
        self.args = args
        self.key_chain = Key_Chain(self)
        
        self.returncode = None
        
        self.set_username(args)
        self.cfg = conf.get_config()
        Output.verbose(pprint.pformat(self.cfg))
        
        self.entries = []
        already_added = []
        for m_name in self.cfg["global"].get("entries_order", ()):
            if m_name in self.cfg["CIFS_mount"]:
                entry = CIFS_Mount(self, self.cfg, m_name, self.key_chain)
                self.entries.append(entry)
                already_added.append(m_name)
                self.cfg["CIFS_mount"][m_name]["entry"] = entry
            else:
                Output.warning("Entry not found '{0}'.".format(m_name))
        for m_name in self.cfg["CIFS_mount"]:
            if m_name not in already_added:
                entry = CIFS_Mount(self, self.cfg, m_name, self.key_chain)
                self.entries.append(entry)
                self.cfg["CIFS_mount"][m_name]["entry"] = entry
        

    def set_username(self, args):
        if args.username is not None:
            validation_answer = validate_username(args.username)
            if validation_answer == "ok":
                conf.save_username(args.username)
            else:
                Output.error(validation_answer)
                self.execution_status(2)

    def execution_status(self, returncode):
        if self.returncode is None:
            self.returncode = returncode
        else:
            self.returncode = max(self.returncode, returncode)

    def run(self):
        if self.returncode is not None:
            return self.returncode

        if self.args.add_bookmark is not None:
            self.execution_status(0)
            for m_name in self.args.add_bookmark:
                if m_name in self.cfg["CIFS_mount"]:
                    conf.save_bookmark(m_name, True)
                else:
                    self.execution_status(1)
                    Output.warning("Skipping to add bookmark {}: Unknown entry.".format(m_name))

        if self.args.rm_bookmark is not None:
            self.execution_status(0)
            for m_name in self.args.rm_bookmark:
                if m_name in self.cfg["CIFS_mount"]:
                    conf.save_bookmark(m_name, False)
                else:
                    self.execution_status(1)
                    Output.warning("Skipping to rm bookmark {}: Unknown entry.".format(m_name))

        if self.returncode is not None:
            return self.returncode

        if self.args.summary:
            # print("self.args : {}".format(self.args))
            self.show_summary()
            return 0
        
        which_entries = []
        if self.args.all:
            self.execution_status(0)
            for entry in self.entries:
                which_entries.append(entry)
        if self.args.named is not None:
            self.execution_status(0)
            for m_name in self.args.named:
                if m_name in self.cfg["CIFS_mount"]:
                    which_entries.append(self.cfg["CIFS_mount"][m_name]["entry"])
                else:
                    self.execution_status(1)
                    Output.warning("Skipping named '{}'. Unknown entry.".format(m_name))
        if self.args.bookmarked:
            self.execution_status(0)
            for entry in self.entries:
                if entry.settings["bookmark"]:
                    which_entries.append(entry)
        
        if len(which_entries) == 0:
            self.execution_status(1)
            Output.warning("No entry selected to (u)mount.")
        
        if self.args.umount:
            umount_list = []
            for entry in which_entries:
                if entry.is_mounted():
                    umount_list.append(entry)
            for entry in umount_list:
                print("+ Umounting {}".format(entry.settings["name"]))
                entry.umount()
        else:
            mount_list = []
            for entry in which_entries:
                if not entry.is_mounted():
                    mount_list.append(entry)
            for entry in mount_list:
                print("+ Mounting {}".format(entry.settings["name"]))
                entry.mount()
        self.show_summary()

        return self.returncode

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

        Output.cli("\033[01;37m*** ENACdrives entries summary ***\033[00m")
        name_width = 1
        label_width = 1
        for entry in self.entries:
            name_width = max(name_width, len(entry.settings["name"]))
            label_width = max(label_width, len(entry.settings["label"]))
        for entry in self.entries:
            Output.cli("{}  \033[00;37m{:<{name_width}}\033[00m  \033[01;37m{:<{label_width}}\033[00m  {}".format(is_bookmarked(entry), entry.settings["name"], entry.settings["label"], is_mounted(entry), name_width=name_width, label_width=label_width))
        if len(self.entries) == 0:
            Output.cli("No entry found.")
        if self.cfg["global"].get("username") is None:
            Output.cli("username not defined. You can set it with argument --username=username")
            self.execution_status(1)

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
    
