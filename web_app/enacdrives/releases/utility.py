import re

from releases import models as mo


def validate_input(data_source, field_name, data_type):
    """
    Validates data received from HTTP requests
    """
    if data_type == "os":
        data = data_source(field_name, "")
        data = data.lower()
        for os in mo.Arch.OS_CHOICES:
            if data == os[1].lower():
                return os[0]
        raise Exception("Invalid os '{0}'".format(data))

    if data_type == "int":
        data = data_source(field_name, "")
        if type(data) == int:
            return data
        else:
            try:
                return int(data)
            except:
                raise Exception("Invalid integer '{0}'".format(data))

    if data_type == "bool":
        data = data_source(field_name, "")
        if data == "False" or data == "false" or data == "0" or data == 0:
            return False
        elif data:
            return True
        else:
            return False

    raise Exception("Unknown data_type '{0}'".format(data_type))


def parse_uploaded_file(filename):
    """
    returns {
        "release_number":"x.y.z",
        "os":mo.Arch.OS_WIN|mo.Arch.OS_LIN|mo.Arch.OS_OSX
    }
    """
    answer = {
        "release_number": mo.Arch.OS_WIN,
        "os": "Unknown",
    }

    # OS
    if filename.endswith("exe"):
        answer["os"] = mo.Arch.OS_WIN
    elif filename.endswith("deb"):
        answer["os"] = mo.Arch.OS_LIN
    elif filename.endswith("dmg") or filename.endswith("pkg"):
        answer["os"] = mo.Arch.OS_OSX
    else:
        raise Exception("Unrecognized OS in {}".format(filename))

    # Release Number
    m = re.search(r"[-_]([0-9.]+)(-[0-9+])?[-_.][^0-9]", filename)
    if m:
        answer["release_number"] = m.groups()[0]
    else:
        raise Exception("Unrecognized release number in {}".format(filename))

    return answer
