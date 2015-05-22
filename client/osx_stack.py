#!/usr/bin/env python3

# Bancal Samuel

# Offers Mac OSX stack for :
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
from utility import Output, which, CancelOperationException


class OSX_CONST():
    CMD_OPEN = which("open") + " -a Finder {path}"
    
    CMD_MOUNT_SMBFS = which("mount_smbfs")
    CMD_UMOUNT = which("umount")


def cifs_is_mounted(mount):
    # This may hang if no network or VPN is missing
    # Problem is fixed by not checking is_mounted if not network present
    Output.write("TODO WARNING. os.path.ismount in osx_stack.cifs_is_mounted")
    return os.path.ismount(mount.settings["local_path"])


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
    cmd = [
        OSX_CONST.CMD_MOUNT_SMBFS,
        r"//{realm_domain}\;{realm_username}@{server_name}/{server_path} {local_path}".format(**mount.settings)
    ]
    Output.write("cmd : %s" % cmd)
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
                timeout=5,
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
                        Output.write("Warning, could not rmdir : {}".format(e))
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
    cmd = [OSX_CONST.CMD_UMOUNT, mount.settings["local_path"]]
    Output.write("cmd : %s" % cmd)
    Output.write("TODO WARNING. subprocess.Popen in osx_stack.cifs_umount")
    subproc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = subproc.communicate()

    if subproc.returncode != 0:
        raise Exception("Error while umounting : %s\n%s" % (stdout, stderr))


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
            Output.write("Warning, could not rmdir : {0}".format(e))


def open_file_manager(mount):
    path = mount.settings["local_path"]
    cmd = [s.format(path=path) for s in OSX_CONST.CMD_OPEN.split(" ")]
    Output.write("cmd : %s" % cmd)
    Output.write("TODO WARNING. subprocess.call in osx_stack.open_file_manager")
    subprocess.call(cmd)


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
        Output.write("Operation cancelled.")
        values["extra_args"]["process_meta"]["was_cancelled"] = True
        # Stop current process
        return True
