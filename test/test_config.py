# standard library
import unittest

# local
from humannotator.config import (
    QUOTECHAR,
    SEPARATOR,
    BOOLEAN_STATES,
    parse_value,
)


class ParseValueTestCase(unittest.TestCase):
    def test_parse_decimal(self):
        tests = ['6', '6\n']
        for i in tests:
            with self.subTest(i=i):
                self.assertEqual(parse_value(i), 6)

    def test_parse_float(self):
        tests = ['6.1', '6.1\n']
        for i in tests:
            with self.subTest(i=i):
                self.assertEqual(parse_value(i), 6.1)

    def test_quoted_string(self):
        tests = {
            f'\n{QUOTECHAR}a{QUOTECHAR}':  'a',
            f'{QUOTECHAR}6{QUOTECHAR}':    '6',
            f'{QUOTECHAR}a\nb{QUOTECHAR}': 'a\nb',
            f'{QUOTECHAR}a, b{QUOTECHAR}': 'a, b',
        }
        for i in tests:
            with self.subTest(i=i):
                self.assertEqual(parse_value(i), tests[i])

    def test_parse_list(self):
        output = 'a b c d e'.split()
        test = (
            "  [a, b,c, \n"
            "   d,  e,\n"
            "  ]\n"
        )
        self.assertEqual(parse_value(test), output)

    def test_parse_list_to_type(self):
        output = [1, 2.1, True, 'a,b', 'x']
        test = '[1, 2.1, True, "a,b", x]'
        self.assertEqual(parse_value(test), output)

    def test_parse_boolean(self):
        for i in BOOLEAN_STATES:
            with self.subTest(i=i):
                self.assertEqual(parse_value(i), BOOLEAN_STATES[i])
                self.assertEqual(parse_value(i.upper()), BOOLEAN_STATES[i])
                self.assertEqual(parse_value(i.capitalize()), BOOLEAN_STATES[i])

    def test_parse_string(self):
        tests = ['3peb,ble', '3peb,ble\n']
        for i in tests:
            with self.subTest(i=i):
                self.assertEqual(parse_value(i), '3peb,ble')


if __name__ == '__main__':
    unittest.main()
