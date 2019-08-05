# local
from humannotator.utils import Base


class Interface(Base):
        self._check_input_('annotations', self.annotations, Annotations)

    def _check_input_(self):
        if not isinstance(self.answer, Answer):
            raise TypeError(
                f"`answer` must be of type {Answer}."
                )

    def __call__(self):
        while True:
            print(f"\n{self.answer.question.instruction}\n{Stop.instruction}\n")
            user = input()
            if user == Stop.character:
                break

            user = self.answer.question(user)
            if not isinstance(user, Invalid):
                print(f"Annotation is success! Value is {user}")
                break


class Stop(object):
    character = '.'
    instruction = f"[{character}] - exit"
