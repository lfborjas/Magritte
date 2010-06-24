"""
Search tests: test the search method and the classification method
"""

from django.test import TestCase
from search.models import DmozCategory, DocumentSurrogate
from django.test.simple import run_tests
from dstest.test_runner import run_tests as sel_tests 
from django.conf import settings
import logging

def custom_run_tests(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    """Set the test indices"""
    settings.CATEGORY_CLASSIFIER_DATA = settings.TEST_CLASSIFIER_DATA
    settings.DJAPIAN_DATABASE_PATH = settings.DJAPIAN_TEST_PATH
    settings.IGNORE_CAPTCHA = True
    #run celery in eager mode (don't depend on the daemon)
    settings.CELERY_ALWAYS_EAGER = True    
    #the selenium test runner has problems with qualified names, so default to the normal runner if that is the case          
    if '.' in str(test_labels):        
        return run_tests(test_labels, verbosity, interactive, extra_tests)
    else:
        return sel_tests(test_labels, verbosity, interactive, extra_tests)

class ClassifierTest(TestCase):
    """ Tests for the classifier module
        
        Basic tests inspired by the djapian test suite:
        http://code.google.com/p/djapian/source/browse/trunk/src/djapian/tests/search.py                
    """
    fixtures = ['testData.json']
    
    def setUp(self):             
        """Set the query, categories and results"""
                                     
        self.query = 'study'
        self.query_candidates = ['Physics','Computer Science']
        
        self.exact_queries = {
                              'en': 'Einstein',
                              'es': 'Einstein',
                              }
        self.exact_candidate ='Quantum Physics'          
        
          
    def test_query(self):
        """Test that a query returns an iterable of categories"""
                
        results = DmozCategory.get_for_query(self.query)
        self.assert_((len(results)
                      and hasattr(results, '__iter__')                      
                      and isinstance(results[0], DmozCategory)))
            
    def test_english_query(self):
        """Test that a query for a category in english works
           
           Must return the quantum physics category and only that one!
        """
        result = list(DmozCategory.get_for_query(self.exact_queries['en'], 'en'))
        if len(result) != 1:
            self.fail('Only expecting one category!')
        resultC = result[0]
        self.assertEqual(resultC, DmozCategory.objects.get(title=self.exact_candidate))
        
    def test_spanish_query(self):
        """Test that a query in spanish works"""
        
        result = list(DmozCategory.get_for_query(self.exact_queries['es'], 'es'))
        if len(result) != 1:
            self.fail('Only expecting one category!')
        resultC = result[0]
        self.assertEqual(resultC, DmozCategory.objects.get(title=self.exact_candidate))
        
    def test_invalid_lang_query(self):
        """Test that, given an invalid language code, the method defaults to the base lang (english)"""
        results = [e.pk for e in DmozCategory.get_for_query(self.query, lang='fr')].sort()
        expected = [e.pk for e in DmozCategory.get_for_query(self.query)].sort()
        self.assertEqual(results, expected)
    
    def test_category_list(self):
        """Test that when given ambiguous queries the classifier returns a list of candidates"""        
        results = sorted([e.pk for e in DmozCategory.get_for_query(self.query)])
        expected = DmozCategory.objects.filter(
                                    title__in=self.query_candidates).order_by('pk').values_list('pk', flat=True)
                             
        self.assertEqual(results, list(expected))
    
    def test_weighting(self):
        """Test that the categories receive a score"""
        results = DmozCategory.get_for_query(self.query)
        self.assert_(hasattr(results[0], 'relative_weight'))
        
    def test_score_range(self):
        """Test that scores are numbers in [0,100]"""
        results = DmozCategory.get_for_query(self.query)
        self.assertFalse([e for e in results if (e.relative_weight > 1 or e.relative_weight < 0)])
        
    def test_score(self):
        """Test that an important candidate receives a high score"""
        results = DmozCategory.get_for_query(self.query)
        self.assert_(results[0].relative_weight >= 0.98)
            
    def test_as_dict(self):
        """Test the dictionary option"""
        results = DmozCategory.get_for_query(self.query)
        dict_results = DmozCategory.get_for_query(self.query, as_dict=True)
        
        result = dict_results.keys().sort()
        expected = [e.pk for e in results].sort()
        self.assertEqual(result, expected)
        
    def test_empty_query(self):
        """Test that no categories are returned for a non-existant word"""
        self.assertFalse(DmozCategory.get_for_query('lorem ipsum'))
    
    def test_empty_query_as_dict(self):
        """Test that the dict option returns an empty iterable if an empty query is ensued"""
        self.assertFalse(DmozCategory.get_for_query('lorem ipsum', as_dict=True))
    
    def test_max_results(self):
        """Check that the max results constraint is respected"""
        self.assertEqual(len(DmozCategory.get_for_query(self.query, max_results=1)), 1)
        



