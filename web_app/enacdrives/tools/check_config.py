# Bancal Samuel

# Check that prod config is matching the shares available on NAS3

# Requirement :
# ./enacmoni.cred

# # pip install pysmb


import os
import re
import sys
import subprocess

# import pickle
# from smb.SMBConnection import SMBConnection
# # from .util import getConnectionInfo
# # from nose.tools import with_setup
# from smb import smb_structs
from django.core.wsgi import get_wsgi_application

os.environ["DJANGO_SETTINGS_MODULE"] = "enacdrives.settings"
my_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(my_path)
application = get_wsgi_application()


# my_path = '/home/sbancal/Projects/ENACdrives/web_app/enacdrives'  # TODO REMOVE THIS

# CRED_FILE = os.path.join(my_path, 'enacmoni.cred')
# with open(CRED_FILE, 'rb') as f:
#     USER = pickle.load(f)
#
#
# smb_structs.SUPPORT_SMB2 = True
# conn = SMBConnection(USER['username'], USER['password'], 'LOCAL-PC', 'enac1files.epfl.ch', USER['domain'], use_ntlm_v2=True, sign_options=SMBConnection.SIGN_WHEN_SUPPORTED, is_direct_tcp=True)
# connected = conn.connect('ENAC1FILES', 445)
# conn.listShares(timeout=30)
# conn.close()


from config import models as mo


CIFS_UNIT_CONFIG = (
    {
        "server": "enac1files.epfl.ch",
        "config name": "NAS3 Files",
        "shares_to_ignore": (
            r".*\$$",  # all shares finished by a "$"
            r"academic-alpole",
            r"antfr-ge",
            r"biomining",
            r"camipro-2018",
            r"digiwalls-ibois-eesd",
            r"ecombine",
            r"enac-prom-acad",
            r"geome",
            r"gestion-unites-enac",
            r"icarus",
            r"infra-sculpture",
            r"ivea",
            r"lablysi",
            r"phlebicite",
            r"proj-.*$",  # all proj- shares
            r"s_pine",
            r"sar-web",
            r"si_topsolid_debug_files",
            r"technologie_du_bati_2",
            r"technologie_du_bati_4",
            r"uhna",
            r"vaertical",
            r"wanhabitats",
        ),
        "units_to_ignore": (),
    },
    {
        "server": "enac1arch.epfl.ch",
        "config name": "NAS3 Arch",
        "shares_to_ignore": (
            r".*\$$",  # all shares finished by a "$"
            r"enac-webcom",
            r"geome",
            r"oldlabs",
            r"sar-winprofiles",
            r"sgc-winprofiles",
            r"ssie-salles",
        ),
        "units_to_ignore": (),
    },
    {
        "server": "enac1raw.epfl.ch",
        "config name": "NAS3 Raw",
        "shares_to_ignore": (r".*\$$",),  # all shares finished by a "$"
        "units_to_ignore": (),
    },
    {
        "server": "enac2raw.epfl.ch",
        "config name": "NAS3 Raw2",
        "shares_to_ignore": (r".*\$$",),  # all shares finished by a "$"
        "units_to_ignore": (),
    },
)

CREDENTIALS_FILE = os.path.join(my_path, "enacmoni.cred")


def list_smb_shares(cfg):
    shares = []
    cmd = ["smbclient", "-A", CREDENTIALS_FILE, "-L", cfg["server"], "-m", "SMB3"]
    output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()

    # parse output
    for line in output.split("\n"):
        match = re.match(r"\s*(\S+)\s+Disk\s.*$", line)
        if match:
            valid_share = True
            share = match.group(1).lower()
            for filter_out in cfg["shares_to_ignore"]:
                if re.match(filter_out, share):
                    valid_share = False
            if valid_share:
                shares.append(share)

    return set(shares)


def check_config(cfg):
    Output.write("Checking {}: ".format(cfg["config name"]), end="")
    shares = list_smb_shares(cfg)
    cfg["shares"] = shares
    c = mo.Config.objects.get(name=cfg["config name"])
    c_units = set([u.name.lower() for u in c.epfl_units.all()])

    missing = shares - c_units
    too_much = c_units - shares
    if len(missing) != 0:
        Output.error("Error. Missing units: {}".format(list(missing)))
    if len(too_much) != 0:
        Output.error("Error. Too much units: {}".format(list(too_much)))
    if len(missing) + len(too_much) == 0:
        Output.write("Units for this filer are correctly configured.")
    Output.write()


class Output:
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
