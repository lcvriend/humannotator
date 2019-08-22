# local
from humannotator.utils import Base
from humannotator.annotations import Annotations, Annotation, Invalid
from humannotator.display.display import Display


class Interface(Base):
    def __init__(self, annotator):
        self.annotator = annotator
        self.validate = annotator.annotations.task
        self.instruction = '\n'.join([
            self.annotator.annotations.task.instruction,
            Stop.instruction,
            ])

    def __call__(self, id):
        annotation = Annotation()
        display = Display(self.annotator, self.instruction)
        display.clear()
        while True:
            display(id)
            user = input()
            display.clear()
            if user == Stop.character:
                return Stop()

            user = self.validate(user)
            if not isinstance(user, Invalid):
                return annotation(user)


class Stop(object):
    character = '.'
    instruction = f"[{character}] - exit"
