# standard library
import re
import unittest

# local
from humannotator.config import PATHS
from humannotator.display.display import Highlighter
from humannotator.display.elements import element_factory


class HighlighterTestCase(unittest.TestCase):
    def setUp(self):
        template = element_factory(
            template_string='**[text]**',
            cls_name='Test'
        )
        self.highlighter = Highlighter(template, 'kirby', flags=re.I)

    def test_highlighter(self):
        test = 'Hey, Kirby'
        output = 'Hey, **Kirby**'
        self.assertEqual(self.highlighter(test), output)

    def tearDown(self):
        del self.highlighter


if __name__ == '__main__':
    unittest.main()
