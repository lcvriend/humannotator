# standard library
import sys
sys.path.insert(0, '../humannotator')
import unittest

# local
from humannotator.core.tasks import (
    Choices,
    Task,
    Task_MultipleChoice,
    Invalid
)


class ChoicesTestCase(unittest.TestCase):
    def test_create_from_iterables(self):
        output = {'a':'a', 'b':'b', 'c':'c'}
        tests = [
            'abc',
            ['a', 'b', 'c'],
        ]
        for i in tests:
            with self.subTest(i=i):
                self.assertEqual(Choices(i).__dict__, output)

    def test_unhashable_choices(self):
        faulty_dct = {
            'a': 'x',
            'b': 2,
            'c': [3],
        }
        self.assertRaises(ValueError, Choices, faulty_dct)

    def test_ordered_items(self):
        output = (('a', 2), ('b', 1), ('c', 3))
        dct = {
            'b': 1,
            'a': 2,
            'c': 3,
        }
        choices = Choices(dct)
        self.assertEqual(choices.ordered_items(), output)


class TaskTestCase(unittest.TestCase):
    def test_equality(self):
        a = Task('a')
        b = Task('a')
        c = Task_MultipleChoice({'a': 1, 'b': 2})
        d = Task_MultipleChoice({'b': 2, 'a': 1})
        tests = [(a == b), (c == d)]
        for i in tests:
            with self.subTest(i=i):
                self.assertTrue(a == b)

    def test_inequality(self):
        a = Task('a')
        b = Task('b')

        c = Task_MultipleChoice({'a': 1, 'b': 2})
        d = Task_MultipleChoice({'b': 3, 'a': 1})
        e = Task_MultipleChoice({'a': 1, 'b': 2})
        f = Task_MultipleChoice({'b': 2, 'c': 1})

        tests = [(a == b), (c == d), (e == f)]
        for i in tests:
            with self.subTest(i=i):
                self.assertFalse(a == b)

    def test_hashability(self):
        a = Task('a')
        dct = {a: 'a'}
        self.assertEqual(dct[a], 'a')

    def test_validation_valid(self):
        a = Task_MultipleChoice({'a': 1, 'b': 2})
        self.assertTrue(a('a') == 'a')

    def test_validation_invalid(self):
        a = Task_MultipleChoice({'a': 1, 'b': 2})
        self.assertIsInstance(a('c'), Invalid)


if __name__ == '__main__':
    unittest.main()
