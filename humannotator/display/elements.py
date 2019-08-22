# standard library
import re
import textwrap
import uuid
from pathlib import Path
from inspect import Parameter, Signature

# local
from humannotator.display.config import SETTINGS, PATHS


TABS = ' ' * SETTINGS.n_tabs


def load_templates(kind, lang=None):
    templates = dict()
    path = getattr(PATHS, kind)
    for file in path.glob(f"*{lang if lang is not None else ''}.html"):
        name_parts = file.stem.split('_')
        templates[name_parts[0]] = file.read_text().strip('\n')
    return templates


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


def element_factory(cls_name, language=SETTINGS.lang):
    path_tmpl  = PATHS.templates / (cls_name.lower() + '.html')
    path_css   = PATHS.styles / (cls_name.lower() + '.css')
    template   = path_tmpl.read_text()
    css        = path_css.read_text().strip('\n')
    api        = ['to_html']
    properties = ['id', 'level', 'css', 'content', 'toc', 'language']
    snippets   = load_templates('snippets', language)
    variables  = re.findall(SETTINGS.regex, template)

    _fields = tuple(
        name for name in variables
        if name not in properties
        and name not in snippets
    )

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        attrs = {
            'level': 1,
            'language': language,
            'id': f"{self.__class__.__name__.lower()}_{str(uuid.uuid4())[-5:]}",
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
        return self.to_html()

    def to_html(self):
        "Return element as html."
        html = self._template

        # Collect replacements to be made
        replacements = dict()
        for key in vars(self):
            replacements[f"[{key}]"] = str(getattr(self, key))
        for key in dir(self):
            if not key.startswith('_') and key not in self._api:
                replacements[f"[{key}]"] = str(getattr(self, key))
        for key in self._snippets:
            replacements[f"[{key}]"] = self._snippets[key]

        # Perform replacements
        for key in replacements:
            html = html.replace(key, replacements[key])
        return html

    cls_attrs = {
        '__init__':    __init__,
        '__iter__':    __iter__,
        '__repr__':    __repr__,
        '_repr_html_': _repr_html_,
        '_fields':     _fields,
        '_api':        api,
        '_template':   template,
        '_snippets':   snippets,
        'to_html':     to_html,
    }

    if 'content' in variables:
        def __call__(self, item):
            "Add item to content"
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
                content.append(textwrap.indent(item.to_html(), TABS))
            return ''.join(content)

        content = property(
            lambda self: self._unpack_content(),
            doc=(
                "All content contained within the element. "
                "Rendered as html recursively. Read-only."
            )
        )

        content_attrs = {
            '__call__': __call__,
            '_content': [],
            '_unpack_content': _unpack_content,
            'content': content,
        }
        cls_attrs.update(content_attrs)

    if 'toc' in variables:
        def _toc(self):
            toc = list()
            for item in self._content:
                if isinstance(item, Element):
                    if 'title' in vars(item):
                        toc_item = (
                            f"{TABS}<li><a href='#{item.id}'>{item.title}</a></li>"
                        )
                        toc.append(toc_item)
            toc_items = '\n'.join(toc)
            return (f"<ol>\n{toc_items}\n</ol>")

        toc = property(
            lambda self: self._toc(),
            doc=(
                "Table of contents, rendered as html ordered list. Read-only."
            )
        )

        toc_attrs = {
            '_toc': _toc,
            'toc':  toc,
        }
        cls_attrs.update(toc_attrs)

    if 'css' in variables:
        cls_attrs.update({'css': css})

    return type(cls_name, (Element,), cls_attrs)
