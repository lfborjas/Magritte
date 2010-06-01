# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from service import build_query, WEB_SERVICES, api_call, re_rank
from search.views import do_search 
try:
    import jsonlib2 as json
except ImportError:
    import json
except ImportError:
    import django.utils.simplejson as json
    
import logging
from django.template.loader import render_to_string
from profile.tasks import update_profile
from django.utils.translation import check_for_language
from django.template.context import RequestContext
from service.auth_backend import basic_auth
from django.views.decorators.http import require_POST, require_GET 

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

@require_GET
@api_call
def start_session(request):
    """Check that this is an authentic session starter call and that the middleware managed to set the profile
        
       if it is, return the html to build the recommender bar
    """
    lang = request.REQUEST.get('lang', 'en')
    if hasattr(request, 'session') and check_for_language(lang):
        request.session['django_language'] = lang         
    #this could contain some attributes for the style or something...       
    raw_bar = render_to_string('recommender_bar.html', {}, context_instance = RequestContext(request))
     
    return HttpResponse(json.dumps({'recommender_bar': raw_bar, 'valid': True, 'status':200}),
                         mimetype="application/json")
    
#Because the text might be too large, we accept POST or GET indistinctly #@require_GET
@api_call
def get_recommendations(request):
    if not 'content' in request.REQUEST:
        return HttpResponseBadRequest("No content provided")
    #get the terms
    context = request.REQUEST['content']
    lang = request.REQUEST.get('lang', 'en')
    service = request.REQUEST.get('service', '')    
    service = service if service in WEB_SERVICES.keys() or (not service and lang == 'en') else 'tagthe'
    use_service = bool(service)    
    
    terms = build_query(context, language=lang, use_web_service=use_service, web_service=service)
     
    #do the search
    results = do_search(terms, lang=lang)
    #re-rank
    if hasattr(request, 'profile'):
        results=re_rank(request.profile, results)
    else:
        return HttpResponseBadRequest("No profile found")
    #return    
    return HttpResponse(json.dumps({'results': results, 'terms': unicode(terms), 'valid': True, 'status': 200}, ensure_ascii=False, encoding='utf-8'),
                         mimetype="application/json")

@api_call
def end_session(request):
    """When a user's session ends, push a task on the queue to evolve his profile"""
    update_profile.delay(request.profile,
                         request.REQUEST.get('context', []),
                         request.REQUEST.getlist('docs'),
                         lang=request.REQUEST.get('lang', 'en'),
                         terms=request.REQUEST.get('t', False))       
    return HttpResponse(json.dumps({'valid': True, 'status': 200}), mimetype="application/json")


@require_POST
@basic_auth
def register_users(request, bulk=False):
    """Register a user or a list of users. If bulk, then it will be asynchronous"""
    if bulk:
        pass #delay
    else:
        pass #get_or_create the user

register_users = api_call(register_users, required=['appId'])