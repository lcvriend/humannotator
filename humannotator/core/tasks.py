# local
import re
from collections.abc import Mapping
from datetime import datetime
from warnings import warn

# third party
import pandas as pd
from pandas import CategoricalDtype

# local
from humannotator.config import BOOLEAN_STATES, KEYS
from humannotator.utils import Base, option


registry = {}
def register(cls):
    registry[cls.kind] = cls
    return cls


class Invalid(object):
    def __init__(self, msg=None):
        self.message = msg


class Null(object):
    character = KEYS.none
    instruction = option(character, 'none')


class Task(Base):
    alias = [None]

    def __init__(self, name, *args, instruction=None, nullable=False, **kwargs):
        self.name = name
        self.nullable = nullable
        if not instruction:
            self._instruction = instruction
        else:
            self._instruction = instruction + '  \n'

    @property
    def instruction(self):
        instruction = self._instruction
        if not instruction:
            instruction = ''
        if self.nullable:
            return instruction + Null.instruction
        return instruction

    @instruction.setter
    def instruction(self, value):
        self._instruction = value

    @property
    def invalid(self):
        return f"Input cannot be parsed as {self.kind}."

    def __call__(self, value):
        if self.nullable:
            if value == Null.character:
                return None
        return value

    def __eq__(self, other):
        if isinstance(other, Task):
            return self.__dict__ == other.__dict__
        return NotImplemented


@register
class Task_str(Task):
    kind = 'str'
    dtype = 'object'

    def __call__(self, value):
        value = super().__call__(value)
        if value:
            try:
                value = str(value)
            except ValueError:
                return Invalid(self.invalid)
        return value


@register
class Task_regex(Task):
    kind = 'regex'
    dtype = 'object'

    def __init__(self, *args, regex, flags=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.regex = re.compile(regex, flags=flags)

    @property
    def invalid(self):
        return f"Input does not match pattern '{self.regex}'."

    def __call__(self, value):
        value = super().__call__(value)
        if not re.fullmatch(self.regex, value):
            return Invalid(self.invalid)
        return value


@register
class Task_int(Task):
    kind = 'int'
    dtype = 'Int64'
    alias = ['int32', 'int64']

    def __call__(self, value):
        value = super().__call__(value)
        if value:
            try:
                value = int(value)
            except ValueError:
                return Invalid(self.invalid)
        return value


@register
class Task_float(Task):
    kind = 'float'
    dtype = 'float64'

    def __call__(self, value):
        value = super().__call__(value)
        if value:
            try:
                value = float(value)
            except ValueError:
                return Invalid(self.invalid)
        return value


@register
class Task_bool(Task):
    kind = 'bool'
    dtype = 'bool'

    def __call__(self, value):
        value = super().__call__(value)
        if value:
            try:
                value = BOOLEAN_STATES[value.lower()]
            except KeyError:
                return Invalid(self.invalid)
        return value


@register
class Task_category(Task):
    kind = 'category'
    dtype = 'category'

    def __init__(self, *args, categories=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(categories, Mapping):
            categories = {str(i):c for i, c in enumerate(categories, start=1)}
        self.categories = categories
        self.dtype = CategoricalDtype(self.categories.values(), ordered=None)
        items = ''.join(option(i,c) for i, c in categories.items())
        if self._instruction:
            self._instruction = self._instruction + items
        else:
            self._instruction = items

    @property
    def invalid(self):
        return f"Input not in categories {list(self.categories.keys())}."

    def __call__(self, value):
        value = super().__call__(value)
        if not value in self.categories:
            return Invalid(self.invalid)
        return self.categories[value]


@register
class Task_date(Task):
    kind = 'date'
    dtype = 'datetime64[ns]'

    def __init__(self, format='%Y-%m-%d', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format = format

    def __call__(self, value):
        value = super().__call__(value)
        try:
            value = datetime.strptime(value, format)
        except ValueError:
            return Invalid(self.invalid)
        return value


def task_factory(kind, *args, **kwargs):
    """Create a specification for an annotation task.
    The specification contains:
    - the task name.
    - the dtype in which the annotation should be stored.
    - the method for validating the annotation input.
    - an instruction (optional)

    Arguments
    ---------
    kind : str, list- or dict-like
        Kind of task. Options are:
            'str' :      String
            'regex' :    Regex validated string
            'int' :      Integer
            'float' :    Float
            'bool' :     Boolean
            'category' : Category
            'date' :     Date
        If `kind` is list-/dict-like, then categories will be inferred from it.
    name : str
        Task name (used as column name in the annotations dataframe).
    instruction : str, default None
        Instruction to be displayed for this task.
    nullable : bool, default False
        If True then the annotation input can be None.

    Other parameters
    ----------------
    regex : str
        Required regex for validating input string if task kind is 'regex'.
    flags : int, default 0 (no flags)
        Flags to pass through to the re module, e.g. re.IGNORECASE.
    categories : list- or dict-like, default None
        Valid categories if task kind is 'category'.
        If a list is passed, then categories are numbered starting from '1'.
        If a dict is passed, then keys are used for validating input.
    format: str, default '%Y-%m-%d'
        Date format for validating input string if task kind is 'date'.
        Default: '%Y-%m-%d'

    Returns
    -------
    task
        Specification of the annotation task.

    Warns
    -----
        If `kind` is list-/dict-like and `categories` is not None.
        Task will be created from list-/dict-like and categories are ignored.
    """

    if isinstance(kind, str):
        if kind not in registry:
            raise KeyError(
                f"Unrecognized task type '{kind}'. "
                f"Choose from: {registry.keys()}."
            )
    else:
        if 'categories' in kwargs:
            warn(
                "Building categories from iterable passed to `kind`. "
                "Therefore, whatever was passed to `categories` "
                "will be ignored."
            )
        kwargs['categories'] = kind
        kind = 'category'

    return registry[kind](*args, **kwargs)
