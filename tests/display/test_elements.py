# standard library
import unittest

# local
from humannotator.config import PATHS
from humannotator.display.elements import element_factory


class ElementFactoryTestCase(unittest.TestCase):
    def setUp(self):
        self.template = (
            "content:\n"
            "[content],\n"
            "fields:[x][y][z],\n"
            "level:[level],\n"
            "tab:'[_tab_]'"
        )
        self.LayOut = element_factory(
            template_string=self.template,
            cls_name='Test'
        )
        self.layout = self.LayOut(x='a', y='b', z='c')

    def test_snippets_type(self):
        self.assertIsInstance(self.LayOut._snippets, dict)

    def test_fields(self):
        self.assertTrue(
            set(self.LayOut._snippets).isdisjoint(set(self.LayOut._fields))
        )

    def test_template(self):
        self.assertIsInstance(self.LayOut._template, str)

    def test_layout_render(self):
        output = (
            "content:\n,"
            "\nfields:abc,\n"
            "level:1,\n"
            "tab:'    '"
        )
        self.assertMultiLineEqual(self.layout.render(), output)

    def test_layout_append_content(self):
        output = (
            "content:\n"
            "    content:\n"
            "    ,\n"
            "    fields:abc,\n"
            "    level:2,\n"
            "    tab:'    ',\n"
            "fields:abc,\n"
            "level:1,\n"
            "tab:'    '"
        )
        self.layout(self.layout)
        self.assertMultiLineEqual(self.layout.render(), output)

    def tearDown(self):
        del self.layout


if __name__ == '__main__':
    unittest.main()
