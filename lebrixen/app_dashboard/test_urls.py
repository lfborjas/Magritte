'''
Created on 23/06/2010

@author: lfborjas
'''
from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
                       #(r'^$', 'prototype.views.index'),
                       #the real ones: the trecs urls:
                       (r'^$', direct_to_template, {'template': 'trecs_home.html'}),
                       (r'^register/$', 'register.views.register'),                                                                                         
                       (r'^dashboard/', include('app_dashboard.urls')),
    
)




urlpatterns += patterns('',                
                (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
        )