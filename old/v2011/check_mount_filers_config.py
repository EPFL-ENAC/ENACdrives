#!/usr/bin/env python

# Bancal Samuel
# 2011.11.03
# 2012.02.22

# source : /home/bancal/Projects/mount_filers/check_mount_filers_config.py
# deploy to enacitmon1 :
#   scp bancal@salsa:Projects/mount_filers/check_mount_filers_config.py /usr/local/nagios/libexec/check_mount_filers_config.py
#   sudo scp bancal@salsa:/etc/enacmoni.accred /etc/enacmoni.accred

# Check mount_filer's config for the following points :
# - Tier1, 2, 4 have the right groups associated

from __future__ import with_statement

import sys
import pickle
import signal
import urllib
import pprint
import shlex, subprocess
import re

URL = "http://enacit1adm1.epfl.ch/mount_filers/dir/adm_config_dump/"
URL_TIMEOUT = 1 # seconds

#~ SMBCLIENT_CMD = "smbclient -A /etc/enacmoni.accred -L {server}"
SMB_SHARES_FILTER_OUT = (
    r'.*\$$', # all shares finished by a "$"
    r'enac-data.*-t.*', # all shares like enac-data*-t*
)


def list_smb_shares(servername):
    shares = []
    #~ cmd = SMBCLIENT_CMD.format(server = servername) # not supported in Python 2.5.2 ...
    cmd = "smbclient -A /etc/enacmoni.accred -L %s" % servername
    cmd = shlex.split(cmd)
    proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    output = proc.communicate()[0]
    
    # parse output
    for line in output.split("\n"):
        match = re.match(r'\s*(\S+)\s+Disk\s.*$', line)
        if match:
            valid_share = True
            share = match.group(1)
            for filter_out in SMB_SHARES_FILTER_OUT:
                if re.match(filter_out, share):
                    valid_share = False
            if valid_share:
                shares.append(share.lower())
    
    return set(shares)

REQUISITE = (
    (
        "description", "Group Storage Tier1", # SELECT
        {
            "groups": list_smb_shares("enacfiles1.epfl.ch"), # REQUIRE
        },
    ),
    (
        "description", "Group Storage Tier2",
        {
            "groups": list_smb_shares("enacfiles2.epfl.ch"),
        },
    ),
    (
        "description", "Group Storage Tier4",
        {
            "groups": list_smb_shares("enacfiles4.epfl.ch"),
        },
    ),
)

class MyTimeout(Exception):
    def __init__(self, timeout):
        self.timeout = timeout
        self.timed_out = False
    
    def __enter__(self):
        self.timed_out = False
        self.old_handler = signal.signal(signal.SIGALRM, self.signal_handler)
        signal.alarm(self.timeout)
    
    def __exit__(self, type, value, traceback):
        signal.alarm(0)
        signal.signal(signal.SIGALRM, self.old_handler)
    
    def signal_handler(self, signum, frame):
        self.timed_out = True
        raise self
    
    def __str__(self):
        if self.timed_out :
            return "Instructions lasted more than %d seconds" % self.timeout
        else:
            return "Timeout of %s seconds" % self.timeout

class MyException(Exception):
    pass

#~ def http_get(url): # python > 2.5.2
    #~ try:
        #~ with MyTimeout(URL_TIMEOUT):
            #~ fh = urllib.urlopen(url)
        #~ if fh.code != 200:
            #~ raise MyException("Error. Could not load url %s" % url)
    #~ except (IOError, MyTimeout):
        #~ raise MyException("Error. Could not load url %s" % url)
    #~ 
    #~ return "".join(fh.readlines())

def http_get(url):
    try:
        with MyTimeout(URL_TIMEOUT):
            url_opener = urllib.URLopener()
            fh = url_opener.open(url)
    except (IOError, MyTimeout):
        raise MyException("Error. Could not load url %s" % url)
    
    return "".join(fh.readlines())

def compare(expected, value):
    """
        Compares 2 elements
        type list -> will return msg with "+item" and/or "-item"
        returns bool, msg
    """
    msg = ""
    if expected == value:
        return True, msg
    if type(expected) == type(set()) and type(value) == type(set()):
        msg += "".join(["+ %s\n" % item for item in expected - value])
        msg += "".join(["- %s\n" % item for item in value - expected])
        msg += "Expected : \n%s\n" % ", ".join(expected)
    else:
        msg += "Expected : \n%s" % expected
    return False, msg

def check_config(config):
    success = True
    
    for req in REQUISITE:
        all_match = False
        output = ""
        for conf in config:
            if conf[req[0]] != req[1]:
                continue
            all_match = True
            for key in req[2]:
                match, msg = compare(req[2][key], conf.get(key))
                if not match:
                    output += "Error, %s[%s]; %s :\n%s" % (req[0], req[1], key, msg)
                    all_match = False
        if not all_match:
            success = False
            print "*"*30
            print output
    
    return success

if __name__ == '__main__':
    try:
        config = pickle.loads(http_get(URL))
        success = check_config(config)
        if not success:
            sys.exit(2)
        print "ok"
        sys.exit(0)
    except MyException, ex:
        print ex
        sys.exit(2)
