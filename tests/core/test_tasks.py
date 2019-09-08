# standard library
import unittest

# third party
from pandas import CategoricalDtype

# local
from humannotator.utils import option
from humannotator.config import BOOLEAN_STATES, KEYS
from humannotator.core.tasks import task_factory, Dependency, Invalid


class TaskFactoryTestCase(unittest.TestCase):
    def test_created_str_task_attributes(self):
        tests = {
            'kind':        'str',
            'dtype':       'object',
            'name':        'a',
            'instruction': 'eat my shorts  \n',
            'nullable':     False,
        }
        task = task_factory('str', 'a', instruction='eat my shorts')
        for i in tests:
            with self.subTest(i=i):
                self.assertEqual(getattr(task, i), tests[i])

    def test_created_int_task_dtype(self):
        task = task_factory('int', 'a')
        self.assertEqual(task.dtype, 'Int64')


class TaskCategoryTestCase(unittest.TestCase):
    def setUp(self):
        self.task = task_factory('category', 'a', categories=['x', 'y', 'z'])

    def test_type_of_dtype(self):
        self.assertIsInstance(self.task.dtype, CategoricalDtype)

    def test_categories(self):
        self.assertEqual(
            self.task.dtype.categories.to_list(),
            ['x', 'y' ,'z']
        )

    def test_instruction(self):
        categories = zip('1 2 3'.split(), 'x y z'.split())
        instruction = ''.join(option(i, c) for i, c in categories)
        self.assertEqual(instruction, self.task.instruction)

    def test_equality_with_task_from_iterable(self):
        task = task_factory(['x', 'y', 'z'], 'a')
        self.assertEqual(task, self.task)

    def tearDown(self):
        del self.task


class NullableTaskTestCase(unittest.TestCase):
    def test_none_if_nullable(self):
        task = task_factory('str', 'a', nullable=True)
        self.assertEqual(task(KEYS.none), None)

    def test_none_if_not_nullable(self):
        task = task_factory('int', 'a', nullable=False)
        self.assertIsInstance(task(KEYS.none), Invalid)


class ValidationTaskTestCase(unittest.TestCase):
    def test_validation_valid_int(self):
        task = task_factory('int', 'a')
        self.assertEqual(task('1337'), 1337)

    def test_validation_invalid_int(self):
        task = task_factory('int', 'a')
        self.assertIsInstance(task('1.0'), Invalid)

    def test_validation_valid_regex(self):
        task = task_factory('regex', 'a', regex=r'[fs]\d{4}r')
        self.assertEqual(task('f0084r'), 'f0084r')

    def test_validation_invalid_regex(self):
        task = task_factory('regex', 'a', regex=r'[fs]\d{4}r')
        self.assertIsInstance(task('f0084r!'), Invalid)

    def test_validation_valid_bool(self):
        key, value = next(iter(BOOLEAN_STATES.items()))
        task = task_factory('bool', 'a')
        self.assertEqual(task(key), value)

    def test_validation_invalid_bool(self):
        task = task_factory('bool', 'a')
        self.assertIsInstance(task('u'), Invalid)

    def test_validation_valid_category(self):
        task = task_factory(['x', 'y', 'z'], 'a')
        self.assertEqual(task('1'), 'x')

    def test_validation_invalid_category(self):
        task = task_factory(['x', 'y', 'z'], 'a')
        self.assertIsInstance(task('u'), Invalid)


class DependencyTestCase(unittest.TestCase):
    def test_dependency_from_tuple(self):
        condition = "`relevant` == True"
        value = None
        output = Dependency(condition, value)
        dependency = (condition, value)
        task = task_factory(
            'str',
            'topic',
            nullable=True,
            dependencies=dependency
        )
        self.assertEqual(task.dependencies[0], output)


if __name__ == '__main__':
    unittest.main()
