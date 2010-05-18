'''
Created on 17/05/2010

@author: lfborjas
'''

from django.conf import settings

class BadApp(Exception):
    def __str__(self):
        return "The app doesn't exist"

class LazyProfile(object):
    def __init__(self, app_id):
        self.app_id = app_id
    
    def __get__(self, request, obj_type=None):
        #Set the cached profile if it doesn't already exist (that is, only query once):
        if not hasattr(request, '_cached_profile'):
            from profile.models import ClientUser
            #If the request has the data, then use that to retrieve the user profile
            if settings.APP_ID in request.REQUEST and settings.APP_USER in request.REQUEST:
                d = request.REQUEST
                #Get the app that is requesting, don't let it through if the app doesn't exist                                
                request.session[settings.APP_ID] =  request.REQUEST.get(settings.APP_ID)
                request.session[settings.APP_USER] = request.REQUEST.get(settings.APP_USER)
            #If they didn't come in the request, resort to the session                 
            elif settings.APP_ID in request.session and settings.APP_USER in request.session:
                d = request.session
            else:
                raise Exception('Insufficient information to retrieve profile. Should have been provided in the init call or in this request')
            
            
            request._cached_profile = ClientUser.objects.get(app_id = self.app_id,
                                                             clientId = d.get(settings.APP_USER))
                
        return request._cached_profile


class ProfileMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'),\
         "The profile middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        request.__class__.profile = LazyProfile()
        return None
