from djapian import space, Indexer, CompositeIndexer

from search.models import DocumentSurrogate

class DocumentIndexer(Indexer):
    fields = ['title', 'summary', 'text']
    tags = [
            ('title', 'title', 3),
            ('summary', 'summary',2),
            ('text', 'text'),
            ]

space.add_index(DocumentSurrogate, DocumentIndexer, attach_as='indexer')