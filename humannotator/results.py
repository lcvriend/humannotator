# local
from src.interface import Invalid, Stop


class Question(object):
    def __init__(self, instruction):
        self.instruction = instruction

    def __call__(self, value):
        value = _check_stop_(value)
        return value

    def _check_stop_(self, value):
        if value == Stop.character:
            return Stop()
        return value


class Question_MultipleChoice(Question):
    def __init__(self, choices):
        super().__self__()
        self.choices = choices

    def __call__(self, value):
        value = super().__call__(value)
        if not isinstance(value, Stop) and not value in choices:
            value = Invalid()
        return value


class Answer(object):
    def __init__(self, question):
        self.question = question
        self._value = None
        self._check_input_()

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
