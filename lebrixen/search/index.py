from djapian import space, Indexer, CompositeIndexer
import logging
from search.models import DocumentSurrogate

class DocumentIndexer(Indexer):
    fields = ['title', 'summary', 'text']
    #TODO: add the date tag, to do an order_by and stuff    
    tags = [
            ('title', 'title', 3),
            ('summary', 'summary',2),
            ('text', 'text'),
            ]

space.add_index(DocumentSurrogate, DocumentIndexer, attach_as='indexer')

try:
    DocumentSurrogate.indexer.update()
except Exception, e:
    logging.error("Error updating index", exc_info=True)