import unittest
import sub_pkg_demo.demo

class TestUM(unittest.TestCase):

    def setUp(self):
        pass
    
    def test_demo_says_something(self):
        self.assertEqual(sub_pkg_demo.demo.mydemo(), "this is my demo")
    

if __name__ == "__main__":
    unittest.main()