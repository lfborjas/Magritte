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
from service import re_rank, api_call
import subprocess
from django.conf import settings
import djapian
from djapian.space import IndexSpace
import base64
from django.http import HttpResponse, HttpResponseServerError, HttpResponseNotModified
from service.auth_backend import basic_auth
from django.utils.importlib import import_module
import re
import json 

index_set = False
def _reset_index():
    """Create a djapian index for the test data
    
        Note that the djapian space needs to be reset because that attribute is set BEFORE
        the test runner call. 
        
        An index is created and then loaded. This method is guaranteed  [in non weird situations]
        to be only performed once in a test run, so it's safe to call it from a setUp
    """
    
    
    global index_set
    if not index_set:
        #RESET the djapian space attribute to point to the correct db 
        djapian.space = IndexSpace(settings.DJAPIAN_DATABASE_PATH, "global")
        djapian.add_index = djapian.space.add_index
        #Create the index
        try:
            #as explained in http://code.google.com/p/djapian/wiki/RunningTheIndexer
            retcode = subprocess.call(['%s/manage.py'%settings.ROOT_PATH, 'index', '--rebuild'])
            if retcode < 0:
                logging.debug("Update index terminated by signal")
            else:
                logging.debug("Update index returned")            
        except OSError:
            logging.error("Execution of update_index failed")            
        #load the indices
        djapian.load_indexes()                
        #ensure that this method won't be called again in a test run
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


class DummyRequest(object):
    """Dummy request class to test the decorators, tailor made to match the attributes needed by those methods
    
        NEVER use in lieu of django.htpp.HttpRequest! (For view testing, use the test client)
    
    """    
    def __init__(self, request={}, auth={}):
        self.REQUEST = request
        self.META = {}
        engine = import_module(settings.SESSION_ENGINE)        
        self.session = engine.SessionStore('2b1189a188b44ad18c35e113ac6ceead')
        if auth and 'username' in auth and 'password' in auth:            
            self.META['HTTP_AUTHORIZATION'] = "basic %s" % base64.b64encode('%s:%s' % (auth['username'], auth['password']))         

class AuthDecoratorTest(TestCase):
    """Test the auth decorator """
    
    fixtures = ['testApp.json']
    
    def setUp(self):
        self.credentials={'username': 'fixtureapp.tmp',
                          'password': 'testapp'}
    
    def test_auth_no_headers(self):
        """If no auth credentials are given, must return a 401"""
        dummy_function = lambda request: HttpResponse()
        decorated_dummy = basic_auth()(dummy_function) 
        self.assertContains(response=decorated_dummy(DummyRequest()), text='', status_code=401)
    
    def test_auth_no_app(self):
        """If auth credentials are given, but the user doesn't exist, expect a 401"""
        
        dummy_function = lambda request: HttpResponse()
        decorated_dummy = basic_auth()(dummy_function) 
        self.assertContains(response=decorated_dummy(DummyRequest(auth={'username': 'lalo','password':'foo'})),
                            text='', status_code=401)
    
    def test_auth_incorrect_password(self):
        """Test that password is actually verified"""
        dummy_function = lambda request: HttpResponse()
        decorated_dummy = basic_auth()(dummy_function) 
        self.assertContains(response=decorated_dummy(DummyRequest(auth={'username': self.credentials['username'],
                                                                        'password':'foo'})),
                            text='', status_code=401)
    
    def test_auth(self):
        """Test that, given credentials, a user authenticates successfully"""
        dummy_function = lambda request: HttpResponse('made it!')
        decorated_dummy = basic_auth()(dummy_function) 
        self.assertContains(response=decorated_dummy(DummyRequest(auth=self.credentials)),
                            text='made it!')

class ApiCallDecoratorTest(TestCase):
    """Test the api_call decorator"""
    
    def _assertJson(self, json_string='', callback=None, status=200, message='', data=None):
        """Assertions for json data"""
        if callback:
            m=re.match(r'%s\((?P<d>.*)\)'%callback, json_string)
            json_string= m.group('d')
        
        json_data= json.loads(json_string)        
        return json_data['status']==status and json_data['message']==message and json_data['data']==data 
             
    
    def test_invalid_callback(self):
        """Test that, if an invalid callback is provided, return a 400"""
        
        dummy_function = lambda request: HttpResponse()
        decorated_dummy = api_call()(dummy_function) 
        self.assertContains(response=decorated_dummy(DummyRequest(request={'callback': '9$'})),
                            text='9$ is not a valid jsonp callback identifier', status_code=400)
    
    def test_missing_required(self):
        """Test that if a required parameter is missing, is a bad request in json"""
        dummy_function = lambda request: HttpResponse()
        decorated_dummy = api_call(required=['arg'])(dummy_function) 
        
        response=decorated_dummy(DummyRequest())
        
        self._assertJson(json_string=response.content, status=400, message='The following arguments are required for this call: arg')
       
                            
    
    def test_missing_required_callback(self):
        """Test that a bad request returns for a callback request without the required args"""
        
        dummy_function = lambda request: HttpResponse()
        decorated_dummy = api_call(required=['arg'])(dummy_function) 
        callback = 'jsonp123'
        response=decorated_dummy(DummyRequest(request={'callback':callback}))
        
        self._assertJson(json_string=response.content,
                         status=400,
                         message='The following arguments are required for this call: arg',
                         callback=callback)
    
    def test_missing_required_callback_expected_data(self):
        """Test that a bad request returns for a callback request without the required args and the data returns with
           the expected structure"""
        data = dict.fromkeys(['data', 'data2'])
        dummy_function = lambda request: HttpResponse()
        decorated_dummy = api_call(required=['arg'], data=['data', 'data2'] )(dummy_function) 
        callback = 'jsonp123'
        response=decorated_dummy(DummyRequest(request={'callback':callback, 'arg': 2}))
        
        self._assertJson(json_string=response.content,
                         status=400,
                         message='The following arguments are required for this call: arg',
                         callback=callback,
                         data=data)
           
    
    def test_error_encoding(self):
        """Test that the decorator converts the http errors from the views in json objects"""
        
        error_message = 'whales killed those little birdies'
        dummy_function = lambda request: HttpResponseServerError(error_message)
        decorated_dummy = api_call(required=['arg'])(dummy_function) 
        #callback = 'jsonp123'
        response=decorated_dummy(DummyRequest(
                                              request={'arg':0}
                                              ))
        
        self._assertJson(json_string=response.content,
                         status=500,
                         message=error_message,
                         #callback=callback
                         )
    
    def test_error_encoding_callback(self):
        """Test that the decorator converts the http errors from the views in json objects when callbacks are used"""
        
        error_message = 'whales killed those little birdies'
        dummy_function = lambda request: HttpResponseServerError(error_message)
        decorated_dummy = api_call()(dummy_function) 
        callback = 'jsonp123'
        response=decorated_dummy(DummyRequest(
                                              request={'callback':callback}
                                              ))
        
        self._assertJson(json_string=response.content,
                         status=500,
                         message=error_message,
                         callback=callback
                         )
        
    def test_error_encoding_expected_data(self):
        """Test that the decorator converts the http errors from the views in json objects and respects expected data"""
        data = dict.fromkeys(['data', 'data2'])
        error_message = 'whales killed those little birdies'
        dummy_function = lambda request: HttpResponseServerError(error_message)
        decorated_dummy = api_call(required=['arg'], data=['data', 'data2'])(dummy_function) 
        #callback = 'jsonp123'
        response=decorated_dummy(DummyRequest(
                                              request={'arg':1}
                                              ))
        
        self._assertJson(json_string=response.content,
                         status=500,
                         message=error_message,
                         data=data
                         )
        
    def test_indirect_success(self):
        """Test that a json object is returned with the expected data from non-200 success pages"""
        
        dummy_function = lambda request: HttpResponseNotModified()
        decorated_dummy = api_call()(dummy_function) 
        #callback = 'jsonp123'
        response=decorated_dummy(DummyRequest())
        
        self._assertJson(json_string=response.content,
                         status=304,
                         message='',                         
                         #callback=callback
                         )

        
    def test_success(self):
        """Test that a json view returns successfully"""
        data = {'r': 0}
        error_message = 'whales killed those little birdies'
        dummy_function = lambda request: {'r': request.REQUEST['arg']}
        decorated_dummy = api_call(required=['arg'], data=['r'])(dummy_function) 
        #callback = 'jsonp123'
        response=decorated_dummy(DummyRequest(
                                              request={'arg':0}
                                              ))
        
        self._assertJson(json_string=response.content,
                         status=200,
                         message='',
                         data=data
                         )
        
    def test_success_callback(self):
        """Test that a json view returns successfully with callback"""
        data = {'r': 0}
        error_message = 'whales killed those little birdies'
        dummy_function = lambda request: {'r': request.REQUEST['arg']}
        decorated_dummy = api_call(required=['arg'], data=['r'])(dummy_function) 
        callback = 'jsonp123'
        response=decorated_dummy(DummyRequest(
                                              request={'arg':0, 'callback': callback}
                                              ))
        
        self._assertJson(json_string=response.content,
                         status=200,
                         message='',
                         data=data,
                         callback=callback
                         )