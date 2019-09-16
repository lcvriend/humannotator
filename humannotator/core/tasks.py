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
    """
    Task
    ====
    Defines an annotation task.
    Validates its input.

    Attributes
    ----------
    kind : str
        The kind of task.
    dtype : str
        String representing the pandas dtype in which the input will be stored.
    alias : list of str
        Aliases for the pandas dtype.
        Used when converting a DataFrame to a list of tasks.
    name : str
        Name of the task.
    instruction : str
        Instruction for the user.
    nullable : boolean, default False
        Whether the input can be null.
    dependencies : list of dependencies, default None
        Any dependencies associated with the task:
        - A dependency consists of a condition and a value.
        - The condition should be a valid pandas query statement.
        - The interface will check the condition before prompting the user.
        - If the condition is met, the value will be automatically assigned.
    has_dependencies : boolean
        True if there is at least one dependency, False otherwise.
    """
    alias = [None]

    def __init__(
        self,
        name,
        instruction=None,
        nullable=False,
        dependencies=None,
        **kwargs,
    ):

        self.name = name
        self.nullable = nullable
        self.instruction = instruction
        self.dependencies = dependencies

    @property
    def instruction(self):
        if self.nullable:
            return self._instruction + Null.instruction
        return self._instruction

    @instruction.setter
    def instruction(self, value):
        if value is None or value != value:
            self._instruction = ''
        else:
            self._instruction = value + '  \n'

    @property
    def invalid(self):
        "Message for when input is invalid."
        return f"Input cannot be parsed as {self.kind}."

    @property
    def dependencies(self):
        "Task dependencies."
        return self._dependencies

    @dependencies.setter
    def dependencies(self, dependencies):
        if dependencies is None:
            self._dependencies = []
        else:
            if isinstance(dependencies, Dependency):
                dependencies = [dependencies]
            elif isinstance(dependencies, tuple):
                dependencies = [Dependency(*dependencies)]
            dependencies = [
                i if isinstance(i, Dependency) else Dependency(*i)
                for i in dependencies
            ]
            for i in dependencies:
                self._validate_dependency(i)
            self._dependencies = dependencies

    def _validate_dependency(self, dependency):
        "Validate the dependency value."
        check = self(dependency.value)
        if isinstance(check, Invalid):
            raise ValueError(
                f"Dependency with condition '{dependency.condition}' "
                f"is associated with an invalid value. {check.message}"
            )

    @property
    def has_dependencies(self):
        "True if there is at least one dependency, False otherwise."
        if self.dependencies:
            return True
        return False

    def __call__(self, value):
        "Validate input."
        if self.nullable:
            if value == Null.character:
                return None
        return value

    def __eq__(self, other):
        if isinstance(other, Task):
            keys = ['pos', 'of']
            this = {k:v for k,v in self.__dict__.items() if k not in keys}
            that = {k:v for k,v in other.__dict__.items() if k not in keys}
            this.update(dtype=self.dtype)
            that.update(dtype=other.dtype)
            return this == that
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        states = {
            '1': 'True',
            '0': 'False',
        }
        items = ''.join(option(i,c) for i, c in states.items())
        if self._instruction:
            self._instruction = self._instruction + items
        else:
            self._instruction = items

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

    def __init__(self, *args, format='%Y-%m-%d', **kwargs):
        super().__init__(*args, **kwargs)
        self.format = format

    def __call__(self, value):
        value = super().__call__(value)
        try:
            value = datetime.strptime(value, self.format)
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
    dependencies : dependency or list of dependencies, default None
        A (list of) condition and value tuple(s) may also be passed.
        Condition:
        - should be a valid pandas query statement.
        - will be evaluated on the current annotation record.
        Value:
        - should be of the correct dtype.
        - will be assigned to the annotation task if the condition is True.

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


class Dependency(Base):
    def __init__(self, condition, value):
        self.condition = condition
        self.value     = value

    def __eq__(self, other):
        if isinstance(other, Dependency):
            return self.__dict__ == other.__dict__
        return NotImplemented
