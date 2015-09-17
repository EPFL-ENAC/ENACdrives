import re
import logging
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
        # all_str = re.findall(r"[\w\.@]", data) # needed for username=a.s.bancal@bluewin.ch (test)
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


def conf_filter(data, iteration_num):
    """
    will replace lines like
    0.Windows_letter = Y:
    1.Windows_letter = X:
    2.Windows_letter = W:
    
    to "Windows_letter = Y:" when iteration_num == 0
    to "Windows_letter = X:" when iteration_num == 1
    to "Windows_letter = W:" when iteration_num == 2
    to nothing otherwise
    
    Other example with "*" :
    0.Windows_letter = Y:
    *.Windows_letter = X:
    
    to "Windows_letter = Y:" when iteration_num == 0
    to "Windows_letter = X:" otherwise (which is not a good idea of course)
    """
    # debug_logger = logging.getLogger("debug")
    iteration_num = str(iteration_num)
    
    def close_section(special_lines, result):
        # debug_logger.debug("close.{} : {}".format(iteration_num, special_lines))
        if len(special_lines) == 0:
            return
        for k in special_lines:
            if iteration_num in special_lines[k]:
                result.append(special_lines[k][iteration_num])
            elif "*" in special_lines[k]:
                result.append(special_lines[k]["*"])
        result.append("")

    lines = data.split("\n")
    special_lines = {}
    result = []
    for l in lines:
        l = l.strip()
        if l == "":
            continue
        if l.startswith("["):
            close_section(special_lines, result)
            special_lines = {}
        m = re.match(r"([\d*]*)\.(([^=]*)=.*)$", l)
        if m:
            i = m.group(1).strip()
            k = m.group(3).strip()
            v = m.group(2).strip()
            # debug_logger.debug("found {} . {} . {}".format(i, k, v))
            special_lines.setdefault(k, {})
            special_lines[k][i] = v
        else:
            result.append(l)
    close_section(special_lines, result)
    
    return "\n".join(result)
