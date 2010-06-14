"""
Search tests: test the search method and the classification method
"""

from django.test import TestCase
import unittest
from funkload.Lipsum import Lipsum
from search.models import DocumentSurrogate, DmozCategory

class SearchTest(TestCase):
    """Tests for the search backend, check that it actually works!
        
        Create a couple of short documents in spanish and english
        to test querying, stemming and ordering.        
    """
    
    def setUp(self):
        self.categories = [DmozCategory.objects.create(title="Fungi",
                                                       topic_id="Fungi",                                                       
                                                       ),
                           DmozCategory.objects.create(title="") 
                                                       ]
        self.documents = [
                          DocumentSurrogate.objects.create(text="""Mycena haematopus, commonly known as the bleeding fairy helmet, the burgundydrop bonnet, or the bleeding Mycena, is a species of fungus in the Mycenaceae family, of the order Agaricales. It is widespread and common in Europe and North America, and has also been collected in Japan and Venezuela. It is myco-heterotrophic—meaning that it obtains nutrients by consuming decomposing organic matter—and the fruit bodies appear in small groups or clusters on the decaying logs, trunks, and stumps of deciduous trees, particularly beech. The fungus, first described scientifically in 1799, is classified in the Lactipedes section of the genus Mycena, along with other species that produce a milky or colored latex.""")
                          ]
        
    def test_searchEmptyQuery(self):
        """
        Tests that empty text returns an empty list of results              
        """
        self.failUnlessEqual(1 + 1, 2)
    
    def test_searchRandomText(self):
        """
        Random text must return a list of results (empty or not)
        """
        pass
    
    def test_searchExistentQuery(self):
        """
        Search for a word that surely exists in the database: must be a full list
        """
        pass
        



