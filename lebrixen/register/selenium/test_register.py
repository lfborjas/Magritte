'''
Created on 23/06/2010

@author: lfborjas
'''
from selenium import selenium
import time, re
from django.test import TestCase
from django.core import mail

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
        try: self.failUnless('/usage/' in sel.get_location())
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.assertEquals(len(mail.outbox),1)
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.assert_('Your T-Recs App key' in mail.outbox[0].subject or 'Su clave' in mail.outbox[0].subject)
        except AssertionError, e: self.verificationErrors.append(str(e))        
        
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

