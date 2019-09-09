# standard library
import os
import re
from collections.abc import Mapping
from itertools import cycle
from unicodedata import normalize

# third party
from markdown import markdown
from IPython.display import HTML, display, clear_output

# local
from humannotator.config import CSS
from humannotator.utils import Base
from humannotator.display.elements import element_factory


def test_for_ipython():
    try:
        get_ipython()
        return True
    except NameError:
        return False


JUPYTER = test_for_ipython()


class ProtoDisplay(Base):
    Counter = element_factory(template_filename='_counter.txt')
    User = element_factory(template_filename='_user.txt')

    def __init__(self, annotator, exit_instruction, *args, **kwargs):
        self.annotator = annotator
        self.data = annotator.data
        self.exit = exit_instruction
        self.highlighter = Highlighter(self.Highlight, *args, **kwargs)
        self.kwargs = kwargs

    def __call__(self, id, task, error=None):
        self.task_counter = self.Counter(
            count=task.pos+1,
            total=task.of
        ).render()

        self.layout_context = {
            'annotator':   self.annotator.name,
            'user':        self.user,
            'index_count': self.index_counter,
            'task_count':  self.task_counter,
            'task_name':   task.name,
            'task_type':   task.kind,
            'item_id':     id,
            'instruction': task.instruction + self.exit,
            'error':       error if error else '',
        }

    def format_item(self, label, value):
        label  = normalize(label)
        kwargs = dict(label=label, value=value)
        return self.Item(**kwargs)

    @property
    def index_counter(self):
        return self.Counter(
            count=self.annotator.i+1,
            total=len(self.annotator.ids)
        ).render()

    @property
    def user(self):
        if self.annotator.user:
            return self.User(user=self.annotator.user).render()
        return ''

    @staticmethod
    def clear():
        if JUPYTER:
            clear_output()
        else:
            os.system('cls||echo -e \\\\033c')


class DisplayJupyter(ProtoDisplay):
    Layout    = element_factory(template_filename='basic_layout.html')
    Item      = element_factory(template_filename='_item.html')
    Highlight = element_factory(template_filename='_highlight.html')

    def __call__(self, id, task, **kwargs):
        super().__call__(id, task, **kwargs)
        self.layout_context.update(
            instruction=markdown(task.instruction + self.exit),
        )
        layout = self.Layout(**self.layout_context)
        for label, item in self.data.record(id):
            layout(self.format_item(label, item))
        display(HTML(layout.render()))


class DisplayText(ProtoDisplay):
    Layout    = element_factory(template_filename='basic_layout.txt')
    Item      = element_factory(template_filename='_item.txt')
    Highlight = element_factory(template_filename='_highlight.txt')

    def __call__(self, id, task, **kwargs):
        super().__call__(id, task, **kwargs)
        n_char   = len(max(self.Layout._snippets.values(), key=len))
        n_lbl_id = len(self.Layout._snippets['_lbl_id_'])
        self.layout_context.update(
            index_count=f"{self.index_counter:>{n_char-n_lbl_id-len(str(id))}}",
            user=f"{self.user:>{n_char-len(self.annotator.name)}}",
        )
        layout = self.Layout(**self.layout_context)
        for label, item in self.data.record(id):
            layout(self.format_item(label, item))
        print(layout.render())


class Display(ProtoDisplay):
    def __new__(self, *args, text_display=None, **kwargs):
        if not text_display:
            if JUPYTER:
                return DisplayJupyter(*args, **kwargs)
        return DisplayText(*args, **kwargs)


class Highlighter(Base):
    styles = CSS.highlight,

    def __init__(self, template, phrases=None, escape=False, flags=0):
        self.template = template
        self.escape   = escape
        self.flags    = flags
        self.phrases  = phrases

    def __call__(self, item):
        if self.phrases is None:
            return item
        for phrase, style in self.phrases.items():
            phrase = re.escape(phrase) if self.escape else phrase
            matches = re.findall(phrase, item, flags=self.flags)
            for match in matches:
                context = {'text': match}
                if 'style' in self.template._fields:
                    context['style'] = style
                item = item.replace(match, self.template(**context).render())
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
