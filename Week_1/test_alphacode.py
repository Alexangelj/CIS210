"""
  Too Many Pins.  Assignment 1, Part 1 CIS 210
  Author: Alexander Angel
  Credits: Nathan Malamud for explaining how unittest module works.
  
  Test Alphacode.py using unittest class.
  """

import unittest
from alphacode import alphacode, error_message

class Test_AlphaCode(unittest.TestCase):
    def test_encode_PINS(self):
        self.assertEqual(alphacode(4327), "lohi")
        self.assertEqual(alphacode(1298), "dizo")

    def test_long_PINS(self):
        self.assertEqual(alphacode(1234567), "begomari")
        self.assertEqual(alphacode(42424242), "lililili")
        self.assertEqual(alphacode(98765), "cuwira")
        self.assertEqual(alphacode(987654), "zotenu")
        self.assertEqual(alphacode(547698), "nutezo")

    def test_negative(self):
        self.assertEqual(alphacode(-52), "")
        self.assertEqual(alphacode(-5435345345), "")

    def test_invalid_args(self):
        self.assertRaises(TypeError, alphacode(3.14))
        self.assertEqual(alphacode(1005040.352), error_message)
        self.assertEqual(alphacode(-3.14), "")

if __name__ == "__main__":
    unittest.main()