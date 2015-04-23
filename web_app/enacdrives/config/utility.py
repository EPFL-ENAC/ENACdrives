import re
from django.utils.encoding import smart_text


def validate_input(data_source, data_type):
    """
    Validates data received from HTTP requests
    """
    if data_type == "username":
        data = data_source(data_type, "")
        data = smart_text(data, errors="ignore")
        data = data.lower()
        all_str = re.findall(r"\w", data)
        data = "".join(all_str)
        return data
    raise Exception("Unknown data_type '{0}'".format(data_type))


def grep_mount_names(config_str):
    """
    Parse config_str and return every *_mount names
    """
    save_name = False
    names = []
    for l in config_str.split("\n"):
        l = l.strip()
        if l.startswith("[CIFS_mount]"):
            save_name = True
            continue
        
        try:
            k, v = re.match(r"([^=]*)=(.*)", l).groups()
            k, v = k.strip(), v.strip()
        except AttributeError:
            continue
        if save_name and k == "name":
            names.append(v)
            save_name = False
    
    return names
