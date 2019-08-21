# standard library
from datetime import datetime

# local
from humannotator.utils import Base


class Task(Base):
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


class Task_MultipleChoice(Task):
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


class Annotation(object):
    def __call__(self, value):
        self.value = value
        self.timestamp = datetime.now()
        return self

    def __repr__(self):
        return f"Annotation(value: {self.value}, timestamp: {self.timestamp})"


class Invalid(object):
    pass
