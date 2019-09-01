# standard library
import re
import textwrap
import uuid
from copy import deepcopy
from inspect import Parameter, Signature
from pathlib import Path

# local
from humannotator.config import ELEMENTS, PATHS


TABS = ' ' * ELEMENTS.n_tabs


def load_building_blocks(kind, suffix, language=None):
    blocks = dict()
    blocks_lang = dict()
    path = getattr(PATHS, kind)
    patterns = dict.fromkeys(['*.txt', f"*{suffix}"]) # ordered set
    for pattern in patterns:
        for file in path.glob(pattern):
            if file.stem.endswith(f"-{language}"):
                name_parts = file.stem.split('-')
                blocks_lang[name_parts[0]] = file.read_text().strip('\n')
            elif '-' not in file.stem:
                blocks[file.stem] = file.read_text().strip('\n')
        blocks.update(blocks_lang)
    return blocks


def make_signature(names):
    return Signature(
        Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) for name in names)


class ElementMeta(type):
    def __new__(cls, name, bases, clsdict):
        clsobj = super().__new__(cls, name, bases, clsdict)
        sig = make_signature(clsobj._fields)
        setattr(clsobj, '__signature__', sig)
        return clsobj


class Element(metaclass=ElementMeta):
    _fields = []
    def __init__(self, *args, **kwargs):
        bound = self.__signature__.bind(*args, **kwargs)
        for name, val in bound.arguments.items():
            setattr(self, name, val)


def element_factory(
    template_filename=None,
    template_string=None,
    cls_name=None,
    language=ELEMENTS.lang
):
    if template_filename:
        path_tmpl = PATHS.templates / template_filename
        type_tmpl = path_tmpl.suffix
        cls_name  = path_tmpl.stem.capitalize()
        template  = path_tmpl.read_text()
    elif template_string:
        template  = template_string
        type_tmpl = '.txt'
        cls_name  = cls_name
    else:
        raise ValueError(
            "Arguments missing:"
            "use either `template_filename` or `template_string`."
        )

    api        = ['render']
    properties = ['id', 'level', 'css', 'content', 'language']
    snippets   = load_building_blocks('snippets', type_tmpl, language=language)
    variables  = {var.lower() for var in re.findall(ELEMENTS.regex, template)}

    _fields = tuple(
        name for name in variables
        if name not in properties
        and name not in snippets
    )

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        attrs = {
            'id': f"{self.__class__.__name__.lower()}_{str(uuid.uuid4())[-5:]}",
            'template_type': type_tmpl,
            'language': language,
            '_content': [],
            'level': 1,
        }
        for name, value in attrs.items():
            setattr(self, name, value)

    def __iter__(self):
        for name in self.__dict__:
            yield getattr(self, name)

    def __repr__(self):
        values = ', '.join('{}={!r}'.format(*i) for i
        in zip(self.__dict__, self))
        return f"{self.__class__.__name__}({values})"

    def _repr_html_(self):
        return self.render()

    def render(self):
        replacements = vars(self).copy()
        replacements.update(self._snippets)
        for key in dir(self):
            if not key.startswith('_') and key not in self._api:
                replacements[key] = getattr(self, key)

        txt = self._template
        for key in replacements:
            txt = re.sub(rf"\[{key}\]", str(replacements[key]), txt, flags=re.I)
        return txt

    cls_attrs = {
        '__init__':    __init__,
        '__iter__':    __iter__,
        '__repr__':    __repr__,
        '_repr_html_': _repr_html_,
        '_fields':     _fields,
        '_api':        api,
        '_template':   template,
        '_snippets':   snippets,
        'render':      render,
    }

    if 'content' in variables:
        def __call__(self, item):
            "Add item to content"
            if item is self:
                item = deepcopy(item)
                item._content = []
            self._content.append(item)

        def _unpack_content(self):
            content = []
            for item in self._content:
                item.level = self.level + 1
                if isinstance(item, Element):
                    try:
                        item._unpack_content()
                    except AttributeError:
                        pass
                content.append(textwrap.indent(item.render(), TABS))
            return ''.join(content)

        content = property(
            lambda self: self._unpack_content(),
            doc=(
                "All content contained within the element. "
                "Rendered recursively. Read-only."
            )
        )

        content_attrs = {
            '__call__': __call__,
            '_unpack_content': _unpack_content,
            'content': content,
        }
        cls_attrs.update(content_attrs)

    if 'css' in variables:
        path_css = (PATHS.styles / template_filename).with_suffix('.css')
        css = path_css.read_text().strip('\n')
        cls_attrs.update({'css': css})

    return type(cls_name, (Element,), cls_attrs)
