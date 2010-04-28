from django.db import models

# Create your models here.
class DocumentSurrogate(models.Model):
    title = models.CharField(max_length=255)
    origin = models.URLField(blank = True)
    summary = models.TextField(blank = True)
    text = models.TextField(blank = True)
    added = models.DateTimeField(auto_now_add = True)
    lang = models.CharField(max_length = 10, default = 'en')
    
    def __unicode__(self):
        return self.title + self.summary
    
    def get_stemming_lang(self):
        return self.lang
     
