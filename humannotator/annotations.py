
# local
from humannotator.utils import Base


class Question(Base):
    def __init__(self, instruction=None):
        self._instruction = instruction

    def __call__(self, value):
        return value

    @property
    def instruction(self):
        return self._instruction

    @instruction.setter
    def instruction(self, instruction):
        self._instruction = instruction


class Question_MultipleChoice(Question):
    def __init__(self, choices, **kwargs):
        super().__init__(**kwargs)
        self.choices = choices
        self._check_input_('choices', self.choices, dict)

    @property
    def instruction(self):
        instruction = list()
        if self._instruction:
            instruction.append(self._instruction)
        for choice in self.choices:
            instruction.append(f"[{choice}] - {self.choices[choice]}")
        return '\n'.join(instruction)

    def __call__(self, value):
        value = super().__call__(value)
        if not value in self.choices:
            value = Invalid()
        return value


class Annotations(Base):
        self.question = question
        self._check_input_('question', self.question, Question)

    def _check_input_(self):
        if not isinstance(self.question, Question):
            raise TypeError(
                f"`question` must be of type {Question}."
                )

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        value = self.question(value)
        self._value = value


class Invalid(object):
    pass
