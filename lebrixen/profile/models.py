from django.db import models
from search.models import DmozCategory as Category
from Crypto.Cipher import AES
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
import logging
# Create your models here.
class BadToken(Exception):
    def __str__(self):
        return "Malformed token"

class ClientApp(models.Model):
    #appId = models.CharField(max_length=320)
    url = models.CharField(blank = True, default="", max_length=512, unique = True)
    
    def get_token(self):
        plaintext = str(self.pk)
        pl = len(plaintext)
        plaintext= plaintext if not pl%16 else plaintext + ' '*(16*(pl/16+1)-pl)
        encripter=AES.new(settings.AES_KEY)
        return encripter.encrypt(plaintext).encode('hex')
    
    @classmethod
    def get_for_token(cls, token, id_only=False):
        decripter=AES.new(settings.AES_KEY)
        if len(token)%16: 
            raise BadToken        
        #must be a hex string    
        try:
            token.decode('hex')
        except TypeError:
            raise BadToken
                     
        id=decripter.decrypt(token.decode('hex'))
        
                                  
        try:            
            app = cls.objects.get(pk=id)
            if id_only:
                return app.pk
            else:
                return app            
        except MultipleObjectsReturned:
            logging.error("Multiple apps match the token %s !" % token)
            raise
        except cls.DoesNotExist:
            logging.error("No app matches the token %s" % token)
            raise

    def __unicode__(self):
        return self.url    
    
class ClientUser(models.Model):
    app = models.ForeignKey(ClientApp, related_name='users')
    clientId = models.CharField(max_length = 320) #the unique id in the app's db
    clientName = models.CharField(max_length=320, blank = True, default="")
    info = models.TextField(blank = True, default = "")
    
    def __unicode__(self):
        return u"%s of %s" % (self.clientId, self.app)
    
class ClientPreference(models.Model):
    user = models.ForeignKey(ClientUser, related_name='preferences')
    category = models.ForeignKey(Category)
    score = models.FloatField(null=True, blank=True, default = 0.0)
    
    def __unicode__(self):
        return u"%s:%s=%s" % (self.user, self.category, self.score)
    
class ClientSession(models.Model):
    user = models.ForeignKey(ClientUser, related_name = 'sessions')
    date = models.DateField(auto_now_add = True)
    documents = models.CommaSeparatedIntegerField(max_length = 255, blank=True, default="")
    context = models.TextField(blank = True, default = "")    