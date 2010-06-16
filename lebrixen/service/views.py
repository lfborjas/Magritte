# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotFound, HttpResponseForbidden
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
from profile.tasks import update_profile, add_bulk_users
from django.utils.translation import check_for_language
from django.template.context import RequestContext
from service.auth_backend import basic_auth
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings 

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


@api_call(required=['appId'])
@require_GET
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
@api_call()
def get_recommendations(request):
    if not 'content' in request.REQUEST:
        return HttpResponseBadRequest("No content provided")
    #get the terms
    context = request.REQUEST['content']
    lang = request.REQUEST.get('lang', 'en')
    service = request.REQUEST.get('service', '')    
    service = service if service in WEB_SERVICES.keys() or (not service and lang == 'en') else 'tagthe'
    use_service = bool(service)    
    
    try:
        terms = build_query(context, language=lang, use_web_service=use_service, web_service=service, fail_silently=False)
    except:
        return HttpResponseServerError("Error extracting terms")
     
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

@api_call()
def end_session(request):
    """When a user's session ends, push a task on the queue to evolve his profile"""
    update_profile.delay(request.profile,
                         request.REQUEST.get('context', []),
                         request.REQUEST.getlist('docs'),
                         lang=request.REQUEST.get('lang', 'en'),
                         terms=request.REQUEST.get('t', False))       
    return HttpResponse(json.dumps({'valid': True, 'status': 200}), mimetype="application/json")




@basic_auth()
@api_call(required=['appId'])
@require_POST
def register_users(request, bulk=False):
    """Register a user or a list of users. If bulk, then it will be asynchronous"""
    from profile.models import ClientApp, ClientUser
    
    try:
        app = ClientApp.get_for_token(request.POST.get('appId'))
    except:
        return HttpResponseNotFound("App not found")

    users = request.POST.getlist('user')
    if not users:
        return HttpResponseBadRequest("Expected at least one 'user' argument, none given")
    
    if app.users.count() - 1 + len(users) >= settings.FREE_USER_LIMIT:
        return HttpResponseForbidden('Impossible to add more users: user limit would be exceeded')
    
    if bulk:
        add_bulk_users.delay(users, app, request.build_absolute_uri('/api/getUsers/'))
        return HttpResponse(json.dumps({'queued': True, 'status': 200, 'valid': True}), mimetype="application/json")
    else:
        #just get the first, then
        user = users[0]
        try:
            u, created = ClientUser.objects.get_or_create(app=app, clientId=user)
            return HttpResponse(json.dumps({'created': created, 'status': 200, 'valid': True}), mimetype="application/json")
        except:
            return HttpResponse(json.dumps({'created': False, 'status': 500, 'valid': False}), mimetype="application/json")
         

#register_users = api_call(required=['appId'])(register_users)


@api_call(required=['appId'])
@require_GET
def app_users(request):
    """Return a dump of all the users in an app"""
    from profile.models import ClientApp   
    
    return HttpResponse(json.dumps({'users': [{'id': e.clientId, 'added': str(e.added)} 
                                              for e in ClientApp.get_for_token(request.GET.get('appId')).users.iterator()], 
                                    'status': 200,
                                    'valid': True }, ensure_ascii=False), mimetype="application/json")
    
    
@basic_auth()
@api_call(required=['appId'])
@require_POST
def delete_user(request):
    """Remove a single user"""
    from profile.models import ClientApp, ClientUser
    
    try:
        app = ClientApp.get_for_token(request.POST.get('appId'))
    except:
        return HttpResponseNotFound("App not found")

    users = request.POST.getlist('user')
    if not users:
        return HttpResponseBadRequest("Expected at least one 'user' argument, none given")
    
        
    
    #just get the first, then
    user = users[0]
    try:
        u = ClientUser.objects.get(app=app, clientId=user)
        u.delete()
        return HttpResponse(json.dumps({'deleted': True, 'status': 200, 'valid': True}), mimetype="application/json")
    except:
        return HttpResponse(json.dumps({'deleted': False, 'status': 500, 'valid': False}), mimetype="application/json")
    
