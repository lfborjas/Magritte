# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'ClientSession'
        db.create_table('profile_clientsession', (
            ('date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('documents', self.gf('django.db.models.fields.CommaSeparatedIntegerField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('context', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sessions', to=orm['profile.ClientUser'])),
        ))
        db.send_create_signal('profile', ['ClientSession'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'ClientSession'
        db.delete_table('profile_clientsession')
    
    
    models = {
        'profile.clientapp': {
            'Meta': {'object_name': 'ClientApp'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '512', 'blank': 'True'})
        },
        'profile.clientpreference': {
            'Meta': {'object_name': 'ClientPreference'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.DmozCategory']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'preferences'", 'to': "orm['profile.ClientUser']"})
        },
        'profile.clientsession': {
            'Meta': {'object_name': 'ClientSession'},
            'context': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'documents': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sessions'", 'to': "orm['profile.ClientUser']"})
        },
        'profile.clientuser': {
            'Meta': {'object_name': 'ClientUser'},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['profile.ClientApp']"}),
            'clientId': ('django.db.models.fields.CharField', [], {'max_length': '320'}),
            'clientName': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '320', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'info': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'})
        },
        'search.dmozcategory': {
            'Meta': {'object_name': 'DmozCategory'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'dmoz_code': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'es_alt': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '320', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['search.DmozCategory']", 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'topic_id': ('django.db.models.fields.CharField', [], {'max_length': '320', 'db_index': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {'default': '0.0', 'null': 'True'})
        }
    }
    
    complete_apps = ['profile']
