# standard library
from collections.abc import Mapping
from datetime import datetime

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

    @property
    def instruction(self):
        return self._instruction

    @instruction.setter
    def instruction(self, instruction):
        self._instruction = instruction


class Task_MultipleChoice(Task):
    def __init__(self, choices, **kwargs):
        super().__init__(**kwargs)
        self.choices = choices
        self._check_input_('choices', self.choices, Mapping)

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


class Annotations(Base):
    def __init__(self, task, annotations=None):
        self.task = task
        self.annotations = dict() if annotations is None else annotations
        self._check_input_('task', self.task, Task)

    def __call__(self):
        return self.annotations

    def __getitem__(self, id):
        return self.annotations[id]

    def __setitem__(self, id, value):
        self.annotations[id] = value

    def to_dataframe(self):
        return pd.DataFrame.from_dict(self.annotations, orient='index')

    @classmethod
    def from_dataframe(cls, df, task=None):
        annotations = dict()
        for tup in df.itertuples():
            annotations[tup.Index] = Annotation(
                value=tup.value, timestamp=tup.timestamp
            )
        if not task:
            task = Task()
        return cls(task, annotations=annotations)


class Annotation(Mapping):
    def __init__(self, value=None, timestamp=None):
        self.value = value
        self.timestamp = timestamp

    def __call__(self, value):
        self.value = value
        self.timestamp = datetime.now()
        return self

    def __repr__(self):
        items = ', '.join('{}={!r}'.format(*i) for i in self.__dict__.items())
        return f"{self.__class__.__name__}({items})"

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        yield from self.__dict__.keys()

    def __len__(self):
        return len(self.__dict__)


class Invalid(object):
    pass
