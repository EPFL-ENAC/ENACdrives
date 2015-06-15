#!/usr/bin/env python3

# Bancal Samuel

# Offers Linux stack for :
# + cifs_is_mount
# + cifs_mount
# + cifs_post_mount
# + cifs_umount
# + cifs_post_umount
# + open_file_manager

import os
import re
import pexpect
from utility import CONST, Output, which, CancelOperationException, BlockingProcess, NonBlockingProcess, NonBlockingThread


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


def cifs_is_mounted(mount, cb=None):
    """
        evaluate if this mount is mounted
        if cb is None make it synchronously (CLI)
        else make it asynchronously (GUI)
    """
    def _cb_gvfs(success, output, exit_code):
        # Output.debug("lin_stack._cb_gvfs")
        # Output.debug("-> gvfs-mount -l : \n{0}\n\n".format(output))
        share_format1 = re.sub(r"\$", r"\\$", mount.settings["server_share"])
        share_format2 = re.sub(r" ", r"%20", mount.settings["server_share"])
        share_format2 = re.sub(r"\$", r"\\$", share_format2)
        i_search = r"{share_format1} .+ {server_name} -> smb://{realm_domain};{realm_username}@{server_name}/{share_format2}".format(
            share_format1=share_format1, share_format2=share_format2, **mount.settings)
        for l in output.split("\n"):
            if re.search(i_search, l, flags=re.IGNORECASE):
                Output.debug(l)
                if cb is None:
                    return True
                else:
                    cb(True)
                    return
        if cb is None:
            return False
        else:
            cb(False)
    
    def _target_mountcifs():
        return os.path.ismount(mount.settings["local_path"])
        
    # Output.debug("lin_stack.cifs_is_mounted")
    if mount.settings["Linux_CIFS_method"] == "gvfs":
        cmd = [LIN_CONST.CMD_GVFS_MOUNT, "-l"]
        # Output.debug("cmd: " + " ".join(cmd))
        if cb is None:
            return _cb_gvfs(**BlockingProcess.run(
                cmd,
                env=dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="C"),
                cache=True,
            ))
        else:
            NonBlockingProcess(
                cmd,
                _cb_gvfs,
                env=dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="C"),
                cache=True,
            )
    else:  # "mount.cifs"
        if cb is None:
            return _target_mountcifs()
        else:
            NonBlockingThread(
                "os.path.ismounted.{}".format(mount.settings["local_path"]),
                _target_mountcifs,
                cb
            )


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
                mount.ui.notify_user("Error : Path {} already exists".format(mount.settings["local_path"]))
                return False

        # 2) Mount
        share = re.sub(r" ", r"%20", mount.settings["server_share"])
        cmd = [LIN_CONST.CMD_GVFS_MOUNT, r"smb://{realm_domain}\;{realm_username}@{server_name}/{share}".format(share=share, **mount.settings)]
        Output.verbose("cmd: " + " ".join(cmd))
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
            mount.ui.notify_user("Error while mounting :<br>{}".format(exc.value))
            return False
        if "error" not in output.lower() and exit_status == 0:
            mount.key_chain.ack_password(mount.settings["realm"])
        else:
            mount.key_chain.invalidate_if_no_ack_password(mount.settings["realm"])
            if process_meta["was_cancelled"]:
                return False
            else:
                mount.ui.notify_user("Mount failure :<br>{}".format(output))
                return False
        if mount.ui.UI_TYPE == "GUI":
            NonBlockingProcess.invalidate_cmd_cache(
                [LIN_CONST.CMD_GVFS_MOUNT, "-l"]
            )
        else:
            BlockingProcess.invalidate_cmd_cache(
                [LIN_CONST.CMD_GVFS_MOUNT, "-l"]
            )

    else:  # "mount.cifs"
        if LIN_CONST.CMD_MOUNT_CIFS is None:
            mount.ui.notify_user("Error missing binary <b>mount.cifs</b>. On Ubuntu you can install it with <i>sudo apt-get install cifs-utils</i>")
            return False
            
        # 1) Make mount dir (remove broken symlink if needed)
        if (os.path.lexists(mount.settings["local_path"]) and
           not os.path.exists(mount.settings["local_path"])):
            os.unlink(mount.settings["local_path"])
        if not os.path.exists(mount.settings["local_path"]):
            try:
                os.makedirs(mount.settings["local_path"])
            except OSError:
                pass
        if (os.path.islink(mount.settings["local_path"]) or
           not os.path.isdir(mount.settings["local_path"])):
            mount.ui.notify_user("Error while creating dir : %s" % mount.settings["local_path"])
            return False

        # 2) Mount
        s_path = re.sub(" ", "\\ ", mount.settings["server_path"])
        cmd = [
            "sudo", LIN_CONST.CMD_MOUNT_CIFS,
            "//{server_name}/{s_path}",
            "{local_path}",
            "-o",
            "user={realm_username},domain={realm_domain},"
            "uid={local_uid},gid={local_gid},"
            "file_mode={Linux_mountcifs_filemode},"
            "dir_mode={Linux_mountcifs_filemode},"
            "{Linux_mountcifs_options}"
        ]
        cmd = [s.format(s_path=s_path, **mount.settings) for s in cmd]
        Output.verbose("cmd: " + " ".join(cmd))
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
                if (os.path.exists(mount.settings["local_path"]) and
                   os.listdir(mount.settings["local_path"]) == []):
                    try:
                        os.rmdir(mount.settings["local_path"])
                    except OSError as e:
                        Output.warning("Could not rmdir : {0}".format(e))
            else:
                mount.ui.notify_user("Mount failure : {}".format(output))
                return False
    return True


def cifs_post_mount(mount):
    """
    Performs tasks when mount is done.
    May happen some seconds after cifs_mount is completed (OS)
    """
    if mount.settings["Linux_CIFS_method"] == "gvfs":
        share = re.sub(r" ", r"%20", mount.settings["server_share"])
        share = re.sub(r"\$", r"\\$", share)
        # 3) Symlink
        if mount.settings["Linux_gvfs_symlink"]:
            if not os.path.lexists(mount.settings["local_path"]):
                mount_point = None
                for f in os.listdir(LIN_CONST.GVFS_DIR):
                    if LIN_CONST.GVFS_GENERATION == 1:
                        if re.match(r"{server_share} \S+ {server_name}".format(**mount.settings), f, flags=re.IGNORECASE):
                            mount_point = os.path.join(LIN_CONST.GVFS_DIR, f)
                    else:
                        if (re.match(r"^smb-share:", f) and
                           re.search(r"domain={realm_domain}(,|$)".format(**mount.settings), f, flags=re.IGNORECASE) and
                           re.search(r"server={server_name}(,|$)".format(**mount.settings), f) and
                           re.search(r"share={share}(,|$)".format(share=share, **mount.settings), f, flags=re.IGNORECASE) and
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
        pass


def cifs_umount(mount):
    def _cb_gvfs(success, output, exit_code):
        if not success:
            mount.ui.notify_user("Umount failure :<br>{}".format(output))
        if mount.ui.UI_TYPE == "GUI":
            NonBlockingProcess.invalidate_cmd_cache(
                [LIN_CONST.CMD_GVFS_MOUNT, "-l"]
            )
        else:
            BlockingProcess.invalidate_cmd_cache(
                [LIN_CONST.CMD_GVFS_MOUNT, "-l"]
            )
    
    if mount.settings["Linux_CIFS_method"] == "gvfs":
        # gvfs umount apparently never locks on open files.
        
        # 1) Umount
        share = re.sub(r" ", r"%20", mount.settings["server_share"])
        cmd = [LIN_CONST.CMD_GVFS_MOUNT, "-u", r"smb://{realm_domain};{realm_username}@{server_name}/{share}".format(share=share, **mount.settings)]
        Output.verbose("cmd: " + " ".join(cmd))
        
        if mount.ui.UI_TYPE == "GUI":
            NonBlockingProcess(
                cmd,
                _cb_gvfs,
                env=dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="C"),
            )
        else:
            _cb_gvfs(**BlockingProcess.run(
                cmd,
                env=dict(os.environ, LANG="C", LC_ALL="C", LANGUAGE="C"),
            ))

    else:  # "mount.cifs"
        # 1) uMount
        cmd = ["sudo", LIN_CONST.CMD_UMOUNT, "{local_path}"]
        cmd = [s.format(**mount.settings) for s in cmd]
        Output.verbose("cmd: " + " ".join(cmd))
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
                return False
            else:
                mount.key_chain.invalidate_if_no_ack_password("sudo")
                mount.ui.notify_user("Umount failure")
                return False


def cifs_post_umount(mount):
    """
    Performs tasks when umount is done.
    May happen some seconds after cifs_umount is completed (OS)
    """
    if mount.settings["Linux_CIFS_method"] == "gvfs":
        # 2) Remove symlink
        if mount.settings["Linux_gvfs_symlink"]:
            if (os.path.lexists(mount.settings["local_path"]) and
               not os.path.exists(mount.settings["local_path"])):
                os.unlink(mount.settings["local_path"])

    else:  # "mount.cifs"
        # 2) Remove mount dir
        if (os.path.exists(mount.settings["local_path"]) and
           os.listdir(mount.settings["local_path"]) == []):
            try:
                os.rmdir(mount.settings["local_path"])
            except OSError as e:
                Output.warning("Could not rmdir : {0}".format(e))


def open_file_manager(mount):
    def _cb(success, output, exit_code):
        pass
        
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
    Output.verbose("cmd: " + " ".join(cmd))
    NonBlockingProcess(
        cmd,
        _cb,
    )


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
        Output.verbose("Operation cancelled.")
        values["extra_args"]["process_meta"]["was_cancelled"] = True
        # Stop current process
        return True
