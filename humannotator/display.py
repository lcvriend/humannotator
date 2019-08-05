# standard library
import os

# third party
from IPython.display import HTML, display, clear_output

# local
from humannotator.utils import Base


def test_for_ipython():
    try:
        get_ipython()
        return True
    except NameError:
        return False


JUPYTER = test_for_ipython()


class Display(Base):
    line = '=' * 36
    tab  = ' ' * 4

    def __init__(self, data, instruction):
        self.data = data
        self.instruction = instruction

    def __call__(self, id):
        to_screen = [
            f"id: {id}",
            'element:',
            f"{self.tab}{self.data(id)}",
            self.line,
            self.instruction,
        ]
        output = '\n'.join(to_screen)
        print(output)

    @staticmethod
    def clear():
        if JUPYTER:
            clear_output()
        else:
            os.system('cls||echo -e \\\\033c')
