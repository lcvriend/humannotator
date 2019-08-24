# standard library
import os

# third party
from markdown import markdown
from IPython.display import HTML, display, clear_output

# local
from humannotator.utils import Base
from humannotator.display.elements import element_factory
from humannotator.display.config import SETTINGS


def test_for_ipython():
    try:
        get_ipython()
        return True
    except NameError:
        return False


_Counter = element_factory(template_filename='_counter.txt')
LayOut_Txt = element_factory(template_filename='basic_layout.txt')
def clear():
    os.system('cls||echo -e \\\\033c')

JUPYTER = test_for_ipython()
if JUPYTER:
    LayOut_Html = element_factory(template_filename='basic_layout.html')
    def clear():
        clear_output()


class ProtoDisplay(Base):
    def __init__(self, annotator, instruction):
        self.annotator = annotator
        self.data = annotator.data
        self.instruction = instruction

    @property
    def counter(self):
        return _Counter(
            count=self.annotator.i+1,
            total=len(self.annotator.ids)
        ).render()

    @staticmethod
    def clear():
        clear()


class DisplayJupyter(ProtoDisplay):
    def __call__(self, id):
        output = LayOut_Html(
            annotator=self.annotator.name,
            item_id=id,
            item=self.data[id],
            instruction=markdown(self.instruction),
            counter=self.counter,
        ).render()
        display(HTML(output))


class DisplayText(ProtoDisplay):
    def __call__(self, id):
        n_char = len(max(LayOut_Txt._snippets.values(), key=len))
        n_lbl  = len(LayOut_Txt._snippets['_lbl_id_'])

        output = LayOut_Txt(
            annotator=self.annotator.name,
            item_id=id,
            item=self.data[id],
            instruction=self.instruction,
            counter=f"{self.counter:>{n_char-n_lbl-len(str(id))}}",
        ).render()
        print(output)


class Display(ProtoDisplay):
    def __new__(self, *args, text_display=None):
        if not text_display:
            if JUPYTER:
                return DisplayJupyter(*args)
        return DisplayText(*args)
