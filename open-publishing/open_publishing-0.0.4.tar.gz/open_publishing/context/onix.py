from open_publishing.core.enums import PublicationType, OnixStyle, OnixType, OnixStatus
from open_publishing.document import Document
from open_publishing.content import Content

class OnixProduct(object):
    def __init__(self,
                 document_id,
                 publication_type,
                 availability):
        self._document_id = document_id

        if publication_type not in PublicationType:
            raise ValueError('expected one of op.publication, got: {0}'.format(publication_type))
        else:
            self._publication_type = publication_type

        self._availability = availability

    @property
    def document_id(self):
        return self._document_id

    @property
    def publication_type(self):
        return self._publication_type

    @property
    def availability(self):
        return self._availability
    
class Onix(object):
    def __init__(self,
                 ctx):
        self._ctx = ctx

    def download(self,
                 guids=None,
                 documents_ids=None,
                 products=None,
                 publication_type=None,
                 status=OnixStatus.current,
                 onix_style=OnixStyle.default,
                 onix_type=None,
                 availability=None,
                 contract_type=None,
                 codelist_issue=None,
                 subject_keyword_in_separate_tag=False):
        if onix_style not in OnixStyle:
            raise ValueError('expected one of op.onix.style, got: {0}'.format(onix_style))
        if (onix_type is not None) and (onix_type not in OnixType):
            raise ValueError('expected one of op.onix.type, got: {0}'.format(onix_type))
        if publication_type not in PublicationType and products is None:
            raise ValueError('expected one of op.publication, got: {0}'.format(publication_type))
        if guids is None and documents_ids is None and products is None:
            raise TypeError('Neither guids, documents_ids nor producest specified')
        elif [guids, documents_ids, products].count(None) < 2:
            raise TypeError('guids, documents_ids or products should be specified, nor both')
        elif guids is not None:
            products = [OnixProduct(Document.id_from_guid(guid), publication_type, availability) for guid in guids]
        elif documents_ids is not None:
            products = [OnixProduct(document_id, publication_type, availability) for document_id in documents_ids]


        data, headers =  self._ctx.gjp.request_onix(products,
                                                    status=status,
                                                    onix_style=onix_style,
                                                    onix_type=onix_type,
                                                    contract_type=contract_type,
                                                    codelist_issue=codelist_issue,
                                                    subject_keyword_in_separate_tag=subject_keyword_in_separate_tag)
        return Content(data, headers)
        
    def save(self,
             filename = None,
             **kwargs):
        content = self.download(**kwargs)
        with open(filename if filename else content.filename, 'wb') as f:
            f.write(content.data)
