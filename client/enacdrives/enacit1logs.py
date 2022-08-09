#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Bancal Samuel - ENACIT1
# 100922
# 101210

# ! Modify :  ~/Projects/enacit1logs/tools/enacit1logs.py !

# # ! Copied to ~/Documents/projets/lucid_ssie/customize_lucid_ssie/resources/usr/local/bin/enacit1logs.py !
# # ! by        ~/Documents/projets/lucid_ssie/customize_lucid_ssie/build_customization_utilities.sh !
#
# # ! Copied to ~/Projects/precise_ssie/customize_precise_ssie/root/usr/local/bin/enacit1logs.py !
# # ! by        ~/Projects/precise_ssie/tools/build_precise_ssie_tarball.sh !

# # ! Copied to ~/Projects/trusty_ssie/customize_trusty_ssie/root/usr/local/bin/enacit1logs.py !
# # ! by        ~/Projects/trusty_ssie/tools/build_trusty_ssie_tarball.sh !

# ! Copied to ~/Projects/xenial-ssie/customize_xenial-ssie/features/global/root/usr/local/bin/enacit1logs.py !
# ! by        ~/Projects/xenial-ssie/tools/build_xenial-ssie_tarball.sh !

# ! Copied to /usr/local/bin/enacit1logs.py !
# ! Copied to /home/bancal/server_basics/usr/local/bin/enacit1logs.py !
# ! By hand ;) !

# ! Copied to ~/Projects/ENACdrives/client/enacit1logs.py !
# ! By hand ;) ... but 2to3 !


# Implemented in :
# - SSIE room
# - ENACdrives
# - Duplicity backups

import sys
import xmlrpc.client
import socket
import getopt

TEST = False

SERVERNAME = "enacit1logs.epfl.ch"
if TEST:
    SERVERURL = "http://%s/enacit1logs_test/xml_rpc" % SERVERNAME
else:
    SERVERURL = "http://%s/enacit1logs/xml_rpc" % SERVERNAME


class SendLogException(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg


def usage():
    print(
        """%s  -h|--help
%s [-n|--dryrun] [-t|--tag one_tag]* [-u|--user "username"] [-m|--message "one message"]
%s                                                          [-f|--file one_file.txt]
%s                                                          [-f|--file -] # Read from stdin"""
        % (
            sys.argv[0],
            " " * len(sys.argv[0]),
            " " * len(sys.argv[0]),
            " " * len(sys.argv[0]),
        )
    )


def ping():
    try:
        rpc = xmlrpc.client.ServerProxy(SERVERURL)
        return rpc.ping()
    except (socket.error, xmlrpc.client.ProtocolError) as inst:
        raise SendLogException("Server %s is not responding!\n%s" % (SERVERNAME, inst))


def send(message, tags, user=""):
    try:
        rpc = xmlrpc.client.ServerProxy(SERVERURL)
        return rpc.post_log(message, tags, user)
    except (socket.error, xmlrpc.client.ProtocolError) as inst:
        raise SendLogException("Server %s is not responding!\n%s" % (SERVERNAME, inst))


if __name__ == "__main__":
    options = {"n": False, "t": [], "u": ""}
    # Read args
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hnt:u:m:f:",
            ["help", "dryrun", "tag=", "user=", "message=", "file="],
        )
    except getopt.GetoptError:
        usage()
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-n", "--dryrun"):
            options["n"] = True
        elif opt in ("-t", "--tag"):
            options["t"].append(arg)
        elif opt in ("-u", "--user"):
            options["u"] = arg
        elif opt in ("-m", "--message"):
            options["m"] = arg
        elif opt in ("-f", "--file"):
            options["f"] = arg
        else:
            print("Unrecognised option : %s -> %s" % (opt, arg))

    # Check options
    if not options["n"]:
        if not ("m" in options) ^ ("f" in options):
            print("Error: one --message or --file has to be given")
            usage()
            sys.exit(1)

    # Get Message
    message = ""
    if "m" in options:
        message = options["m"]
    if "f" in options:
        if options["f"] == "-":
            f = sys.stdin
        else:
            f = open(options["f"], "r")
        for line in f.readlines():
            message += line
        f.close()

    if not options["n"] and message == "":
        print("Nothing to send.")
        sys.exit()

    if options["n"]:
        try:
            print("ping ... %s" % ping())
        except SendLogException as inst:
            print("Error pinging server :\n%s" % inst.msg)
            sys.exit(1)
    else:
        try:
            send(message, options["t"], options["u"])
        except SendLogException as inst:
            print("Error sending message to server :\n%s" % inst.msg)
            sys.exit(1)
