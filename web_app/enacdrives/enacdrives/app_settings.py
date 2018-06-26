import os

SERVICE_NAME = "ENACDRIVES"

RELEASE_VERSION = "0.3.3"
RELEASE_DATE = "2018-06-26"

SERVER_HOSTNAME = os.uname()[1]

if SERVER_HOSTNAME == "enacit1sbtest4":
    CONTEXT = "dev"
    from enacdrives.settings_enacit1sbtest4 import *
if SERVER_HOSTNAME == "enacit1pc4":
    CONTEXT = "dev"
    from enacdrives.settings_enacit1pc4 import *
if SERVER_HOSTNAME == "enacit1vm1":
    CONTEXT = "prod"
    from enacdrives.settings_enacit1vm1 import *
