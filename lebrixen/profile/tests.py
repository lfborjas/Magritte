#encoding=utf-8
"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from profile.models import ClientUser
from search.models import DmozCategory, DocumentSurrogate
from profile.tasks import update_profile
import itertools

class ProfileTest(TestCase):
    """Test the profile evolution
    
        Tests are functional tests: because the user never interacts
        with this method, should only test that it's behavior meets the
        requirements.       
     
    """
    
    fixtures = ['testData.json', 'testApp.json']
    def setUp(self):
        self.profile = ClientUser.objects.get('testUser1')
    
    def _check_expected_profile(self, profile, categories):
        """Given a collection of categories, check they match those in a given profile"""
        expected = sorted([e.category.pk for e in profile.preferences.iterator()])
        #due to propagation, must take into account the parents of the categories:
        all_categories = categories
        for c in categories:            
            for p in c.get_parents():
                all_categories.append(p)
        #remove duplicates:
        all_categories = set(all_categories)
        result = sorted([e.pk for e in all_categories])
        
        return result == expected
        
        
    def test_build_query_english(self):
        """Test that a profile is created given an english context"""
        categories = DmozCategory.get_for_query(query="Einstein", lang='en')
        ctx = """Einstein himself is well known for rejecting some of the claims of quantum mechanics."""                 
        r = update_profile.apply(args=[self.profile, ctx, []], kwargs={'lang': 'en', 'terms': False})
        
        self.assert_(self._check_expected_profile(self.profile, categories))
    
    def test_build_query_spanish(self):
        """Test that a profile is created given a spanish context"""
        
        categories = DmozCategory.get_for_query(query="Einstein", lang='es')
        ctx = """El mismo Einstein es conocido por haber rechazado algunas de las demandas de la mecánica cuántica"""                 
        r = update_profile.apply(args=[self.profile, ctx, []], kwargs={'lang': 'es', 'terms': False})
        
        self.assert_(self._check_expected_profile(self.profile, categories))
        
    def test_classify_terms_english(self):
        """Test that a profile is created with a direct query"""
        categories = DmozCategory.get_for_query(query="Einstein", lang='en')                         
        r = update_profile.apply(args=[self.profile, 'Einstein', []], kwargs={'lang': 'en', 'terms': True})
        
        self.assert_(self._check_expected_profile(self.profile, categories))
       
        
    def test_classify_terms_spanish(self):
        """Test that a profile is created with a direct query in spanish"""
        
        categories = DmozCategory.get_for_query(query="Einstein", lang='es')                         
        r = update_profile.apply(args=[self.profile, 'Einstein', []], kwargs={'lang': 'es', 'terms': True})
        
        self.assert_(self._check_expected_profile(self.profile, categories))
        
    def test_classify_terms_incorrect_lang(self):
        """Test that a profile is created with the default language if a given one is not supported"""
        categories = DmozCategory.get_for_query(query="Einstein", lang='en')                         
        r = update_profile.apply(args=[self.profile, 'Einstein', []], kwargs={'lang': 'fr', 'terms': True})
        
        self.assert_(self._check_expected_profile(self.profile, categories))
        
    
    def test_classify_only_docs(self):
        """Test that a profile is created with only documents"""
        categories = DmozCategory.get_for_query(query="study")
        docs = list(DocumentSurrogate.objects.filter(category__in=categories).values_list('pk', flat=True))
        
        r = update_profile.apply(args=[self.profile, [], docs])
        
        self.assert_(self._check_expected_profile(self.profile, categories))
    
    def test_classify_empty_context(self):
        """Test that no profile is created if no context is given"""                               
        r = update_profile.apply(args=[self.profile, [], []])
        self.assertEqual([], list(self.profile.preferences))
                
    
    def test_profile_creation(self):
        """Test that a profile is created in the normal case: a context and documents"""
        categories = DmozCategory.get_for_query(query="study")      
        other_cats = DmozCategory.get_for_query(query="Einstein")                
        docs = list(DocumentSurrogate.objects.filter(category__in=categories).values_list('pk', flat=True))
        
        r = update_profile.apply(args=[self.profile, 'Einstein', docs], kwargs={'lang': 'en', 'terms': False})
        
        self.assert_(self._check_expected_profile(self.profile, itertools.chain(categories, other_cats)))
        
        
    def test_profile_creation_query(self):
        """Test that a profile is created with a direct query and documents"""
        categories = DmozCategory.get_for_query(query="study")      
        other_cats = DmozCategory.get_for_query(query="Einstein")                
        docs = list(DocumentSurrogate.objects.filter(category__in=categories).values_list('pk', flat=True))
        
        r = update_profile.apply(args=[self.profile, 'Einstein', docs], kwargs={'lang': 'en', 'terms': True})
        
        self.assert_(self._check_expected_profile(self.profile, itertools.chain(categories, other_cats)))
        
    
    def test_profile_decay(self):
        """"Test that a profile decays properly with no new categories"""
        #create the profile:
        r = update_profile.apply(args=[self.profile, 'Einstein', []], kwargs={'lang': 'en', 'terms': True})
        before = sum(self.profile.preferences.all())
        r = update_profile.apply(args=[self.profile, [], []], kwargs={'lang': 'en', 'terms': True})
        after = sum(self.profile.preferences.all())
        
        self.assert_(before > after)
        
        
    
    def test_profile_evolution(self):
        """Test that a profile evolves with a normal context"""
        
        categories = DmozCategory.get_for_query(query="study")      
        other_cats = DmozCategory.get_for_query(query="Einstein")                
        docs = list(DocumentSurrogate.objects.filter(category__in=categories).values_list('pk', flat=True))
        #first pass: both are added
        r = update_profile.apply(args=[self.profile, 'Einstein', docs], kwargs={'lang': 'en', 'terms': True})
        p = self.profile.preferences.all()
        before_boost = {} 
        [before_boost.update({e.category.pk: e.score}) for e in p if e.category in categories]
        before_decay = {} 
        [before_decay.update({e.category.pk: e.score}) for e in p if e.category in other_cats]
        #second pass: only the docs:
        r = update_profile.apply(args=[self.profile, [], docs], kwargs={'lang': 'en', 'terms': True})
        q = self.profile.preferences.all()
        after_boost = {} 
        [after_boost.update({e.category.pk: e.score}) for e in q if e.category in categories]
        after_decay = {} 
        [after_decay.update({e.category.pk: e.score}) for e in q if e.category in other_cats]
        #the docs must've been boosted, the others, decayed:
        self.assertFalse([k for k,v in after_boost if after_boost[k] <= before_boost[k]]
                         +[k for k,v in after_decay if after_decay[k] >= before_decay[k]])
        
        
    
    def test_profile_expansion(self):
        """Test that a profile behaves properly with new preferences"""        
        categories = DmozCategory.get_for_query(query="study")      
        other_cats = DmozCategory.get_for_query(query="Einstein")                
        docs = list(DocumentSurrogate.objects.filter(category__in=categories).values_list('pk', flat=True))
        #first pass: both are added
        r = update_profile.apply(args=[self.profile, 'Einstein'], kwargs={'lang': 'en', 'terms': True})
        before = self.profile.preferences.count()
        r = update_profile.apply(args=[self.profile, [], docs], kwargs={'lang': 'en', 'terms': True})
        after = self.profile.preferences.count()
        
        self.assert_(after > before)
    
    def test_propagation(self):
        """Test that preferences propagate properly"""
        cat = DmozCategory.objects.get(title='Quantum physics')
        categories = [cat.pk,] + [p.pk for p in cat.get_parents()]
        categories.sort()
        docs = list(DocumentSurrogate.objects.filter(category=cat).values_list('pk', flat=True))
        
        r = update_profile.apply(args=[self.profile, [], docs], kwargs={'lang': 'en', 'terms': True})
        
        self.assert_(categories == sorted(list(self.profile.preferences.values_list('category', flat=True))))
                     
                     
    
        
        
    

