#!/usr/bin/env python3

# Bancal Samuel

# Offers Config parsing from different sources

import re
import pprint
from utility import Output


def validate_value(option, value):
    if option == "Linux_CIFS_method":
        if value not in ("gvfs", "mount.cifs"):
            raise Exception("Error, Linux_CIFS_method has to be 'gvfs' or 'mount.cifs'.")
    elif option in ("server_path", "local_path"):
        value = re.sub(r"\\", "/", value)
    elif option == "domain":
        value = value.upper()
    elif option == "username":
        value = value.lower()
    elif option == "server_name":
        if bool(re.search(r"[^a-zA-Z0-9.-]", value)):
            raise Exception("Error, server_name can only contain alphanumeric, and '-' and '.' symbols.")
    elif option in ("stared", "Linux_gvfs_symlink"):
        value = str(value).lower()
        return value in ("yes", "y", "true", "1", "on")
    elif option == "Windows_letter":
        value = value.upper()
        if not re.match(r"[A-Z]:$", value):
            raise Exception("Error, Windows drive letter has to be on the form 'Z:'.")
    return value


def read_config_source(src):
    """
        Readlines on src
            [global]
            Linux_CIFS_method = gvfs
            
            [realm]
            name = EPFL
            domain = INTRANET
            username = bancal

            [CIFS_mount]
            name = private
            label = bancal@files9
            realm = EPFL
            server_name = files9.epfl.ch
            server_path = data/bancal
            local_path = {MNT_DIR}/bancal_on_files9
            #    {MNT_DIR}
            #    {HOME_DIR}
            #    {DESKTOP_DIR}
            #    {LOCAL_USERNAME}
            #    {LOCAL_GROUPNAME}
            stared = false
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
            {'CIFS_mount': [{'Linux_CIFS_method': 'gvfs',
                             'Linux_gvfs_symlink': True,
                             'Linux_mountcifs_dirmode': '0770',
                             'Linux_mountcifs_filemode': '0770',
                             'Linux_mountcifs_options': 'rw,nobrl,noserverino,iocharset=utf8,sec=ntlm',
                             'Windows_letter': 'Z:',
                             'label': 'bancal@files9',
                             'local_path': '{MNT_DIR}/bancal_on_files9',
                             'name': 'private',
                             'realm': 'EPFL',
                             'server_name': 'files9.epfl.ch',
                             'server_path': 'data/bancal',
                             'stared': False}],
             'global': {'Linux_CIFS_method': 'gvfs'},
             'realm': [{'domain': 'INTRANET', 'name': 'EPFL', 'username': 'bancal'}]}
    """
    multi_entries_sections = ("CIFS_mount", "realm")
    allowed_options = {
        "global": ("Linux_CIFS_method", ),
        "CIFS_mount": (
            "name",
            "label",
            "realm",
            "server_name",
            "server_path",
            "local_path",
            "stared",
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
    }
    
    cfg = {}
    current_section = ""
    current_entry = {}
    line_nb = 0
    for line in src.readlines():
        line_nb += 1
        l = line
        l = re.sub(r"#.*", "", l)  # remove comments
        l = l.strip()  # remove white spaces
        if l == "":
            continue
        # Output.write(l)
        
        # New section
        if l.startswith("["):
            try:
                new_section = re.match(r"\[(\S+)\]$", l).groups()[0]
            except AttributeError:
                Output.write("Error : Unexpected content at line {0}:\n{1}".format(line_nb, line))
                continue
            if current_section in multi_entries_sections and current_entry != {}:
                # Save previous section content
                cfg.setdefault(current_section, []).append(current_entry)
            if new_section in allowed_options:
                current_section = new_section
                current_entry = {}
            else:
                Output.write("Error : Unexpected section name '{0}' at line {1}:\n{2}".format(new_section, line_nb, line))
                current_section = ""
            continue
        
        if current_section == "":
            Output.write("Error : Unexpected content at line {0}:\n{1}".format(line_nb, line))
            continue
        
        # New option
        try:
            k, v = re.match(r"([^=]*)=(.*)", l).groups()
            k, v = k.strip(), v.strip()
        except AttributeError:
            continue
        if k not in allowed_options[current_section]:
            Output.write("Error : Unexpected option at line {0}:\n{1}".format(line_nb, line))
            continue
        
        try:
            if current_section in multi_entries_sections:
                # This is a multi entries section type
                current_entry[k] = validate_value(k, v)
            else:
                # This is a single entry section type
                cfg.setdefault(current_section, {})[k] = validate_value(k, v)
        except Exception as e:
            Output.write(str(e))
            
        # Output.write("'{0}' = '{1}'".format(k, v))
    
    if current_section in multi_entries_sections and current_entry != {}:
        # Save last section content
        cfg.setdefault(current_section, []).append(current_entry)
    
    return cfg


def main():
    with Output():
        f_name = "test.conf"
        with open(f_name, "r") as f:
            cfg = read_config_source(f)
            Output.write(pprint.pformat(cfg))

if __name__ == "__main__":
    main()
