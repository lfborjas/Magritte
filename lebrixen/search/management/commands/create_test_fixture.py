#encoding=utf-8
'''
Created on 14/06/2010

@author: lfborjas

Creates two test documents and a test ontology. Also trains a test category classifier.
Deletes the documents and the ontology from the db after all, as to not affect the database.
'''
from __future__ import division
from django.core.management.base import NoArgsCommand
import logging
import xappy
from django.conf import settings
from search.models import DmozCategory, DocumentSurrogate
from django.utils.html import strip_tags
import os
from django.core import serializers
import itertools
from datetime import datetime 

class Command(NoArgsCommand):
    help = "Create test data for the unit tests of the search and profiling apps"
    
    def train_classifier(self, categories):
        """Not the DRY-est method ever: train a category classifier for the test data
           
           Categories is an iterable of DmozCategory instances
        """
        i_connection = xappy.IndexerConnection(settings.TEST_CLASSIFIER_DATA)
        #determine the fields for indexing:
        i_connection.add_field_action('description', xappy.FieldActions.INDEX_FREETEXT, weight=2, language='en', nopos=True)
        i_connection.add_field_action('en_text', xappy.FieldActions.INDEX_FREETEXT, language='en', nopos=True)
        i_connection.add_field_action('es_text', xappy.FieldActions.INDEX_FREETEXT, language='es', nopos=True)
        i_connection.add_field_action('category_id', xappy.FieldActions.INDEX_EXACT)
        i_connection.add_field_action('category_id', xappy.FieldActions.STORE_CONTENT)
        i_connection.add_field_action('category_title', xappy.FieldActions.INDEX_EXACT)
        i_connection.add_field_action('category_title', xappy.FieldActions.STORE_CONTENT)
                
        #for every category, get the documents that belong to it:
                
        for category in categories:
            logging.debug("Processing category %s" %category.topic_id)
            u_doc = xappy.UnprocessedDocument()
            u_doc.fields.append(xappy.Field('category_id',str(category.pk)))
            u_doc.fields.append(xappy.Field('category_title',category.topic_id))
            u_doc.fields.append(xappy.Field('description', strip_tags(category.description)))
            #add each document to the corresponding text of the category
            for document in category.documentsurrogate_set.iterator(): #instead of all, an exclude(text='') ?
                try:
                    u_doc.fields.append(xappy.Field('%s_text' % (document.lang or 'en'), document.text or '' + 
                                                    document.summary or ''+
                                                    document.title or ''))                   
                except:
                    logging.error("Error processing document %s for category %s" %(document.title, category.topic_id),
                                   exc_info = True)
                    continue
            
            #add the category
            try:                
                i_connection.add(u_doc)
            except:
                #use the replace method?
                logging.error("Error adding document %s for category %s to index" % (document.title, category.topic_id),
                              exc_info = True)                       
        
        try:
            #commit the changes to the db (I'm HOPING that it will auto-flush if too much memory is used...)
            i_connection.flush()
            #close the connection to the xappy db:
            i_connection.close()            
        except:
            logging.error("Exception closing database", exc_info = True)
            
    def ponder_categories(self, categories):
        """Another anti-DRY method, this time, ponder the categories with the same approach as the initial time"""
        c = 0
        for category in categories:             
            s = category.documentsurrogate_set.count()
            sub_categories = category.dmozcategory_set.all() 
            for sc in sub_categories:
                #if it has no documents, count the category as a document
                s += sc.documentsurrogate_set.count() or 1            
            #logging.debug("Category %s has %s documents" % (category.topic_id, s))
            for sc in sub_categories:
                sub_docs = sc.documentsurrogate_set.count()
                #give a minimum non-zero weight if this category has no documents:
                #sc.weight = sub_docs / s if sub_docs else 1 / s
                #logging.debug("From a total of %s, category %s has %s documents (%s percent)" % (s, sc.topic_id, sub_docs, sub_docs/s*100))
                sc.weight = 1 - sub_docs / s 
                sc.save()
                #logging.debug("Weight: %s" % sc.weight)
            c += 1
        
        logging.debug("Done pondering %s categories" % c)
                    
    def handle_noargs(self, **options):
        #Step 1: create the test categories        
        #Top category
        logging.debug('Creating categories')
        science_cat = DmozCategory.objects.create(title = "Science",
                                              topic_id = 'Top/Science',)
        #middle categories
        physics_cat = DmozCategory.objects.create(title= 'Physics',
                                                   topic_id='Top/Science/Physics',
                                                   parent = science_cat)
        cs_cat =      DmozCategory.objects.create(title= 'Computer Science',
                                                   topic_id='Top/Science/Computer_Science',
                                                   parent = science_cat)                            
        #leaf category                         
        qp_cat = DmozCategory.objects.create(title= 'Quantum Physics',
                                                   topic_id='Top/Science/Quantum_Physics',
                                                   parent = physics_cat) 
        
        categories = [science_cat, physics_cat, cs_cat, qp_cat]
        logging.debug('Categories: %s' % [e.pk for e in categories])                                          
        #Step 2: create the test documents
        logging.debug('Creating documents')
        #science documents:
        heute = datetime.today()
        en_scidoc = DocumentSurrogate.objects.create(title='Science',
                                                   origin = "http://en.wikipedia.org/wiki/Science",
                                                   summary="",
                                                   text="""Systematic enterprise of gathering knowledge about the world
                                                            and organizing and condensing that knowledge into testable laws and theories""",
                                                   lang='en',
                                                   category = science_cat,
                                                   type = 'html',
                                                   added = heute
                                                           )
        
        es_scidoc = DocumentSurrogate.objects.create(title='Ciencia',
                                                   origin = "http://es.wikipedia.org/wiki/Ciencia",
                                                   summary="",
                                                   text="""Conjunto de conocimientos obtenidos mediante la observación y el razonamiento,
                                                           sistemáticamente estructurados y de los que se deducen principios y leyes generales""",
                                                   lang='es',
                                                   category = science_cat,
                                                   type = 'html',
                                                   added = heute
                                                   )
        #physics doc:
        en_phydoc = DocumentSurrogate.objects.create(title='Physics',
                                                   origin = "http://en.wikipedia.org/wiki/Physics",
                                                   summary="",
                                                   text="""is a natural science that involves the study of matter and its motion through spacetime,
                                                           as well as all applicable concepts, such as energy and force""",
                                                   lang='en',
                                                   category = physics_cat,
                                                   type = 'html',
                                                   added = heute
                                                   )
        #Quantum physics docs:
        en_qpdoc = DocumentSurrogate.objects.create(title='Quantum Physics',
                                                   origin = "http://en.wikipedia.org/wiki/Quantum_physics",
                                                   summary="",
                                                   text="""Einstein himself is well known for rejecting some of the claims of quantum mechanics.
                                                           He did not accept the more philosophical consequences and interpretations of quantum mechanics""",
                                                   lang='en',
                                                   category = qp_cat,
                                                   type = 'html',
                                                   added = heute
                                                   )
        
        es_qpdoc = DocumentSurrogate.objects.create(title='Física Cuántica',
                                                   origin = "http://es.wikipedia.org/wiki/Mec%C3%A1nica_cu%C3%A1ntica",
                                                   summary="",
                                                   text="""El mismo Einstein es conocido por haber rechazado algunas de las demandas de la mecánica cuántica.
                                                    No aceptó la interpretación ortodoxa de la mecánica cuántica""",
                                                   lang='es',
                                                   category = qp_cat,
                                                   type = 'html',
                                                   added = heute
                                                   )
        #computer science docs:
        en_csdoc = DocumentSurrogate.objects.create(title='Computer Science',
                                                   origin = "http://en.wikipedia.org/wiki/Computer_science",
                                                   summary="",
                                                   text="""The study of the theoretical foundations of information and computation,
                                                    and of practical techniques for their implementation and application in computer systems""",
                                                   lang='en',
                                                   category = cs_cat,
                                                   type = 'html',
                                                   added = heute
                                                   )
        
        es_csdoc = DocumentSurrogate.objects.create(title='Ciencias Computacionales',
                                                   origin = "http://es.wikipedia.org/wiki/Ciencias_de_la_computaci%C3%B3n",
                                                   summary="",
                                                   text="""Son aquellas que abarcan el estudio de las bases teóricas de la información
                                                    y la computación y su aplicación en sistemas computacionales.""",
                                                   lang='es',
                                                   category = cs_cat,
                                                   type = 'html',
                                                   added = heute
                                                   )
        documents = [ en_scidoc, es_scidoc,
                      en_phydoc,
                      en_qpdoc, es_qpdoc,
                      en_csdoc, es_csdoc]
        logging.debug('Documents: %s' % [e.pk for e in documents])
        
        cats = DmozCategory.objects.filter(pk__in = [e.pk for e in categories])
        docs = DocumentSurrogate.objects.filter(pk__in = [e.pk for e in documents])
        
        #ponder categories:
        logging.debug('Pondering categories')        
        self.ponder_categories(cats)
        #HACK: get the categories again... (to ensure the changes have taken effect)
        cats = DmozCategory.objects.filter(pk__in = [e.pk for e in categories])
        #create the fixture:        
        logging.debug('Creating fixture')
        json_serializer = serializers.get_serializer('json')()        
        fixture = open(os.path.join(settings.ROOT_PATH, 'search', 'fixtures', 'testData.json'), 'w')
        
        try:
            json_serializer.serialize(itertools.chain(cats, docs), stream = fixture)
        except:
            logging.error('Couldnt serialize!', exc_info=True)
            pass   
        else:
            #step 4: train the test classifier            
            logging.debug('Classifying categories')
            self.train_classifier(cats)
        finally:
            fixture.close()        
        #step 5: delete the categories and documents from the real db
        logging.debug('Deleting these objects from db')
        cats.delete()
        docs.delete()
        
