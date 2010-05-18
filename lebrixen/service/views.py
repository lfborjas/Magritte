# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from service import build_query, WEB_SERVICES, jsonp_view
try:
    import json
except ImportError:
    import django.utils.simplejson as json
import logging
from django.template.loader import render_to_string

def get_terms(request):
    """Given an ajax request, return, in a json, the index terms"""
    context = request.REQUEST.get('context')
    lang = request.REQUEST.get('lang', 'en')
    service = request.REQUEST.get('service')    
    service = service if service in WEB_SERVICES.keys() or not service else 'yahoo'
    use_service = bool(service)    
    
    if context:        
        terms = build_query(context, language=lang, use_web_service=use_service, web_service=service)
    else:
        terms = ""
        
    if request.is_ajax():
        return HttpResponse(json.dumps({'terms': terms}, ensure_ascii=False), mimetype="application/json")
    else:
        return HttpResponse(terms, mimetype="text/plain")


def start_session(request):
    """Check that this is an authentic session starter call and that the middleware managed to set the profile
        
       if it is, return the html to build the recommender bar
    """
    from profile import APP_ID, PROFILE_ID
    #the sole purpose of this call is to set these!
    if not (APP_ID in request.REQUEST and PROFILE_ID in request.REQUEST):                
        return HttpResponseBadRequest("'appId' and 'appUser' must have been provided to start the session")
    if not 'callback' in request.REQUEST:
        return HttpResponseBadRequest("Can't return jsonp response without callback")
    elif hasattr(request, 'profile'):
        #The profile was successfully retrieved, so we can proceed to return the whole bar now, and append it
        #to the caller's page body with javascript!        
        raw_bar = render_to_string('recommender_bar.html', {}) #this could contain some attributes for the style or something...
        return HttpResponse("%s(%s)"%(request.REQUEST['callback'], json.dumps({'recommender_bar': raw_bar})),
                             mimetype="application/json")
    else:
        return HttpResponseServerError("Oops, somehow we couldn't get the profile!")
        