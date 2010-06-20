# -*- coding: iso-8859-15 -*-
"""Simple FunkLoad test

$Id: test_Simple.py 54228 2010-04-14 22:11:52Z bdelbosc $
"""
import unittest
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase
import json
import re
import time

class ApiTest(FunkLoadTestCase):
    """This test uses the configuration file ApiTest.conf."""
    
    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')
        self.app = self.conf_get('main', 'username')
        self.token = self.conf_get('main', 'token')
        self.password = self.conf_get('main', 'password')
        self.user = self.conf_get('main', 'user')        
        self.build_url = lambda url: '%s/%s/'%(self.server_url, url)
        self.limit = self.conf_get('main', 'users_limit')
           
    def _generate_user(self):
        return "%testUser_%s" % (self.user_prefix, time.time())   
        
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
            return data['data']['key'] 

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
        self._assertJson(json_string=response.body,
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
        
        if limit: #add the user:
            users = [self._generate_user() for i in range(1,limit)]
            response = self.post(self.build_url('bulkRegisterUsers'), params={'appId':self.token, 'user': [users]},
                                 description="Register a user whose name is the current timestamp")
            
            self._assertJson(json_string=response.body,
                                          status=200,
                                          message="",
                                          data = {'added': True}
                                         )
            #check if it was added:
            list_response = self.get(self.build_url('getUsers'), params={'appId': self.token},
                                     description="Get the users for %s" %self.app)
            self._assertJson(json_string=response.body,
                                          status=200,
                                          message="",
                                          expected_data = ['users']
                                         )
            
            raw_users = self._get_json_data(list_response.body, 'users')
            user_list = [e['id'] for e in raw_users]
            self.assert_(set(users)  & set(user_list))
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
        
        user =self._get_json_data(before.body, 'users')[0]['id']
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
        self._assertJson(json_string=response.body,
                                      status=200,
                                      message="",
                                      expected_data = ['users']
                                     )
        
        raw_users = self._get_json_data(list_response.body, 'users')
        users = [e['id'] for e in raw_users]
        self.assert_(user not in users)
        self.clearBasicAuth()
    
    def test_get_recommendations(self):
        pass
    
    def test_update_profile(self):
        pass


if __name__ in ('main', '__main__'):
    unittest.main()
