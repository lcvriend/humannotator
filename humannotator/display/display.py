# standard library
import os

# third party
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


class ProtoDisplay(Base):
    line = '=' * 36
    tab  = ' ' * SETTINGS.n_tabs

    def __init__(self, annotator, instruction):
        self.annotator = annotator.name
        self.data = annotator.data
        self.instruction = instruction

    def __call__(self, id):
        to_screen = [
            f"{self.annotator}",
            self.line,
            f"id: {id}",
            'item:',
            f"{self.tab}{self.data[id]}",
            self.line,
            self.instruction,
        ]
        output = '\n'.join(to_screen)
        print(output)


JUPYTER = test_for_ipython()


if JUPYTER:
    class Display(ProtoDisplay):
        @staticmethod
        def clear():
            clear_output()

else:
    class Display(ProtoDisplay):
        @staticmethod
        def clear():
            os.system('cls||echo -e \\\\033c')
