#!/usr/bin/env python3

# Bancal Samuel

# Offers main CLI

import datetime
from utility import Output, CONST


def main_CLI():
    Output.write()
    Output.write("*"*10 + " " + str(datetime.datetime.now()) + " " + "*"*10)

    Output.write("Detected OS : " + CONST.OS_DISTRIB + " " + CONST.OS_SYS + " " + CONST.OS_VERSION)
    Output.write("Local username:" + CONST.LOCAL_USERNAME)
    Output.write("Local groupname:" + CONST.LOCAL_GROUPNAME)
    Output.write("Local uid:" + str(CONST.LOCAL_UID))
    Output.write("Local gid:" + str(CONST.LOCAL_GID))
    Output.write("Home dir:" + CONST.HOME_DIR)
