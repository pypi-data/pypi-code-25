#!/usr/bin/env python

'''
	Some tests for JPath
'''

# Define metadata
__version__ 	= '1.0.0'
__author__ 		= 'Vladimir Saltykov'
__copyright__ 	= 'Copyright 2017, Vladimir Saltykov'
__email__ 		= 'vowatchka@mail.ru'
__license__ 	= "MIT"
__date__ 		= '2017-12-04'

# Import modules and packages
import json
import unittest
import jpathpy

JSON = { "store": { \
			"book": [ \
			  { "category": "reference", \
				"author": "Nigel Rees", \
				"title": "Sayings of the Century", \
				"price": 8 \
			  }, \
			  { "category": "fiction", \
				"author": "Evelyn Waugh", \
				"title": "Sword of Honour", \
				"price": "1299e-2" \
			  }, \
			  { "category": "fiction", \
				"author": "Herman Melville", \
				"title": "Moby Dick", \
				"isbn": "0-553-21311-3" \
			  }, \
			  { "category": "fiction", \
				"author": "J. R. R. Tolkien", \
				"title": "The Lord of the Rings", \
				"isbn": "0-395-19395-8", \
				"price": 22.99 \
			  } \
			], \
			"bicycle": { \
			  "color": "red", \
			  "price": 19.95, \
			  "brand": None
			} \
		  } \
		}

def pretty_json(jobj):
	print('ORIGINAL JSON:\r\n' + json.dumps(jobj, indent = '    '))
	
def make_test(about_test, jpath, json, mode = jpathpy.ALL):
	print('MAKE TEST: ' + about_test)
	print('JPATH: ' + jpath)
	pretty_json(json)
	r = jpathpy.select_members(jpath, json, mode = mode)
	print()
	print('SELECTED MEMBERS:\r\nJMembers(' + ( r.s(True) if r else str([])) + ')')
	return r

class TestJPath(unittest.TestCase):
	def test_root(self):
		r = make_test('Selection from root', r'$', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_simple_selection(self):
		r = make_test('Simple selection', r'$."store"', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_deep_selection(self):
		r = make_test('Deep selection', r'$.."price"', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_execute_function(self):
		r = make_test('Execute function', r'$.."category".title()', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_disclosure_list(self):
		r = make_test('Disclosure list', r'$."store"."book"[*]', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_selection_by_index(self):
		r = make_test('Selection by index', r'$.."author"[0]', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
	
	def test_selection_by_indecies(self):
		r = make_test('Selection by indicies', r'$.."isbn"[1,3,15,0]', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_selection_by_slice(self):
		r = make_test('Selection by slice', r'$.."author"[1:3]', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_selection_by_index_from_list(self):
		r = make_test('Selection by index from list', r'$.."book".[0]', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_selection_by_indecies_from_list(self):
		r = make_test('Selection by indices from list', r'$.."book".[15,3,1,5,2]', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_selection_by_slice_from_list(self):
		r = make_test('Selection by slice from list', r'$.."book".[-1::-1]', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_selection_by_filter(self):
		r = make_test('Selection by filter', r'$."store".."price"[.isflt()]', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_empty_selection(self):
		r = make_test('Empty selection', r'$."book"', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_mode_any(self):
		r = make_test('Mode ANY', r'$.."author"', JSON, jpathpy.ANY)
		self.assertIsInstance(r, jpathpy.utils.JMember)
		
	def test_mode_index(self):
		r = make_test('Mode INDEX', r'$.."author"', JSON, 2)
		self.assertIsInstance(r, jpathpy.utils.JMember)
		
	def test_mode_index_none(self):
		r = make_test('Mode INDEX (index will be out of range)', r'$.."author"', JSON, 5)
		self.assertIsNone(r)
		
	def test_mode_slice(self):
		r = make_test('Mode SLICE', r'$.."author"', JSON, (3,1,-1))
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_selection_with_negation(self):
		r = make_test('Selection with negation' , r'$.."book"[*][!."price"]', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
	def test_selection_with_more_filtering(self):
		r = make_test('Selection with more filtering' , r'$."store"[."book".isarr() and ."bicycle"[."brand".val() = null]]', JSON)
		self.assertIsInstance(r, jpathpy.utils.JMembers)
		
if __name__ == '__main__':
	unittest.main(defaultTest = 'TestJPath')