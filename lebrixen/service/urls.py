'''
Created on 18/05/2010

@author: lfborjas
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('service.views',
    (r'^startSession/$', 'start_session'),
    (r'^getRecommendations/$', 'get_recommendations'),
    (r'^endSession/$', 'end_session'),
)


