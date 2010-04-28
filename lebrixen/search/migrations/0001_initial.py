
from south.db import db
from django.db import models
from search.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'DocumentSurrogate'
        db.create_table('search_documentsurrogate', (
            ('id', orm['search.DocumentSurrogate:id']),
            ('title', orm['search.DocumentSurrogate:title']),
            ('origin', orm['search.DocumentSurrogate:origin']),
            ('summary', orm['search.DocumentSurrogate:summary']),
            ('text', orm['search.DocumentSurrogate:text']),
            ('added', orm['search.DocumentSurrogate:added']),
            ('lang', orm['search.DocumentSurrogate:lang']),
        ))
        db.send_create_signal('search', ['DocumentSurrogate'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'DocumentSurrogate'
        db.delete_table('search_documentsurrogate')
        
    
    
    models = {
        'search.documentsurrogate': {
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '10'}),
            'origin': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }
    
    complete_apps = ['search']
