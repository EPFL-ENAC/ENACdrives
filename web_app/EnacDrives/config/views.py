from django.shortcuts import render
from django.http import HttpResponse, Http404


def http_config(request):
    if request.method != "GET":
        raise Http404

    config_given = ""
    username = request.GET.get("username", None)
    if username is not None:
        config_given += "Hello sam!\n"
    
    return HttpResponse(config_given + "\n", content_type="text/plain; charset=utf-8")
