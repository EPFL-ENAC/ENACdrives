# Bancal Samuel
# 110510

from django.http import HttpResponse

import re
import ldap

# LDAP CONSTANTS
LDAP_SERVER = "ldap://ldap.epfl.ch"
LDAP_BASE_DN = "o=epfl,c=ch"

class Ldap(object):
    def __init__(self):
        self.ldap_conn = ldap.initialize(LDAP_SERVER)
    
    def read_ldap(self, ldap_filter, ldap_attrs):
        return self.ldap_conn.search_s(
            base = LDAP_BASE_DN,
            scope = ldap.SCOPE_SUBTREE,
            filterstr = ldap_filter,
            attrlist = ldap_attrs
        )
    
    def get_uid_number(self, username):
        ldap_attrs = ["uidNumber"]
        ldap_res = self.read_ldap(
            ldap_filter = "uid=%s" % username,
            ldap_attrs = ldap_attrs
        )
        try:
            return ldap_res[0][1]['uidNumber'][0]
        except IndexError:
            return None

    def get_domains(self, username):
        uid_number = self.get_uid_number(username)
        if uid_number == None:
            return []
        
        domain_filters = {
            "etu" : "students",
        }
        
        ldap_res = self.read_ldap(
            ldap_filter = "uidNumber=%s" % uid_number,
            ldap_attrs = ["uidNumber"]
        )
        
        domains = []
        for entry in ldap_res:
            d = re.findall(r'ou=([^,]+)', entry[0])[-1]
            if d in domain_filters:
                d = domain_filters[d]
            if not d in domains:
                domains.append(d)
        
        return domains
    
    def get_sciper(self, username):
        ldap_res = self.read_ldap(
            ldap_filter = "uid=%s" % username,
            ldap_attrs = ["uniqueIdentifier"]
        )
        try:
            last_sciper = ldap_res[0][1]['uniqueIdentifier'][0][-1]
        except IndexError:
            last_sciper = None
        
        return last_sciper
    
    def get_labos(self, username):
        uid_number = self.get_uid_number(username)
        if uid_number == None:
            return []
        
        ldap_res = self.read_ldap(
            ldap_filter = "uidNumber=%s" % uid_number,
            ldap_attrs = ["uidNumber"]
        )
        
        labos = []
        for entry in ldap_res:
            l = re.findall(r'ou=([^,]+)', entry[0])[0]
            if not l in labos:
                labos.append(l)
        
        return labos


def return_non_ldap_user():
    return HttpResponse("\n", mimetype="text/plain")

def get_domains(request):
    username = request.GET.get('username', '')
    if username == '':
        return HttpResponse('', mimetype="text/plain")
    
    epfl_ldap = Ldap()
    domains = epfl_ldap.get_domains(username)
    if len(domains) == 0:
        return_non_ldap_user()
    return HttpResponse("\n".join(domains), mimetype="text/plain")

def get_sciper(request):
    username = request.GET.get('username', '')
    if username == '':
        return HttpResponse('', mimetype="text/plain")
    
    epfl_ldap = Ldap()
    last_sciper = epfl_ldap.get_sciper(username)
    if last_sciper == None:
        return_non_ldap_user()
    return HttpResponse(last_sciper, mimetype="text/plain")

def get_labos(request):
    username = request.GET.get('username', '')
    if username == '':
        return HttpResponse('', mimetype="text/plain")
    
    epfl_ldap = Ldap()
    labos = epfl_ldap.get_labos(username)
    if len(labos) == 0:
        return_non_ldap_user()
    return HttpResponse("\n".join(labos), mimetype="text/plain")

def get_config(request):
    """
        # for all
        [mount]
        name = priv
        label = __USERNAME__@files__SCIPER__ (individuel)
        server_name = files__SCIPER__.epfl.ch
        server_path = data/__USERNAME__
        local_path = __MNT_DIR__/__USERNAME___on_files__SCIPER__
        
        # only for employees
        [mount]
        name = lab1
        label = __LABO__@enacfiles1 (collectif tier1)
        server_name = enacfiles1.epfl.ch
        server_path = __LABO__
        local_path = __MNT_DIR__/__LABO___on_enacfiles1
        
        # only for employees
        [mount]
        name = lab2
        label = __LABO__@enacfiles2 (collectif tier2)
        server_name = enacfiles2.epfl.ch
        server_path = __LABO__
        local_path = __MNT_DIR__/__LABO___on_enacfiles2
    """
    username = request.GET.get('username', '')
    epfl_ldap = Ldap()
    domains = epfl_ldap.get_domains(username)
    
    if len(domains) == 0: # TODO : doesn't seem to filter!?!
        return_non_ldap_user()
    
    answer = """\
[mount]
name = priv
label = __USERNAME__@files__SCIPER__ (individuel)
server_name = files__SCIPER__.epfl.ch
server_path = data/__USERNAME__
local_path = __MNT_DIR__/__USERNAME___on_files__SCIPER__

"""
    if domains != ["students"]:
        answer += """\
[mount]
name = lab1
label = __LABO__@enacfiles1 (collectif tier1)
server_name = enacfiles1.epfl.ch
server_path = __LABO__
local_path = __MNT_DIR__/__LABO___on_enacfiles1

[mount]
name = lab2
label = __LABO__@enacfiles2 (collectif tier2)
server_name = enacfiles2.epfl.ch
server_path = __LABO__
local_path = __MNT_DIR__/__LABO___on_enacfiles2

"""
    return HttpResponse(answer, mimetype="text/plain")

if __name__ == '__main__':
    for username in ["bancal", "bonjour", "dameylan", "derochat", "arsenije", "bajic"]:
        print "\n" + "-" * 50
        print username
        for f in [get_domains, get_sciper, get_labos]:
            print "-> %s" % ", ".join(f(username).split("\n"))

