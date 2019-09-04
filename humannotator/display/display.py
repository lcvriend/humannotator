# standard library
import os
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

DEFAULTS = {
    'highlight_style': CSS.highlight[0],
}


class ProtoDisplay(Base):
    def __init__(self, annotator, exit_instruction, **kwargs):
        self.annotator = annotator
        self.data = annotator.data
        self.exit = exit_instruction
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
        items = (normalize('NFKD', item) for item in items)
        kwargs = dict(zip(['label', 'value'], items))
        kwargs['value'] = self.highlighter(kwargs['value'], **self.kwargs)
        return self.item_layout(**kwargs)

    def highlighter(self, item, highlight_text=None, **kwargs):
        context = dict(text=highlight_text)
        for key in kwargs:
            if key in self.highlight_template._fields:
                context[key] = kwargs[key]
        for key in self.highlight_template._fields:
            if key not in context:
                context[key] = DEFAULTS[key]
        if not highlight_text is None:
            item = item.replace(
                highlight_text,
                self.highlight_template(**context).render()
            )
        return item

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
