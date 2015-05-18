import os
import json
import shutil
import logging
import datetime


from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.template.defaulttags import register
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template.context_processors import csrf
from django.http import HttpResponse, Http404, HttpResponseForbidden

from enacdrives import app_settings
from releases import models as mo
from releases import utility as ut


def http_home(request):
    return redirect("../get", permanent=True)


def http_admin(request):
    if request.method != "GET":
        raise Http404
    try:
        username = request.META["REMOTE_USER"]
    except KeyError:
        return HttpResponseForbidden()

    installers = {}
    for o_s, os_name in mo.Installer.OS_CHOICES:
        installers[os_name] = mo.Installer.objects.filter(os=o_s).order_by("upload_date")
        
    params = {
        "installers": installers,
        "username": username,
        "oss": [e[1] for e in mo.Installer.OS_CHOICES],
        "upload_url": reverse("do_upload"),
        "enable_url": reverse("do_enable"),
    }
    
    debug_logger = logging.getLogger("debug")
    debug_logger.error("HELLO")
    debug_logger.debug("params: {}".format(params))
    
    params.update(csrf(request))
    return render_to_response("admin.html", params, RequestContext(request))


def do_upload(request):
    # Receive uploaded file and move it to /var/www/enacdrives.epfl.ch/private_html/
    # Create an mo.Installer entry, disabled by default.

    if request.method != "POST":
        raise Http404
    try:
        username = request.META["REMOTE_USER"]
    except KeyError:
        return HttpResponseForbidden()
    
    # debug_logger = logging.getLogger("debug")
    
    try:
        uploaded_file = request.FILES["file"]
        filename = uploaded_file.name
        file_attributes = ut.parse_uploaded_file(filename)
    except Exception as e:
        response = {
            "status": "error",
            "msg": e.__str__(),
        }
        return HttpResponse(json.dumps(response), content_type="application/json")
    
    now = datetime.datetime.now()
    storage_name = "{:04}-{:02}-{:02}-{:02}{:02}{:02}-{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second, filename)
    dest_path = os.path.join(app_settings.APACHE_PRIVATE_DIR, storage_name)
    try:
        # Uploaded file is big -> TemporaryUploadedFile
        src_path = uploaded_file.temporary_file_path()
        shutil.move(src_path, dest_path)
    except AttributeError:
        # Uploaded file is small -> InMemoryUploadedFile
        destination = open(dest_path, 'wb')
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
        destination.close()
    
    inst = mo.Installer(
        upload_username=username,
        upload_date=now,
        release_number=file_attributes["release_number"],
        os=file_attributes["os"],
        file_name=filename,
        storage_name=storage_name,
        enabled=False
    )
    inst.save()
    
    response = {
        "status": "ok",
    }
    return HttpResponse(json.dumps(response), content_type="application/json")


def do_enable(request):
    if request.method != "POST":
        raise Http404
    try:
        username = request.META["REMOTE_USER"]
    except KeyError:
        return HttpResponseForbidden()
    
    installer_id = ut.validate_input(request.POST.get, "int")
    enabled = ut.validate_input(request.POST.get, "bool")
    inst = get_object_or_404(
        mo.Installer,
        id=installer_id
    )
    if enabled:
        os.symlink(
            os.path.join(app_settings.APACHE_PRIVATE_DIR, inst.storage_name),
            os.path.join(app_settings.APACHE_PUBLIC_DIR, inst.file_name)
        )
    else:
        os.unlink(os.path.join(app_settings.APACHE_PUBLIC_DIR, inst.file_name))
    inst.enabled = enabled
    inst.save()


def api_latest_release_number(request):
    if request.method != "GET":
        raise Http404
    
    try:
        os = ut.validate_input(request.GET.get, "os")
        inst = mo.Installer.objects.filter(os=os).order_by("-upload_date")[0]
        answer = inst.release_number
    except:
        answer = "This OS has no release."
    return HttpResponse(answer, content_type="text/plain; charset=utf-8")


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
