# local
from humannotator.utils import Base, option
from humannotator.config import KEYS
from humannotator.display.display import Display
from humannotator.core.tasks import Invalid


class Interface(Base):
    """
    Interface
    =========
    - Receives and validates user input.
    - Interacts with the display.
    - Stores the annotations internally.
    - Exits; drops last row if unfinished.
    """

    def __init__(self, annotator, **kwargs):
        self.annotator = annotator
        self.annotations = annotator.annotations
        self.tasks = annotator.annotations.tasks
        self.data = annotator.annotations.data
        self.active = True
        self.kwargs = kwargs

    def __call__(self, id):
        display = Display(self.annotator, Exit.instruction, **self.kwargs)
        display.clear()
        for task in self.tasks:
            # check for dependencies
            if task.has_dependencies:
                check = False
                for i in task.dependencies:
                    if not self.data.loc[[id]].query(i.condition).empty:
                        self.annotations[(id, task.name)] = i.value
                        check = True
                        break
                if check:
                    continue

            # user input
            error = None
            while True:
                display(id, task, error=error)
                user = input()
                display.clear()
                if user == Exit.character:
                    self.data.drop(id, inplace=True, errors='ignore')
                    self.active = False
                    return None
                user = task(user)
                if not isinstance(user, Invalid):
                    break
                error = user.message
            self.annotations[(id, task.name)] = user
        return None


class Exit(object):
    character = KEYS.exit
    instruction = option(character, 'exit')
