'''
Created on 08/05/2010

@author: lfborjas
'''

from django.conf import settings
from search.models import DmozCategory
from django.core.management.base import NoArgsCommand, CommandError
from django.utils.html import strip_tags
import logging
import xappy

class Command(NoArgsCommand):
    help = "Update the category classifier"
    
    def handle_noargs(self, **options):
        #instance the xappy indexer connection
        i_connection = xappy.IndexerConnection(settings.CATEGORY_CLASIFFIER_DATA)
        #determine the fields for indexing:
        i_connection.add_field_action('description', xappy.FieldActions.INDEX_FREETEXT, weight=2, language='en', nopos=True)
        i_connection.add_field_action('en_text', xappy.FieldActions.INDEX_FREETEXT, language='en', nopos=True)
        i_connection.add_field_action('es_text', xappy.FieldActions.INDEX_FREETEXT, language='es', nopos=True)
        i_connection.add_field_action('category_id', xappy.FieldActions.INDEX_EXACT)
        i_connection.add_field_action('category_id', xappy.FieldActions.STORE_CONTENT)
        i_connection.add_field_action('category_title', xappy.FieldActions.INDEX_EXACT)
        i_connection.add_field_action('category_title', xappy.FieldActions.STORE_CONTENT)
                
        #for every category, get the documents that belong to it:
        categories = DmozCategory.objects.all()
        for category in categories:
            logging.debug("Processing category %s" %category.topic_id)
            u_doc = xappy.UnprocessedDocument()
            u_doc.fields.append(xappy.Field('category_id',category.pk))
            u_doc.fields.append(xappy.Field('category_title',category.topic_id))
            u_doc.fields.append(xappy.Field('description', strip_tags(category.description)))
            #add each document to the corresponding text of the category
            for document in category.documentsurrogate_set.all(): #instead of all, an exclude(text='') ?
                try:
                    u_doc.fields.append(xappy.Field('%s_text' % (document.lang or 'en'), document.text or '' + 
                                                    document.summary or ''+
                                                    document.title or ''))
                except:
                    logging.error("Error processing document %s for category %s" %(document.title, category.topic_id),
                                   exc_info = True)
                    continue
            #add the document
            i_connection.add(u_doc)
            #commit the changes to the db
            i_connection.flush()
            logging.debug("Done with category %s" % category.topic_id)
            
        #close the connection to the xappy db:
        i_connection.close()
        logging.debug("Finished indexing categories")
        try:
            import smtplib
            mailer = smtplib.SMTP()
            mailer.connect()
            mailer.sendmail('root@localhost', 'lfborjas@unitec.edu',
                             'Finished indexing categories')
        except:
            logging.error("Could not send mail", exc_info = True)
                
        