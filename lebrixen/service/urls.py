'''
Created on 18/05/2010

@author: lfborjas
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('service.views',
    (r'^getWidget/$', 'start_session'),
    (r'^getRecommendations/$', 'get_recommendations'),
    (r'^updateProfile/$', 'end_session'),
)


