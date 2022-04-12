import unittest
from .number import *


class MyTestCase(unittest.TestCase):
    def test_remove_exponent_zero(self):
        self.assertEqual(remove_exponent_zero(Decimal('0.11100000')), Decimal('0.111'))
        self.assertEqual(remove_exponent_zero(Decimal('100.000000')), Decimal('100'))
        self.assertEqual(str(remove_exponent_zero(Decimal('0.100000'))), '0.1')


if __name__ == '__main__':
    unittest.main()
