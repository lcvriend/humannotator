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
    - Navigates through the annotations.
    - Exits; drops last row if unfinished.
    """

    def __init__(self, annotator, **kwargs):
        self.annotator = annotator
        self.annotations = annotator.annotations
        self.tasks = annotator.annotations.tasks
        self.user = annotator.user
        self.kwargs = kwargs

    def __call__(self, ids):
        self.ids = ids
        rotation = {}
        for i, id in enumerate(self.ids):
            rotation[i] = id
            self.i = i

            while True:
                # check position
                self.first = True if self.i == 0 else False
                self.state = 'fresh' if self.i == i else 'stale'

                # run interface
                navigation = self._interface(id)

                # process navigation
                if isinstance(navigation, Previous):
                    if not self.i == 0:
                        self.i -= 1
                if isinstance(navigation, Next):
                    if self.i < i:
                        self. i += 1
                if isinstance(navigation, Continue):
                    break
                if isinstance(navigation, Exit):
                    return None
                id = rotation[self.i]

    def _interface(self, id):
        display = Display(self.annotator, self, **self.kwargs)
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

                if user_input in NAVIGATION:
                    if self.state == 'fresh':
                        self.annotations.data.drop(
                            id,
                            inplace=True,
                            errors='ignore',
                        )
                    return NAVIGATION[user_input]
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

    def get_instruction(self):
        if self.state == 'fresh' and self.first:
            return Exit.instruction
        elif self.state == 'fresh' and not self.first:
            return ' '.join([Exit.instruction, Previous.instruction])
        elif self.state == 'stale' and self.first:
            return ' '.join([Exit.instruction, Next.instruction])
        else:
            return ' '.join([nav.instruction for nav in NAV_CLASSES])


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


NAV_CLASSES = [Exit, Previous, Next]
NAVIGATION = {nav.character:nav() for nav in NAV_CLASSES}
