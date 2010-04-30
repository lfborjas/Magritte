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
     
class DmozCategory(models.Model):
    """Based loosely on the structure of the dmoz RDF dump"""
    title = models.CharField(max_length = 255, blank= True, default = "") 
    topic_id = models.CharField(max_length = 320, db_index = True)
    dmoz_code = models.IntegerField(null = True)
    last_updated = models.DateTimeField(null = True)
    description = models.TextField(null = True)
    parent = models.ForeignKey('self', null = True)
    es_alt = models.CharField(max_length = 320, blank = True, default = "") #the alternate in spanish