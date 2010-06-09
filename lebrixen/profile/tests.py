"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
import urllib2 
from django.utils.http import urlencode
username = "xkcd.com"
token = "816ba169c8d6288c7a6a80ae2c087e2c"
password = "68xxsknhv3"
protocol = 'http://'
superUrl = protocol+"trecs.com/api/"

urls = {
        'register' : superUrl+"registerUser/",
        'bulk' : superUrl+"bulkRegisterUsers/",
        'get' : superUrl+"getUsers/",
        'delete' : superUrl+"deleteUser/",
}

class RegistrationTest(TestCase):
    fixtures = ['testAccounts.json']
    
    def setUp(self):             
        #set the auth mechanism:
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        #set the credentials for the superUrl
        passman.add_password(None, superUrl, username, password)
        #auth handler
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        #the new opener
        opener = urllib2.build_opener(authhandler)        
        urllib2.install_opener(opener)

