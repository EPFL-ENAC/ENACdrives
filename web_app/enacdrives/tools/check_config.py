# Bancal Samuel
# 2015-06-03

# Check that prod config is matching the shares available on NAS2/NAS3

# Requirement :
# sudo vi /etc/samba/smb.conf
# snip
# [global]
#   workgroup = INTRANET
# snap


import os
import re
import sys
import subprocess

from django.core.wsgi import get_wsgi_application

os.environ["DJANGO_SETTINGS_MODULE"] = "enacdrives.settings"
my_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(my_path)
application = get_wsgi_application()

from config import models as mo


CIFS_UNIT_CONFIG = (
    {"server": "enacfiles1.epfl.ch",
     "config name": "NAS2 Tier1"},
    {"server": "enacfiles2.epfl.ch",
     "config name": "NAS2 Tier2"},
    {"server": "enacfiles4.epfl.ch",
     "config name": "NAS2 Tier4"},
    {"server": "enac1files.epfl.ch",
     "config name": "NAS3 Files"},
)

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "enacmoni.credentials")
SMB_SHARES_FILTER_OUT = (
    r'.*\$$',  # all shares finished by a "$"
    r'enac-data.*-t.*',  # all shares like enac-data*-t*
)


def list_smb_shares(servername):
    shares = []
    cmd = ["smbclient", "-A", CREDENTIALS_FILE, "-L", servername, "-W", "INTRANET"]
    output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()
    
    # parse output
    for line in output.split("\n"):
        match = re.match(r'\s*(\S+)\s+Disk\s.*$', line)
        if match:
            valid_share = True
            share = match.group(1)
            for filter_out in SMB_SHARES_FILTER_OUT:
                if re.match(filter_out, share):
                    valid_share = False
                # Special transition NAS2 -> NAS3
                # NAS2 used to serve a share "cdt-enac" which should be named "cdt". Skip it.
                if share.lower() == "cdt-enac":
                    valid_share = False
            if valid_share:
                shares.append(share.lower())
    
    return set(shares)


def check_config(cfg):
    Output.write("Checking {}: ".format(cfg["config name"]), end="")
    shares = list_smb_shares(cfg["server"])
    cfg["shares"] = shares
    c = mo.Config.objects.get(name=cfg["config name"])
    c_units = set([u.name.lower() for u in c.epfl_units.all()])
    # Special transition NAS2 -> NAS3 :
    # remove all still existing NAS2 shares to found NAS3 shares (they are not migrated yet).
    if cfg["config name"] == "NAS3 Files":
        for s in CIFS_UNIT_CONFIG[0]["shares"]:
            try:
                shares.remove(s)
            except KeyError:
                pass
    
    missing = shares - c_units
    too_much = c_units - shares
    if len(missing) != 0:
        Output.error("Error. Missing units: {}".format(list(missing)))
    if len(too_much) != 0:
        Output.error("Error. Too much units: {}".format(list(too_much)))
    if len(missing) + len(too_much) == 0:
        Output.write("Units for are correctly configured.")
    Output.write()


class Output():
    def __init__(self, dest=None):
        if dest is not None:
            self.output = dest
        else:
            self.output = sys.stdout
        self.status = 0
    
    def __enter__(self):
        Output.set_instance(self)
        return self

    def __exit__(self, typ, value, traceback):
        Output.del_instance()

    def do_write(self, msg):
        self.output.write(msg)
    
    def do_warning(self, msg):
        self.output.write(msg)
        self.status = max(self.status, 1)
    
    def do_error(self, msg):
        self.output.write(msg)
        self.status = max(self.status, 2)
    
    def get_status(self):
        return self.status

    @classmethod
    def set_instance(cls, instance):
        cls.instance = instance

    @classmethod
    def del_instance(cls):
        cls.instance = None

    @classmethod
    def write(cls, msg="", end="\n"):
        cls.instance.do_write(msg + end)

    @classmethod
    def warning(cls, msg="", end="\n"):
        cls.instance.do_warning(msg + end)

    @classmethod
    def error(cls, msg="", end="\n"):
        cls.instance.do_error(msg + end)


if __name__ == "__main__":
    with Output() as o:
        for cfg in CIFS_UNIT_CONFIG:
            check_config(cfg)
        status = o.get_status()
    sys.exit(status)
