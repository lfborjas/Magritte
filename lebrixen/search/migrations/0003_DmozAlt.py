
from south.db import db
from django.db import models
from search.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding field 'DmozCategory.es_alt'
        db.add_column('search_dmozcategory', 'es_alt', orm['search.dmozcategory:es_alt'])
        
    
    
    def backwards(self, orm):
        
        # Deleting field 'DmozCategory.es_alt'
        db.delete_column('search_dmozcategory', 'es_alt')
        
    
    
    models = {
        'search.dmozcategory': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'dmoz_code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'es_alt': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '320', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.DmozCategory']", 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'topic_id': ('django.db.models.fields.CharField', [], {'max_length': '320', 'db_index': 'True'})
        },
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
