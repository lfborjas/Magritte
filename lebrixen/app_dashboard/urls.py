'''
Created on 01/06/2010

@author: lfborjas
'''

from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
urlpatterns = patterns('app_dashboard.views',
                       (r'^$', 'dashboard'),
                       (r'^users/$', 'get_users'),
                       (r'^users/remove/$', 'remove_user'),
                       (r'^login/$', login, {'template_name': 'dashboard_login.html'}),
                       (r'^logout/$', logout, {'next_page': '/'}),    
)


