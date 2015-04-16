# from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist

from config import models as mo


def http_config(request):
    if request.method != "GET":
        raise Http404

    config_given = ""
    username = request.GET.get("username", None)
    if username is not None:
        try:
            u = mo.User.objects.get(name=username)
            for conf in mo.Config.objects.filter(users=u):
                config_given += conf.data + "\n"
        except ObjectDoesNotExist:
            pass
    
    return HttpResponse(config_given + "\n", content_type="text/plain; charset=utf-8")
