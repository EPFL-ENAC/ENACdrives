#!/usr/bin/env python3

# Bancal Samuel

# Offers Linux stack for :
# + CIFS (is_mount, mount, umount)
# + open_file_manager

import os
import re
import pexpect
import subprocess
from utility import CONST, Live_Cache, Output, which, CancelOperationException


class LIN_CONST():
    CMD_OPEN = which("xdg-open") + " {path}"

    CMD_MOUNT_CIFS = which("mount.cifs")
    CMD_UMOUNT = which("umount")

    CMD_GVFS_MOUNT = which("gvfs-mount")
    if CONST.OS_VERSION in ("10.04", "10.10", "11.04", "11.10", "12.04"):
        GVFS_GENERATION = 1
        GVFS_DIR = os.path.join(CONST.HOME_DIR, ".gvfs")
    elif CONST.OS_VERSION in ("12.10", "13.04"):
        GVFS_GENERATION = 2
        GVFS_DIR = "/run/user/{0}/gvfs".format(CONST.LOCAL_USERNAME)
    else:
        GVFS_GENERATION = 3
        GVFS_DIR = "/run/user/{0}/gvfs".format(CONST.LOCAL_UID)


def cifs_is_mounted(mount):
    if mount.settings["Linux_CIFS_method"] == "gvfs":
        cmd = [LIN_CONST.CMD_GVFS_MOUNT, "-l"]
        # Output.write(" ".join(cmd))
        lines = Live_Cache.subprocess_check_output(
            cmd,
            env=dict(os.environ, LANG="C", LC_ALL="C"),
        )
        # Output.write("-> gvfs-mount -l : \n{0}\n\n".format(lines))
        i_search = r"{server_share} .+ {server_name} -> smb://{realm_domain};{realm_username}@{server_name}/{server_share}".format(**mount.settings)
        for l in lines.split("\n"):
            if re.search(i_search, l):
                # Output.write(l)
                return True
    else:  # "mount.cifs"
        return os.path.ismount(mount.settings["local_path"])


def cifs_mount(mount):
    if mount.settings["Linux_CIFS_method"] == "gvfs":
        # 1) Remove broken symlink or empty dir
        if mount.settings["Linux_gvfs_symlink"]:
            if (os.path.lexists(mount.settings["local_path"]) and
               not os.path.exists(mount.settings["local_path"])):
                os.unlink(mount.settings["local_path"])
            if (os.path.isdir(mount.settings["local_path"]) and
               os.listdir(mount.settings["local_path"]) == []):
                os.rmdir(mount.settings["local_path"])
            if os.path.exists(mount.settings["local_path"]):
                raise Exception("Error : Path %s already exists" % mount.settings["local_path"])

        # 2) Mount
        cmd = [LIN_CONST.CMD_GVFS_MOUNT, r"smb://{realm_domain}\;{realm_username}@{server_name}/{server_share}".format(**mount.settings)]
        Output.write(" ".join(cmd))
        process_meta = {
            "was_cancelled": False,
        }
        try:
            (output, exit_status) = pexpect.runu(
                command=" ".join(cmd),
                events={
                    "Password:": pexpect_ask_password,
                },
                extra_args={
                    "auth_realms": [
                        (r"Password:", mount.settings["realm"])
                    ],
                    "key_chain": mount.key_chain,
                    "process_meta": process_meta,
                },
                env=dict(os.environ, LANG="C", LC_ALL="C"),
                withexitstatus=True,
                timeout=5,
            )
        except pexpect.ExceptionPexpect as exc:
            raise Exception("Error while mounting : %s" % exc.value)
        if exit_status == 0:
            mount.key_chain.ack_password(mount.settings["realm"])
        else:
            mount.key_chain.invalidate_if_no_ack_password(mount.settings["realm"])
            if process_meta["was_cancelled"]:
                return False
            else:
                mount.ui.notify_user("Mount failure")
                raise Exception("Error while mounting : %d %s" % (exit_status, output))
        Live_Cache.invalidate_cmd_cache([LIN_CONST.CMD_GVFS_MOUNT, "-l"])

        # 3) Symlink
        if mount.settings["Linux_gvfs_symlink"]:
            mount_point = None
            for f in os.listdir(LIN_CONST.GVFS_DIR):
                if LIN_CONST.GVFS_GENERATION == 1:
                    if re.match(r"{server_share} \S+ {server_name}".format(**mount.settings), f):
                        mount_point = os.path.join(LIN_CONST.GVFS_DIR, f)
                else:
                    if (re.match(r"^smb-share:", f) and
                       re.search(r"domain={realm_domain}(,|$)".format(**mount.settings), f, flags=re.IGNORECASE) and
                       re.search(r"server={server_name}(,|$)".format(**mount.settings), f) and
                       re.search(r"share={server_share}(,|$)".format(**mount.settings), f) and
                       re.search(r"user={realm_username}(,|$)".format(**mount.settings), f)):
                        mount_point = os.path.join(LIN_CONST.GVFS_DIR, f)

            if mount_point is None:
                raise Exception("Error: Could not find the GVFS mountpoint.")

            target = os.path.join(mount_point, mount.settings["server_subdir"])
            try:
                os.symlink(target, mount.settings["local_path"])
            except OSError as e:
                raise Exception("Could not create symbolic link : %s" % e.args[1])
            if not os.path.islink(mount.settings["local_path"]):
                raise Exception("Could not create symbolic link : %s <- %s" % (target, mount.settings["local_path"]))

    else:  # "mount.cifs"
        # 1) Make mount dir (remove broken symlink if needed)
        if (os.path.lexists(mount.settings["local_path"]) and
           not os.path.exists(mount.settings["local_path"])):
            os.unlink(mount.settings["local_path"])
        if not os.path.exists(mount.settings["local_path"]):
            try:
                os.makedirs(mount.settings["local_path"])
            except OSError:
                pass
        if not os.path.isdir(mount.settings["local_path"]):
            raise Exception("Error while creating dir : %s" % mount.settings["local_path"])

        # 2) Mount
        cmd = [
            "sudo", LIN_CONST.CMD_MOUNT_CIFS,
            "//{server_name}/{server_path}",
            "{local_path}",
            "-o",
            "user={realm_username},domain={realm_domain},"
            "uid={local_uid},gid={local_gid},"
            "file_mode={Linux_mountcifs_filemode},"
            "dir_mode={Linux_mountcifs_filemode},"
            "{Linux_mountcifs_options}"
        ]
        cmd = [s.format(**mount.settings) for s in cmd]
        Output.write(" ".join(cmd))
        # for i in xrange(3): # 3 attempts (for passwords mistyped)
        process_meta = {
            "was_cancelled": False,
        }
        (output, exit_status) = pexpect.runu(
            command=" ".join(cmd),
            events={
                "(?i)password": pexpect_ask_password,
            },
            extra_args={
                "auth_realms": [
                    (r"\[sudo\] password", "sudo"),
                    (r"Password", mount.settings["realm"])
                ],
                "key_chain": mount.key_chain,
                "process_meta": process_meta,
            },
            env=dict(os.environ, LANG="C", LC_ALL="C"),
            withexitstatus=True,
            timeout=5,
        )
        if exit_status == 0:
            mount.key_chain.ack_password("sudo")
            mount.key_chain.ack_password(mount.settings["realm"])
        else:
            mount.key_chain.invalidate_if_no_ack_password("sudo")
            mount.key_chain.invalidate_if_no_ack_password(mount.settings["realm"])
            if process_meta["was_cancelled"]:
                pass
            else:
                mount.ui.notify_user("Mount failure")
                raise Exception("Error while mounting : %d %s" % (exit_status, output))
    return True
    

def cifs_umount(mount):
    if mount.settings["Linux_CIFS_method"] == "gvfs":
        # gvfs apparently umount never locks on open files.
        
        # 1) Umount
        cmd = [LIN_CONST.CMD_GVFS_MOUNT, "-u", r"smb://{realm_domain};{realm_username}@{server_name}/{server_share}".format(**mount.settings)]
        Output.write(" ".join(cmd))
        try:
            output = subprocess.check_output(
                cmd,
                env=dict(os.environ, LANG="C", LC_ALL="C"),
            )
        except subprocess.CalledProcessError as e:
            mount.ui.notify_user("Umount failure")
            raise Exception("Error (%s) while umounting : %s" % (e.returncode, e.output.decode()))
        Live_Cache.invalidate_cmd_cache([LIN_CONST.CMD_GVFS_MOUNT, "-l"])

        # 2) Remove symlink
        if mount.settings["Linux_gvfs_symlink"]:
            if (os.path.lexists(mount.settings["local_path"]) and
               not os.path.exists(mount.settings["local_path"])):
                os.unlink(mount.settings["local_path"])

    else:  # "mount.cifs"
        # 1) uMount
        cmd = ["sudo", LIN_CONST.CMD_UMOUNT, "{local_path}"]
        cmd = [s.format(**mount.settings) for s in cmd]
        Output.write(" ".join(cmd))
        # for i in xrange(3): # 3 attempts (for passwords mistyped)
        process_meta = {
            "was_cancelled": False,
        }
        (output, exit_status) = pexpect.runu(
            command=" ".join(cmd),
            events={
                "(?i)password": pexpect_ask_password,
            },
            extra_args={
                "auth_realms": [
                    (r"\[sudo\] password", "sudo"),
                ],
                "key_chain": mount.key_chain,
                "process_meta": process_meta,
            },
            env=dict(os.environ, LANG="C", LC_ALL="C"),
            withexitstatus=True,
            timeout=5,
        )
        if exit_status == 0:
            mount.key_chain.ack_password("sudo")
        else:
            if process_meta["was_cancelled"]:
                mount.key_chain.invalidate_if_no_ack_password("sudo")
            elif "device is busy" in output:
                mount.key_chain.ack_password("sudo")
                mount.ui.notify_user("Umount failure: Device is busy.")
                raise Exception("Error while umounting (device is busy) : %d %s" % (exit_status, output))
            else:
                mount.key_chain.invalidate_if_no_ack_password("sudo")
                mount.ui.notify_user("Umount failure")
                raise Exception("Error while umounting : %d %s" % (exit_status, output))

        # 2) Remove mount dir
        if (os.path.exists(mount.settings["local_path"]) and
           os.listdir(mount.settings["local_path"]) == []):
            try:
                os.rmdir(mount.settings["local_path"])
            except OSError:
                pass


def open_file_manager(mount):
    if (mount.settings["Linux_CIFS_method"] == "gvfs" and
       not mount.settings["Linux_gvfs_symlink"]):
        path = None
        for f in os.listdir(LIN_CONST.GVFS_DIR):
            if LIN_CONST.GVFS_GENERATION == 1:
                if re.match(r"{server_share} \S+ {server_name}".format(**mount.settings), f):
                    path = os.path.join(LIN_CONST.GVFS_DIR, f, mount.settings["server_subdir"])
            else:
                if (re.match(r"^smb-share:", f) and
                   re.search(r"domain={realm_domain}(,|$)".format(**mount.settings), f, flags=re.IGNORECASE) and
                   re.search(r"server={server_name}(,|$)".format(**mount.settings), f) and
                   re.search(r"share={server_share}(,|$)".format(**mount.settings), f) and
                   re.search(r"user={realm_username}(,|$)".format(**mount.settings), f)):
                    path = os.path.join(LIN_CONST.GVFS_DIR, f, mount.settings["server_subdir"])
        if path is None:
            raise Exception("Error: Could not find the GVFS mountpoint.")
    else:
        path = mount.settings["local_path"]
    cmd = [s.format(path=path) for s in LIN_CONST.CMD_OPEN.split(" ")]
    Output.write("cmd : %s" % cmd)
    subprocess.call(cmd)


def pexpect_ask_password(values):
    """
        Interact with process when pexpect found a matching string for password question
        It may Ack previously entered password if several password are asked in the same run.
        
        This is a mirror from osx_stack.pexpect_ask_password
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