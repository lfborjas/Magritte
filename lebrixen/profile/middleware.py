'''
Created on 17/05/2010

@author: lfborjas
'''

from django.http import HttpResponseNotFound, HttpResponseBadRequest, HttpResponse
import re
import logging
import validate_jsonp
try:
    import jsonlib2 as json
except ImportError:
    import json
except ImportError:
    import django.utils.simplejson as json

API_URLS = r'^/api/.*$'

class LazyProfile(object):
    def __init__(self, app_id):        
        self.app_id = app_id
    
    def __get__(self, request, obj_type=None):
        #Set the cached profile if it doesn't already exist (that is, only query once):        
        if not hasattr(request, '_cached_profile'):
            from profile import get_profile            
            request._cached_profile = get_profile(request, self.app_id)               
        return request._cached_profile


class ProfileMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'),\
         "The profile middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        m = re.match(API_URLS, request.path)
        if not m:            
            return None
        from profile import APP_ID, APP_KEY, PROFILE_ID
        from profile.models import ClientApp
        #try to respect REST:, if they provide the appId again, it must be that they like doing queries all the time:        
        if APP_ID in request.REQUEST:
            message = "No app with the given token is registered or the token is invalid"
            try:                
                a = ClientApp.get_for_token(request.REQUEST[APP_ID], id_only=True)
                request.session[APP_KEY] = a
                request.__class__.profile = LazyProfile(request.session[APP_KEY])
                if not hasattr(request, 'profile') and PROFILE_ID in request.REQUEST:
                    message = "The requested user does not exist"
                    raise Exception('Not existent user')
                #limit the number of requests:
                #r=ClientRequest(date=date.today(), app=a, ip=request.META.get('REMOTE_ADDRESS', ''));r.save() 
                #if ClientRequest.objects.filter(date = date.today(), app = a).count() > REQUEST_LIMIT: rval = "403 Exceeded";raise Exc
                #limit the number of users:
                #if ClientApp.objects.get(pk=a).users.count() >= USER_LIMIT: rval="403 usr limit exceeded"; raise Exc 
            except:
                rval = json.dumps({'message': message,
                                   'status': 404,
                                   'data': {}})
                cb = ''
                if 'callback' in request.REQUEST:
                    cb = request.REQUEST['callback']            
                    if not validate_jsonp.is_valid_jsonp_callback_value(cb):
                        return HttpResponseBadRequest('%s is not a valid jsonp callback identifier' % cb,
                                     mimetype='text/plain')
                    rval = '%s(%s)' % (cb, rval)
                return HttpResponse(rval, mimetype='application/json')
            
        #elif not APP_KEY in request.session:
        #    return HttpResponseBadRequest("An app token must have been provided in a call to startSession or in this request")
                        
        return None
