# Create your views here.
from django.http import HttpResponse
from service import build_query, WEB_SERVICES
try:
    import json
except ImportError:
    import django.utils.simplejson as json
import logging

def get_terms(request):
    """Given an ajax request, return, in a json, the index terms"""
    context = request.REQUEST.get('context')
    lang = request.REQUEST.get('lang', 'en')
    service = request.REQUEST.get('service', 'yahoo')    
    service = service if service in WEB_SERVICES.keys() else 'yahoo'
    
    if context:        
        terms = build_query(context, language=lang, web_service=service)
    else:
        terms = ""
        
    if request.is_ajax():
        return HttpResponse(json.dumps({'terms': terms}, ensure_ascii=False), mimetype="application/json")
    else:
        return HttpResponse(terms, mimetype="text/plain")