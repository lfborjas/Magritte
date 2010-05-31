from django.db import models
from search.models import DmozCategory as Category
from Crypto.Cipher import AES
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth.models import get_hexdigest, check_password
import logging

# Create your models here.
class BadToken(Exception):
    def __str__(self):
        return "Malformed token"

class ClientApp(models.Model):
    #appId = models.CharField(max_length=320)
    url = models.CharField(blank = True, default="", max_length=512, unique = True)
    password = models.CharField(max_length=128, blank=True, default="")
    
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
    
    def set_password(self, raw_password):
        import random
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
        hsh = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hsh)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        encryption formats behind the scenes.
        """
        # Backwards-compatibility check. Older passwords won't include the
        # algorithm or salt.
        if '$' not in self.password:
            is_correct = (self.password == get_hexdigest('md5', '', raw_password))
            if is_correct:
                # Convert the password to the new, more secure format.
                self.set_password(raw_password)
                self.save()
            return is_correct
        return check_password(raw_password, self.password)
    
    @classmethod
    def make_random_password(cls, length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
        "Generates a random password with the given length and given allowed_chars"
        # Note that default value of allowed_chars does not have "I" or letters
        # that look like it -- just to avoid confusion.
        from random import choice
        return ''.join([choice(allowed_chars) for i in range(length)])    
    
class ClientUser(models.Model):
    app = models.ForeignKey(ClientApp, related_name='users')
    clientId = models.CharField(max_length = 320, db_index=True) #the unique id in the app's db
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
