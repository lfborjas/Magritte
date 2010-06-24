'''
Created on 23/06/2010

@author: lfborjas
'''
from selenium import selenium
import time, re
from django.test import TestCase
from django.core import mail
import logging
#import unittest

class test_register(TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
    
    def test_normal_registration(self):
        """Test that a registration for a new app works fine"""
        sel = self.selenium
        sel.open("/register/")
        sel.type("id_url", "newapp.com")              
        sel.type("id_mail", "new@app.com")
        sel.click("register-submit")
        sel.click("register-submit")
        sel.wait_for_page_to_load("30000")
        #test redirection:
        try: self.failUnless('/usage/' in sel.get_location())
        except AssertionError, e: self.verificationErrors.append(str(e))
        #test the email:
        try: self.assertEquals(len(mail.outbox),1)
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.assert_('Your T-Recs App key' in mail.outbox[0].subject or 'Su clave' in mail.outbox[0].subject)
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def test_empty_url(self):
        """Test that attempts to register with a blank username fail"""
        sel = self.selenium
        sel.open("/register/")                      
        sel.type("id_mail", "new@app.com")
        sel.click("register-submit")        
        sel.wait_for_page_to_load("30000")
        #test error reporting:
        txt=sel.get_text("//form[@id='register-form']/table/tbody/tr[1]/td[2]/ul/li")
        try: self.assert_("This field is required" in txt or "Este campo es obligatorio" in txt 
                           , 'Should have reported it')
        except AssertionError, e: self.verificationErrors.append(str(e))
                
        
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

