#encoding=utf-8
"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from profile.models import ClientUser
from search.models import DocumentSurrogate, DmozCategory
import logging
from service import WebServiceException, web_extract_terms, build_query
from django.contrib.webdesign import lorem_ipsum
import urllib
from profile.tasks import update_profile
from search.views import do_search
from service import re_rank
import subprocess
from django.conf import settings
import djapian
from djapian.space import IndexSpace

index_set = False
def _reset_index():
    global index_set
    if not index_set:
        djapian.space = IndexSpace(settings.DJAPIAN_DATABASE_PATH, "global")
        djapian.add_index = djapian.space.add_index
        try:
            #as explained in http://code.google.com/p/djapian/wiki/RunningTheIndexer
            retcode = subprocess.call(['%s/manage.py'%settings.ROOT_PATH, 'index', '--rebuild'])
            if retcode < 0:
                logging.debug("Update index terminated by signal")
            else:
                logging.debug("Update index returned")            
        except OSError:
            logging.error("Execution of update_index failed")            
        djapian.load_indexes()                
        DocumentSurrogate.indexer.update()
        index_set = True

class WebExtractionTest(TestCase):
    """Test the helper methods for text extraction by web services
       Only the three major services are tested
       (tagthe, yahoo, alchemy)
    """
    def setUp(self):
        self.query = 'einstein is a scientist'
        self.es_query = """La batalla de Heraclea ocurrió en el 280 a. C., en la ciudad de Heraclea,
                          la actual Polícoro, dando inicio a las Guerras Pírricas.
                          Estas guerras fueron el último intento de las poleis de la Magna Grecia
                          de impedir la expansión por la península itálica de la joven República romana.
                          Para conseguir frenar a los romanos llamaron en su ayuda al rey Pirro de Epiro,
                          de ahí el nombre del conflicto."""
                          
        self.expected_terms = ['einstein', 'scientist']
        
    
    def test_invalid_service(self):
        """test that only valid services are called"""
        self.assertRaises(ValueError, web_extract_terms('', service='FOOBAR'))      
    
    def test_tagthe_extraction(self):
        """
        Test terms extraction with tagthe
        """
        terms = web_extract_terms(self.query, service='tagthe')
        
        self.assert_(set(self.expected_terms) & set(terms))
        
    def test_yahoo_extraction(self):
        """Test term extraction with yahoo"""
        terms = web_extract_terms(self.query, service='yahoo')
        
        self.assert_(set(self.expected_terms) & set(terms))
    
    def test_alchemy_extraction(self):
        """Test term extraction with alchemy"""
        terms = web_extract_terms(self.query, service='alchemy')
                       
        self.assert_(set(self.expected_terms) & set(terms))
        
    def test_spanish_query_tagthe(self):
        """Test tagthe's prowess for spanish language queries"""
        terms = web_extract_terms(self.es_query, service='tagthe')
        
        self.assert_(terms, 'No terms returned')
        
    def test_spanish_query_yahoo(self):
        """Test yahoo's prowess for spanish language queries"""
        terms = web_extract_terms(self.es_query, service='yahoo')
        
        self.assert_(terms, 'No terms returned')
        
    def test_spanish_query_alchemy(self):
        """Test alchemy's prowess for spanish language queries"""
        terms = web_extract_terms(self.es_query, service='alchemy')
        
        self.assert_(terms, 'No terms returned')
    
    def test_big_query_tagthe(self):
        """Test that tagthe supports queries with more than 2048 characters
            
           tagthe is a special case because requests are made via GET           
        """
        #500 words are > 2048 characters
        try:
            terms = web_extract_terms(lorem_ipsum.words(500), service = 'tagthe')
        except WebServiceException:
            self.fail("Tagthe can't handle more than 500 words")
        except:            
            self.fail("other exception!")
        
        self.assert_(hasattr(terms, '__iter__'))
        
    def test_big_query_yahoo(self):
        """Test a big query on yahoo (more than 2048 characters)           
        """
        #500 words are > 2048 characters
        
        try:
            terms = web_extract_terms(lorem_ipsum.words(500), service = 'yahoo')
        except WebServiceException:
            self.fail("yahoo can't handle more than 500 words")
        except:            
            self.fail("other exception!")       
        
        self.assert_(hasattr(terms, '__iter__'))
        
    def test_big_query_alchemy(self):
        """Test a big query on alchemy (more than 2048 characters)
        """
        #500 words are > 2048 characters
        try:
            terms = web_extract_terms(lorem_ipsum.words(500), service = 'alchemy')
        except WebServiceException:
            self.fail("alchemy can't handle more than 500 words")
        except:            
            self.fail("other exception!")       
        
        self.assert_(hasattr(terms, '__iter__'))

    
    def test_query_limit_alchemy(self):
        """Alchemy has a limit of 150Kb of text"""
        txt = lorem_ipsum.words(500000)
        while len(txt)/1000 <= 150:
            txt = lorem_ipsum.words(500000)
        
        self.assertRaises(WebServiceException, web_extract_terms(txt, service = 'alchemy'))
    
    def test_query_limit_yahoo(self):
        """Test the same limit on alchemy for yahoo
           
           It shouldn't fail, as they don't state a limit
        """
        txt = lorem_ipsum.words(500000)
        while len(txt)/1000 <= 150:
            txt = lorem_ipsum.words(500000)
        
        self.assert_(hasattr(web_extract_terms(txt, service = 'yahoo'), '__iter__'), 'Yahoo cannot handle 150kb of txt')
    
    def test_query_limit_tagthe(self):
        """Test the same limit on alchemy for tagthe
           
           It shouldn't fail, as they don't state a limit
           
           BUT, with practical tests, tagthe breaks like crackers when submitted text this large...
        """
        txt = lorem_ipsum.words(500000)
        while len(txt)/1000 <= 150:
            txt = lorem_ipsum.words(500000)
        
        self.assert_(hasattr(web_extract_terms(txt, service = 'tagthe'), '__iter__'), 'Tagthe cannot handle 150kb of txt')
    
    

class TestQueryBuilding(TestCase):
    """Test the query building method"""
    
    def setUp(self):
        self.dirty_query= "<div><strong>einstein was a scientist</strong></div>"
        self.es_dirty_query= u"<div><strong>einstein era un científico</strong></div>"
    
    def test_query_building(self):
        """test that a query is built with the default arguments"""        
        self.assert_(len(build_query(self.dirty_query)), 'No query was built')
    
    def test_spanish_query_building(self):
        """test that a query in spanish is built"""
        
        self.assert_(len(build_query(self.es_dirty_query, language='es')), 'No query was built')
        
    def test_offline_fail(self):
        """test that query building with web services fails loudly when an http error arises"""
        try:
            urllib.urlopen('http://www.google.com')
        except IOError: #no connection
            self.assertRaises(AttributeError,build_query(self.es_dirty_query, language='es', fail_silently=False))
        else:
            self.fail('Must try this without internet connection')
    
    def test_offline_silent_fail(self):
        """test that query building with web services fails silently when an http error arises"""
        try:
            urllib.urlopen('http://www.google.com')
        except IOError: #no connection
            self.assertFalse(build_query(self.dirty_query, language='es', fail_silently=True))
        else:
            self.fail('Must try this without internet connection')
    
    def test_topia_big_query(self):
        """test topia's behavior with average big queries"""
        self.assert_(build_query(lorem_ipsum.words(500), language='en', fail_silently=True))
    
    def test_topia_limit_query(self):
        """test the topia extraction method with a practical limit query 
            
           Limited by the lower bound set by alchemy
        """
        txt = lorem_ipsum.words(500000)
        while len(txt)/1000 <= 150:
            txt = lorem_ipsum.words(500000)
        
        self.assert_(build_query(txt, language='en', fail_silently=True))
        

           

class ReRankingTest(TestCase):
    """Test the re ranking method"""
    
    fixtures = ['testData.json', 'testApp.json']
    
    def setUp(self):
        self.profile = ClientUser.objects.get(clientId='testUser1')        
        #HACK: re-index the test documents EVERY time a test is performed:
        _reset_index()
        
    def test_re_ranking(self):
        """Given a profile and some search results, test that preferred categories are ranked high"""
        
        #'matter' yields only physics as it's category
        categories = DmozCategory.get_for_query(query="matter", lang='en')
        docs = list(DocumentSurrogate.objects.filter(category__in=categories).values_list('pk', flat=True))
        
        r = update_profile.apply(args=[self.profile, 'matter', []], kwargs={'lang': 'en', 'terms': True})
        
        #'study' yields both physics and computer science as it's categories
        results = do_search('study')
        re_ranked = re_rank(self.profile, results)
        re_ranked = [e['id'] for e in re_ranked]
        logging.debug('Results: %s' % results)
        logging.debug('ReRanked: %s' % re_ranked)                
        self.assertEqual(sorted(re_ranked[:len(docs)]), sorted(docs))
    
    def test_re_ranking_spanish(self):
        """Given a profile and some search results in spanish, test that preferred categories are ranked high"""
        #'computación' yields only computer science as it's category
        categories = DmozCategory.get_for_query(query="computación", lang='es')
        docs = list(DocumentSurrogate.objects.filter(category__in=categories, lang='es').values_list('pk', flat=True))
        
        r = update_profile.apply(args=[self.profile, 'computación', []], kwargs={'lang': 'es', 'terms': True})
        
        #'sistema' yields both science and computer science as it's categories
        results = do_search('sistemas OR sistemáticamente')
        logging.debug('Results: %s' % results)
        re_ranked = re_rank(self.profile, results)
        logging.debug('ReRanked: %s' % re_ranked)
        re_ranked = [e['id'] for e in re_ranked]
        
                        
        self.assertEqual(sorted(re_ranked[:len(docs)]), sorted(docs))
        
#
#class DecoratorsTest(TestCase):
#    """Test the auth and api calls decorators """
#    pass
