# local
from humannotator.utils import Base
from humannotator.annotations import Annotations, Annotation, Invalid
from humannotator.display import Display


class Interface(Base):
    def __init__(self, data, annotations):
        self.data = data
        self.annotations = annotations
        self.instruction = '\n'.join([
            self.annotations.task.instruction,
            Stop.instruction,
            ])

    def __call__(self, id):
        annotation = Annotation()
        display = Display(self.data, self.instruction)
        while True:
            display(id)
            user = input()
            display.clear()
            if user == Stop.character:
                return Stop()

            user = self.annotations.task(user)
            if not isinstance(user, Invalid):
                return annotation(user)


class Stop(object):
    character = '.'
    instruction = f"[{character}] - exit"
