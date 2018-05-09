from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.interface import implements


class CSSVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = []
        registry = getUtility(IRegistry)
        styles = registry['collective.tiles.advancedstatic.css_styles']
        for style in styles:
            term = style.split('|')  # get value and title
            items.append(SimpleTerm(term[0], term[0], term[1]))
        items.sort(lambda x, y: cmp(x.title, y.title))
        return SimpleVocabulary(items)


CSSVocabulary = CSSVocabulary()
