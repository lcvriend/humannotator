# standard library
from collections.abc import Iterable, Mapping, Hashable, Sequence

# third party
import pandas as pd

# local
from humannotator.utils import Base


class Task(Base):
    def __init__(self, instruction=None):
        self._instruction = instruction

    def __call__(self, value):
        "Validate value."
        return value

    def __key(self):
        return (self._instruction)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Task):
            return self.__key() == other.__key()
        return NotImplemented

    @property
    def instruction(self):
        return self._instruction

    @instruction.setter
    def instruction(self, instruction):
        self._instruction = instruction


class Task_MultipleChoice(Task):
    def __init__(self, choices, **kwargs):
        super().__init__(**kwargs)
        self.choices = Choices(choices)

    def __key(self):
        return (self._instruction, self.choices.ordered_items())

    @property
    def instruction(self):
        instruction = list()
        if self._instruction:
            instruction.append(self._instruction)
        for choice in self.choices:
            instruction.append(f"[{choice}] - {self.choices[choice]}")
        return '  \n'.join(instruction)

    def __call__(self, value):
        value = super().__call__(value)
        if not value in self.choices:
            value = Invalid()
        return value


class Choices(Base):
    def __init__(self, choices):
        if not isinstance(choices, Mapping):
            choices = {i:i for i in choices}
        if not all((isinstance(value, Hashable) for value in choices.values())):
            raise ValueError(
                "All values in choices must be hashable."
            )
        self.__dict__.update(choices)

    def __iter__(self):
        for key in self.__dict__:
            yield getattr(self, key)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __len__(self):
        return len(self.__dict__)

    def ordered_items(self):
        return tuple((key, self[key]) for key in sorted(self.__dict__))


class Invalid(object):
    pass
