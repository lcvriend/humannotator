# standard library
import sys
sys.path.insert(0, '../humannotator')

import unittest

# local
from humannotator.annotations import Annotations


class AnnotationsTestCase(unittest.TestCase):
    def setUp(self):
        dct = {
            'timestamp': {
                'a': Timestamp('2019-08-25 02:17:33.106594'),
                'b': Timestamp('2019-08-25 02:17:33.831085'),
                'c': Timestamp('2019-08-25 02:17:34.598477'),
                'd': Timestamp('2019-08-25 02:17:35.310781'),
                'e': Timestamp('2019-08-25 02:17:36.055024'),
                'f': Timestamp('2019-08-25 02:17:36.687190'),
            },
            'value': {
                'a': '0',
                'b': '0',
                'c': '1',
                'd': '1',
                'e': '3',
                'f': '3',
            }
        }
        df = pd.DataFrame.from_dict(dct)
        self.annotations = Annotations.from_dataframe(df)

    def tearDown(self):
        pass
