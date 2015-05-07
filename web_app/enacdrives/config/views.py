import pprint

# from django.shortcuts import render
from django.http import HttpResponse, Http404
# from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from config import models as mo
from config import utility as ut
from config.ldap_epfl import get_user_settings, UserNotFoundException


def http_home(request):
    raise PermissionDenied


def http_validate_username(request):
    if request.method != "GET":
        raise Http404

    username = ut.validate_input(request.GET.get, "username")

    answer = "ok"
    if username == "":
        answer = "No information given."
    elif "\\" in username:
        answer = "Do not prefix your username with the domain."
    else:
        try:
            get_user_settings(username)
        except UserNotFoundException:
            answer = "Username mistyped."
    return HttpResponse(answer, content_type="text/plain; charset=utf-8")


def http_get(request):
    if request.method != "GET":
        raise Http404

    username = ut.validate_input(request.GET.get, "username")
    
    ranked_mount_names = []
    config_given = ""
    try:
        user_settings = get_user_settings(username)
        
        # Config for all users
        for conf in mo.Config.objects.filter(enabled=True, category=mo.Config.CAT_ALL).order_by("rank"):
            data = conf.data.format(
                username=username,
                auth_domain=user_settings["auth_domain"],
                displayName=user_settings["displayName"],
                last_sciper_digit=user_settings["last_sciper_digit"],
                sciper=user_settings["sciper"],
                MNT_DIR="{MNT_DIR}",
                HOME_DIR="{HOME_DIR}",
                DESKTOP_DIR="{DESKTOP_DIR}",
                LOCAL_USERNAME="{LOCAL_USERNAME}",
                LOCAL_GROUPNAME="{LOCAL_GROUPNAME}",
            )
            config_given += data + "\n\n"

            mount_names = ut.grep_mount_names(data)
            ranked_mount_names.extend(mount_names)

        # Config for that user
        for conf in mo.Config.objects.filter(enabled=True, category=mo.Config.CAT_USER, users__name=username).order_by("rank"):
            data = conf.data.format(
                username=username,
                auth_domain=user_settings["auth_domain"],
                displayName=user_settings["displayName"],
                last_sciper_digit=user_settings["last_sciper_digit"],
                sciper=user_settings["sciper"],
                MNT_DIR="{MNT_DIR}",
                HOME_DIR="{HOME_DIR}",
                DESKTOP_DIR="{DESKTOP_DIR}",
                LOCAL_USERNAME="{LOCAL_USERNAME}",
                LOCAL_GROUPNAME="{LOCAL_GROUPNAME}",
            )
            config_given += data + "\n\n"

            mount_names = ut.grep_mount_names(data)
            ranked_mount_names.extend(mount_names)

        # Config for his/her EPFL Units
        for unit in user_settings["epfl_units"]:
            for conf in mo.Config.objects.filter(enabled=True, category=mo.Config.CAT_EPFL_UNIT, epfl_units__name=unit).order_by("rank"):
                data = conf.data.format(
                    username=username,
                    auth_domain=user_settings["auth_domain"],
                    displayName=user_settings["displayName"],
                    last_sciper_digit=user_settings["last_sciper_digit"],
                    sciper=user_settings["sciper"],
                    group=unit,
                    MNT_DIR="{MNT_DIR}",
                    HOME_DIR="{HOME_DIR}",
                    DESKTOP_DIR="{DESKTOP_DIR}",
                    LOCAL_USERNAME="{LOCAL_USERNAME}",
                    LOCAL_GROUPNAME="{LOCAL_GROUPNAME}",
                )
                config_given += data + "\n\n"
                
                mount_names = ut.grep_mount_names(data)
                ranked_mount_names.extend(mount_names)

        # Config for his/her Ldap groups
        for group in user_settings["ldap_groups"]:
            for conf in mo.Config.objects.filter(enabled=True, category=mo.Config.CAT_LDAP_GROUP, ldap_groups__name=group).order_by("rank"):
                data = conf.data.format(
                    username=username,
                    auth_domain=user_settings["auth_domain"],
                    displayName=user_settings["displayName"],
                    last_sciper_digit=user_settings["last_sciper_digit"],
                    sciper=user_settings["sciper"],
                    group=group,
                    MNT_DIR="{MNT_DIR}",
                    HOME_DIR="{HOME_DIR}",
                    DESKTOP_DIR="{DESKTOP_DIR}",
                    LOCAL_USERNAME="{LOCAL_USERNAME}",
                    LOCAL_GROUPNAME="{LOCAL_GROUPNAME}",
                )
                config_given += data + "\n\n"
                
                mount_names = ut.grep_mount_names(data)
                ranked_mount_names.extend(mount_names)
        
        # Rank *_mount entries
        if len(ranked_mount_names) != 0:
            config_given += "[global]\n"
            config_given += "entries_order = {0}\n\n".format(", ".join(ranked_mount_names))

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
