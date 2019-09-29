# standard library
import unittest

# third party
import pandas as pd
from pandas import CategoricalDtype

# local
from humannotator.core.tasks import task_factory
from humannotator.core.annotations import Annotations, Tasks


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
        columns = ['a', 'b', 'c', 'd', 'timestamp', 'user']
        dtypes = {
            'a': 'object',
            'b': 'Int64',
            'c': 'float',
            'd': 'bool',
            'timestamp': 'datetime64[ns]',
            'user': 'object',
        }
        data = pd.DataFrame(
            columns=columns
        ).astype(dtypes)
        self.assertTrue(self.instance.data.equals(data))

    def test_ntasks(self):
        self.assertEqual(self.instance.ntasks, len(self.names))

    def test_from_df_constructor(self):
        df = pd.DataFrame(columns=self.names
        ).astype(dict(zip(self.names, self.dtypes)))
        constructed = Annotations.from_df(
            df, instructions=self.instructions
        )
        self.assertTrue(constructed == self.instance)


class ConstructorTestCase(unittest.TestCase):
    def setUp(self):
        self.df = pd.util.testing.makeMixedDataFrame()

    def test_from_mixed_df_constructor(self):
        annotations = Annotations.from_df(self.df)
        self.assertIsInstance(annotations, Annotations)


class AnnotationTasksTestcase(unittest.TestCase):
    def setUp(self):
        self.df = pd.util.testing.makeMixedDataFrame()

    def test_add_task(self):
        annotations = Annotations.from_df(self.df)
        annotations.tasks['e'] = 'str'
        self.assertTrue('e' in annotations.data.columns)


class TasksTestCase(unittest.TestCase):
    def setUp(self):
        self.names = ['a', 'b', 'c', 'd']
        self.dtypes = ['str', 'int', 'float', 'bool']

        self.task = task_factory(self.dtypes[0], self.names[0])
        self.tasks = [
            task_factory(args[0], args[1])
            for args in zip(self.dtypes, self.names)
        ]

        self.instance = Tasks(self.tasks)

    def test_init_single_task(self):
        self.assertIsInstance(Tasks(self.task), Tasks)

    def test_order(self):
        output = {idx:name for idx, name in enumerate(self.names)}
        self.assertEqual(self.instance.order, output)

    def test_change_order_by_idx(self):
        self.names.insert(0, self.names.pop())
        output = {idx:name for idx, name in enumerate(self.names)}
        self.instance.order = [3, 0, 1, 2]
        self.assertEqual(self.instance.order, output)

    def test_change_order_by_names(self):
        self.names.insert(0, self.names.pop())
        output = {idx:name for idx, name in enumerate(self.names)}
        self.instance.order = self.names
        self.assertEqual(self.instance.order, output)

    def test_equality(self):
        output = [
            task_factory(args[0], args[1])
            for args in zip(self.dtypes, self.names)
        ]
        self.assertEqual(self.tasks, output)

    def test_inequality(self):
        self.names.insert(0, self.names.pop())
        self.dtypes.insert(0, self.dtypes.pop())
        output = [
            task_factory(args[0], args[1])
            for args in zip(self.dtypes, self.names)
        ]
        self.assertNotEqual(self.tasks, output)

    def test_contains(self):
        self.assertTrue(task_factory('str', 'a') in self.instance)


if __name__ == '__main__':
    unittest.main()
