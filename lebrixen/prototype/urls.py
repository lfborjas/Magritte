'''
Created on 21/05/2010

@author: lfborjas
'''
from django.conf.urls.defaults import *

urlpatterns = patterns('prototype.views',    
    (r'^$', 'index'),
    (r'^demo/$', 'demo'),
    (r'^getUsers/$', 'get_users'), #an ajax view
)


