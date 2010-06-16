"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from profile.models import ClientUser
import logging
from service import WebServiceException, web_extract_terms, build_query

class ExtractionTest(TestCase):
    """Test the helper methods for text extraction
       Only the three major services are tested
       (tagthe, yahoo, alchemy)
    """
    def setUp(self):
        self.query = 'einstein is a scientist'
        self.expected_terms = ['einstein', 'scientist']
    
    def test_tagthe_extraction(self):
        """
        Test terms extraction with tagthe
        """
        

class APITest(TestCase):
    """Test the api methods"""
    pass

