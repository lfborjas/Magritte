"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from profile.models import ClientUser


class ProfileTest(TestCase):
    """Test the profile evolution"""
    
    fixtures = ['testData.json', 'testApp.json']
    def setUp(self):
        self.profile = ClientUser.objects.get('testUser1')
        
        
        
    

