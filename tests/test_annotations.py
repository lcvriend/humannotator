# standard library
import sys
sys.path.insert(0, '../humannotator')
import unittest

# third party
import pandas as pd

# local
from humannotator.core.tasks import Task
from humannotator.core.annotations import (
    Datum,
    Annotation,
    Annotations
)


class DatumTestCase(unittest.TestCase):
    def test_add_attribute(self):
        datum = Datum()
        self.assertRaises(AttributeError, setattr, datum, 'c', 1)


class AnnotationTestCase(unittest.TestCase):
    def setUp(self):
        self.task_a = Task('a')
        self.task_b = Task('b')
        self.task_c = Task('c')
        self.annotation = Annotation([self.task_a, self.task_b])

    def test_set_and_get_from_valid_dict(self):
        dct = {
            self.task_a: Annotation('a'),
            self.task_b: Annotation('b'),
        }
        self.annotation['id_1'] = dct
        self.assertTrue(self.annotations(), dct)

    def test_set_and_get_from_invalid_dict(self):
        tests = [{
                self.task_a: Annotation('a'),
            },
            {
                self.task_a: Annotation('a'),
                self.task_b: Annotation('b'),
                self.task_c: Annotation('c'),
            },
        ]

        for i in tests:
            with self.subTest(i=i):
                self.assertRaises(
                    ValueError,
                    self.annotations.__setitem__,
                    'id_1',
                    i,
                )

    def test_set_and_get_from_list(self):
        lst = [
            Annotation('a'),
            Annotation('b'),
        ]
        self.annotations['id_1'] = lst
        self.assertTrue(self.annotations(), lst)


class AnnotationsTestCase(unittest.TestCase):
    def setUp(self):
        self.task_a = Task('a')
        self.task_b = Task('b')
        self.task_c = Task('c')
        self.annotations = Annotations([self.task_a, self.task_b])

    def tearDown(self):
        del self.task_a
        del self.task_b
        del self.annotations


if __name__ == '__main__':
    unittest.main()
