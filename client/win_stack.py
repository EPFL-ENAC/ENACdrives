#!/usr/bin/env python3

# Bancal Samuel

# Offers Windows stack for :
# + CIFS (is_mount, mount, umount)
# + open_file_manager

import re
import subprocess
from utility import CONST, Live_Cache, Output, debug_send, CancelOperationException


def cifs_is_mounted(mount):
    cmd = ["wmic", "logicaldisk"]  # List all Logical Disks
    lines = Live_Cache.subprocess_check_output(cmd)
    lines = lines.split("\n")
    caption_index = lines[0].index("Caption")
    providername_index = lines[0].index("ProviderName")
    i_search = r"^\\{server_name}\{server_path}$".format(**mount.settings)
    i_search = i_search.replace("\\", "\\\\")
    # Output.write("i_search='{0}'".format(i_search))
    for l in lines[1:]:
        try:
            drive_letter = re.findall(r"^(\S+)", l[caption_index:])[0]
            try:
                provider = re.findall(r"^(\S+)", l[providername_index:])[0]
                if re.search(i_search, provider):
                    mount.settings["Windows_letter"] = drive_letter
                    return True
            except IndexError:
                provider = ""
            # Output.write("{0} : '{1}'".format(drive_letter, provider))
        except IndexError:
            pass
    return False


def cifs_mount(mount):
    # Couldn't make this work : TODO
    # cmd = [
    #     "NET", "USE", "{Windows_letter}",
    #     r"\\{server_name}\{server_path}", "*",
    #     r"/USER:{realm_domain}\{realm_username}", "/PERSISTENT:no"
    # ]
    # cmd = [s.format(**mount.settings) for s in cmd]
    # Output.write(" ".join(cmd))
    # child = winpexpect.winspawn(cmd[0], cmd[1:])
    # child.expect("password")
    # child.sendline("BLABLAPWD")
    # ... terminate

    # STARTUPINFO : Prevents cmd to be opened when subprocess.Popen is called.
    # http://stackoverflow.com/a/24171096/446302
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

    # 1) First attempt without password
    cmd = [
        "NET",
        "USE", "{Windows_letter}",
        r"\\{server_name}\{server_path}", 
        r"/USER:{realm_domain}\{realm_username}", "/PERSISTENT:no"
    ]
    cmd = [s.format(**mount.settings) for s in cmd]
    s_cmd = " ".join(cmd)
    Output.write("Running : {0}".format(s_cmd))
    p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, startupinfo=startupinfo)
    while True:
        try:
            stdout, stderr = p.communicate(timeout=1)
            stdout = "\n".join([l.strip() for l in stdout.decode("UTF-8").split("\n") if l.strip() != ""])
            stderr = "\n".join([l.strip() for l in stderr.decode("UTF-8").split("\n") if l.strip() != ""])
            if stdout != "":
                Output.write("out:{0}".format(stdout))
            if stderr != "":
                Output.write("err:{0}".format(stderr))
            if stdout == "" and stderr == "":
                Output.write("<no output>")
            if "Enter the password" in stdout:
                p.kill()
                break
            if stderr != "":
                debug_send("{0}\nout: {1}\nerr: {2}".format(s_cmd, stdout, stderr))
            if p.returncode == 0:
                Live_Cache.invalidate_cmd_cache(["wmic", "logicaldisk"])
                return True
            if p.returncode is not None:
                debug_send("{0}\nout: {1}\nerr: {2}\nreturncode: {3}".format(s_cmd, stdout, stderr, p.returncode))
                break
        except subprocess.TimeoutExpired:
            Output.write(".", end="")

    if p.returncode != 0:
        # 2) Second attempt with password
        for _ in range(3):
            cmd = [
                "NET",
                "USE", "{Windows_letter}",
                r"\\{server_name}\{server_path}", "***",
                r"/USER:{realm_domain}\{realm_username}", "/PERSISTENT:no"
            ]
            cmd = [s.format(**mount.settings) for s in cmd]
            s_cmd = " ".join(cmd)
            try:
                cmd[4] = mount.key_chain.get_password(mount.settings["realm"])
            except CancelOperationException:
                Output.write("Operation cancelled.")
                break
            Output.write("Running : {0}".format(s_cmd))
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, startupinfo=startupinfo)
            while True:
                try:
                    stdout, stderr = p.communicate(timeout=1)
                    stdout = "\n".join([l.strip() for l in stdout.decode("UTF-8").split("\n") if l.strip() != ""])
                    stderr = "\n".join([l.strip() for l in stderr.decode("UTF-8").split("\n") if l.strip() != ""])
                    if stdout != "":
                        Output.write("out:{0}".format(stdout))
                    if stderr != "":
                        Output.write("err:{0}".format(stderr))
                    if stdout == "" and stderr == "":
                        Output.write("<no output>")
                    if "password is not correct" in stderr:
                        p.kill()
                        break
                    if "bad password" in stderr:
                        p.kill()
                        break
                    if stderr != "":
                        debug_send("{0}\nout: {1}\nerr: {2}".format(s_cmd, stdout, stderr))
                    if p.returncode == 0:
                        Live_Cache.invalidate_cmd_cache(["wmic", "logicaldisk"])
                        mount.key_chain.ack_password(mount.settings["realm"])
                        return True
                    if p.returncode is not None:
                        debug_send("{0}\nout: {1}\nerr: {2}\nreturncode: {3}".format(s_cmd, stdout, stderr, p.returncode))
                        break
                except subprocess.TimeoutExpired:
                    Output.write(".", end="")
                except Exception as e:
                    Output.write("Exception : {0}".format(e))
                    debug_send("{0}\nException: {1}\n".format(s_cmd, e))


def cifs_umount(mount):
    # TODO : manage this message ... (cross languages!)
    # There are open files and/or incomplete directory searches pending on the connect
    # ion to Z:.
    #
    # Is it OK to continue disconnecting and force them closed? (Y/N) [N]:
    cmd = ["NET", "USE", mount.settings["Windows_letter"], "/delete"]
    Output.write(" ".join(cmd))
    try:
        # STARTUPINFO : Prevents cmd to be opened when subprocess.Popen is called.
        # http://stackoverflow.com/a/24171096/446302
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        output = subprocess.check_output(cmd, shell=False, startupinfo=startupinfo)
    except subprocess.CalledProcessError as e:
        raise Exception("Error (%s) while umounting : %s" % (e.returncode, e.output.decode()))
    Live_Cache.invalidate_cmd_cache(["wmic", "logicaldisk"])


def open_file_manager(mount):
    path = mount.settings["Windows_letter"]
    cmd = [s.format(path=path) for s in CONST.CMD_OPEN.split(" ")]
    Output.write("cmd : %s" % cmd)
    subprocess.call(cmd)
