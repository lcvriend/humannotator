# local
from humannotator.utils import Base, option
from humannotator.config import KEYS
from humannotator.display.display import Display
from humannotator.core.tasks import Invalid


class Interface(Base):
    def __init__(self, annotator, *args, **kwargs):
        self.annotator = annotator
        self.args = args
        self.kwargs = kwargs

    def __call__(self, id):
        display = Display(self.annotator, Exit.instruction, **self.kwargs)
        display.clear()
        annotation = []
        for task in self.annotator.annotations.tasks:
            error = None
            while True:
                display(id, task, error=error)
                user = input()
                display.clear()
                if user == Exit.character:
                    return Exit()
                user = task(user)
                if not isinstance(user, Invalid):
                    annotation.append(user)
                    break
                error = user.message
        return annotation


class Exit(object):
    character = KEYS.exit
    instruction = option(character, 'exit')
