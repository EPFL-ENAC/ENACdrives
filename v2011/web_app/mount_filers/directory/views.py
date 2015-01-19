# Bancal Samuel
# 110510
# 110708

# TODO :
#   check between : return '', return None, return error_non_ldap_user

import re
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from mount_filers.directory.models import Config, Username, Groupname
from mount_filers.directory.epfl import get_user_settings


def check_condition(condition):
    def format_version_for_comparision(version):
        result = []
        for v in version.split("."):
            try:
                result.append(int(v))
            except:
                m = re.match(r'(\d*)(.*)', v)
                i = m.group(1)
                try:
                    i = int(i)
                except:
                    pass
                s = m.group(2)
                result.append((i, s))
        return result
    
    m = re.search(r'^([^<>=!]+)\s*([<>=!]+)\s*([^<>=!]+)$', condition)
    if not m:
        raise Exception ("Error, could not evaluate condition \"%s\"." % (condition))
    left, criterion, right = m.groups()
    left = format_version_for_comparision(left.strip())
    right = format_version_for_comparision(right.strip())
    if criterion == "<":
        if left < right:
            return True
    if criterion == "<=":
        if left <= right:
            return True
    elif criterion == ">":
        if left > right:
            return True
    elif criterion == ">=":
        if left >= right:
            return True
    elif criterion == "==":
        if left == right:
            return True
    elif criterion == "!=":
        if left != right:
            return True
    return False

def error_non_ldap_user():
    return HttpResponse("\n", mimetype="text/plain")

def http_get_domain(request):
    try:
        username = request.GET.get('username', None)
        settings = get_user_settings(username)
        return HttpResponse(settings["auth_domain"], mimetype="text/plain")
    except Exception:
        return error_non_ldap_user()

def http_get_sciper(request):
    try:
        username = request.GET.get('username', None)
        settings = get_user_settings(username)
        return HttpResponse(settings["last_sciper_digit"], mimetype="text/plain")
    except Exception:
        return error_non_ldap_user()

def http_get_labos(request):
    try:
        username = request.GET.get('username', None)
        settings = get_user_settings(username)
        return HttpResponse("\n".join(settings["epfl_units"]), mimetype="text/plain")
    except Exception:
        return error_non_ldap_user()

def http_get_settings(request):
    import pprint
    try:
        username = request.GET.get('username', None)
        settings = get_user_settings(username)
        return HttpResponse(pprint.pformat(settings), mimetype="text/plain")
    except Exception:
        return error_non_ldap_user()

def http_get_config(request):
    version = request.GET.get('version', None)
    username = request.GET.get('username', None)
    if version == None and username == None:
        return HttpResponse('', mimetype="text/plain")
    
    if version == None:
        version = "0.3.9" # default, since previous to 0.4.0 didn't provide version number
    
    answer = ""
    
    # context : GLOBAL
    if username == None:
        for conf in Config.objects.filter(context = "g").order_by("rank"):
            if conf.version == "" or \
               check_condition("%s%s" % (version, conf.version)):
                answer += conf.config.format(
                    # http://enacit1adm1.epfl.ch/mount_filers/dir/config?username=__USERNAME__&version=__VERSION__
                    url_config_user = request.build_absolute_uri(reverse('http_get_config')) + "?username=__USERNAME__&version=__VERSION__",
                    # http://enacit1adm1.epfl.ch/mount_filers/dir/validate?username=
                    url_validate_username = request.build_absolute_uri(reverse('http_validate')) + "?username=",
                    # http://enacit1adm1.epfl.ch/mount_filers/dir/domain?username=__USERNAME__
                    url_get_domain = request.build_absolute_uri(reverse('http_get_domain')) + "?username=__USERNAME__",
                    # http://enacit1adm1.epfl.ch/mount_filers/dir/sciper?username=__USERNAME__
                    url_get_sciper = request.build_absolute_uri(reverse('http_get_sciper')) + "?username=__USERNAME__",
                )
                answer += "\n"
    
    # context : USER 
    else:
        try:
            settings = get_user_settings(username)
        except Exception:
            return error_non_ldap_user()
        
        # all users :
        for conf in Config.objects.filter(username__name = "", groupname__name = "", context = "u").order_by("rank"):
            if conf.version == "" or \
               check_condition("%s%s" % (version, conf.version)):
                answer += conf.config.format(
                    username = username,
                    display_name = settings["displayName"],
                    sciper = settings["sciper"],
                    last_sciper_digit = settings["last_sciper_digit"],
                )
                answer += "\n"
        
        # user specific :
        for conf in Config.objects.filter(username__name = username, context = "u").order_by("rank"):
            if conf.version == "" or \
               check_condition("%s%s" % (version, conf.version)):
                answer += conf.config.format(
                    username = username,
                    display_name = settings["displayName"],
                    sciper = settings["sciper"],
                    last_sciper_digit = settings["last_sciper_digit"],
                )
                answer += "\n"
        
        # groups specific :
        for group in settings["epfl_units"]:
            for conf in Config.objects.filter(groupname__name = group, context = "u").order_by("rank"):
                if conf.version == "" or \
                   check_condition("%s%s" % (version, conf.version)):
                    answer += conf.config.format(
                        username = username,
                        display_name = settings["displayName"],
                        sciper = settings["sciper"],
                        last_sciper_digit = settings["last_sciper_digit"],
                        group = group,
                    )
                    answer += "\n"
        
        for group in settings["ldap_groups"]:
            if group in ("enacproj-sd", "enacproj-sll"): # Temp exception for these ldap_groups !!! TODO !!!
                for conf in Config.objects.filter(groupname__name = group, context = "u").order_by("rank"):
                    if conf.version == "" or \
                       check_condition("%s%s" % (version, conf.version)):
                        answer += conf.config.format(
                            username = username,
                            display_name = settings["displayName"],
                            sciper = settings["sciper"],
                            last_sciper_digit = settings["last_sciper_digit"],
                            group = group,
                        )
                        answer += "\n"
    
    return HttpResponse(answer, mimetype="text/plain")

def http_get_config_classic(request): # used the time while filling the database
    """
        ######################
        ?version=
        
        [global]
        username = __USERNAME__
        domain = __DOMAIN__
        method = smb
        auth_realm = EPFL
        
        [config]
        import = http://enacit1adm1.epfl.ch/mount_filers/dir/config?username=__USERNAME__
        
        [require]
        url = http://enacit1adm1.epfl.ch/mount_filers/dir/config?username=__USERNAME__
        load_cache = True
        # msg = Couldn't get EPFL/ENAC's online config. Doing with cache values (if any).
        abort = False
        
        [substitution]
        label = __USERNAME__
        ask = Enter your EPFL username :
        constraint = lowercase
        validate = http://enacit1adm1.epfl.ch/mount_filers/dir/validate?username=
        
        [substitution]
        label = __DOMAIN__
        constraint = uppercase
        url_saved = http://enacit1adm1.epfl.ch/mount_filers/dir/domain?username=__USERNAME__
        ask = Enter your EPFL ActiveDirectory domain :
        
        [substitution]
        label = __SCIPER__
        url_saved = http://enacit1adm1.epfl.ch/mount_filers/dir/sciper?username=__USERNAME__
        ask = Enter the last digit of your SCIPER number (0-9) :
        
        
        ######################
        ?username=
        
        # For all
        [message]
        label = user : {full_username} ({username})
        rank = 1
        reset = __USERNAME__
        reset = __SCIPER__
        reset = __DOMAIN__
        
        # for all
        [require] 
        smb = files{sciper}.epfl.ch
        msg = Couldn't connect to EPFL's filer. Please check that you're connected to the network and using a VPN client if outside the EPFL.
        abort = True
        
        # for all
        [mount]
        username = {username}
        domain = {domain}
        name = priv
        label = {username}@files{sciper} (individuel)
        server_name = files{sciper}.epfl.ch
        server_path = data/{username}
        local_path = __MNT_DIR__/{username}_on_files{sciper}
        
        # only for employees, one per labo
        [mount]
        name = lab_{labo}_tier1
        label = {labo}@enacfiles1 (collectif tier1)
        server_name = enacfiles1.epfl.ch
        server_path = {labo}
        local_path = __MNT_DIR__/{labo}_on_enacfiles1
        
        # only for employees, one per labo
        [mount]
        name = lab_{labo}_tier2
        label = {labo}@enacfiles2 (collectif tier2)
        server_name = enacfiles2.epfl.ch
        server_path = {labo}
        local_path = __MNT_DIR__/{labo}_on_enacfiles2
        
    """
    version = request.GET.get('version', None)
    username = request.GET.get('username', None)
    if version == None and username == None:
        return HttpResponse('', mimetype="text/plain")
    
    answer = ""
    
    if version != None and username == None:
        answer += """\
[global]
username = __USERNAME__
domain = __DOMAIN__
method = smb
auth_realm = EPFL

[config]
import = {url_config_user}

[require]
url = {url_config_user}
load_cache = True
# msg = Couldn't get EPFL/ENAC's online config. Doing with cache values (if any).
abort = False

[substitution]
label = __USERNAME__
ask = Enter your EPFL username :
constraint = lowercase
validate = {url_validate_username}

[substitution]
label = __DOMAIN__
constraint = lowercase
url_saved = {url_get_domain}
ask = Enter your EPFL ActiveDirectory domain :

[substitution]
label = __SCIPER__
url_saved = {url_get_sciper}
ask = Enter the last digit of your SCIPER number (0-9) :


""".format(
        # http://enacit1adm1.epfl.ch/mount_filers/dir/config?username=__USERNAME__&version=__VERSION__
        url_config_user = request.build_absolute_uri(reverse('http_get_config')) + "?username=__USERNAME__&version=__VERSION__",
        # http://enacit1adm1.epfl.ch/mount_filers/dir/validate?username=
        url_validate_username = request.build_absolute_uri(reverse('http_validate')) + "?username=",
        # http://enacit1adm1.epfl.ch/mount_filers/dir/domain?username=__USERNAME__
        url_get_domain = request.build_absolute_uri(reverse('http_get_domain')) + "?username=__USERNAME__",
        # http://enacit1adm1.epfl.ch/mount_filers/dir/sciper?username=__USERNAME__
        url_get_sciper = request.build_absolute_uri(reverse('http_get_sciper')) + "?username=__USERNAME__",
    )
    
    if username != None:
        settings = get_user_settings(username)
        
        domain = settings["auth_domain"]
        labos = settings["epfl_units"]
        last_sciper = settings["last_sciper_digit"]
        full_username = settings["displayName"]
        
        if len(domain) == 0:
            return error_non_ldap_user()
        
        if version != None:
            answer += """\
[message]
label = user : {full_username} ({username})
rank = 1
reset = __USERNAME__
reset = __SCIPER__
reset = __DOMAIN__

""".format(
        username = username,
        full_username = full_username,
    )
        answer += """\
[require] 
smb = files{last_sciper}.epfl.ch
msg = Couldn't connect to EPFL's filer. Please check that you're connected to the network and using a VPN client if outside the EPFL.
abort = True

[mount]
name = private
label = {username}@files{last_sciper} (individuel)
server_name = files{last_sciper}.epfl.ch
server_path = data/{username}
local_path = __MNT_DIR__/{username}_on_files{last_sciper}

""".format(
        username = username,
        last_sciper = last_sciper,
    )
        
        if domain != "students":
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

""".format(
        labo = labo,
    )
    
    return HttpResponse(answer, mimetype="text/plain")

def http_validate(request):
    username = request.GET.get('username', None)
    if username == None:
        return HttpResponse('No information given.', mimetype="text/plain")
    if "\\" in username:
        return HttpResponse('Do not prefix your username with the domain.', mimetype="text/plain")
    try:
        settings = get_user_settings(username)
        return HttpResponse('ok', mimetype="text/plain")
    except Exception:
        return HttpResponse('Username mistyped.', mimetype="text/plain")
