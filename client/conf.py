#!/usr/bin/env python3

# Bancal Samuel

# Offers get_config() which
#  + parse config from
#    + default values (hard coded in source)
#    + http://enacdrives.epfl.ch/config?username=xxx
#    + System's config
#    + User's config
#  + merge them
#  + validate

import os
import re
import io
import pprint
import socket
import hashlib
import urllib.error
import urllib.request
from utility import Output, CONST, bytes_decode


FileNotFoundException = getattr(__builtins__, 'FileNotFoundError', IOError)


class ConfigException(Exception):
    pass


def get_config():
    # Create cache_dir if not already existent
    if not os.path.exists(CONST.USER_CACHE_DIR):
        os.makedirs(CONST.USER_CACHE_DIR)

    # HARD CODED CONFIG
    default_config = {
        'global': {
         'Linux_CIFS_method': 'gvfs',
         'Linux_gvfs_symlink': True,
         'Linux_mountcifs_dirmode': '0770',
         'Linux_mountcifs_filemode': '0770',
         'Linux_mountcifs_options': 'rw,nobrl,noserverino,iocharset=utf8,sec=ntlm'},
        'CIFS_mount': {},
        'network': {},
        'realm': {}
    }
    cfg = default_config

    # USER CONFIG -> get only username from [global]
    user_config = None
    username = None
    try:
        with open(CONST.USER_CONF_FILE, "r") as f:
            user_config = read_config_source(f)
        username = user_config.get("global", {}).get("username", None)
        if username is not None:
            Output.verbose("Loaded username '{}' from User context. ({})".format(username, CONST.USER_CONF_FILE))
        else:
            Output.normal("Username not found in User context. ({})".format(CONST.USER_CONF_FILE))
    except FileNotFoundException:
        Output.normal("Username not found in User context. ({})".format(CONST.USER_CONF_FILE))
    
    if username is None:
        if CONST.AD_USERNAME is not None:
            username = CONST.AD_USERNAME
            Output.verbose("Loaded username '{}' from environment variables (user in domain '{}').".format(username, CONST.AD_DOMAIN))
            # Save to config file and reload it for after
            save_username(username)
            with open(CONST.USER_CONF_FILE, "r") as f:
                user_config = read_config_source(f)
        else:
            Output.normal("Username not found in environment variables (user not in a domain).")

    # ENACDRIVE SERVER CONFIG (included cache function)
    if username is not None:
        config_url = CONST.CONFIG_URL.format(username=username)
        cache_filename = os.path.join(CONST.USER_CACHE_DIR, hashlib.md5(config_url.encode()).hexdigest())
        try:
            with urllib.request.urlopen(config_url, timeout=CONST.URL_TIMEOUT) as response:
                lines = [bytes_decode(l) for l in response.readlines()]
                Output.debug("get_config {} : {}".format(config_url, lines))
                s_io = io.StringIO("".join(lines))
                enacdrives_config = read_config_source(s_io)
                merge_configs(cfg, enacdrives_config)
                s_io.seek(0)
                with open(cache_filename, "w") as f:
                    f.writelines(s_io.readlines())
            Output.verbose("Loaded config from ENACdrives server ({})".format(config_url))
        except (socket.timeout, urllib.error.URLError, ConfigException) as e:
            Output.warning("Could not load config ENACdrives server. ({})".format(config_url))
            Output.warning("Got error : {}".format(e))
            try:
                with open(cache_filename, "r") as f:
                    cached_config = read_config_source(f)
                    merge_configs(cfg, cached_config)
                Output.normal("Loaded config from cache file. ({})".format(cache_filename))
            except FileNotFoundException:
                Output.warning("Could not load config from cache file. ({})".format(cache_filename))
    else:
        Output.normal("Skipping config from ENACdrives server (no username).")

    # SYSTEM CONFIG
    try:
        with open(CONST.SYSTEM_CONF_FILE, "r") as f:
            system_config = read_config_source(f)
            merge_configs(cfg, system_config)
        Output.verbose("Loaded config from System context. ({})".format(CONST.SYSTEM_CONF_FILE))
    except FileNotFoundException:
        Output.normal("No config found from System context. ({})".format(CONST.SYSTEM_CONF_FILE))

    # USER CONFIG
    if user_config is not None:
        merge_configs(cfg, user_config)
        Output.verbose("Loaded config from User context. ({})".format(CONST.USER_CONF_FILE))
    else:
        Output.normal("No config found from User context. ({})".format(CONST.USER_CONF_FILE))

    cfg = validate_config(cfg)
    return cfg


def save_username(username):
    """
    Parse config file and change/add only what is necessary
    """

    lines = ["", ]
    try:
        with open(CONST.USER_CONF_FILE, "r") as f:
            lines = f.readlines()

        # Parse file, search for username = xxx in [global]
        current_section = None
        line_nb = -1
        global_section_line_nb = None
        username_line_nb = None
        for l in lines:
            line_nb += 1
            if l.startswith("["):
                try:
                    current_section = re.match(r"\[(\S+)\]$", l).groups()[0]
                    if current_section == "global" and global_section_line_nb is None:
                        global_section_line_nb = line_nb
                except AttributeError:
                    current_section = None
                continue
            if current_section != "global":
                continue
            try:
                k, v = re.match(r"([^=]*)=(.*)", l).groups()
                k, v = k.strip(), v.strip()
            except AttributeError:
                continue
            if k == "username":
                username_line_nb = line_nb
                break

        # username found in config file
        if username_line_nb is not None:
            Output.verbose("Changing to username='{}' in config file {}".format(username, CONST.USER_CONF_FILE))
            lines[username_line_nb] = "username = {}\n".format(username)

        # username not found, but [global] found
        elif global_section_line_nb is not None:
            Output.verbose("Saving username='{}' in config file {}".format(username, CONST.USER_CONF_FILE))
            lines.insert(global_section_line_nb+1, "username = {}\n".format(username))

        # [global] not found
        else:
            Output.verbose("Saving username='{}' in config file {}".format(username, CONST.USER_CONF_FILE))
            lines.insert(0, "[global]\n")
            lines.insert(1, "username = {}\n".format(username))
            lines.insert(2, "\n")

    except FileNotFoundException:
        Output.verbose("Saving username='{}' to new config file {}".format(username, CONST.USER_CONF_FILE))
        lines.insert(0, "[global]\n")
        lines.insert(1, "username = {}\n".format(username))
        lines.insert(2, "\n")

    with open(CONST.USER_CONF_FILE, "w") as f:
        f.writelines(lines)


def save_bookmark(section_name, bookmark_on):
    """
    Parse config file and change/add only what is necessary
    """

    lines = ["", ]
    try:
        with open(CONST.USER_CONF_FILE, "r") as f:
            lines = f.readlines()

        # Parse file, search for name = section_name in [CIFS_mount]
        line_nb = -1
        good_section_name = False
        bookmark_w_no_section_name_line_nb = None
        skip_this_section = True
        section_name_line_nb = None
        option_line_nb = None
        for l in lines:
            line_nb += 1
            if l.startswith("["):
                good_section_name = False
                bookmark_w_no_section_name_line_nb = None
                try:
                    current_section = re.match(r"\[(\S+)\]$", l).groups()[0]
                    if current_section == "CIFS_mount":
                        skip_this_section = False
                except AttributeError:
                    skip_this_section = True
                continue
            if skip_this_section:
                continue

            try:
                k, v = re.match(r"([^=]*)=(.*)", l).groups()
                k, v = k.strip(), v.strip()
            except AttributeError:
                continue
            if k == "name":
                if v == section_name:
                    good_section_name = True
                    if bookmark_w_no_section_name_line_nb is not None:
                        option_line_nb = bookmark_w_no_section_name_line_nb
                        break
                    if section_name_line_nb is None:
                        section_name_line_nb = line_nb
                else:
                    skip_this_section = True
                continue
            elif k == "bookmark":
                if good_section_name:
                    option_line_nb = line_nb
                    break
                else:  # Unknown name=xyz yet
                    bookmark_w_no_section_name_line_nb = line_nb

        # bookmark found in config file
        if option_line_nb is not None:
            Output.verbose("Changing {}'s bookmark='{}' in config file {}".format(section_name, bookmark_on, CONST.USER_CONF_FILE))
            lines[option_line_nb] = "bookmark = {}\n".format(bookmark_on)

        # bookmark not found, but [CIFS_mount] found
        elif section_name_line_nb is not None:
            Output.verbose("Saving {}'s bookmark='{}' in config file {}".format(section_name, bookmark_on, CONST.USER_CONF_FILE))
            lines.insert(section_name_line_nb+1, "bookmark = {}\n".format(bookmark_on))

        # [CIFS_mount] not found
        else:
            Output.verbose("Saving {}'s bookmark='{}' in config file {}".format(section_name, bookmark_on, CONST.USER_CONF_FILE))
            lines.append("[CIFS_mount]\n")
            lines.append("name = {}\n".format(section_name))
            lines.append("bookmark = {}\n".format(bookmark_on))
            lines.append("\n")

    except FileNotFoundException:
        Output.verbose("Saving {}'s bookmark='{}' to new config file {}".format(section_name, bookmark_on, CONST.USER_CONF_FILE))
        lines.append("[CIFS_mount]\n")
        lines.append("name = {}\n".format(section_name))
        lines.append("bookmark = {}\n".format(bookmark_on))
        lines.append("\n")

    with open(CONST.USER_CONF_FILE, "w") as f:
        f.writelines(lines)


def save_windows_letter(section_name, letter):
    """
    Parse config file and change/add only what is necessary
    """

    lines = ["", ]
    try:
        with open(CONST.USER_CONF_FILE, "r") as f:
            lines = f.readlines()

        # Parse file, search for name = section_name in [CIFS_mount]
        line_nb = -1
        good_section_name = False
        letter_w_no_section_name_line_nb = None
        skip_this_section = True
        section_name_line_nb = None
        option_line_nb = None
        for l in lines:
            line_nb += 1
            if l.startswith("["):
                good_section_name = False
                letter_w_no_section_name_line_nb = None
                try:
                    current_section = re.match(r"\[(\S+)\]$", l).groups()[0]
                    if current_section == "CIFS_mount":
                        skip_this_section = False
                except AttributeError:
                    skip_this_section = True
                continue
            if skip_this_section:
                continue

            try:
                k, v = re.match(r"([^=]*)=(.*)", l).groups()
                k, v = k.strip(), v.strip()
            except AttributeError:
                continue
            if k == "name":
                if v == section_name:
                    good_section_name = True
                    if letter_w_no_section_name_line_nb is not None:
                        option_line_nb = letter_w_no_section_name_line_nb
                        break
                    if section_name_line_nb is None:
                        section_name_line_nb = line_nb
                else:
                    skip_this_section = True
                continue
            elif k == "Windows_letter":
                if good_section_name:
                    option_line_nb = line_nb
                    break
                else:  # Unknown name=xyz yet
                    letter_w_no_section_name_line_nb = line_nb

        # Windows_letter found in config file
        if option_line_nb is not None:
            Output.verbose("Changing {}'s Windows_letter='{}' in config file {}".format(section_name, letter, CONST.USER_CONF_FILE))
            lines[option_line_nb] = "Windows_letter = {}\n".format(letter)

        # Windows_letter not found, but [CIFS_mount] found
        elif section_name_line_nb is not None:
            Output.verbose("Saving {}'s Windows_letter='{}' in config file {}".format(section_name, letter, CONST.USER_CONF_FILE))
            lines.insert(section_name_line_nb+1, "Windows_letter = {}\n".format(letter))

        # [CIFS_mount] not found
        else:
            Output.verbose("Saving {}'s Windows_letter='{}' in config file {}".format(section_name, letter, CONST.USER_CONF_FILE))
            lines.append("[CIFS_mount]\n")
            lines.append("name = {}\n".format(section_name))
            lines.append("Windows_letter = {}\n".format(letter))
            lines.append("\n")

    except FileNotFoundException:
        Output.verbose("Saving {}'s Windows_letter='{}' to new config file {}".format(section_name, letter, CONST.USER_CONF_FILE))
        lines.append("[CIFS_mount]\n")
        lines.append("name = {}\n".format(section_name))
        lines.append("Windows_letter = {}\n".format(letter))
        lines.append("\n")

    with open(CONST.USER_CONF_FILE, "w") as f:
        f.writelines(lines)


def merge_configs(cfg, cfg_to_merge):
    cfg.setdefault("global", {})

    # merge entries_order (priority to cfg_to_merge, then add missing from cfg)
    cfg_to_merge.setdefault("global", {})
    cfg_to_merge["global"].setdefault("entries_order", [])
    for entry in cfg["global"].get("entries_order", []):
        if entry not in cfg_to_merge["global"]["entries_order"]:
            cfg_to_merge["global"]["entries_order"].append(entry)

    # merge ["global"]
    cfg["global"].update(cfg_to_merge.get("global", {}))

    # merge ["CIFS_mount"]
    cfg.setdefault("CIFS_mount", {})
    for cifs_m in cfg_to_merge.get("CIFS_mount", {}):
        cfg["CIFS_mount"].setdefault(cifs_m, {})
        cfg["CIFS_mount"][cifs_m].update(cfg_to_merge["CIFS_mount"][cifs_m])

    # merge ["realm"]
    cfg.setdefault("realm", {})
    for realm in cfg_to_merge.get("realm", {}):
        cfg["realm"].setdefault(realm, {})
        cfg["realm"][realm].update(cfg_to_merge["realm"][realm])

    # merge ["network"]
    cfg.setdefault("network", {})
    for net in cfg_to_merge.get("network", {}):
        cfg["network"].setdefault(net, {})
        cfg["network"][net].update(cfg_to_merge["network"][net])

    return cfg


def validate_value(option, value):
    if option == "Linux_CIFS_method":
        if value not in ("gvfs", "mount.cifs"):
            raise ConfigException("Error, Linux_CIFS_method has to be 'gvfs' or 'mount.cifs'.")
    elif option == "entries_order":
        value = [e.strip() for e in value.split(",")]
    elif option in ("unc", "server_path", "local_path"):
        value = re.sub(r"\\", "/", value)
    elif option == "domain":
        value = value.upper()
    elif option == "username":
        value = value.lower()
    elif option == "server_name":
        if bool(re.search(r"[^a-zA-Z0-9.-]", value)):
            raise ConfigException("Error, server_name can only contain alphanumeric, and '-' and '.' symbols.")
    elif option in ("bookmark", "Linux_gvfs_symlink"):
        value = str(value).lower()
        return value in ("yes", "y", "true", "1", "on")
    elif option == "Windows_letter":
        # Letter can be forced to <empty> or any Letter followed by ":"
        if value != "":
            value = value.upper()
            if not re.match(r"[A-Z]:$", value):
                raise ConfigException("Error, Windows drive letter has to be empty or a letter formated like 'Z:'.")
    return value


def read_config_source(src):
    """
        Readlines on src
            [global]
            username = bancal
            Linux_CIFS_method = gvfs
            Linux_mountcifs_filemode = 0770
            Linux_mountcifs_dirmode = 0770
            Linux_mountcifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm
            Linux_gvfs_symlink = true
            
            [network]
            name = Internet
            ping = www.epfl.ch
            ping = enacit.epfl.ch
            error_msg = Error, you are not connected to the network. You won't be able to mount this resource.
            
            [network]
            name = Epfl
            parent = Internet
            cifs = files0.epfl.ch
            cifs = files1.epfl.ch
            cifs = files8.epfl.ch
            cifs = files9.epfl.ch
            cifs = enac1files.epfl.ch
            error_msg = Error, you are not connected to the intranet of EPFL. Run a VPN client to be able to mount this resource.

            [realm]
            name = EPFL
            domain = INTRANET
            username = bancal

            [CIFS_mount]
            name = private
            label = bancal@files9
            require_network = Epfl
            realm = EPFL
            server_name = files9.epfl.ch
            server_path = data/bancal
            local_path = {MNT_DIR}/bancal_on_files9
            #    {MNT_DIR}
            #    {HOME_DIR}
            #    {DESKTOP_DIR}
            #    {LOCAL_USERNAME}
            #    {LOCAL_GROUPNAME}
            bookmark = false
            #    default : False
            Linux_CIFS_method = gvfs
            #    mount.cifs : Linux's mount.cifs (requires sudo ability)
            #    gvfs : Linux's gvfs-mount
            Linux_mountcifs_filemode = 0770
            Linux_mountcifs_dirmode = 0770
            Linux_mountcifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm
            Linux_gvfs_symlink = yes
            #    Enables the creation of a symbolic link to "local_path" after mount with gvfs method.
            #    default : True
            Windows_letter = Z:
            #    Drive letter to use for the mount

        And return cfg as
            {'CIFS_mount': {
              'private': {
               'Linux_CIFS_method': 'gvfs',
               'Linux_gvfs_symlink': True,
               'Linux_mountcifs_dirmode': '0770',
               'Linux_mountcifs_filemode': '0770',
               'Linux_mountcifs_options': 'rw,nobrl,noserverino,iocharset=utf8,sec=ntlm',
               'Windows_letter': 'Z:',
               'label': 'bancal@files9',
               'local_path': '{MNT_DIR}/bancal_on_files9',
               'realm': 'EPFL',
               'server_name': 'files9.epfl.ch',
               'server_path': 'data/bancal',
               'bookmark': False,
               'require_network': 'Epfl'}},
             'network': {
              'Internet': {
               'ping': ['www.epfl.ch', 'enacit.epfl.ch'],
               'error_msg': 'Error, you are not connected to the network. You won't be able to mount this resource.'
              },
              'Epfl': {
               'ping': ['files0.epfl.ch', 'files1.epfl.ch', 'files8.epfl.ch', 'files9.epfl.ch'],
               'parent': 'Internet',
               'error_msg': 'Error, you are not connected to the intranet of EPFL. Run a VPN client to be able to mount this resource.'
              }
             }
             'global': {
              'username': 'bancal',
              'Linux_CIFS_method': 'gvfs',
              'Linux_gvfs_symlink': True,
              'Linux_mountcifs_dirmode': '0770',
              'Linux_mountcifs_filemode': '0770',
              'Linux_mountcifs_options': 'rw,nobrl,noserverino,iocharset=utf8,sec=ntlm'},
             'realm': {
              'EPFL': {
               'domain': 'INTRANET',
               'username': 'bancal'}}}

       If >50% of the lines have unexpected content ... then raise ConfigException()
    """

    def save_current_section():
        try:
            name = current_section_values["name"]
            del(current_section_values["name"])
            cfg.setdefault(current_section_name, {})
            cfg[current_section_name].setdefault(name, {})
            cfg[current_section_name][name].update(current_section_values)
        except KeyError:
            Output.error("Expected name option not found at line {}. Skipping that section.".format(section_line_nb))

    multi_entries_sections = ("CIFS_mount", "realm", "network")
    allowed_options = {
        "global": (
            "username",
            "entries_order",
            "require_network",
            "realm",
            "Linux_CIFS_method",
            "Linux_mountcifs_filemode",
            "Linux_mountcifs_dirmode",
            "Linux_mountcifs_options",
            "Linux_gvfs_symlink",
        ),
        "CIFS_mount": (
            "name",
            "label",
            "require_network",
            "realm",
            "unc",
            "server_name",
            "server_path",
            "local_path",
            "bookmark",
            "Linux_CIFS_method",
            "Linux_mountcifs_filemode",
            "Linux_mountcifs_dirmode",
            "Linux_mountcifs_options",
            "Linux_gvfs_symlink",
            "Windows_letter",
        ),
        "realm": (
            "name",
            "domain",
            "username",
        ),
        "network": (
            "name",
            "parent",
            "ping",
            "cifs",
            "error_msg",
        )
    }

    cfg = {}
    current_section_name = ""
    current_section_values = {}
    line_nb = 0
    section_line_nb = 0
    nb_unexpected_lines = 0
    for line in src.readlines():
        if type(line) == bytes:
            line = bytes_decode(line)
        line_nb += 1
        l = line
        l = re.sub(r"#.*", "", l)  # remove comments
        l = l.strip()  # remove white spaces
        if l == "":
            continue
        # Output.debug(l)

        # New section
        if l.startswith("["):
            try:
                new_section = re.match(r"\[(\S+)\]$", l).groups()[0]
            except AttributeError:
                Output.error("Unexpected content at line {}:\n{}".format(line_nb, line))
                nb_unexpected_lines += 1
                continue
            if current_section_name in multi_entries_sections and current_section_values != {}:
                # Save previous section content
                save_current_section()
            if new_section in allowed_options:
                current_section_name = new_section
                current_section_values = {}
                section_line_nb = line_nb
            else:
                Output.error("Unexpected section name '{}' at line {}:\n{}".format(new_section, line_nb, line))
                current_section_name = ""
                nb_unexpected_lines += 1
            continue

        if current_section_name == "":
            Output.error("Unexpected content at line {}:\n{}".format(line_nb, line))
            nb_unexpected_lines += 1
            continue

        # New option
        try:
            k, v = re.match(r"([^=]*)=(.*)", l).groups()
            k, v = k.strip(), v.strip()
        except AttributeError:
            nb_unexpected_lines += 1
            continue
        if k not in allowed_options[current_section_name]:
            Output.error("Unexpected option at line {}:\n{}".format(line_nb, line))
            nb_unexpected_lines += 1
            continue

        try:
            if current_section_name in multi_entries_sections:
                # This is a multi entries section type
                if current_section_name == "network" and k == "ping":
                    # network.ping is a list
                    current_section_values.setdefault(k, [])
                    current_section_values[k].append(validate_value(k, v))
                elif current_section_name == "network" and k == "cifs":
                    # network.cifs is a list
                    current_section_values.setdefault(k, [])
                    current_section_values[k].append(validate_value(k, v))
                else:
                    # other are literals
                    current_section_values[k] = validate_value(k, v)
            else:
                # This is a single entry section type
                cfg.setdefault(current_section_name, {})[k] = validate_value(k, v)
        except ConfigException as e:
            Output.error(str(e))

        # Output.debug("'{}' = '{}'".format(k, v))

    if current_section_name in multi_entries_sections and current_section_values != {}:
        # Save last section content
        save_current_section()

    if nb_unexpected_lines > (line_nb / 2):
        Output.warning("Too many unexpected lines found. Skipping this source.")
        raise ConfigException("Too many unexpected lines found. Skipping this source.")

    return cfg


def validate_config(cfg):
    """
    Validates that there is everything necessary in the config to do the job.
    Will output error message otherwise
    """

    def expect_option(entry, section, option, alert=True, ored_options=None):
        if option not in entry:
            if alert:
                if ored_options is not None:
                    option = "' or '".join(ored_options)
                Output.error("expected '{}' option in {} section.".format(option, section))
            return False
        return True

    invalid_cifs_m = []
    invalid_realm = []
    invalid_network = []
    expected_realms = {}
    expected_networks_by_CIFS_m = {}
    for m_name in cfg.get("CIFS_mount", {}):
        # If not defined, deduct local_path from m_name
        if "local_path" not in cfg["CIFS_mount"][m_name]:
            cfg["CIFS_mount"][m_name]["local_path"] = "{MNT_DIR}/" + m_name
        
        # If not defined, deduct label from m_name
        if "label" not in cfg["CIFS_mount"][m_name]:
            cfg["CIFS_mount"][m_name]["label"] = m_name
        
        # If specified, extract server_name and server_path from unc
        if "unc" in cfg["CIFS_mount"][m_name]:
            m = re.match(r"[\\/]{2}([^\\/]+)[\\/](.*)$", cfg["CIFS_mount"][m_name]["unc"])
            if m:
                cfg["CIFS_mount"][m_name]["server_name"] = m.group(1)
                cfg["CIFS_mount"][m_name]["server_path"] = m.group(2)
            else:
                Output.error("unrecognized 'unc' option in CIFS_mount section ({}).".format(cfg["CIFS_mount"][m_name]["unc"]))
        
        is_ok = (
            expect_option(cfg["CIFS_mount"][m_name], "CIFS_mount", "label") and
            expect_option(cfg["CIFS_mount"][m_name], "CIFS_mount", "server_name") and
            expect_option(cfg["CIFS_mount"][m_name], "CIFS_mount", "server_path") and
            expect_option(cfg["CIFS_mount"][m_name], "CIFS_mount", "local_path") and
            (expect_option(cfg.get("global", {}), "CIFS_mount", "realm", alert=False) or
             expect_option(cfg["CIFS_mount"][m_name], "CIFS_mount", "realm"))
        )
        if is_ok:
            if "realm" in cfg["CIFS_mount"][m_name]:
                realm = cfg["CIFS_mount"][m_name]["realm"]
            else:
                realm = cfg["global"]["realm"]
            expected_realms.setdefault(realm, [])
            expected_realms[realm].append(m_name)
            net = cfg["CIFS_mount"][m_name].get("network")
            if net is not None:
                expected_networks_by_CIFS_m.setdefault(net, [])
                expected_networks_by_CIFS_m[net].append(m_name)
        else:
            Output.error("Removing incomplete CIFS_mount '{}'.".format(m_name))
            invalid_cifs_m.append(m_name)

    for realm in expected_realms:
        if realm not in cfg.get("realm", []):
            Output.error("Missing realm '{}'.".format(realm))
            for m_name in expected_realms[realm]:
                Output.error("Removing CIFS_mount '{}' depending on realm '{}'.".format(m_name, realm))
                invalid_cifs_m.append(m_name)

    for realm in cfg.get("realm", []):
        is_ok = (
            expect_option(cfg["realm"][realm], "realm", "username") and
            expect_option(cfg["realm"][realm], "realm", "domain")
        )
        if not is_ok:
            Output.error("Removing incomplete realm '{}'.".format(realm))
            invalid_realm.append(realm)
            for m_name in expected_realms.get(realm, []):
                Output.error("Removing CIFS_mount '{}' depending on realm '{}'.".format(m_name, realm))
                invalid_cifs_m.append(m_name)
    
    for net in expected_networks_by_CIFS_m:
        if net not in cfg.get("network", []):
            Output.error("Missing network '{}'.".format(net))
            for m_name in expected_networks_by_CIFS_m[net]:
                Output.error("Removing 'require_network' to CIFS_mount '{}'.".format(m_name))
                del(cfg["CIFS_mount"][m_name]["require_network"])
                
    for net in cfg.get("network", []):
        is_ok = (
            (expect_option(cfg["network"][net], "network", "ping", alert=False) or
             expect_option(cfg["network"][net], "network", "cifs", ored_options=("ping", "cifs"))) and
            expect_option(cfg["network"][net], "network", "error_msg")
        )
        if not is_ok:
            Output.error("Removing incomplete network '{}'.".format(net))
            invalid_network.append(net)
    
    had_change = True
    while had_change:
        had_change = False
        for net in cfg.get("network", []):
            if net in invalid_network:
                continue
            parent_network = cfg["network"][net].get("parent")
            if parent_network is None:
                continue
            if (
             parent_network in invalid_network or 
             parent_network not in cfg["network"]):
                invalid_network.append(net)
                had_change = True

    for m_name in invalid_cifs_m:
        del(cfg["CIFS_mount"][m_name])

    for realm in invalid_realm:
        del(cfg["realm"][realm])

    for net in invalid_network:
        del(cfg["network"][net])
        for m_name in expected_networks_by_CIFS_m.get(net, []):
            Output.error("Removing 'require_network' to CIFS_mount '{}'.".format(m_name))
            del(cfg["CIFS_mount"][m_name]["require_network"])

    return cfg


def main():
    with Output():
        cfg = get_config()
        Output.debug(pprint.pformat(cfg))

if __name__ == "__main__":
    main()
