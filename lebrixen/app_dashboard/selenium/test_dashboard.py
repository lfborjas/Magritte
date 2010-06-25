#encoding=utf-8
from selenium import selenium
import time, re
from django.test import TransactionTestCase
from django.core import mail
import logging
from profile.models import ClientApp
from django.contrib.auth.models import User
from uuid import uuid4
from django.conf import settings

class TestDashboard(TransactionTestCase):
    urls = 'app_dashboard.test_urls'
    
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:8000/")
        self.selenium.start()
        #self.selenium.set_speed(2000)
        self.selenium.window_maximize()
        self.app = ClientApp.objects.get_or_create(url='fixtureapp.tmp')[0]
        self.pwd = "test"
        #self.user=None
        
        try:
            self.app_user =  User.objects.create_user(self.app.url, 'testapp@localhost.com', self.pwd)
            self.app.user = self.app_user
            self.app.save()
        except:
            logging.debug("error saving user", exc_info=True)
            pass
        
        #login for every test:
        sel = self.selenium
        sel.open("/dashboard/login/?next=/dashboard/")
        sel.wait_for_page_to_load("30000")                
        sel.type("id_username", self.app.user.username)
        sel.type('id_password', self.pwd)        
        sel.click("login-submit")
        sel.wait_for_page_to_load("30000")       
        
        try: self.assert_('/login/' not in sel.get_location(), 'Should have logged in')
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def test_register_users(self):
        """Test regular user registration"""
        sel = self.selenium
        #always login:
#        sel.open("/dashboard/logout/")
#        sel.wait_for_page_to_load("30000")
#        sel.open('/dashboard/')
#        logging.debug("opened dashboard...")             
        
        limit = settings.FREE_USER_LIMIT - self.app.users.count() 
        if not limit or limit <=2:
            self.fail("User limit exceeded")
        #hack: http://jira.openqa.org/browse/SEL-683
                     
        #register a couple of users:              
        u1= "testUser_%s"%uuid4()
        u2= "testUser_%s"%uuid4()
        sel.type("id_form-0-name", u1 )
        #sel.click("//form[@id='register-users-form']/table/td/a[@class='add-row']")
        #cf: http://thoughthaus.net/blog/?page_id=116
        #und http://blog.vishnuiyengar.com/2009/08/testing-ajax-applications-with-selenium.html
        sel.wait_for_condition('selenium.browserbot.getCurrentWindow().jQuery("#register-users-form a.add-row").trigger("click")', 3000)
        #sel.click("css=#register-users-form a.add-row")                
        try: self.assert_(sel.is_element_present('css=#form-1-id_form-0-name'), 'New input should be present!')
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.type("form-1-id_form-0-name", u2)
        try: self.assert_(sel.is_element_present('css=#register-users-form a.add-row'), 'Should be present!')
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("css=input.trecs-submit")                
        sel.wait_for_page_to_load("30000")
        
        #check they're registered        
        sel.open("/dashboard/users/")        
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present(u1))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present(u2))
        except AssertionError, e: self.verificationErrors.append(str(e))
    
    def test_users_list(self):
        """Test that an app's users are correctly listed"""           
        sel = self.selenium
        users = []
        for u in range(settings.FREE_USER_LIMIT/3):
            users.append(self.app.users.create(clientId="testUser_%s"%uuid4()))
        
        #sel.open("/users/")        
        sel.open("/dashboard/?ul=1")
        sel.wait_for_page_to_load("30000")
#        sel.wait_for_condition('selenium.browserbot.getCurrentWindow().jQuery("#tabs").tabs("select",1);\
#        selenium.browserbot.getCurrentWindow().jQuery("#tabs").tabs("load",1);',
#                                 3000)
        for user in users:
            try: self.failUnless(sel.is_text_present(user.clientId))
            except AssertionError, e: self.verificationErrors.append(str(e))
            try: self.failUnless(sel.is_text_present(str(user.added.date())))
            except AssertionError, e: self.verificationErrors.append(str(e))
    
    def test_limit_respect(self):
        """Test that we can only add users up to the limit"""
        sel = self.selenium

        users = []        
        for u in range(settings.FREE_USER_LIMIT):
            users.append("testUser_%s"%uuid4())
        
        
        sel.type("id_form-0-name", users[0])
        #register users till it tops:
        for i,u in enumerate(users[1:]):
            sel.wait_for_condition('selenium.browserbot.getCurrentWindow().jQuery("#register-users-form a.add-row").trigger("click")',
                                    3000)
        #sel.click("css=#register-users-form a.add-row")                                
            sel.type("form-%s-id_form-0-name"%(i+1), u)
            
        cnd = sel.wait_for_condition('!Boolean(selenium.browserbot.getCurrentWindow().jQuery("a.add-row").is(":visible"));',
                                                  20000)
                
        
        #register
        sel.click("css=input.trecs-submit")                
        sel.wait_for_page_to_load("30000")
            
        #the warning should be here, and the submit button, not:        
        try: self.assert_(sel.is_element_present('css=span.warning'), 'Warning should be here')
        except AssertionError, e: self.verificationErrors.append(str(e))
        
        txt=sel.get_text("css=span.warning")
        
        try: self.assert_(u"Límite de usuarios excedido" in txt 
                          or "User limit exceeded" in txt, 'Warning should be here')
        except AssertionError, e: self.verificationErrors.append(str(e))
        
        
        try: self.assertFalse(sel.is_element_present('css=input.trecs-submit'), 'REGISTER Should NOT be present!')
        except AssertionError, e: self.verificationErrors.append(str(e))
        
        #the users should be listed:
        sel.open("/dashboard/users/")        
        sel.wait_for_page_to_load("30000")
        for user in users:
            try: self.failUnless(sel.is_text_present(user))
            except AssertionError, e: self.verificationErrors.append(str(e))            
        
    def test_delete(self):
        """Test that users can be deleted"""
        sel = self.selenium
        
        #create users
        users = []
        for u in range(settings.FREE_USER_LIMIT/3):
            users.append(self.app.users.create(clientId="testUser_%s"%uuid4()))
        
#       #click the tab
        if sel.is_element_present("link=All Users"):
            sel.click("link=All Users")
        elif sel.is_element_present("link=Usuarios"):
            sel.click("link=Usuarios")
        else:
            self.verificationErrors.append('No tab link is present!')
        
        #wait a second for the ajax
        time.sleep(1)
        
        #try erasing a user, but cancel:
        sel.click("%s" % users[0].pk)
        sel.click("//div[3]/button[2]")
        #sel.wait_for_page_to_load("30000")
        time.sleep(1)
        
        #erase the others:
        for user in users[1:]:
            sel.click("%s" % user.pk)
            sel.click("//div[3]/button[1]")
            #sel.wait_for_page_to_load("30000")
            time.sleep(1)
            
        #check that only the first one is present:
        try: self.failUnless(sel.is_text_present(users[0].clientId), 'Should be present!')
        except AssertionError, e: self.verificationErrors.append(str(e))
        
        #check that the other ones are not present
        for user in users[1:]:
            try: self.assertFalse(sel.is_text_present(user.clientId), 'Should NOT be present!')
            except AssertionError, e: self.verificationErrors.append(str(e))
            
        
#    def test_delete_update(self):
#        #has the impasse of the jquery tab...
#        """Test that, when an app is full, deleting n random users results in being able to add again"""
#        pass
    
    def tearDown(self):
#        try:
#            self.app.users.all().delete()
#        except: 
#            logging.debug("no users to delete")
#            pass
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

