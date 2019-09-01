# standard library
import sys
sys.path.insert(0, '../humannotator')
import unittest

# third party
import pandas as pd
from pandas import CategoricalDtype

# local
from humannotator.core.tasks import task_factory
from humannotator.core.annotations import Annotations


class AnnotationsTestCase(unittest.TestCase):
    def setUp(self):
        self.names = ['a', 'b', 'c', 'd']
        self.dtypes = ['str', 'int', 'float', 'bool']
        self.instructions = ['Enter string', 'Enter integer', None, None]

        tasks = [
            task_factory(args[0], args[1], instruction=args[2])
            for args in zip(self.dtypes, self.names, self.instructions)
        ]
        self.instance = Annotations(tasks)

    def test_annotations_data(self):
        columns = ['a', 'b', 'c', 'd', 'timestamp']
        dtypes = {
            'a': 'object',
            'b': 'Int64',
            'c': 'float',
            'd': 'bool',
            'timestamp': 'datetime64[ns]',
        }
        data = pd.DataFrame(
            columns=columns
        ).astype(dtypes)
        self.assertTrue(self.instance.data.equals(data))

    def test_ntasks(self):
        self.assertEqual(self.instance.ntasks, len(self.names))

    def test_instructions(self):
        self.assertEqual(self.instance.instructions, self.instructions)

    def test_from_df_constructor(self):
        df = pd.DataFrame(columns=self.names
        ).astype(dict(zip(self.names, self.dtypes)))
        constructed = Annotations.from_df(
            df, instructions=self.instructions
        )
        self.assertTrue(constructed == self.instance)

    def tearDown(self):
        del self.names
        del self.dtypes
        del self.instructions
        del self.instance


if __name__ == '__main__':
    unittest.main()
