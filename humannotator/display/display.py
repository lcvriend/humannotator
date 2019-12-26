"""
This module controls the display of the annotator. If the annotator is run
in Jupyter the display will be rendered in html, otherwise the display will be
text-based.

Classes
=======
ProtoDisplay:
    Class containing the methods and attributes that are common to both the
    Jupyter and text display.
DisplayJupyter:
    Class containing the methods and attributes specific to the Jupyter display.
DisplayText:
    Class containing the methods and attributes specific to the text display.
Display:
    Class factory that instantiates either the Jupyter or the Text display.
"""


# standard library
import html
import os
from collections.abc import Mapping

# third party
import pandas as pd
from markdown import markdown
try:
    from IPython.display import HTML, display, clear_output
except ModuleNotFoundError:
    pass

# local
from humannotator.config import COMPONENTS
from humannotator.display import JUPYTER
from humannotator.display.elements import element_factory
from humannotator.display.components import (
    AnnotationDisplayJupyter,
    AnnotationDisplayText,
    Highlighter,
    TruncaterJupyter,
    TruncaterText,
    normalize,
)
from humannotator.utils import Base


class ProtoDisplay(Base):
    Counter = element_factory(template_filename='_counter.txt')
    User    = element_factory(template_filename='_user.txt')

    def __init__(
        self,
        annotator,
        interface,
        *args,
        escape_html=False,
        **kwargs
    ):
        self.annotator = annotator
        self.interface = interface
        self.data = annotator._data
        self.highlight = Highlighter(self.Highlight, *args, **kwargs)
        self.navigation = interface.get_instruction()
        self.escape_html = escape_html

    def __call__(self, id, task=None, error=None):
        self.layout_context = {
            'annotator':   self.annotator.name,
            'user':        self.user,
            'index_count': self.index_counter,
            'item_id':     id,
        }
        self.task_context = {
                'task_name':   'Navigation',
                'instruction': self.navigation,
                'task_count':  '',
                'task_type':   '',
                'error':       '',
            }

        if task:
            task_counter = self.Counter(
                count=task.pos+1,
                total=task.of
            ).render()
            self.task_context = {
                'task_name':   task.name,
                'instruction': task.instruction + '\n' + self.navigation,
                'task_count':  'Task ' + task_counter,
                'task_type':   f"({task.kind})",
                'error':       error if error else '',
            }

        if not self.interface.fresh:
            try:
                self.annotation = self.annotator.annotated.loc[id]
            except KeyError:
                self.annotation = pd.Series()
        else:
            self.annotation = pd.Series()

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

    def format_value(self, value):
        value = normalize(value)
        if self.escape_html:
            value = html.escape(value)
        return value


class DisplayJupyter(ProtoDisplay):
    Layout    = element_factory(template_filename='basic_layout.html')
    Tasks     = element_factory(template_filename='tasks.html')
    Item      = element_factory(template_filename='_item.html')
    Highlight = element_factory(template_filename='_highlight.html')

    def __init__(self, *args, maxheight=COMPONENTS.maxheight, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxheight = str(maxheight)
        self.truncate = TruncaterJupyter(**kwargs)

    def __call__(self, id, *args, **kwargs):
        super().__call__(id, *args, **kwargs)
        self.task_context.update(
            instruction=markdown(self.task_context['instruction']),
        )
        self.layout_context.update(
            tasks=self.Tasks(**self.task_context).render(),
            annotation=AnnotationDisplayJupyter(self.annotation).render()
        )
        layout = self.Layout(**self.layout_context)
        for label, item in self.data.record(id):
            layout(self.format_item(label, item))
        display(HTML(layout.render()))

    def format_item(self, label, value):
        label  = normalize(label)
        value  = self.format_value(value)
        value  = self.highlight(self.truncate(value))
        kwargs = dict(label=label, value=value, maxheight=self.maxheight)
        return self.Item(**kwargs)


class DisplayText(ProtoDisplay):
    Layout    = element_factory(template_filename='basic_layout.txt')
    Tasks     = element_factory(template_filename='tasks.txt')
    Item      = element_factory(template_filename='_item.txt')
    Highlight = element_factory(template_filename='_highlight.txt')

    n_char    = len(Layout._snippets['_line_'])
    n_lbl_id  = len(Layout._snippets['_lbl_id_'])

    def __call__(self, id, *args, **kwargs):
        super().__call__(id, *args, **kwargs)
        indent_index = self.n_char - self.n_lbl_id - len(str(id))
        indent_user  = self.n_char - len(self.annotator.name)

        self.layout_context.update(
            tasks=self.Tasks(**self.task_context).render(),
            annotation=AnnotationDisplayText(self.annotation).render()
        )
        self.truncate = TruncaterText(
            length=self.n_char,
            tab=self.Layout._snippets['_tab_'],
            **kwargs
        )
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
        value  = self.format_value(value)
        value  = self.truncate(self.highlight(value), label)
        kwargs = dict(label=label, value=value)
        return self.Item(**kwargs)


class Display(ProtoDisplay):
    def __new__(self, *args, text_display=None, **kwargs):
        if not text_display:
            if JUPYTER:
                return DisplayJupyter(*args, **kwargs)
        return DisplayText(*args, **kwargs)
