# local
from humannotator.utils import Base
from humannotator.annotations import Annotations, Annotation, Invalid


class Interface(Base):
    def __init__(self, annotations):
        self.annotations = annotations
        self._check_input_('annotations', self.annotations, Annotations)

    def __call__(self, id):
        annotation = Annotation()
        while True:
            instruction = '\n'.join(
                self.annotations.question.instruction,
                Stop.instruction
                )

            user = input()
            if user == Stop.character:
                return Stop()

            user = self.annotations.question(user)
            if not isinstance(user, Invalid):
                return annotation(user)


class Stop(object):
    character = '.'
    instruction = f"[{character}] - exit"
