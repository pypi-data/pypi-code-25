from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings
from django.template import loader
from oauth import OAuth

oauthWrapper = OAuth(settings.NCTU_APP_CLIENT_ID, settings.NCTU_APP_CLIENT_SECRET, settings.NCTU_APP_REDIRECT_URI)

def login(request):
    # check for token from nctu oauth redirection
	if OAuth.get_profile(request) == None:
		return oauthWrapper.authorize()
	return redirect('/')
