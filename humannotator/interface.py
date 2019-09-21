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
        self.user = annotator.user
        self.active = True
        self.kwargs = kwargs

    def __call__(self, ids):
        self.ids = ids
        rotation = {}
        for i, id in enumerate(self.ids):
            rotation[i] = id
            self.i = i
            self.active = True
            while True:
                navigation = self._interface(id)
                if isinstance(navigation, Previous):
                    self.active = False
                    if not self.i == 0:
                        self.i -= 1
                if isinstance(navigation, Next):
                    if not self.i > i:
                        self.active = False
                        self. i += 1
                    else:
                        self.active = True
                if isinstance(navigation, Continue):
                    break
                if isinstance(navigation, Exit):
                    break
                id = rotation[self.i]
            if isinstance(navigation, Exit):
                break

    def _interface(self, id):
        display = Display(self.annotator, self, nav_instructions, **self.kwargs)
        display.clear()
        for task in self.tasks:
            if task.has_dependencies:
                if self._process_dependencies(id, task):
                    continue

            # user input
            error = None
            while True:
                display(id, task, error=error)
                user_input = input()
                display.clear()

                if user_input in navigation:
                    if self.active:
                        self.annotations.data.drop(
                            id, inplace=True, errors='ignore'
                        )
                    return navigation[user_input]
                user_input = task(user_input)
                if not isinstance(user_input, Invalid):
                    break
                error = user_input.message
            self.annotations[(id, task.name)] = user_input
        else:
            if self.user:
                self.annotations[(id, 'user')] = self.user
        return Continue()

    def _process_dependencies(self, id, task):
        for i in task.dependencies:
            try:
                df = self.annotations.data.loc[[id]]
                if not df.query(i.condition).empty:
                    self.annotations[(id, task.name)] = task(i.value)
                    return True
            except KeyError:
                return False
        return False


class Exit(object):
    character = KEYS.exit
    instruction = option(character, 'exit', newline=False)


class Previous(object):
    character = KEYS.prev
    instruction = option(character, 'previous', newline=False)


class Next(object):
    character = KEYS.next
    instruction = option(character, 'next',)


class Continue(object):
    pass


nav_classes = [Exit, Previous, Next]
navigation = {nav.character:nav() for nav in nav_classes}
nav_instructions = ' '.join([nav.instruction for nav in nav_classes])
