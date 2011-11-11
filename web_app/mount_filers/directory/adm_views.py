# Bancal Samuel

import pickle
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.core.context_processors import csrf
from mount_filers.directory.models import Config, Username, Groupname


def http_adm_browse(request):
    #~ return HttpResponse('ok', mimetype="text/plain")
    config = []
    for conf in Config.objects.order_by("rank"):
        config.append({
            "id": conf.id,
            "description": conf.description,
            "context": conf.get_context_display(),
            "users": conf.get_users(),
            "groups": conf.get_groups(),
            "profile": conf.profile,
            "version": conf.version,
            "config": conf.config,
        })
    params = {
        'config': config,
    }
    params.update(csrf(request))
    return render_to_response('adm/browse.html', params)

def http_adm_edit(request, conf_id):
    prefilled = {
        "id": conf_id,
        "description": "",
        "context": "",
        "users": "",
        "groups": "",
        "profile": "",
        "config": "",
    }
    if conf_id == "new":
        pass
    elif conf_id == "save":
        try:
            save_id = request.POST["id"]
            if save_id == "new":
                conf = Config()
                conf.rank = Config.objects.count() + 1
                conf.save()
            else:
                conf = get_object_or_404(Config, pk=save_id)
            conf.description = request.POST["description"]
            conf.context = request.POST["context"]
            conf.set_users(request.POST["users"])
            conf.set_groups(request.POST["groups"])
            conf.profile = request.POST["profile"]
            conf.version = request.POST["version"]
            config = request.POST["config"]
            while config[-2:] != "\n\n" and \
                  config[-4:] != "\r\n\r\n": # add 2 "\n" if needed
                config += "\n"
                
            conf.config = config
            conf.save()
        except (KeyError, Config.DoesNotExist):
            raise Http404
        return HttpResponseRedirect(reverse('mount_filers.directory.adm_views.http_adm_browse'))
    elif conf_id == "delete":
        try:
            delete_id = request.POST["id"]
            conf = get_object_or_404(Config, pk=delete_id)
            rank = conf.rank
            conf.delete()
            
            # Re-arrange rank
            for conf in Config.objects.filter(rank__gt = rank):
                conf.rank -= 1
                conf.save()
        except (KeyError, Config.DoesNotExist):
            raise Http404
        
        return HttpResponseRedirect(reverse('mount_filers.directory.adm_views.http_adm_browse'))
    elif conf_id == "rank_up":
        rerank_id = request.POST["id"]
        conf = get_object_or_404(Config, pk=rerank_id)
        if conf.rank != 1: # no rank_up for the first
            conf2 = get_object_or_404(Config, rank = conf.rank-1)
            conf.rank, conf2.rank = conf2.rank, conf.rank # swap
            conf.save()
            conf2.save()
        return HttpResponseRedirect(reverse('mount_filers.directory.adm_views.http_adm_browse'))
    elif conf_id == "rank_down":
        rerank_id = request.POST["id"]
        conf = get_object_or_404(Config, pk=rerank_id)
        if conf.rank != Config.objects.count(): # no rank_down for the last
            conf2 = get_object_or_404(Config, rank = conf.rank+1)
            conf.rank, conf2.rank = conf2.rank, conf.rank # swap
            conf.save()
            conf2.save()
        return HttpResponseRedirect(reverse('mount_filers.directory.adm_views.http_adm_browse'))
    else:
        conf = get_object_or_404(Config, pk=conf_id)
        prefilled.update({
            "description" : conf.description,
            "context" : conf.context,
            "users" : conf.get_users(),
            "groups" : conf.get_groups(),
            "profile" : conf.profile,
            "version" : conf.version,
            "config" : conf.config,
        })
        
    
    params = {
        'prefilled': prefilled,
        'context_choices': Config.CONTEXT_CHOICES,
    }
    params.update(csrf(request))
    return render_to_response('adm/edit.html', params)

def http_get_config_dump(request):
    result = []
    for conf in Config.objects.order_by("rank"):
        result.append({
            "description": conf.description,
            "rank": conf.rank,
            "users": conf.get_users(),
            "groups": conf.get_groups(),
            "context": conf.context,
            "profile": conf.profile,
            "version": conf.version,
            "config": conf.config,
        })
    return HttpResponse(pickle.dumps(result), mimetype="text/plain")
