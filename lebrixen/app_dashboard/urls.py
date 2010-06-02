'''
Created on 01/06/2010

@author: lfborjas
'''

from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout, password_reset, password_reset_confirm
urlpatterns = patterns('app_dashboard.views',
                       (r'^$', 'dashboard'),
                       (r'^users/$', 'get_users'),
                       (r'^users/remove/$', 'remove_user'),
                       #user authentication
                       (r'^login/$', login, {'template_name': 'dashboard_login.html'}),
                       (r'^logout/$', logout, {'next_page': '/'}),
                       (r'^password_reset/$', password_reset, {'template_name': 'dashboard_pwd_reset.html',
                                                       'post_reset_redirect': '/',
                                                       'email_template_name': 'dashboard_mail/password_reset_confirm.txt'}),
                       (r'^password_reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 
                        password_reset_confirm, {'template_name': 'dashboard_pwd_reset_confirm.html',
                                                       'post_reset_redirect': '/'}),
                                                       
                           
)


