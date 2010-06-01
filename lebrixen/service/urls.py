'''
Created on 18/05/2010

@author: lfborjas
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('service.views',
    #service core
    (r'^getWidget/$', 'start_session'),
    (r'^getRecommendations/$', 'get_recommendations'),
    (r'^updateProfile/$', 'end_session'),
    #user related
    (r'^registerUser/$', 'register_users'),
    (r'^bulkRegisterUsers/$', 'register_users', {'bulk': True}),
    (r'^getUsers/$', 'app_users'),
)


