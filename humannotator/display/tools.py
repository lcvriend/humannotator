# standard library
import os
import re
import unicodedata
from collections.abc import Mapping
from itertools import cycle

# local
from humannotator.config import CSS
from humannotator.utils import Base, JUPYTER
from humannotator.display.elements import element_factory


class Truncater(Base):
    def __call__(self, value, limit=32):
        bag = value.split()
        if len(bag) > limit:
            show = ' '.join(bag[:73]) + ' [...]'
            hide = '[...] ' + ' '.join(bag[73:])
            return show, hide
        return value, None


class TruncaterJupyter(Truncater):
    Expandable = element_factory(template_filename='_expandable.html')

    def __call__(self, value, **kwargs):
        show, hide = super().__call__(value, **kwargs)
        if hide is not None:
            return self.Expandable(show=show, hide=hide).render()
        return show


class TruncaterText(Truncater):
    def __init__(self, length):
        self.length = length

        return '\n'.join(
            wrap(
                value,
                width=self.width,
                initial_indent=' '*(len(label)+2),
                subsequent_indent=self.tab),
        ).strip()


class Highlighter(Base):
    styles = CSS.highlight,

    def __init__(self, template, phrases=None, escape=False, flags=0, **kwargs):
        self.template = template
        self.escape   = escape
        self.flags    = flags
        self.phrases  = phrases

    def __call__(self, item):
        def marker(match):
            context = {'text': match[0]}
            if 'style' in self.template._fields:
                context['style'] = style
            return self.template(**context).render()

        if self.phrases is None:
            return item
        for phrase, style in self.phrases.items():
            phrase = re.escape(phrase) if self.escape else phrase
            item = re.sub(phrase, marker, item, flags=self.flags)
        return item

    @property
    def phrases(self):
        return self._phrases

    @phrases.setter
    def phrases(self, phrases):
        if phrases is None:
            self._phrases = None
        else:
            if isinstance(phrases, str):
                phrases = [phrases]
            if phrases is not Mapping:
                phrases = dict(zip(phrases, cycle(*self.styles)))
            self._phrases = phrases


def normalize(value):
    if JUPYTER:
        value = value.replace('$', '\$')
    return unicodedata.normalize('NFKC', str(value))
