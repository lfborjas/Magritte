'''
Created on 30/04/2010

@author: lfborjas

Nifty utilities I've found here and there
'''
from django.core.exceptions import MultipleObjectsReturned

def update_or_create(attrs, filter_attrs, model):
    """
        Found in http://blog.roseman.org.uk/2010/03/9/easy-create-or-update/
        Updates a model or creates it. Use it only if update is more expected than create
        Args:
            attrs: the attributes to update
            filter_attrs: by which attributes to filter
            model: the class of the model to use
        Returns:
            The object just created/updated
    """
    #attrs = {'field1': 'value1', 'field2': 'value2'}
    #filter_attrs = {'filter_field': 'filtervalue'}
    rows = model.objects.filter(**filter_attrs).update(**attrs)
    if not rows:
        attrs.update(**filter_attrs)
        obj = model.objects.create(**attrs)
    return obj

def create_or_update(init_attrs, filter_attrs, model, do_update=True):
    """
        Found in http://blog.roseman.org.uk/2010/03/9/easy-create-or-update/
        Creates a model instance or updates it. As its name states, use it if create
        is more probable than update
        Args: 
            init_attrs: a dictionary of the attributes to initialize the instance
            filter_attrs: a dictionary of the attributes which will filter the queryset
            model: the class of the model to instantiate
            do_update: whether to actually update or just pass
        Returns:
            the created/updated object, already saved
    """
    try:
        obj = model.objects.get(**filter_attrs)
        if do_update:
            obj.update(**init_attrs)
        return obj      
    except MultipleObjectsReturned:
        #undesirable exception...
        raise
        #obj = model.objects.filter(**filter_attrs)
        #obj.update(**init_attrs)
        #return obj        
    except model.DoesNotExist:
        return model.objects.create(**init_attrs)
     
        
    
        
        