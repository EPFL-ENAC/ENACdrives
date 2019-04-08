#!/usr/bin/env python3

# Bancal Samuel

# Offers Mac OSX stack for :
# + os_check
# + cifs_is_mount
# + cifs_mount
# + cifs_post_mount
# + cifs_umount
# + cifs_post_umount
# + open_file_manager

import os
import re
import pexpect
import subprocess
from utility import CONST, Output, which, CancelOperationException, NonBlockingQtThread, NonBlockingQtProcess


class OSX_CONST():
    CMD_OPEN = which("open") + " -a Finder \"{path}\""

    CMD_MOUNT_SMBFS = which("mount_smbfs")
    CMD_UMOUNT = which("umount")


def os_check(ui):
    """
    Check that OS has all pre-requisite functionalities
    """
    pass


def cifs_uncache_is_mounted(mount):
    pass


def cifs_is_mounted(mount, cb):
    def _target_mountcifs():
        return os.path.ismount(mount.settings["local_path"])

    NonBlockingQtThread(
        "os.path.ismounted.{}".format(mount.settings["local_path"]),
        _target_mountcifs,
        cb
    )


def cifs_mount(mount):
    # 1) Make mountpoint
    if not os.path.exists(mount.settings["local_path"]):
        try:
            os.makedirs(mount.settings["local_path"])
        except OSError:
            pass
    if not os.path.isdir(mount.settings["local_path"]):
        raise Exception("Error while creating dir : %s" % mount.settings["local_path"])

    # 2) Mount
    s_path = re.sub(r" ", r"%20", mount.settings["server_path"])
    cmd = [
        OSX_CONST.CMD_MOUNT_SMBFS,
        r"//{realm_domain}\;{realm_username}@{server_name}/{s_path}".format(s_path=s_path, **mount.settings),
        "\"{local_path}\"".format(**mount.settings)
    ]
    Output.verbose("cmd: " + " ".join(cmd))
    for _ in range(3):  # 3 attempts (for passwords mistyped)
        process_meta = {
            "was_cancelled": False,
        }
        try:
            (output, exit_status) = pexpect.runu(
                command=" ".join(cmd),
                events={
                    "(?i)password": pexpect_ask_password,
                },
                extra_args={
                    "auth_realms": [
                        (r"Password", mount.settings["realm"])
                    ],
                    "key_chain": mount.key_chain,
                    "process_meta": process_meta,
                },
                env=dict(os.environ, LANG="C", LC_ALL="C"),
                withexitstatus=True,
                timeout=CONST.MOUNT_TIMEOUT,
            )
        except pexpect.ExceptionPexpect as e:
            raise Exception("Error while mounting : %s" % e.value)
        if exit_status == 0:
            mount.key_chain.ack_password(mount.settings["realm"])
            return True
        elif exit_status == 77:  # Bad password
            mount.key_chain.invalidate_if_no_ack_password(mount.settings["realm"])
        else:
            mount.key_chain.invalidate_if_no_ack_password(mount.settings["realm"])
            if process_meta["was_cancelled"]:
                if (os.path.isdir(mount.settings["local_path"]) and
                   os.listdir(mount.settings["local_path"]) == []):
                    try:
                        os.rmdir(mount.settings["local_path"])
                    except OSError as e:
                        Output.warning("Could not rmdir : {}".format(e))
                return False
            else:
                mount.ui.notify_user("Mount failure :<br>{}".format(output))
                return False
    mount.ui.notify_user("Mount failure")


def cifs_post_mount(mount):
    """
    Performs tasks when mount is done.
    May happen some seconds after cifs_mount is completed (OS)
    """
    pass


def cifs_umount(mount):
    def _cb(success, output, exit_code):
        if not success:
            mount.ui.notify_user("Umount failure :<br>{}".format(output))

    cmd = [
        OSX_CONST.CMD_UMOUNT,
        "\"{local_path}\"".format(**mount.settings)
    ]
    Output.verbose("cmd: " + " ".join(cmd))
    NonBlockingQtProcess(
        cmd,
        _cb,
    )


def cifs_post_umount(mount):
    """
    Performs tasks when umount is done.
    May happen some seconds after cifs_umount is completed (OS)
    """
    if (os.path.isdir(mount.settings["local_path"]) and
       os.listdir(mount.settings["local_path"]) == []):
        try:
            os.rmdir(mount.settings["local_path"])
        except OSError as e:
            Output.warning("Could not rmdir : {0}".format(e))


def open_file_manager(mount):
    def _cb(success, output, exit_code):
        pass

    path = mount.settings["local_path"]
    cmd = [s.format(path=path) for s in OSX_CONST.CMD_OPEN.split(" ")]
    Output.verbose("cmd: " + " ".join(cmd))
    NonBlockingQtProcess(
        cmd,
        _cb,
    )


def pexpect_ask_password(values):
    """
        Interact with process when pexpect found a matching string for password question
        It may Ack previously entered password if several password are asked in the same run.

        This is a mirror from lin_stack.pexpect_ask_password
    """
    process_question = values["child_result_list"][-1]
    try:
        for pattern, auth_realm in values["extra_args"]["auth_realms"]:
            if re.search(pattern, process_question):
                if values["extra_args"]["process_meta"].setdefault("previous_auth_realm", None) == None:
                    password_mistyped = False
                elif values["extra_args"]["process_meta"]["previous_auth_realm"] != auth_realm:
                    values["extra_args"]["key_chain"].ack_password(values["extra_args"]["process_meta"]["previous_auth_realm"])
                    password_mistyped = False
                else:
                    password_mistyped = True
                values["extra_args"]["process_meta"]["previous_auth_realm"] = auth_realm
                return values["extra_args"]["key_chain"].get_password(auth_realm, password_mistyped) + "\n"
    except CancelOperationException:
        Output.normal("Operation cancelled.")
        values["extra_args"]["process_meta"]["was_cancelled"] = True
        # Stop current process
        return True
