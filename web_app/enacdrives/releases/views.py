import json

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template.context_processors import csrf
from django.http import HttpResponse, Http404, HttpResponseForbidden

from releases import models as mo
from releases import utility as ut


def http_download(request):
    if request.method != "GET":
        raise Http404

    params = {
    }
    return render_to_response("download.html", params)


def http_admin(request):
    if request.method != "GET":
        raise Http404
    try:
        username = request.META["REMOTE_USER"]
    except KeyError:
        return HttpResponseForbidden()

    params = {
        "installers": mo.Installer.objects.all().order_by("os", "upload_date"),
        "username": username,
        "oss": [e[1] for e in mo.Installer.OS_CHOICES],
        "upload_url": reverse("http_upload"),
    }
    params.update(csrf(request))
    return render_to_response("admin.html", params)


def http_upload(request):
    if request.method != "POST":
        raise Http404
    try:
        username = request.META["REMOTE_USER"]
    except KeyError:
        return HttpResponseForbidden()
    
    response = {
        "status": "ok",
    }
    return HttpResponse(json.dumps(response), content_type="application/json")


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
