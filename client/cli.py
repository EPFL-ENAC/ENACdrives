#!/usr/bin/env python3

# Bancal Samuel

# Offers main CLI

import datetime
from utility import Output, CONST


def main_CLI(args):
    Output.verbose("*"*10 + " " + str(datetime.datetime.now()) + " " + "*"*10)
    Output.verbose("ENACdrives " + CONST.FULL_VERSION)
    Output.verbose("Detected OS : " + CONST.OS_DISTRIB + " " + CONST.OS_SYS + " " + CONST.OS_VERSION)
    Output.debug("LOCAL_USERNAME:" + CONST.LOCAL_USERNAME)
    Output.debug("LOCAL_GROUPNAME:" + CONST.LOCAL_GROUPNAME)
    Output.debug("LOCAL_UID:" + str(CONST.LOCAL_UID))
    Output.debug("LOCAL_GID:" + str(CONST.LOCAL_GID))
    Output.debug("HOME_DIR:" + CONST.HOME_DIR)
    Output.debug("USER_CONF_FILE:" + CONST.USER_CONF_FILE)
    Output.debug("RESOURCES_DIR:" + CONST.RESOURCES_DIR)
    Output.br()
