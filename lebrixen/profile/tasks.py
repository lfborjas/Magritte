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

#decay factor between sessions
DECAY = 0.2 

def _interest_score(profile, concept):
    """Determine the interest score in the given profile for the given concept"""
    try:
        p = profile.preferences.get(category__id=concept).values_list('score')
        return p[0]
    except ClientPreference.DoesNotExist:
        return 0.0

@task
def update_profile(profile, context, docs, lang='en', **kwargs):
    """Update a profile with a spreading activation algorithm: determine the concepts in which the user might be interested, 
       save the session and update the activation values, proceeding then to update the profile itself
       
       Args:
           profile: the client user
           context: the last context terms 
           docs: the ids of the documents of our database the user found interesting                     
    """
    #build the context list:
    #context = context + list(DocumentSurrogate.)
    
    #STEP 0: build the concepts set and set their activation values:    
    CON = {}      
    if not hasattr(context, '__iter__'):
        context = [context,]
    #Populate the concepts list with a dictionary of the form {concept: similarity}    
    for d in context:             
        CON.update(DmozCategory.get_for_query(d, lang, as_dict=True))
    for d in DocumentSurrogate.objects.filter(pk__in=docs).values_list('category', flat=True).iterator():
        #TODO: should I compute the document's summary similarity to its alleged category?
        CON.update({d:1.0})
    
    #Spreading: add to the interest list the attenuated weight of it's ancestors:    
    for c in CON.keys():        
        curr_concept = c
        parent = DmozCategory.objects.filter(pk=curr_concept).values_list('parent', flat=True)[0]
        while parent:
            #multiple children of a parent might be in CON, ensure that the maximum score is the one that survives
            #by selecting the maximum each time
            ch_weight= DmozCategory.objects.filter(pk=curr_concept).values_list('weight', flat=True)[0]                     
            CON.update({parent: max(CON.get(parent, 0.0), CON[curr_concept] * ch_weight)})
            curr_concept = parent
            parent = DmozCategory.objects.filter(pk=curr_concept).values_list('parent', flat=True)[0]                    
    
    #STEP 2: Evolve the profile
    #Use linear combination to update
    existing_preferences = []    
    for preference in profile.preferences.iterator():
        #if the preference is not in this session, decay
        ctg = preference.category.pk
        if not ctg in CON:
            preference.score = DECAY*preference.score
        else: #it is, augment:
            preference.score = DECAY*preference.score + (1-DECAY)*CON[ctg]
        preference.save()
        #add the preference to the set of existing ones:
        existing_preferences += [ctg,] 
            
    #determine which preferences to add to the profile:
    to_add = set(CON.keys()) - set(existing_preferences)
    for newcat in to_add:
        #pref = ClientPreference(category=DmozCategory.objects.get(pk=c), score=CON[newcat], user=profile)
        #DO NOT store zero weighted preferences:
        if CON[newcat]:
            new_pref = ClientPreference(category_id=newcat, score=CON[newcat], user=profile)
            new_pref.save()    
    
    return True
                
@task
def add_document(profile, doc):
    """Add a user-provided document to the database"""
    #clean it and leave pure text -> create a function in utilities...
    #get index terms with some web service/termextract
    #get_for_query candidate categories
    #select the category with most weight that is also in the preferences
    pass
                             
                
        
        
            
            
            
    
