'''
Created on 23/06/2010

@author: lfborjas
'''
from django.conf.urls.defaults import patterns
from django.conf import settings
from urls import urlpatterns

urlpatterns += patterns('',                
                (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
        )