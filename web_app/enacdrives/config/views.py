import pprint

# from django.shortcuts import render
from django.http import HttpResponse, Http404
# from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from config import models as mo
from config import utility as ut
from config.ldap_epfl import get_user_settings, UserNotFoundException


def http_get(request):
    if request.method != "GET":
        raise Http404

    username = ut.validate_input(request.GET.get, "username")
    
    config_given = ""
    try:
        user_settings = get_user_settings(username)
        u = mo.User.objects.get(name=username)
        for conf in mo.Config.objects.filter(users=u):
            config_given += conf.data + "\n"
    except UserNotFoundException:
        pass
    except ObjectDoesNotExist:
        pass
    
    return HttpResponse(config_given + "\n", content_type="text/plain; charset=utf-8")
    

def http_ldap_settings(request):
    if request.method != "GET":
        raise Http404

    username = ut.validate_input(request.GET.get, "username")
    
    output = ""
    try:
        user_settings = get_user_settings(username)
        output += "username = {0}\n".format(user_settings["username"])
        output += "auth_domain = {0}\n".format(user_settings["auth_domain"])
        output += "displayName = {0}\n".format(user_settings["displayName"])
        output += "last_sciper_digit = {0}\n".format(user_settings["last_sciper_digit"])
        output += "sciper = {0}\n".format(user_settings["sciper"])
        output += "epfl_units = {0}\n".format(pprint.pformat(user_settings["epfl_units"]))
        output += "ldap_groups = {0}\n".format(pprint.pformat(user_settings["ldap_groups"]))
    except UserNotFoundException:
        pass
    
    return HttpResponse(output + "\n", content_type="text/plain; charset=utf-8")


def http_home(request):
    raise PermissionDenied
