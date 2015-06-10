#!/usr/bin/env python3

# Bancal Samuel

# Offers main CLI

import datetime
from utility import Output, CONST


def main_CLI():
    Output.br()
    Output.info2("*"*10 + " " + str(datetime.datetime.now()) + " " + "*"*10)

    Output.info2("Detected OS : " + CONST.OS_DISTRIB + " " + CONST.OS_SYS + " " + CONST.OS_VERSION)
    Output.info2("Local username:" + CONST.LOCAL_USERNAME)
    Output.info2("Local groupname:" + CONST.LOCAL_GROUPNAME)
    Output.info2("Local uid:" + str(CONST.LOCAL_UID))
    Output.info2("Local gid:" + str(CONST.LOCAL_GID))
    Output.info2("Home dir:" + CONST.HOME_DIR)
