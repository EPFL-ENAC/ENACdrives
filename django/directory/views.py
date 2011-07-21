# Bancal Samuel
# 110510
# 110708

# TODO :
#        check between : return '', return None, return non_ldap_user
#        deploy to production
#        

from django.http import HttpResponse

import re
import ldap

class Ldap(object):
    def __init__(self):
        self.server = "ldap://ldap.epfl.ch"
        self.base_dn = "o=epfl,c=ch"
        self.scope = ldap.SCOPE_SUBTREE
        self.l = ldap.initialize(self.server)
    
    def read_ldap(self, l_filter, l_attrs):
        return self.l.search_s(
            base = self.base_dn,
            scope = self.scope,
            filterstr = l_filter,
            attrlist = l_attrs
        )
    
    def get_uid_number(self, username):
        l_attrs = ["uidNumber"]
        ldap_res = self.read_ldap(
            l_filter = "uid=%s" % username,
            l_attrs = l_attrs
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
            l_filter = "uidNumber=%s" % uid_number,
            l_attrs = ["uidNumber"]
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
            l_filter = "uid=%s" % username,
            l_attrs = ["uniqueIdentifier"]
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
            l_filter = "uidNumber=%s" % uid_number,
            l_attrs = ["uidNumber"]
        )
        
        labos = []
        for entry in ldap_res:
            l = re.findall(r'ou=([^,]+)', entry[0])[0]
            if not l in labos:
                labos.append(l)
        
        return labos

class AD(object):
    def __init__(self):
        self.server = "ldap://intranet.epfl.ch:3268"
        self.base_dn = "DC=intranet,DC=epfl,DC=ch"
        self.scope = ldap.SCOPE_SUBTREE
        self.dn = "enac\enacit-svcshareauth"
        self.secret = "P4$Sw0Rd1965-2+10"
        self.l = ldap.initialize(self.server)
        self.l.set_option(ldap.OPT_REFERRALS, 0)
        self.l.protocol_version = 3
        self.l.simple_bind_s(self.dn, self.secret)
        #~ filter = "(&(objectClass=user)(sAMAccountName=bancal))"
        #~ attrs = ["employeeID", "userPrincipalName", "memberof"]
    
    def read_ldap(self, l_filter, l_attrs):
        return self.l.search_s(
            base = self.base_dn,
            scope = self.scope,
            filterstr = l_filter,
            attrlist = l_attrs
        )
    
    def get_domain(self, username):
        try:
            ldap_res = self.read_ldap(
                l_filter = "sAMAccountName=%s" % username,
                l_attrs = ["userPrincipalName"]
            )
            userPrincipalName = ldap_res[0][1]['userPrincipalName'][0]
            domain = re.search(r'@([^.]+)', userPrincipalName).group(1)
            return domain.lower()
        except IndexError:
            return None
    
    def get_sciper(self, username):
        try:
            ldap_res = self.read_ldap(
                l_filter = "sAMAccountName=%s" % username,
                l_attrs = ["employeeID"]
            )
            employeeID = ldap_res[0][1]['employeeID'][0]
            return employeeID[-1]
        except IndexError:
            return None

def non_ldap_user():
    return HttpResponse("\n", mimetype="text/plain")

def get_domain(request):
    username = request.GET.get('username', None)
    if username == None:
        return HttpResponse('', mimetype="text/plain")
    
    ad = AD()
    domain = ad.get_domain(username)
    if domain == None:
        return non_ldap_user()
    return HttpResponse(domain, mimetype="text/plain")
    #~ epfl_ldap = Ldap()
    #~ domains = epfl_ldap.get_domains(username)
    #~ if len(domains) == 0:
        #~ return non_ldap_user()
    #~ return HttpResponse("\n".join(domains), mimetype="text/plain")

def get_sciper(request):
    username = request.GET.get('username', None)
    if username == None:
        return HttpResponse('', mimetype="text/plain")
    
    epfl_ldap = Ldap()
    last_sciper = epfl_ldap.get_sciper(username)
    if last_sciper == None:
        return non_ldap_user()
    return HttpResponse(last_sciper, mimetype="text/plain")

def get_labos(request):
    username = request.GET.get('username', None)
    if username == None:
        return HttpResponse('', mimetype="text/plain")
    
    epfl_ldap = Ldap()
    labos = epfl_ldap.get_labos(username)
    if len(labos) == 0:
        return non_ldap_user()
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
    username = request.GET.get('username', None)
    if username == None:
        return HttpResponse('', mimetype="text/plain")
    
    ad = AD()
    domain = ad.get_domain(username)
    
    if len(domain) == 0:
        return non_ldap_user()
    
    answer = """\
[mount]
name = priv
label = __USERNAME__@files__SCIPER__ (individuel)
server_name = files__SCIPER__.epfl.ch
server_path = data/__USERNAME__
local_path = __MNT_DIR__/__USERNAME___on_files__SCIPER__

"""
    if domain != "students":
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

def get_full_config(request):
    """
        # for all
        [mount]
        name = priv
        label = __USERNAME__@files__SCIPER__ (individuel)
        server_name = files__SCIPER__.epfl.ch
        server_path = data/__USERNAME__
        local_path = __MNT_DIR__/__USERNAME___on_files__SCIPER__
        
        # only for employees, repeat one per labo
        [mount]
        name = lab1
        label = __LABO__@enacfiles1 (collectif tier1)
        server_name = enacfiles1.epfl.ch
        server_path = __LABO__
        local_path = __MNT_DIR__/__LABO___on_enacfiles1
        
        # only for employees, repeat one per labo
        [mount]
        name = lab2
        label = __LABO__@enacfiles2 (collectif tier2)
        server_name = enacfiles2.epfl.ch
        server_path = __LABO__
        local_path = __MNT_DIR__/__LABO___on_enacfiles2
    """
    username = request.GET.get('username', None)
    if username == None:
        return HttpResponse('', mimetype="text/plain")
    
    epfl_ldap = Ldap()
    ad = AD()
    domain = ad.get_domain(username)
    last_sciper = epfl_ldap.get_sciper(username)
    
    if domain == None:
        return non_ldap_user()
    
    answer = """\
[mount]
name = priv
label = {username}@files{sciper} (individuel)
server_name = files{sciper}.epfl.ch
server_path = data/{username}
local_path = __MNT_DIR__/{username}_on_files{sciper}

""".format(username = username, sciper = last_sciper)
    
    if domain != "students":
        labos = epfl_ldap.get_labos(username)
        for labo in labos:
            answer += """\
[mount]
name = lab_{labo}_tier1
label = {labo}@enacfiles1 (collectif tier1)
server_name = enacfiles1.epfl.ch
server_path = {labo}
local_path = __MNT_DIR__/{labo}_on_enacfiles1

[mount]
name = lab_{labo}_tier2
label = {labo}@enacfiles2 (collectif tier2)
server_name = enacfiles2.epfl.ch
server_path = {labo}
local_path = __MNT_DIR__/{labo}_on_enacfiles2

""".format(labo = labo)
    return HttpResponse(answer, mimetype="text/plain")

if __name__ == '__main__':
    ld = Ldap()
    ad = AD()
    
    for username in ["bancal", "bonjour", "dameylan", "derochat",
                     "arsenije", "bajic", "volos", "angel", "gowal",
                     "fooo"]:
        print "\n" + "-" * 50
        print username
        print "domain : %s %s" % (
            ",".join(ld.get_domains(username)),
            ad.get_domain(username)
        )
        print "sciper : %s %s" % (
            ld.get_sciper(username),
            ad.get_sciper(username)
        )
        print "labos : %s" % (
            ",".join(ld.get_labos(username)),
        )

