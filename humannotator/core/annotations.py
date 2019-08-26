# standard library
from collections.abc import Iterable, Mapping, Hashable, Sequence

# third party
import pandas as pd

# local
from humannotator.utils import Base
from humannotator.core.tasks import Task


class Annotations(Base):
    def __init__(self, tasks, annotations=None):
        if not isinstance(tasks, list):
            tasks = [tasks]
        self.tasks = tasks
        for task in self.tasks:
            self._check_input('task', task, Task)
        self.data = dict() if annotations is None else annotations

    def __call__(self):
        return self.data

    def __getitem__(self, id):
        return self.data[id]

    def __setitem__(self, id, annotation):
        self._check_input('annotation', annotation, Annotation)
        self.data[id] = annotation

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


class Annotation(Base):
    def __init__(self, tasks):
        if not isinstance(tasks, list):
            tasks = [tasks]
        for task in tasks:
            self._check_input('task', task, Task)
        self.__dict__.update(dict.fromkeys(tasks))

    def __getitem__(self, idx):
        key = self.__dict__.keys()[idx]
        return key, self.__dict__[key]

    def __call__(self, id, data):
        if isinstance(data, Sequence):
            data = dict(zip(self.__dict__.keys(), data))
        if not data.keys() == self.__dict__.keys():
            raise ValueError(
                "Mismatch between annotation data and annotation tasks."
            )
        if not all(isinstance(i, Datum) for i in data.values()):
            raise ValueError(
                "All annotation data must be of type Datum"
            )
        self.__dict__.update(data)

    def __len__(self):
        return len(self.__dict__)


class Datum(object):
    __slots__ = ('value', 'timestamp')

    def __init__(self, value=None, timestamp=None):
        self.value     = value
        self.timestamp = timestamp

    def __call__(self, value):
        self.value     = value
        self.timestamp = pd.Timestamp('now')
        return self

    def __repr__(self):
        items = (f"{i}={getattr(self, i)!r}" for i in self.__slots__)
        return f"{self.__class__.__name__}({', '.join(items)})"
