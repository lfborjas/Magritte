# -*- coding: utf-8 -*-
"""Simple FunkLoad test

$Id: test_Simple.py 54228 2010-04-14 22:11:52Z bdelbosc $
"""
import unittest
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase
import json
import re
from uuid import uuid4

class ApiTest(object):
    """This test uses the configuration file ApiTest.conf."""
    
    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')
        self.app = self.conf_get('main', 'username')
        self.token = self.conf_get('main', 'token')
        self.password = self.conf_get('main', 'password')
        self.user = self.conf_get('main', 'user')        
        self.build_url = lambda url: '%s/%s/'%(self.server_url, url)
        self.limit = self.conf_getInt('main', 'users_limit')
           
    def _generate_user(self):
        return "testUser_%s" % (uuid4())   
        
    def _assertJson(self, json_string='', callback=None, status=200, message='', data=None, expected_data=[]):
        """Assertions for json data"""
        if callback:
            m=re.match(r'%s\((?P<d>.*)\)'%callback, json_string)
            json_string= m.group('d')
        
        json_data= json.loads(json_string)        
        
        if expected_data and 'data' in json_data:
            contained = set(expected_data) == set(json_data['data'].keys())
        else:
            contained = True
        
        data_cmp = (json_data['data']==data) if data else True
        
        self.assert_(json_data['status']==status
                            and json_data['message']==message
                            and data_cmp
                            and contained) 
        
    def _get_json_data(self, json_string, key=''):
        """Get data from a json string, if no key is passed, the whole object is returned"""
        data = json.loads(json_string)
        if key:
            return data['data'][key] 
        else:
            return data['data']


    
        

class UserApiTest(ApiTest, FunkLoadTestCase):
    """User related tests"""
    
    def test_register(self):                
        self.setBasicAuth(self.app, self.password)
        #add the user:
        user = self._generate_user()
        response = self.post(self.build_url('registerUser'), params={'appId':self.token, 'user': user},
                             description="Register a user whose name is the current timestamp")
        
        self._assertJson(json_string=response.body,
                                      status=200,
                                      message="",
                                      data = {'added': True}
                                     )
        #check if it was added:
        list_response = self.get(self.build_url('getUsers'), params={'appId': self.token},
                                 description="Get the users for %s" %self.app)
        
        self._assertJson(json_string=list_response.body,
                                      status=200,
                                      message="",
                                      expected_data = ['users']
                                     )        
        raw_users = self._get_json_data(list_response.body, 'users')
        users = [e['id'] for e in raw_users]
        self.assert_(user in users)
        self.clearBasicAuth()
    
    def test_bulk(self):                
        self.setBasicAuth(self.app, self.password)
        before = self.get(self.build_url('getUsers'), params={'appId': self.token},
                                 description="Get the users for %s" %self.app)
        limit = self.limit - len(self._get_json_data(before.body, 'users'))
        
        if limit: 
            users = [self._generate_user() for i in range(1,limit)]
            response = self.post(self.build_url('bulkRegisterUsers'), params={'appId':self.token, 'user': users},
                                 description="Register a user whose name is the current timestamp")
            
            self._assertJson(json_string=response.body,
                                          status=200,
                                          message="",
                                          data = {'added': True}
                                         )
            #check if they were added:
            list_response = self.get(self.build_url('getUsers'), params={'appId': self.token},
                                     description="Get the users for %s" %self.app)
            self._assertJson(json_string=list_response.body,
                                          status=200,
                                          message="",
                                          expected_data = ['users']
                                         )
            
            raw_users = self._get_json_data(list_response.body, 'users')
            user_list = [e['id'] for e in raw_users]
            self.assert_(set(users)  <= set(user_list))
        else: #try to push the limit:
            response = self.post(self.build_url('bulkRegisterUsers'), params={'appId':self.token, 'user': [self._generate_user(),]},
                                 description="Register a user whose name is the current timestamp")
            self._assertJson(json_string=response.body,
                                          status=403,
                                          message='Impossible to add more users: user limit would be exceeded',
                                          expected_data=['added']                                          
                                         )
            
            
        self.clearBasicAuth()
        
    def test_delete(self):                
        self.setBasicAuth(self.app, self.password)
        
        #get a user:        
        before = self.get(self.build_url('getUsers'), params={'appId': self.token},
                                 description="Get the users for %s" %self.app)
        
        user =[e['id'] for e in self._get_json_data(before.body, 'users') if e['id']!=self.user][0]        
        if not user:
            self.fail('No more users to delete')
        
        response = self.post(self.build_url('deleteUser'), params={'appId':self.token, 'user': user},
                             description="Delete a user")
        
        self._assertJson(json_string=response.body,
                                      status=200,
                                      message="",
                                      data = {'deleted': True}
                                     )
        #check if it was deleted:
        list_response = self.get(self.build_url('getUsers'), params={'appId': self.token},
                                 description="Get the users for %s" %self.app)
        self._assertJson(json_string=list_response.body,
                                      status=200,
                                      message="",
                                      expected_data = ['users']
                                     )
        
        raw_users = self._get_json_data(list_response.body, 'users')
        users = [e['id'] for e in raw_users]
        self.assert_(user not in users)
        self.clearBasicAuth()


class RecommendationsApiTest(ApiTest, FunkLoadTestCase):
    """Recommendations related tests"""
    def test_get_recommendations(self):
        ctx = """Scientists maintain that scientific investigation must adhere to the scientific method,
         a rigorous process for properly developing and evaluating natural explanations for observable phenomena
         based on reliable empirical evidence and neutral, unbiased independent verification, and not on arguments
         from authority or popular preferences. Science therefore bypasses supernatural explanations; 
         it instead only considers natural explanations that may be falsifiable.
         Fields of science are distinguished as pure science or applied science. 
         Pure science is principally involved with the discovery of new truths with little or no regard to their practical applications.
         Applied science is principally involved with the application of existing knowledge in new ways,
         including advances in technology.
         Mathematics is the language in which scientific information is best presented,
         often it is the only way to formulate and present scientific knowledge. 
         Therefore whether mathematics is a science in itself or the framework of science is a matter of perspective."""
         
        response = self.get(self.build_url('getRecommendations'), params={'appId': self.token, 'appUser': self.user,                                                                          
                                                                          'context': ctx})
        self.logd(response.body)
        self._assertJson(json_string=response.body,
                                      status=200,
                                      message="",
                                      expected_data = ['terms', 'results']
                                     )
        
    def test_get_recommendations_spanish(self):
        ctx = u"""La ciencia (del latín scientia, "conocimiento") es un conjunto de métodos
         y técnicas para la adquisición y organización de conocimientos sobre la estructura de un conjunto de hechos objetivos
         y accesibles a varios observadores. La aplicación de esos métodos y conocimientos conduce a la generación de más conocimiento
         objetivo en forma de predicciones concretas, cuantitativas y comprobables referidas a hechos observables pasados, presentes y 
         futuros.
         Con frecuencia esas predicciones pueden ser formuladas mediante razonamientos y son estructurables en forma de reglas o
         leyes universales, que dan cuenta del comportamiento de un sistema y predicen cómo actuará dicho sistema en determinadas
         circunstancias.""".encode('utf-8')
         
        response = self.get(self.build_url('getRecommendations'), params={'appId': self.token, 'appUser': self.user,                                                                          
                                                                          'context': ctx, 'lang':'es'})
        self.logd(response.body)
        self._assertJson(json_string=response.body,
                                      status=200,
                                      message="",
                                      expected_data = ['terms', 'results']
                                     )

        
    
    def test_update_profile(self):
        response = self.get(self.build_url('updateProfile'), params={'appId': self.token, 'appUser': self.user,                                                                          
                                                                          'context': 'science physics', 't': True})
        self.logd(response.body)
        self._assertJson(json_string=response.body,
                                      status=200,
                                      message="",
                                      data = {'queued': True}
                                     )
    def _bench_test(self):
        self.test_get_recommendations()
        self.test_get_recommendations_spanish()
        self.test_update_profile()


if __name__ in ('main', '__main__'):
    unittest.main()
