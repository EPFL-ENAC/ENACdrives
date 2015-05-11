from releases import models as mo


def validate_input(data_source, data_type):
    """
    Validates data received from HTTP requests
    """
    if data_type == "os":
        data = data_source(data_type, "")
        data = data.lower()
        for os in mo.Installer.OS_CHOICES:
            if data == os[1].lower():
                return os[0]
        raise Exception("Invalid os '{0}'".format(data))
    raise Exception("Unknown data_type '{0}'".format(data_type))
