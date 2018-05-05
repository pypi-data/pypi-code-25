from collections import OrderedDict
import unittest

from easy_init import _generate_init


class TestInitGenerate(unittest.TestCase):
    def test_empty(self):
        expected = '''def __init__(self):
    pass'''
        self.assertEqual(_generate_init([], {}), expected)

    def test1nondefault(self):
        expected = '''def __init__(self, red):
    self.red = red'''
        self.assertEqual(_generate_init(['red'], {}), expected)

    def test1default(self):
        expected = '''def __init__(self, red=0):
    self.red = red'''
        self.assertEqual(_generate_init([], {'red': 0}), expected)

    def testmultiplenondefault(self):
        expected = '''def __init__(self, red, green):
    self.red = red
    self.green = green'''
        self.assertEqual(_generate_init(['red', 'green'], {}), expected)

    def testmultipledefault(self):
        expected = '''def __init__(self, red=0, green=0):
    self.red = red
    self.green = green'''
        self.assertEqual(_generate_init([], OrderedDict([('red', 0), ('green', 0)])), expected)

    def test1defaultmultiplenondefault(self):
        expected = '''def __init__(self, red, green, blue=0):
    self.red = red
    self.green = green
    self.blue = blue'''
        self.assertEqual(_generate_init(['red', 'green'], OrderedDict([('blue', 0)])), expected)

    def testmultipledefault1nondefault(self):
        expected = '''def __init__(self, red, green=0, blue=0):
    self.red = red
    self.green = green
    self.blue = blue'''
        self.assertEqual(_generate_init(['red'],
                                       OrderedDict([('green', 0),('blue', 0)])),
                         expected)

    def testmultipleboth(self):
        expected = '''def __init__(self, red, green, blue=5, alpha=1.0):
    self.red = red
    self.green = green
    self.blue = blue
    self.alpha = alpha'''
        self.assertEqual(_generate_init(['red','green'],
                                       OrderedDict([('blue', 5),('alpha', 1.0)])),
                         expected)


if __name__ == '__main__':
    unittest.main()
