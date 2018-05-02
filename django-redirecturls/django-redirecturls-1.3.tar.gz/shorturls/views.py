from shorturls.models import Shorturls, Hit
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404


def index(request, shortname):
    p = get_object_or_404(Shorturls, shortname=shortname)
    Hit(url=p).save()
    return HttpResponseRedirect(p.url)
