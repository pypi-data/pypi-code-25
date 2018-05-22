import unittest
import wake

class TestMethods(unittest.TestCase):
  
  def test_get_nested_links(self):
    text = """ish fleet defeated Alfred's fleet, which may have been weakened in the previous engagement.{{sfn|Woodruff|1993|p=86}}
[[File:Southwark Bridge City Plaque.JPG|thumb|A plaque in the [[City of London]] noting the restoration of the Roman walled city by Alfred.]]
A year later, in 886, Alfre"""
    links = wake.get_links(text)
    self.assertEqual(len(links), 2)

  def test_find_index_of_sublist(self):
    types = ["open", "open", "close", "close"]
    open_index, close_index = wake.find_index_of_sublist(types, ["open", "close"])
    self.assertEqual(open_index, 1)
    self.assertEqual(close_index, 2)

    types = ["open", "open", "close", "close", "open", "close"]
    open_index, close_index = wake.find_index_of_sublist(types, ["open", "close"])
    self.assertEqual(open_index, 1)
    self.assertEqual(close_index, 2)
