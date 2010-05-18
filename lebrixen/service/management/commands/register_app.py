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

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
                  make_option('--url', dest='app_url',                    
                    help='The url of the app to register'),
                                             )
    help = "The url of the app to register"
    args = 'url'      
                
    def handle(self, url, *args, **options):
        try:
            app = ClientApp(url=url)
            app.save()
            return app.get_token()
        except Exception, e:
            raise CommandError(e.message)




