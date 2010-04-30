
from south.db import db
from django.db import models
from search.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'DmozCategory'
        db.create_table('search_dmozcategory', (
            ('id', orm['search.dmozcategory:id']),
            ('title', orm['search.dmozcategory:title']),
            ('topic_id', orm['search.dmozcategory:topic_id']),
            ('dmoz_code', orm['search.dmozcategory:dmoz_code']),
            ('last_updated', orm['search.dmozcategory:last_updated']),
            ('description', orm['search.dmozcategory:description']),
            ('parent', orm['search.dmozcategory:parent']),
        ))
        db.send_create_signal('search', ['DmozCategory'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'DmozCategory'
        db.delete_table('search_dmozcategory')
        
    
    
    models = {
        'search.dmozcategory': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'dmoz_code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
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
