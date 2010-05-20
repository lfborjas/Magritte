'''
Created on 17/05/2010

@author: lfborjas

Comprises the tasks that will be executed in background, such as categorizing and profiling
'''
from __future__ import division
import math
from profile.models import ClientPreference
from search.models import DmozCategory, DocumentSurrogate
from celery.decorators import task
#from heapq import heappush, heappop, heapify

#Normalization constant for the preferences vector
K = 1

def _interest_score(profile, concept):
    """Determine the interest score in the given profile for the given concept"""
    try:
        p = profile.preferences.get(category=concept).values_list('score')
        return p[0]
    except ClientPreference.DoesNotExist:
        return 1.0

@task
def update_profile(profile, context, docs, lang='en'):
    """Update a profile with a spreading activation algorithm: determine the concepts in which the user might be interested, 
       save the session and update the activation values, proceeding then to update the profile itself
       
       Args:
           profile: the client user
           context: the last context terms and the documents which the user found interesting                     
    """
    #build the context list:
    #context = context + list(DocumentSurrogate.)
    
    #STEP 0: build the concepts set    
    CON = []
    for d in context:
        #if it is a stored document, just add it's category
        if hasattr(d, 'category'):
            CON += d.category
        else: #it's a query or a new document
            CON += DmozCategory.get_for_query(d, lang)
    #remove duplicates:
    CON = set(CON)    
    #STEP 1: the actual spreading algorithm
    for d in context:              
        #a category mapping of {pk: weight} for this document:
        if not hasattr(d, 'category'):
            prob_categories = DmozCategory.get_for_query(d, lang, as_dict=True)
        
        #determine the activation value    
        for c in CON:
            sim = 0
            if hasattr(d, 'category') and c == d.category:
                sim = 1
            else:
                sim = prob_categories.get(c.pk, 0.0)
            
            if sim:
                c.activation = _interest_score(profile, c) * sim                
            else:
                c.activation = 0.0
                                     
            for parent in c.get_parents():
                parent.activation = c.activation * c.weight                                                                       
                CON.update(set([parent,]))
                
    
    #STEP 2: Evolve the profile
    n = 0
    #profile_concepts = profile.preferences.values_list('category', flat=True)
    for c in CON:
        pref = ClientPreference.objects.get_or_create(category = c, user=profile)[0]
        pref.score = pref.score * c.activation
    
    user_preferences = profile.preferences.all()
    #get the vector length: square root of the sum of all squared elements (euclidean distance):
    for p in user_preferences:         
        n += p.score**2 
    n = math.sqrt(n)
    #normalize the vector: v/|v|
    for p in user_preferences:
        p.score = (p.score*K)/n
        p.save()
    
    return True
                
@task
def add_document(profile, doc):
    """Add a user-provided document to the database"""
    #clean it and leave pure text -> create a function in utilities...
    #get index terms with some web service/termextract
    #get_for_query candidate categories
    #select the category with most weight that is also in the preferences
    pass
                             
                
        
        
            
            
            
    
