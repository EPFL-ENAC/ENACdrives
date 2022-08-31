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
    return redirect(reverse("http_admin"), permanent=True)


def http_admin(request):
    if request.method != "GET":
        raise Http404
    try:
        username = request.META["REMOTE_USER"]
    except KeyError:
        return HttpResponseForbidden()

    debug_logger = logging.getLogger("debug")

    installers = {}
    current_installer_id = {}
    for arch in mo.Arch.objects.all():
        installers[arch] = mo.Installer.objects.filter(arch=arch).order_by(
            "upload_date"
        )
        if arch.current_installer is not None:
            current_installer_id[arch] = arch.current_installer.id

    params = {
        "installers": installers,
        "current_installer_id": current_installer_id,
        "username": username,
        "archs": mo.Arch.objects.all().order_by("id"),
        "upload_url": reverse("do_upload"),
        "enable_url": reverse("do_enable"),
    }

    params.update(csrf(request))
    debug_logger.debug("params: {}".format(params))
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

    debug_logger = logging.getLogger("debug")

    try:
        uploaded_file = request.FILES["file"]
        filename = uploaded_file.name
        file_attributes = ut.parse_uploaded_file(filename)
        debug_logger.debug("file_attributes : {}".format(file_attributes))
    except Exception as e:
        response = {
            "status": "error",
            "msg": e.__str__(),
        }
        return HttpResponse(json.dumps(response), content_type="application/json")

    arch, _ = mo.Arch.objects.get_or_create(os=file_attributes["os"])

    now = datetime.datetime.now()
    storage_name = "{:04}-{:02}-{:02}-{:02}{:02}{:02}-{}".format(
        now.year, now.month, now.day, now.hour, now.minute, now.second, filename
    )
    dest_path = os.path.join(app_settings.APACHE_PRIVATE_DIR, storage_name)
    try:
        # Uploaded file is big -> TemporaryUploadedFile
        src_path = uploaded_file.temporary_file_path()
        shutil.move(src_path, dest_path)
    except AttributeError:
        # Uploaded file is small -> InMemoryUploadedFile
        destination = open(dest_path, "wb")
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
        destination.close()

    inst = mo.Installer(
        upload_username=username,
        upload_date=now,
        release_number=file_attributes["release_number"],
        arch=arch,
        file_name=filename,
        storage_name=storage_name,
    )
    inst.save()

    response = {
        "status": "ok",
    }
    return HttpResponse(json.dumps(response), content_type="application/json")


def do_enable(request):
    debug_logger = logging.getLogger("debug")
    debug_logger.debug("AA")
    if request.method != "POST":
        raise Http404
    debug_logger.debug("AB")
    try:
        username = request.META["REMOTE_USER"]
    except KeyError:
        return HttpResponseForbidden()
    debug_logger.debug("AC")

    arch_id = ut.validate_input(request.POST.get, "arch", "int")
    installer_id = ut.validate_input(request.POST.get, "inst", "int")
    arch = get_object_or_404(mo.Arch, id=arch_id)
    inst = get_object_or_404(mo.Installer, id=installer_id)
    if inst.arch == arch:
        arch.current_installer = inst
        arch.save()
        response = {
            "status": "ok",
        }
        return HttpResponse(json.dumps(response), content_type="application/json")
    response = {
        "status": "error",
        "msg": "This installer is not of the right Architecture.",
    }
    return HttpResponse(json.dumps(response), content_type="application/json")


def do_download(request):
    if request.method != "GET":
        raise Http404

    try:
        o_s = ut.validate_input(request.GET.get, "os", "os")
        arch = mo.Arch.objects.get(os=o_s)
        inst = arch.current_installer
        answer = inst.release_number
    except:
        answer = "This OS has no release."
        return HttpResponse(answer, content_type="text/plain; charset=utf-8")

    response = HttpResponse(content_type="application/force-download")
    response["Content-Disposition"] = "attachment; filename={}".format(inst.file_name)
    response["X-Sendfile"] = os.path.join(
        app_settings.APACHE_PRIVATE_DIR, inst.storage_name
    )
    # It"s usually a good idea to set the "Content-Length" header too.
    # You can also set any other required headers: Cache-Control, etc.
    return response


def api_latest_release_number(request):
    if request.method != "GET":
        raise Http404

    try:
        o_s = ut.validate_input(request.GET.get, "os", "os")
        arch = mo.Arch.objects.get(os=o_s)
        inst = arch.current_installer
        answer = inst.release_number
    except:
        answer = "This OS has no release."
    return HttpResponse(answer, content_type="text/plain; charset=utf-8")


def api_latest_release_date(request):
    if request.method != "GET":
        raise Http404

    try:
        o_s = ut.validate_input(request.GET.get, "os", "os")
        arch = mo.Arch.objects.get(os=o_s)
        inst = arch.current_installer
        answer = "{:02}-{:02}-{:04}".format(
            inst.upload_date.day, inst.upload_date.month, inst.upload_date.year
        )
    except:
        answer = "This OS has no release."
    return HttpResponse(answer, content_type="text/plain; charset=utf-8")


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
