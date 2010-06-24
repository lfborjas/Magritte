#encoding=utf-8
'''
Created on 23/06/2010

@author: lfborjas
'''
from selenium import selenium
import time, re
from django.test import TestCase
from django.core import mail
import logging
from profile.models import ClientApp
#import unittest

class test_register(TestCase):
    #fixtures = ['testApp.json']
    
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
        self.selenium.window_maximize()
        #self.selenium.set_speed(200)
        self.app = ClientApp.objects.get_or_create(url='fixtureapp.tmp')[0]
        
    
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
    
    def test_empty_email(self):
        """Test that attempts to register with a blank email fail"""
        sel = self.selenium
        sel.open("/register/")                      
        sel.type("id_url", "newapp.com")
        sel.click("register-submit")        
        sel.wait_for_page_to_load("30000")
        #test error reporting:
        txt=sel.get_text("//form[@id='register-form']/table/tbody/tr[2]/td[2]/ul/li")
        try: self.assert_("This field is required" in txt or "Este campo es obligatorio" in txt 
                           , 'Should have reported it')
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def test_invalid_email(self):
        """Test that attempts to register with an invalid email fail"""
        sel = self.selenium
        sel.open("/register/")                      
        sel.type("id_url", "newapp.com")
        sel.type("id_mail", "notanemail")
        sel.click("register-submit")        
        sel.wait_for_page_to_load("30000")
        #test error reporting:
        txt=sel.get_text("//form[@id='register-form']/table/tbody/tr[2]/td[2]/ul/li")
        try: self.assert_("Enter a valid e-mail address." in txt or u"Introduzca una dirección de correo electrónico válida." in txt 
                           , 'Should have reported it')
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def test_duplicate_url(self):
        """Test that attempts to register with a duplicate url fail"""
        sel = self.selenium
        sel.open("/register/")                      
        sel.type("id_url", self.app.url)
        sel.type("id_mail", "fixture@app.com")
        sel.click("register-submit")        
        sel.wait_for_page_to_load("30000")
        #test error reporting:
        txt=sel.get_text("//form[@id='register-form']/table/tbody/tr[1]/td[2]/ul/li")
        try: self.assert_("There is an app with that name already registered" in txt
                          or u"¡Ya hay una aplicación registrada bajo ese nombre!" in txt 
                           , 'Should have reported it')
        except AssertionError, e: self.verificationErrors.append(str(e))
                
        
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

