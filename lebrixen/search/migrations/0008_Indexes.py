# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        try: 
            # Adding index on 'DocumentSurrogate', fields ['origin']
            db.create_index('search_documentsurrogate', ['origin'])

            # Adding index on 'DocumentSurrogate', fields ['title']
            db.create_index('search_documentsurrogate', ['title'])
	except:
	    pass
    
    
    def backwards(self, orm):
        
        # Removing index on 'DocumentSurrogate', fields ['origin']
        db.delete_index('search_documentsurrogate', ['origin'])

        # Removing index on 'DocumentSurrogate', fields ['title']
        db.delete_index('search_documentsurrogate', ['title'])
    
    
    models = {
        'search.dmozcategory': {
            'Meta': {'object_name': 'DmozCategory'},
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
            'Meta': {'object_name': 'DocumentSurrogate'},
            'added': ('django.db.models.fields.DateTimeField', [], {'default': "'Tue May  4 11:29:16 2010'", 'null': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.DmozCategory']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '10'}),
            'origin': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '512', 'db_index': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }
    
    complete_apps = ['search']
