# standard library
import os
from unicodedata import normalize

# third party
from markdown import markdown
from IPython.display import HTML, display, clear_output

# local
from humannotator.utils import Base
from humannotator.display.elements import element_factory


def test_for_ipython():
    try:
        get_ipython()
        return True
    except NameError:
        return False

_Counter = element_factory(template_filename='_counter.txt')
Layout_Txt = element_factory(template_filename='basic_layout.txt')
def clear():
    os.system('cls||echo -e \\\\033c')

JUPYTER = test_for_ipython()
if JUPYTER:
    Layout_Html = element_factory(template_filename='basic_layout.html')
    def clear():
        clear_output()


class ProtoDisplay(Base):
    def __init__(self, annotator, exit_instruction):
        self.annotator = annotator
        self.data = annotator.data
        self.exit = exit_instruction

    def __call__(self, id, task, error=None):
        self.task_counter = _Counter(count=task.pos+1, total=task.of).render()
        self.kwargs = {
            'annotator':  self.annotator.name,
            'task_count': self.task_counter,
            'task_name':  task.name,
            'task_type':  task.kind,
            'item_id':    id,
            'error':      error if error else '',
        }

    def _create_items(self, items):
        items = (normalize('NFKD', item) for item in items)
        kwargs = dict(zip(['label', 'value'], items))
        return self._item_layout(**kwargs)

    @property
    def index_counter(self):
        return _Counter(
            count=self.annotator.i+1,
            total=len(self.annotator.ids)
        ).render()

    @staticmethod
    def clear():
        clear()


class DisplayJupyter(ProtoDisplay):
    _item_layout = element_factory(template_filename='_item.html')

    def __call__(self, id, task, **kwargs):
        super().__call__(id, task, **kwargs)
        layout = Layout_Html(
            **self.kwargs,
            instruction=markdown(task.instruction + self.exit),
            index_count=self.index_counter,
        )
        for items in self.data[id].items():
            layout(self._create_items(items))
        display(HTML(layout.render()))


class DisplayText(ProtoDisplay):
    _item_layout = element_factory(template_filename='_item.txt')

    def __call__(self, id, task, **kwargs):
        super().__call__(id, task, **kwargs)
        n_char = len(max(Layout_Txt._snippets.values(), key=len))
        n_lbl  = len(Layout_Txt._snippets['_lbl_id_'])
        layout = Layout_Txt(
            **self.kwargs,
            instruction=task.instruction + self.exit,
            index_count=f"{self.index_counter:>{n_char-n_lbl-len(str(id))}}",
        )
        for items in self.data[id].items():
            layout(self._create_items(items))
        print(layout.render())


class Display(ProtoDisplay):
    def __new__(self, *args, text_display=None):
        if not text_display:
            if JUPYTER:
                return DisplayJupyter(*args)
        return DisplayText(*args)

    def __call__(self):
        pass
