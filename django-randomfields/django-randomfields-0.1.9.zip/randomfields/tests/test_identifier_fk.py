import copy
import pickle

from django.test import TestCase
from randomfields.checks import DJANGO_VERSION_17
from randomfields.tests.models import TestIdentifierValue, TestIdentifierFKValue
from randomfields.models.fields.integer import IntegerIdentifier
from unittest import skipIf


@skipIf(DJANGO_VERSION_17, "Not supported on Django 17")
class IdentifierFKTests(TestCase):
    def test_reverse_accessor(self):
        obj = TestIdentifierValue.objects.create()
        rel = TestIdentifierFKValue.objects.create(data=obj)
        
        instance = TestIdentifierFKValue.objects.get(pk=rel.pk)
        
        # ensure we don't raise a type error when accessing the reverse relation
        # encountering the following exception when we do at the moment:
        #    TypeError: __new__() missing 3 required positional arguments: 'possibilities', 'lower_bound', and 'upper_bound'
        # this issue began to occur in Django 2.0 and seems to be an issue
        # with copy/deepcopy and the IntegerIdentifier class
        instance.data
    
    def test_integer_identifier_copy(self):
        value = IntegerIdentifier(1, 3, -1, 1)
        value_copy = copy.copy(value)
        self.assertEqual(value, value_copy)

    def test_integer_identifier_deepcopy(self):
        value = IntegerIdentifier(1, 3, -1, 1)
        value_deepcopy = copy.deepcopy(value)
        self.assertEqual(value, value_deepcopy)
    
    def test_integer_identifier_pickle_dumps(self):
        value = IntegerIdentifier(1, 3, -1, 1)
        pickle.dumps(value)
    
    def test_integer_identifier_pickle_loads(self):
        value = IntegerIdentifier(1, 3, -1, 1)
        value_pickled = pickle.dumps(value)
        value_unpickled = pickle.loads(value_pickled)
        
        self.assertEqual(value, value_unpickled)
