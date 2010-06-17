#encoding=utf-8
"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from profile.models import ClientUser, ClientApp
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
import unittest 

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
        
        data_cmp = (json_data['data']==data) if data else True
        
        return self.assert_(json_data['status']==status
                            and json_data['message']==message
                            and data_cmp) 
             
    
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
        response=decorated_dummy(DummyRequest(request={'callback':callback}))
        
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
        decorated_dummy = api_call(required=[])(dummy_function) 
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
        decorated_dummy = api_call(required=[])(dummy_function) 
        #callback = 'jsonp123'
        response=decorated_dummy(DummyRequest())
        logging.debug(response.content)
        self._assertJson(json_string=response.content,
                         status=304,
                         message='',                         
                         #callback=callback
                         )

        
    def test_success(self):
        """Test that a json view returns successfully"""
        data = {'r': 0}
        
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

#now, the api calls!
#this multiple inheritance hack: http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class
class CommonApiTest(object):
    """Test base common cases for all api calls
    
       Every child should define a setUp that sets the url
       and the call method, which is expected to be one of the following methods from django.TestCase:
       self.client.get
       self.client.post
       self.client.put
       self.client.delete
    """
    
    fixtures = ['testData.json', 'testApp.json']
    
    def _assertJson(self, json_string='', callback=None, status=200, message='', data=None, expected_data=[]):
        """Assertions for json data"""
        if callback:
            m=re.match(r'%s\((?P<d>.*)\)'%callback, json_string)
            json_string= m.group('d')
        
        json_data= json.loads(json_string)
        
        #check the expected structure of the internal data        
        if expected_data and 'data' in json_data:
            contained = set(expected_data) == set(json_data['data'].keys())
        else:
            contained = True
        
        data_cmp = (json_data['data']==data) if data else True
        
        return json_data['status']==status and json_data['message']==message and data_cmp and contained 
    
    def setUp(self):
        self.app = ClientApp.objects.get(url='fixtureapp.tmp')
        self.user = ClientUser.objects.get(clientId='testUser1')
        
    def test_invalid_token(self):
        """Test that passing non existing apps raises a 404"""
        response = self.call(self.url, {'appId': 'lalo123'})
        self.assert_(self._assertJson(json_string=response.content,
                                      status=404,
                                      message="No app with the given token is registered or the token is invalid",
                                      ))
        
    def test_invalid_token_callback(self):
        """Test that passing non existing apps raises a 404 in callbacks"""
        callback = 'jsonp123'
        response = self.call(self.url, {'appId': 'lalo123', 'callback': callback})
        self.assert_(self._assertJson(json_string=response.content,
                                      status=404,
                                      message="No app with the given token is registered or the token is invalid",
                                      callback=callback
                                      ))
    
    def test_valid_token(self):
        """Test that valid tokens return valid responses"""
        response = self.call(self.url, {'appId': self.app.get_token()})
        self.assertNotEqual(response.status_code, 404)
    

class UserApiTest(CommonApiTest):
    """Common tests for api calls that require both app and user"""
    
    def test_invalid_user(self):
        """Test that non existing users raise a 404"""
        response = self.call(self.url, {'appId': self.app.get_token(), 'appUser': 'nonExistentUser'})
        self.assert_(self._assertJson(json_string=response.content,
                                      status=404,
                                      message="The requested user does not exist",
                                      ))
        
    def test_invalid_user_callback(self):
        """Test that non existing users raises a 404 in callbacks"""
        callback = 'jsonp123'
        response = self.call(self.url, {'appId': self.app.get_token(), 'appUser': 'nonExistentUser','callback': callback})
        logging.debug(response.content)
        self.assert_(self._assertJson(json_string=response.content,
                                      status=404,
                                      message="The requested user does not exist",
                                      callback=callback
                                      ))
    
    def test_valid_user(self):
        """Test that valid users don't raise 404s"""
        response = self.call(self.url, {'appId': self.app.get_token(), 'appUser': self.user.clientId})
        self.assertNotEqual(response.status_code, 404)
        
class AuthApiTest(CommonApiTest):
    """Test api calls that require authentication
       
       the decorator is tested in other test case, so don't go through that again...
    """
    
    def setUp(self):
        super(AuthApiTest, self).setUp()
        self.good_credentials = "basic %s" % base64.b64encode('%s:%s' % ('fixtureapp.tmp', 'testapp'))
        self.bad_credentials = "basic %s" % base64.b64encode('%s:%s' % ('nonexistent.tmp', 'FOOBAR'))
    

        
class TestGetUsers(AuthApiTest, TestCase):
    """Tests for the getUsers api call"""
    
    def setUp(self):
        super(TestGetUsers, self).setUp()
        self.url = '/api/getUsers/'
        self.call = lambda url,request:self.client.get(url, request, HTTP_AUTHORIZATION=self.good_credentials)
    
    def test_call(self):
        """Test that the users for a valid app are retrieved"""
        response = self.call(self.url, {'appId':self.app.get_token()})
        #check that users come in the response
        self.assert_(self._assertJson(json_string=response.content,
                                      status=200,
                                      message="",                                      
                                      data = {'users': [{'id': e.clientId, 'added': str(e.added)} 
                                              for e in self.app.users.iterator()]}
                                      ))
        
        
    def test_callback(self):
        """Test that the users for a valid app are retrieved in callbacks"""
        callback ='jsonp123'
        response = self.call(self.url, {'appId':self.app.get_token(), 'callback': callback})
        #check that users come in the response
        self.assert_(self._assertJson(json_string=response.content,
                                      status=200,
                                      message="",
                                      expected_data = ['users'],
                                      callback = callback
                                      ))
    def test_bad_method(self):
        """Test that the method validation works"""
        response = self.client.post(self.url, {'appId':self.app.get_token()}, HTTP_AUTHORIZATION=self.good_credentials)
        
        self.assert_(self._assertJson(json_string=response.content,
                                      status=405,
                                      message="",               
                                      expected_data = ['users'],                                                            
                                      ))

class TestRegisterUser(AuthApiTest, TestCase):
    """Tests for the registerUser api call"""
    
    def setUp(self):
        super(TestRegisterUser, self).setUp()
        self.url = '/api/registerUser/'
        self.call = lambda url,request:self.client.post(url, request, HTTP_AUTHORIZATION=self.good_credentials)
    
    def test_missing_required(self):
        """Test that if a required parameter is missing, is a bad request in json, and callback"""
        response = self.call(self.url, {'appId': self.app.get_token()})
                
        self.assert_(self._assertJson(json_string=response.content,
                          status=400, message='The following arguments are required for this call: appId, user'))
        
        callback = 'jsonfunction'
        response = self.call(self.url, {'appId': self.app.get_token(), 'callback': callback})
        
        self.assert_(self._assertJson(json_string=response.content,
                          status=400, message='The following arguments are required for this call: appId, user',
                          callback=callback))
        
    
    def test_call(self):
        """Test that a user is correctly added"""
        before = list(self.app.users.all().values_list('clientId', flat=True))
        response = self.call(self.url, {'appId':self.app.get_token(), 'user':'newUser'})
        after = list(self.app.users.all().values_list('clientId', flat=True))
        #check that users come in the response
        self.assert_(self._assertJson(json_string=response.content,
                                      status=200,
                                      message="",
                                      data = {'added': True}
                                     ))
        #check that the user was actually added:
        self.assert_('newUser' not in before
                     and 'newUser' in after, 'The user was not added')
        
        
    def test_duplicate_addition(self):
        """Test that a user is not added if it's a duplicate"""
        
        duplicate = self.user.clientId
        before = list(self.app.users.all().values_list('clientId', flat=True))
        response = self.call(self.url, {'appId':self.app.get_token(), 'user':duplicate})
        after = list(self.app.users.all().values_list('clientId', flat=True))
        
        self.assert_(self._assertJson(json_string=response.content,
                                      status=200,
                                      message="",
                                      data = {'added': False}
                                     ))
        #check that the user was actually added:
        self.assert_(duplicate in before
                     and len(before) == len(after), 'The user is duplicate!')
        
        
    def test_callback(self):
        """Test that callbacks also add users"""
        callback ='jsonp123'
        before = list(self.app.users.all().values_list('clientId', flat=True))
        response = self.call(self.url, {'appId':self.app.get_token(), 'user':'newUser', 'callback': callback})
        after = list(self.app.users.all().values_list('clientId', flat=True))
        #check that users come in the response
        self.assert_(self._assertJson(json_string=response.content,
                                      status=200,
                                      message="",
                                      data = {'added': True},
                                      callback = callback
                                     ))
        #check that the user was actually added:
        self.assert_('newUser' not in before
                     and 'newUser' in after, 'The user was not added')
        
    def test_bad_method(self):
        """Test that the method validation works"""
        before = list(self.app.users.all().values_list('clientId', flat=True))
        response = self.client.get(self.url, {'appId':self.app.get_token(), 'user': 'newUser'}, HTTP_AUTHORIZATION=self.good_credentials)
        after = list(self.app.users.all().values_list('clientId', flat=True))
        
        self.assert_(self._assertJson(json_string=response.content,
                                      status=405,
                                      message="",
                                      expected_data=['added']                                                                           
                                      ))
        #check that it wasn't magically added:
        self.assertEqual(sorted(before), sorted(after))
        
    def test_quota_respect(self):
        """Test that the quota validation works"""
        current = self.app.users.count()
        limit = settings.FREE_USER_LIMIT - current
        for i in range(limit):
            response = self.call(self.url, {'appId':self.app.get_token(),
                                                   'user': 'newUser%s'%i})
        #try to add one more:        
        before = list(self.app.users.all().values_list('clientId', flat=True))
        response = self.call(self.url, {'appId':self.app.get_token(),
                                               'user': 'newUserOverflow'})
        
        self.assert_(self._assertJson(json_string=response.content,
                                      status=403,
                                      message='Impossible to add more users: user limit would be exceeded',
                                      expected_data=['added']                                                                           
                                      ))
        
        after = list(self.app.users.all().values_list('clientId', flat=True))
        
        #check that the length is actually the limit
        self.assertEqual(len(after), settings.FREE_USER_LIMIT)
        #check that it wasn't magically added:
        self.assertEqual(sorted(before), sorted(after))
        
class TestBulkRegisterUsers(AuthApiTest, TestCase):
    """Tests for the bulkRegisterUsers api call
        
       ideally, it has the same cases that the registerUser call, but because
       they're both on the same method, those which are structurally identical
       are not repeated here 
    """
    
    def setUp(self):
        super(TestBulkRegisterUsers, self).setUp()
        self.url = '/api/bulkRegisterUsers/'
        self.call = lambda url,request:self.client.post(url, request, HTTP_AUTHORIZATION=self.good_credentials)
    
    def test_call(self):
        """Test that a list of users is correctly added"""
        
        test_users = ['newUser1', 'newUser2', 'newUser3']
               
        before = list(self.app.users.all().values_list('clientId', flat=True))
        response = self.call(self.url, {'appId': self.app.get_token(), 'user': test_users})
                                         
        after = list(self.app.users.all().values_list('clientId', flat=True))
        #check that users come in the response
        self.assert_(self._assertJson(json_string=response.content,
                                      status=200,
                                      message="",
                                      data = {'added': True}
                                     ))
        #check that the user was actually added:
        self.assert_(not (set(test_users) <= set(before))
                     and  set(test_users) <= set(after), 'The user was not added')
        
        
    def test_duplicate_addition(self):
        """Test users are not added if it's a duplicate"""
        
        test_users = ['testUser1', 'testUser2', 'newUser3']
        before = list(self.app.users.all().values_list('clientId', flat=True))
        response = self.call(self.url, {'appId': self.app.get_token(), 'user': test_users})
        after = list(self.app.users.all().values_list('clientId', flat=True))
        
        self.assert_(self._assertJson(json_string=response.content,
                                      status=200,
                                      message="",
                                      data = {'added': True}
                                     ))
        #check that the user was actually added:
        new_users = set(test_users) - set(before)
        
        self.assert_(new_users <= set(after)
                     and len(after) == len(before)+len(new_users))
       
    def test_quota_respect(self):
        """Test that the quota validation works"""
        current = self.app.users.count()
        limit = settings.FREE_USER_LIMIT - current
        
        test_users=[]
        for i in range(limit):
            test_users.append('newUser%s' %i)
            
        #get to the limit
        response = self.call(self.url, {'appId': self.app.get_token(), 'user': test_users})
        
        #try to add one more:                
        before = list(self.app.users.all().values_list('clientId', flat=True))
        response = self.call(self.url, {'appId':self.app.get_token(),
                                               'user': 'newUserOverflow'})        
        self.assert_(self._assertJson(json_string=response.content,
                                      status=403,
                                      message='Impossible to add more users: user limit would be exceeded',
                                      expected_data=['added']                                                                           
                                      ))
        
        after = list(self.app.users.all().values_list('clientId', flat=True))        
        #check that the length is actually the limit
        self.assertEqual(len(after), settings.FREE_USER_LIMIT)
        #check that it wasn't magically added:
        self.assertEqual(sorted(before), sorted(after))

class TestDeleteUser(AuthApiTest, TestCase):
    """Tests for the deleteUser api call"""
    
    def setUp(self):
        super(TestDeleteUser, self).setUp()
        self.url = '/api/deleteUser/'
        self.call = lambda url,request:self.client.post(url, request, HTTP_AUTHORIZATION=self.good_credentials)
    
    def test_missing_required(self):
        """Test that if a required parameter is missing, is a bad request in json, and callback"""
        response = self.call(self.url, {'appId': self.app.get_token()})
                
        self.assert_(self._assertJson(json_string=response.content,
                          status=400, message='The following arguments are required for this call: appId, user'))
        
        callback = 'jsonfunction'
        response = self.call(self.url, {'appId': self.app.get_token(), 'callback': callback})
        
        self.assert_(self._assertJson(json_string=response.content,
                          status=400, message='The following arguments are required for this call: appId, user',
                          callback=callback))
        
    
    def test_call(self):
        """Test that a user is correctly removed"""
        before = list(self.app.users.all().values_list('clientId', flat=True))
        response = self.call(self.url, {'appId':self.app.get_token(), 'user':self.user.clientId})
        after = list(self.app.users.all().values_list('clientId', flat=True))
        
        self.assert_(self._assertJson(json_string=response.content,
                                      status=200,
                                      message="",
                                      data = {'deleted': True}
                                     ))
        #check that the user was actually added:
        self.assert_(self.user.clientId in before
                     and self.user.clientId not in after, 'The user was not deleted')
        
    def test_call_invalid_user(self):
        """Test the non-existent user escenario"""
        before = list(self.app.users.all().values_list('clientId', flat=True))
        response = self.call(self.url, {'appId':self.app.get_token(), 'user':'idonotexist'})
        after = list(self.app.users.all().values_list('clientId', flat=True))
        
        self.assert_(self._assertJson(json_string=response.content,
                                      status=200,
                                      message="",
                                      data = {'deleted': False}
                                     ))
        #check that the user was actually added:
        self.assertEqual(sorted(before), sorted(after))
        
    def test_callback(self):
        """Test that callbacks also delete users"""
        callback ='jsonp123'
        before = list(self.app.users.all().values_list('clientId', flat=True))
        response = self.call(self.url, {'appId':self.app.get_token(), 'user':self.user.clientId, 'callback': callback})
        after = list(self.app.users.all().values_list('clientId', flat=True))
        #check that users come in the response
        self.assert_(self._assertJson(json_string=response.content,
                                      status=200,
                                      message="",
                                      data = {'deleted': True},
                                      callback = callback
                                     ))
        #check that the user was actually added:
        self.assert_(self.user.clientId in before
                     and self.user.clientId not in after, 'The user was not deleted')
        
    def test_bad_method(self):
        """Test that the method validation works for user deletion"""
        before = list(self.app.users.all().values_list('clientId', flat=True))
        response = self.client.get(self.url, {'appId':self.app.get_token(), 'user': self.user.clientId},
                                    HTTP_AUTHORIZATION=self.good_credentials)
        after = list(self.app.users.all().values_list('clientId', flat=True))
        
        self.assert_(self._assertJson(json_string=response.content,
                                      status=405,
                                      message="",
                                      expected_data=['deleted']                                                                           
                                      ))
        #check that it wasn't magically added:
        self.assertEqual(sorted(before), sorted(after))
        
    def test_quota_respect(self):
        """Test that, for delete, the quota validation works: reach it, then delete a user and see if now we can add"""
        current = self.app.users.count()
        limit = settings.FREE_USER_LIMIT - current
        for i in range(limit):
            response = self.call('/api/registerUser/', {'appId':self.app.get_token(),
                                                   'user': 'newUser%s'%i})
        #try to add one more:        
        before = list(self.app.users.all().values_list('clientId', flat=True))
        response = self.call('/api/registerUser/', {'appId':self.app.get_token(),
                                               'user': 'newUserOverflow'})
        
        self.assert_(self._assertJson(json_string=response.content,
                                      status=403,
                                      message='Impossible to add more users: user limit would be exceeded',
                                      expected_data=['added']                                                                           
                                      ))
        
        after = list(self.app.users.all().values_list('clientId', flat=True))
        
        #check that the length is actually the limit
        self.assertEqual(len(after), settings.FREE_USER_LIMIT)
        #check that it wasn't magically added:
        self.assertEqual(sorted(before), sorted(after))
        
        #now, delete a user:
        response = self.call(self.url, {'appId':self.app.get_token(), 'user':self.user.clientId})
        new_before = list(self.app.users.all().values_list('clientId', flat=True))
        #check that now there's space:
        self.assert_(self.user.clientId in after and self.user.clientId not in new_before, 'could not delete an old user')
        
        #add a user: it should work!
        response = self.call('/api/registerUser/', {'appId':self.app.get_token(), 'user':'userOverflow'})
        new_after = list(self.app.users.all().values_list('clientId', flat=True))
        self.assert_('userOverflow' not in new_before and 'userOverflow' in new_after)
        
class TestUpdateProfile(UserApiTest, TestCase):
    """Test the profile update
    
        For more thorough tests, use the profile evolution test case
    """
    
    def setUp(self):
        super(TestUpdateProfile, self).setUp()
               
        self.url = '/api/updateProfile/'
               
        self.call = lambda url,request:self.client.get(url, request)
        #this method also allows calls by post, so test that also!
        self.call_post = lambda url,request:self.client.post(url, request)
        
        self.terms_context = 'study'
        self.context = "Einstein and the quantum mechanics"
        self.es_terms_context = 'estudio'
        self.es_context = 'Einstein y la mecánica cuántica'
        self.docs = list(DocumentSurrogate.objects.filter(category__title="Computer Science").values_list(
                                                                                                          'pk',flat=True))
                
    def _assertEvolution(self, request):
        """common method to check that a profile evolves
            
            does a get and a post and checks 'em
        """
        get_response = self.call(self.url, request)
        self.assert_(self._assertJson(json_string=get_response.content,
                                      status=200,
                                      message="",
                                      data = {'queued': True},                                      
                                     ))
        post_response = self.call_post(self.url, request)
        
        self.assertEqual(get_response.content, post_response.content)
        
    def test_only_context(self):
        """Test that the profile evolves only with a context"""
        self._assertEvolution({'appId': self.app.get_token(),
                               'appUser': self.user.clientId,
                               'context': self.context})
        
    def test_terms_context(self):
        """Test that the profile evolves with a terms context"""
        self._assertEvolution({'appId': self.app.get_token(),
                               'appUser': self.user.clientId,
                               'context': self.terms_context,
                               't': True})
        
    def test_spanish_context(self):
        """Test evolution in spanish"""
        self._assertEvolution({'appId': self.app.get_token(),
                               'appUser': self.user.clientId,
                               'context': self.es_context,
                               'lang': 'es'})
        
    def test_spanish_terms_context(self):
        """Test evolution with spanish terms context"""
        self._assertEvolution({'appId': self.app.get_token(),
                               'appUser': self.user.clientId,
                               'context': self.es_terms_context,
                               't': True,
                               'lang': 'es'})
        
    
    def test_invalid_lang_context(self):
        """Test evolution for invalid languages"""
        self._assertEvolution({'appId': self.app.get_token(),
                               'appUser': self.user.clientId,
                               'context': self.context,
                               'lang': 'fr'})
    
    def test_docs_context(self):
        """Test evolution with a context and documents involved"""        
        self._assertEvolution({'appId': self.app.get_token(),
                               'appUser': self.user.clientId,
                               'docs': self.docs,
                               'context': self.context
                               })
        
    def test_docs_spanish_context(self):
        """Test evolution with docs and a spanish context"""
        self._assertEvolution({'appId': self.app.get_token(),
                               'appUser': self.user.clientId,
                               'docs': self.docs,
                               'context': self.es_context,
                               'lang': 'es'                               
                               })
        
    def test_docs_terms_context(self):
        """Test evolution with a terms context and documents involved"""
        self._assertEvolution({'appId': self.app.get_token(),
                               'appUser': self.user.clientId,
                               'docs': self.docs,
                               'context': self.context,
                               't': True
                               }) 
        
    def test_docs_terms_spanish_context(self):
        """Test evolution with a spanish terms context and documents involved"""
        self._assertEvolution({'appId': self.app.get_token(),
                               'appUser': self.user.clientId,
                               'docs': self.docs,
                               'context': self.es_terms_context,
                               't': True,
                               'lang': 'es'
                               }) 
    
        
def suite():
    """The test suite only comprises the test cases directly related to the api.
       
       Term extraction and query building must be run individually, as they use lots of resources       
    """
    auth_suite = unittest.TestLoader().loadTestsFromTestCase(AuthDecoratorTest)
    api_call_suite = unittest.TestLoader().loadTestsFromTestCase(ApiCallDecoratorTest)
    
    get_users_suite = unittest.TestLoader().loadTestsFromTestCase(TestGetUsers)
    add_user_suite = unittest.TestLoader().loadTestsFromTestCase(TestRegisterUser)
    bulk_users_suite = unittest.TestLoader().loadTestsFromTestCase(TestBulkRegisterUsers)
    delete_user_suite = unittest.TestLoader().loadTestsFromTestCase(TestDeleteUser)
    update_profile_suite = unittest.TestLoader.loadTestsFromTestCase(TestUpdateProfile)
    
    return unittest.TestSuite([auth_suite,
                               api_call_suite,
                               get_users_suite,
                               add_user_suite,
                               bulk_users_suite,
                               delete_user_suite,
                               update_profile_suite]) 