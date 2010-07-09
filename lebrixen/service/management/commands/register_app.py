#!/usr/bin/env python
#encoding = utf-8
'''
Created on 18/05/2010

@author: lfborjas
'''
from django.conf import settings
from profile.models import ClientApp
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.contrib.auth.models import User 

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
                  make_option('--url', dest='app_url',                    
                    help='The url of the app to register'),
                  make_option('--email', dest='app_email',                    
                    help='The contact email of the app to register'),
                                             )
    help = "Register an app and get it's credentials"
    args = 'url email'      
                
    def handle(self, url, email, *args, **options):
        try:
            app = ClientApp(url=url)
            app.save()
            
            raw_pass = User.objects.make_random_password()
            u = User.objects.create_user(app.url, email, raw_pass)
            u.save()                                           
            #logging.debug('pass for %s: %s' % (app.url, raw_pass))
            app.user = u
            app.save()
            
            return app.get_token(), app.user.username, raw_pass
        except Exception, e:
            raise CommandError(e.message)




