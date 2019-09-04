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

Counter = element_factory(template_filename='_counter.txt')
Layout_Txt = element_factory(template_filename='basic_layout.txt')
def clear():
    os.system('cls||echo -e \\\\033c')

JUPYTER = test_for_ipython()
if JUPYTER:
    Layout_Html = element_factory(template_filename='basic_layout.html')
    def clear():
        clear_output()


class ProtoDisplay(Base):
    def __init__(self, annotator, exit_instruction, *args, **kwargs):
        self.annotator = annotator
        self.data = annotator.data
        self.exit = exit_instruction
        self.highlighter = Highlighter(self.highlight_template, *args, **kwargs)
        self.kwargs = kwargs

    def __call__(self, id, task, error=None):
        self.task_counter = Counter(count=task.pos+1, total=task.of).render()
        self.layout_context = {
            'annotator':  self.annotator.name,
            'task_count': self.task_counter,
            'task_name':  task.name,
            'task_type':  task.kind,
            'item_id':    id,
            'error':      error if error else '',
        }

    def format_items(self, items):
        items = (normalize('NFKD', str(item)) for item in items)
        kwargs = dict(zip(['label', 'value'], items))
        kwargs['value'] = self.highlighter(kwargs['value'])
        return self.item_layout(**kwargs)

    @property
    def index_counter(self):
        return Counter(
            count=self.annotator.i+1,
            total=len(self.annotator.ids)
        ).render()

    @staticmethod
    def clear():
        clear()


class DisplayJupyter(ProtoDisplay):
    item_layout = element_factory(template_filename='_item.html')
    highlight_template = element_factory(template_filename='_highlight.html')

    def __call__(self, id, task, **kwargs):
        super().__call__(id, task, **kwargs)
        layout = Layout_Html(
            **self.layout_context,
            instruction=markdown(task.instruction + self.exit),
            index_count=self.index_counter,
        )
        for items in self.data.items(id):
            layout(self.format_items(items))
        display(HTML(layout.render()))


class DisplayText(ProtoDisplay):
    item_layout = element_factory(template_filename='_item.txt')
    highlight_template = element_factory(template_filename='_highlight.txt')

    def __call__(self, id, task, **kwargs):
        super().__call__(id, task, **kwargs)
        n_char = len(max(Layout_Txt._snippets.values(), key=len))
        n_lbl  = len(Layout_Txt._snippets['_lbl_id_'])
        layout = Layout_Txt(
            **self.layout_context,
            instruction=task.instruction + self.exit,
            index_count=f"{self.index_counter:>{n_char-n_lbl-len(str(id))}}",
        )
        for items in self.data.items(id):
            layout(self.format_items(items))
        print(layout.render())


class Display(ProtoDisplay):
    def __new__(self, *args, text_display=None, **kwargs):
        if not text_display:
            if JUPYTER:
                return DisplayJupyter(*args, **kwargs)
        return DisplayText(*args, **kwargs)


class Highlighter(Base):
    styles = CSS.highlight,

    def __init__(self, template, phrases, escape=False, flags=0):
        self.template = template
        self.escape   = escape
        self.flags    = flags
        self.phrases  = phrases

    def __call__(self, item):
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
