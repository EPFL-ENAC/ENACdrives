import re
from django.utils.encoding import smart_text


def validate_input(data_source, data_type):
    if data_type == "username":
        data = data_source(data_type, "")
        data = smart_text(data, errors="ignore")
        data = data.lower()
        all_str = re.findall(r"\w", data)
        data = "".join(all_str)
        return data
    raise Exception("Unknown data_type '{0}'".format(data_type))
