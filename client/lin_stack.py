#!/usr/bin/env python3

# Bancal Samuel

# Offers Linux stack for :
# + CIFS (is_mount, mount, umount)
# + open_file_manager

import os
import re
import pexpect
import subprocess
from utility import CONST, Live_Cache, Output, CancelOperationException


def cifs_is_mounted(mount):
    if mount.settings["Linux_CIFS_method"] == "gvfs":
        cmd = [CONST.CMD_GVFS_MOUNT, "-l"]
        # Output.write(" ".join(cmd))
        lines = Live_Cache.subprocess_check_output(cmd)
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
        cmd = [CONST.CMD_GVFS_MOUNT, r"smb://{realm_domain}\;{realm_username}@{server_name}/{server_share}".format(**mount.settings)]
        Output.write(" ".join(cmd))
        process_meta = {
            "was_cancelled": False,
        }
        try:
            (output, exit_status) = pexpect.runu(
                command=" ".join(cmd),
                events={
                    'Password:': pexpect_ask_password,
                },
                extra_args={
                    "auth_realms": [
                        (r'Password:', mount.settings["realm"])
                    ],
                    "key_chain": mount.key_chain,
                    "process_meta": process_meta,
                    # "context" : "gvfs_mount_%s" % mount.settings["name"]
                },
                withexitstatus=True,
                timeout=5,
            )
        except pexpect.ExceptionPexpect as exc:
            raise Exception("Error while mounting : %s" % exc.value)
        if exit_status == 0:
            mount.key_chain.ack_password(mount.settings["realm"])
        elif process_meta["was_cancelled"]:
            pass
        elif exit_status != 0:
            raise Exception("Error while mounting : %d %s" % (exit_status, output))
        Live_Cache.invalidate_cmd_cache([CONST.CMD_GVFS_MOUNT, "-l"])

        # 3) Symlink
        if mount.settings["Linux_gvfs_symlink"]:
            mount_point = None
            for f in os.listdir(CONST.GVFS_DIR):
                if CONST.GVFS_GENERATION == 1:
                    if re.match(r'{server_share} \S+ {server_name}'.format(**mount.settings), f):
                        mount_point = os.path.join(CONST.GVFS_DIR, f)
                else:
                    if (re.match(r'^smb-share:', f) and
                       re.search(r'domain={realm_domain}(,|$)'.format(**mount.settings), f, flags=re.IGNORECASE) and
                       re.search(r'server={server_name}(,|$)'.format(**mount.settings), f) and
                       re.search(r'share={server_share}(,|$)'.format(**mount.settings), f) and
                       re.search(r'user={realm_username}(,|$)'.format(**mount.settings), f)):
                        mount_point = os.path.join(CONST.GVFS_DIR, f)

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
        # 1) Make mount dir
        if not os.path.exists(mount.settings["local_path"]):
            try:
                os.makedirs(mount.settings["local_path"])
            except OSError:
                pass
        if not os.path.isdir(mount.settings["local_path"]):
            raise Exception("Error while creating dir : %s" % mount.settings["local_path"])

        # 2) Mount
        cmd = [
            "sudo", CONST.CMD_MOUNT_CIFS,
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
                '(?i)password': pexpect_ask_password,
            },
            extra_args={
                "auth_realms": [
                    (r'\[sudo\] password', "sudo"),
                    (r'Password', mount.settings["realm"])
                ],
                "key_chain": mount.key_chain,
                "process_meta": process_meta,
            },
            withexitstatus=True,
            timeout=5,
        )
        if exit_status == 0:
            mount.key_chain.ack_password("sudo")
            mount.key_chain.ack_password(mount.settings["realm"])
            # break
        elif process_meta["was_cancelled"]:
            pass
        elif exit_status != 0:
            raise Exception("Error while mounting : %d %s" % (exit_status, output))
    

def cifs_umount(mount):
    if mount.settings["Linux_CIFS_method"] == "gvfs":
        # 1) Umount
        cmd = [CONST.CMD_GVFS_MOUNT, "-u", r"smb://{realm_domain};{realm_username}@{server_name}/{server_share}".format(**mount.settings)]
        Output.write(" ".join(cmd))
        try:
            output = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            raise Exception("Error (%s) while umounting : %s" % (e.returncode, e.output.decode()))
        Live_Cache.invalidate_cmd_cache([CONST.CMD_GVFS_MOUNT, "-l"])

        # 2) Remove symlink
        if mount.settings["Linux_gvfs_symlink"]:
            if (os.path.lexists(mount.settings["local_path"]) and
               not os.path.exists(mount.settings["local_path"])):
                os.unlink(mount.settings["local_path"])

    else:  # "mount.cifs"
        # 1) uMount
        cmd = ["sudo", CONST.CMD_UMOUNT, "{local_path}"]
        cmd = [s.format(**mount.settings) for s in cmd]
        Output.write(" ".join(cmd))
        # for i in xrange(3): # 3 attempts (for passwords mistyped)
        process_meta = {
            "was_cancelled": False,
        }
        (output, exit_status) = pexpect.runu(
            command=" ".join(cmd),
            events={
                '(?i)password': pexpect_ask_password,
            },
            extra_args={
                "auth_realms": [
                    (r'\[sudo\] password', "sudo"),
                ],
                "key_chain": mount.key_chain,
                "process_meta": process_meta,
            },
            withexitstatus=True,
            timeout=5,
        )
        if exit_status == 0:
            mount.key_chain.ack_password("sudo")
            # break
        elif process_meta["was_cancelled"]:
            pass
        elif exit_status != 0:
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
        for f in os.listdir(CONST.GVFS_DIR):
            if CONST.GVFS_GENERATION == 1:
                if re.match(r'{server_share} \S+ {server_name}'.format(**mount.settings), f):
                    path = os.path.join(CONST.GVFS_DIR, f, mount.settings["server_subdir"])
            else:
                if (re.match(r'^smb-share:', f) and
                   re.search(r'domain={realm_domain}(,|$)'.format(**mount.settings), f, flags=re.IGNORECASE) and
                   re.search(r'server={server_name}(,|$)'.format(**mount.settings), f) and
                   re.search(r'share={server_share}(,|$)'.format(**mount.settings), f) and
                   re.search(r'user={realm_username}(,|$)'.format(**mount.settings), f)):
                    path = os.path.join(CONST.GVFS_DIR, f, mount.settings["server_subdir"])
        if path is None:
            raise Exception("Error: Could not find the GVFS mountpoint.")
    else:
        path = mount.settings["local_path"]
    cmd = [s.format(path=path) for s in CONST.CMD_OPEN.split(" ")]
    Output.write("cmd : %s" % cmd)
    subprocess.call(cmd)


def pexpect_ask_password(values):
    process_question = values["child_result_list"][-1]
    try:
        for pattern, auth_realm in values["extra_args"]["auth_realms"]:
            if re.search(pattern, process_question):
                return values["extra_args"]["key_chain"].get_password(auth_realm) + "\n"
    except CancelOperationException:
        Output.write("Operation cancelled.")
        values["extra_args"]["process_meta"]["was_cancelled"] = True
        # Stop current process
        return True
