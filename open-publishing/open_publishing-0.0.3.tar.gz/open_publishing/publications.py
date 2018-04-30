from open_publishing.core.enums import ValueStatus, FieldKind, PublicationType
from open_publishing.core import Field

class PublicationsField(Field):
    def __init__(self,
                 document):
        super(PublicationsField, self).__init__(database_object=document,
                                                aspect='ebook.*,book.*,product_form.*',
                                                kind = FieldKind.regular)
        self._value = None
    
    @property
    def value(self):
        if self.status is ValueStatus.none:
            raise RuntimeError('Accessing to field which is not set')
        else :
            return self._value.copy()

    def hard_set(self,
                 value):
        if not isinstance(value, set):
            raise TypeError('Expected set, got: {0}'.format(type(value)))
        for i in value:
            if i not in PublicationType:
                raise ValueError('Expected set of op.publication.*, got : {0}'.format(i))
        self._value = value
        self._status = ValueStatus.hard
        
    def update(self,
               gjp):
        if self._status is not ValueStatus.hard:
            master_obj = self._master_object(gjp)
            if ('ebook' in master_obj
                and 'book' in master_obj
                and 'product_form' in master_obj
                and 'epub_for_sale' in master_obj['ebook']
                and 'mobi_for_sale' in master_obj['ebook']
                and 'pdf_for_sale' in master_obj['ebook']
                and 'book_for_sale' in master_obj['book']
                and 'has_software' in master_obj['product_form']
                and 'has_audiobook' in master_obj['product_form']):
                self._value = set()
                if master_obj['ebook']['epub_for_sale'] == True:
                    self._value.add(PublicationType.epub)
                if master_obj['ebook']['mobi_for_sale'] == True:
                    self._value.add(PublicationType.mobi)
                if master_obj['ebook']['pdf_for_sale'] == True:
                    self._value.add(PublicationType.pdf)
                if master_obj['book']['book_for_sale'] == True:
                    self._value.add(PublicationType.pod)
                if master_obj['product_form']['has_software'] == True:
                    self._value.add(PublicationType.software)
                if master_obj['product_form']['has_audiobook'] == True:
                    self._value.add(PublicationType.audiobook)
                self._status = ValueStatus.soft
            
    def gjp(self,
            gjp):
        if self._status is ValueStatus.hard:
            if 'ebook' not in gjp:
                gjp['ebook'] = {}
            if 'book' not in gjp:
                gjp['book'] = {}
            if 'product_form' not in gjp:
                gjp['product_form'] = {}
            gjp['ebook']['epub_for_sale'] = PublicationType.epub in self._value
            gjp['ebook']['mobi_for_sale'] = PublicationType.mobi in self._value
            gjp['ebook']['pdf_for_sale'] = PublicationType.pdf in self._value
            gjp['book']['book_for_sale'] = PublicationType.pod in self._value
            gjp['product_form']['has_software'] = PublicationType.software in self._value
            gjp['product_form']['has_audiobook'] = PublicationType.audiobook in self._value

