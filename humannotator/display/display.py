# standard library
import html
import os
from collections.abc import Mapping

# third party
import pandas as pd
from markdown import markdown
from IPython.display import HTML, display, clear_output

# local
from humannotator.display.elements import element_factory
from humannotator.display.tools import (
    AnnotatedJupyter,
    AnnotatedText,
    Highlighter,
    TruncaterJupyter,
    TruncaterText,
    normalize,
)
from humannotator.utils import Base, JUPYTER


class ProtoDisplay(Base):
    Counter = element_factory(template_filename='_counter.txt')
    User = element_factory(template_filename='_user.txt')

    def __init__(self, annotator, interface, nav_instruction, *args, **kwargs):
        self.annotator = annotator
        self.interface = interface
        self.data = annotator.data
        self.nav = nav_instruction
        self.highlight = Highlighter(self.Highlight, *args, **kwargs)

    def __call__(self, id, task, error=None):
        self.task_counter = self.Counter(
            count=task.pos+1,
            total=task.of
        ).render()

        if not self.interface.active:
            try:
                self.annotation = self.annotator.annotated.loc[id]
            except KeyError:
                self.annotation = pd.Series()
        else:
            self.annotation = pd.Series()

        self.layout_context = {
            'annotator':   self.annotator.name,
            'user':        self.user,
            'index_count': self.index_counter,
            'task_count':  self.task_counter,
            'task_name':   task.name,
            'task_type':   task.kind,
            'item_id':     id,
            'instruction': task.instruction + self.nav,
            'error':       error if error else '',
        }

    @property
    def index_counter(self):
        return self.Counter(
            count=self.interface.i+1,
            total=len(self.interface.ids)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.truncate = TruncaterJupyter(**kwargs)

    def __call__(self, id, task, **kwargs):
        super().__call__(id, task, **kwargs)
        self.layout_context.update(
            instruction=markdown(task.instruction + self.nav),
            annotation=AnnotatedJupyter(self.annotation).render()
        )
        layout = self.Layout(**self.layout_context)
        for label, item in self.data.record(id):
            layout(self.format_item(label, item))
        display(HTML(layout.render()))

    def format_item(self, label, value):
        label  = normalize(label)
        value  = self.highlight(self.truncate(html.escape(normalize(value))))
        kwargs = dict(label=label, value=value)
        return self.Item(**kwargs)


class DisplayText(ProtoDisplay):
    Layout    = element_factory(template_filename='basic_layout.txt')
    Item      = element_factory(template_filename='_item.txt')
    Highlight = element_factory(template_filename='_highlight.txt')

    n_char    = len(Layout._snippets['_line_'])
    n_lbl_id  = len(Layout._snippets['_lbl_id_'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout_context.update(
            instruction=markdown(task.instruction + self.exit),
            annotation=AnnotatedText(self.annotation).render()
        )
        self.truncate = TruncaterText(
            length=self.n_char,
            tab=self.Layout._snippets['_tab_'],
            **kwargs
        )

    def __call__(self, id, task, **kwargs):
        super().__call__(id, task, **kwargs)
        indent_index = self.n_char - self.n_lbl_id - len(str(id))
        indent_user  = self.n_char - len(self.annotator.name)

        self.layout_context.update(
            index_count=f"{self.index_counter:>{indent_index}}",
            user=f"{self.user:>{indent_user}}",
        )
        layout = self.Layout(**self.layout_context)
        for label, item in self.data.record(id):
            layout(self.format_item(label, item))
        print(layout.render())

    def format_item(self, label, value):
        label  = normalize(label)
        value  = self.truncate(self.highlight(value), label)
        kwargs = dict(label=label, value=value)
        return self.Item(**kwargs)


class Display(ProtoDisplay):
    def __new__(self, *args, text_display=None, **kwargs):
        if not text_display:
            if JUPYTER:
                return DisplayJupyter(*args, **kwargs)
        return DisplayText(*args, **kwargs)
