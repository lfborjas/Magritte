'''
Created on 18/05/2010

@author: lfborjas
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('service.views',
    (r'^startSession/$', 'start_session'),
)


