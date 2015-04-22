import os
import re
import json
import ldap3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class UserNotFoundException(Exception):
    pass


class Ldap():
    """
        EPFL Ldap connector
    """
    def __init__(self):
        self.server_name = "ldap.epfl.ch"
        self.base_dn = "o=epfl,c=ch"  # "c=ch"
        self.scope = ldap3.SEARCH_SCOPE_WHOLE_SUBTREE
        self.s = ldap3.Server(self.server_name)
        self.c = ldap3.Connection(self.s)

    def read_ldap(self, l_filter, l_attrs):
        """
            + Proceed a request to the LDAP
            + sort entries (only possible if "uid" attribute was requested)
                + 1st is main accreditation
                + other accreditations come after, unsorted
        """
        with self.c:
            if not self.c.search(
                search_base=self.base_dn,
                search_filter=l_filter,
                search_scope=self.scope,
                attributes=l_attrs,
            ):
                raise Exception("Could not search to {0}".format(self.server_name))

            if self.c.response is None:
                return []

            results = self.c.response

        # results = [e["attributes"] for e in self.c.response]
        # Return main accreditation first.
        # + main's uid attribute has 2 values : "username", "username@unit"
        # + other's uid attribute has 1 value : "username@unit"
        return sorted(
            results,
            key=lambda e: len(e["attributes"].get("uid", [])),
            reverse=True
        )


class AD(object):
    def __init__(self):
        self.server_name = "ldap://intranet.epfl.ch:3268"
        self.base_dn = "DC=intranet,DC=epfl,DC=ch"
        self.scope = ldap3.SEARCH_SCOPE_WHOLE_SUBTREE
        with open(BASE_DIR + "/ad_credentials.json", "r") as f:
            self.dn, self.secret = json.load(f)
        self.s = ldap3.Server(self.server_name)
        self.c = ldap3.Connection(self.s, user=self.dn, password=self.secret, read_only=True)

    def read_ldap(self, l_filter, l_attrs):
        with self.c:
            if not self.c.search(
                search_base=self.base_dn,
                search_filter=l_filter,
                search_scope=self.scope,
                attributes=l_attrs,
            ):
                raise Exception("Could not search to {0}".format(self.server_name))

            if self.c.response is None:
                return []
            
            return self.c.response


def get_user_settings(username):
    """
    1) Search ldap.epfl.ch for that username
        -> uniqueIdentifier
    2) Search ldap.epfl.ch for that uniqueIdentifier
        -> epfl_units (third "ou=xxx" of dn)
        -> ldap_groups
    returns {
                "auth_domain": "INTRANET",
                "displayName": None,
                "sciper": None,
                "last_sciper_digit": None,
                "epfl_units": [],
                "ldap_groups": [],
            }
    """
    l = Ldap()
    user_settings = {
        "username": username,
        "auth_domain": None,
        "displayName": None,
        "sciper": None,
        "last_sciper_digit": None,
        "epfl_units": [],
        "ldap_groups": [],
    }
    
    # A) Look for his/her uniqueIdentifier (#SCIPER)
    # -> displayName
    # -> sciper
    # -> last_sciper_digit
    r = l.read_ldap("(uid={0})".format(username), ["uniqueIdentifier", "displayName", ])
    if len(r) == 0:
        raise UserNotFoundException(username)
    sciper_no = r[0]["attributes"]["uniqueIdentifier"][0]
    user_settings["displayName"] = r[0]["attributes"]["displayName"][0]
    user_settings["sciper"] = sciper_no
    user_settings["last_sciper_digit"] = sciper_no[-1]

    # B) Look for all his/her accreditations
    # -> epfl_units
    # -> ldap_groups
    ldap_groups = set()
    r = l.read_ldap("(uniqueIdentifier={0})".format(sciper_no), ["uid", "memberOf", ])
    for accred in r:
        all_ou = re.findall(r"ou=([^,]+)", accred["dn"])
        if len(all_ou) >= 3:
            user_settings["epfl_units"].append(all_ou[-3])
        try:
            ldap_groups = ldap_groups.union(accred["attributes"]["memberOf"])
        except KeyError:
            pass
    user_settings["ldap_groups"] = list(ldap_groups)

    # C) Look in AD
    # -> auth_domain
    ad = AD()
    r = ad.read_ldap(l_filter="(sAMAccountName={0})".format(username), l_attrs=["dn"])
    all_dc = re.findall(r"DC=(\w+)", r[0]["dn"])
    user_settings["auth_domain"] = all_dc[0].upper()
    
    return user_settings
