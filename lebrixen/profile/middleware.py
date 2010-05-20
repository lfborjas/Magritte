'''
Created on 17/05/2010

@author: lfborjas
'''

from django.http import HttpResponseNotFound, HttpResponseBadRequest
import re
import logging

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
        from profile import APP_ID, APP_KEY
        from profile.models import ClientApp
        #try to respect REST:, if they provide the appId again, it must be that they like doing queries all the time:        
        if APP_ID in request.REQUEST:
            try:
                a = ClientApp.get_for_token(request.REQUEST[APP_ID], id_only=True)
                request.session[APP_KEY] = a
            except:
                return HttpResponseNotFound("No app with the given token is registered or the token is invalid")
        elif not APP_KEY in request.session:
            return HttpResponseBadRequest("An app token must have been provided in a call to startSession or in this request")
            
        request.__class__.profile = LazyProfile(request.session[APP_KEY])
        
        return None
