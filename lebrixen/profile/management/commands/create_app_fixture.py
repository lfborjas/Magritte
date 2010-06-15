'''
Created on 14/06/2010

@author: lfborjas

Create an app an a couple of users for testing
'''

from django.core.management.base import NoArgsCommand
from django.conf import settings
import os
from profile.models import ClientApp, ClientUser
from django.contrib.auth.models import User
import itertools
from django.core import serializers

class Command(NoArgsCommand):
    help = "Create test application data for the unit tests of the search and profiling apps"
    
    def handle_noargs(self, **options):
        print "Creating application"
        app = ClientApp(url='fixtureapp.tmp')
        app.save()
        usr = User.objects.create_user(app.url, 'test@app.com', 'testapp')
        app.user = usr
        app.save()
        print "Creating test users for application"
        client1 = ClientUser(app=app, clientId='testUser1')
        client1.save()
        client2 = ClientUser(app=app, clientId='testUser2')
        client2.save()
        
        json_serializer = serializers.get_serializer('json')()        
        fixture = open(os.path.join(settings.ROOT_PATH, 'profile', 'fixtures', 'testApp.json'), 'w')
        
        print "Creating fixture"
        try:
            json_serializer.serialize([app,usr,client1,client2], stream = fixture)
        except:
            print "couldn't serialize"
            pass
        
        print "Deleting from db"
        app.delete()
        usr.delete()
        client1.delete()
        client2.delete()
        