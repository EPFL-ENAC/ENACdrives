import re
import ldap
from django.utils.encoding import smart_unicode


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

class AD(object):
    def __init__(self):
        self.server = "ldap://intranet.epfl.ch:3268"
        self.base_dn = "DC=intranet,DC=epfl,DC=ch"
        self.scope = ldap.SCOPE_SUBTREE
        self.dn = "intranet\enacmoni"
        self.secret = "It5Mon5Nag"
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

def get_user_settings(username):
    """
        Used to get :
        {'displayName': 'Samuel Bancal',
         'epfl_units': ['enac-it', 'iie-ge'],
         'ldap_groups': ['transporsrv2-admin',
                         'HPC-tech',
                         'enac-hpc',
                         'fi-logiciel-libre',
                         'testCampusRoule',
                         'enac-it2_annonce',
                         'transpor-admin',
                         'Logiciels-Libres',
                         'enac-it1',
                         'enac-linux',
                         'lte-server-admin',
                         'respinfo-epfl',
                         'enacit-docsenacit',
                         'vmusers',
                         'disal-server-admin'],
         'sciper': '189989',
         'last_sciper_digit': '9',
         'uid_number': '90989',
         'auth_domain': 'enac',
        }
    """
    settings = {}
    
    my_ldap = Ldap()
    my_ad = AD()
    
    # uidNumber
    ldap_res = my_ldap.read_ldap(
        l_filter = "uid=%s" % username,
        l_attrs = ["uidNumber"]
    )
    try:
        settings["uid_number"] = smart_unicode(ldap_res[0][1]['uidNumber'][0])
    except IndexError:
        raise Exception("Non ldap user")
    
    # displayName, uniqueIdentifier, memberOf
    ldap_res = my_ldap.read_ldap(
        l_filter = "uidNumber=%s" % settings["uid_number"],
        l_attrs = ["displayName", "uniqueIdentifier", "memberOf"]
    )
    
    try:
        # displayName
        settings["displayName"] = smart_unicode(ldap_res[0][1]["displayName"][0])
    
        # sciper, last_sciper_digit
        settings["sciper"] = smart_unicode(ldap_res[0][1]['uniqueIdentifier'][0])
        settings["last_sciper_digit"] = smart_unicode(settings["sciper"][-1])

        # epfl_units
        settings["epfl_units"] = []
        for entry in ldap_res:
            l = re.findall(r'ou=([^,]+)', entry[0])[0]
            if not l in settings["epfl_units"]:
                settings["epfl_units"].append(smart_unicode(l))

        # ldap_groups
        ldap_groups = set()
        for entry in ldap_res:
            try:
                ldap_groups = ldap_groups.union(entry[1]["memberOf"])
            except KeyError:
                pass
        settings["ldap_groups"] = [smart_unicode(g) for g in ldap_groups]

        # auth_domain
        ldap_res = my_ad.read_ldap(
            l_filter = "sAMAccountName=%s" % username,
            l_attrs = ["dn"]
            #l_attrs = ["userPrincipalName"]
        )
        #~ userPrincipalName = ldap_res[0][1]['userPrincipalName'][0]
        #~ domain = re.search(r'@([^.]+)', userPrincipalName).group(1)
        #~ settings["auth_domain"] = smart_unicode(domain.lower())
        settings["auth_domain"] = re.findall(r'DC=(\w+)', ldap_res[0][0])[0].upper()
    except (IndexError, KeyError):
        raise Exception("Non ldap user")
    
    return settings

