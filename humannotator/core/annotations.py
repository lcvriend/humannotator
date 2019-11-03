"""
This module connects the annotation tasks and their results. The Annotations
class is the main container taking care of this. It contains the tasks to be
performed, as well as the storage for the annotations themselves. The tasks are
maintained and ordered in the Tasks class.
"""


# local
import warnings

# third party
import pandas as pd

# local
from humannotator.utils import Base
from humannotator.core.tasks import REGISTRY, task_factory, Task


class Annotations(Base):
    """
    Annotations
    ===========
    Stores the tasks to be performed.
    Collects the annotations from the user input.

    Attributes
    ----------
    tasks : Tasks object
    data : DataFrame
        df for storing the annotations.
        - Each task gets its own column.
        - Timestamp and user are stored with each annotation.
    """

    def __init__(self, tasks=None, dependencies=None):
        self.tasks = tasks
        self.data = self._build_data_structure()

    @property
    def tasks(self):
        return self._tasks

    @tasks.setter
    def tasks(self, tasks):
        if isinstance(tasks, Tasks):
            self._tasks = tasks
        else:
            self._tasks = Tasks(tasks)

    @property
    def data(self):
        self._check_data_structure()
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def ntasks(self):
        return len(self.tasks)

    @property
    def instructions(self):
        return [task.instruction for task in self.tasks]

    def __setitem__(self, id, value):
        now = pd.Timestamp('now')
        if isinstance(id, tuple):
            idx, task = id
            self.data.loc[idx, [task, 'timestamp']] = (value, now)
        else:
            values.append(pd.Timestamp('now'))
            annotation = pd.Series(values, index=self.data.columns, name=id)
            self.data = self.data.append(annotation)

    def __eq__(self, other):
        if isinstance(other, Annotations):
            return (
                self.data.equals(other.data) and
                self.tasks == other.tasks
            )
        return NotImplemented

    def _build_data_structure(self):
        dtypes = {task.name:task.dtype for task in self.tasks}
        dtypes.update({'timestamp': 'datetime64[ns]'})
        items = [
            pd.DataFrame(columns=dtypes.keys()),
            pd.DataFrame(columns=['timestamp']),
            pd.DataFrame(columns=['user']),
        ]
        return pd.concat(items, sort=False).astype(dtypes)

    def _check_data_structure(self):
        for task in self.tasks:
            if task not in Tasks.from_df(self._data):
                df = self._build_data_structure()
                df = df.append(self._data, sort=False)
                self._data = df
                break

    @classmethod
    def from_df(cls, df, **kwargs):
        supported_dtypes = [item.dtype for item in REGISTRY.values()]
        df = convert_dtypes(df).select_dtypes(include=supported_dtypes)
        if 'timestamp' not in df.columns:
            df['timestamp'] = pd.Series(index=df.index, dtype='datetime64[ns]')
        if 'user' not in df.columns:
            df['user'] = None
        tasks = Tasks.from_df(
            df.drop(['timestamp', 'user'], axis=1, errors='ignore'), **kwargs
        )
        annotations = cls(tasks)
        annotations.data = df
        return annotations


class Tasks(Base):
    """
    Tasks
    =====

    Class for storing tasks for annotation.
    - Tasks can be set and accessed through subscription.
    - Evaluates to False if no tasks are defined.
    - Numbers the tasks in order (used in the display).

    Attributes
    ----------
    tasks : dict of Task objects
        Dictionary containing all Task objects.
        - key: name of task
        - value: task
    order : dict of Task objects
        Dictionary containing all Task objects.
        - key: index
        - value: task
    """

    def __init__(self, tasks=None):
        self.tasks = tasks

    @property
    def tasks(self):
        "Tasks to be performed."
        return self._tasks

    @tasks.setter
    def tasks(self, tasks):
        if tasks is None:
            self._tasks = {}
        else:
            if isinstance(tasks, Task):
                tasks = [tasks]
            elif isinstance(tasks, pd.DataFrame):
                tasks = self.extract_tasks_from_df(tasks)

            if isinstance(tasks, list):
                assert all(isinstance(i, Task) for i in tasks)
                self._tasks = {task.name:task for task in tasks}
            else:
                assert all(isinstance(v, Task) for v in tasks.values())
                self._tasks = tasks
            self._set_pos_in_tasks()

    @property
    def order(self):
        "Order in which tasks are to be performed."
        return {idx:task for idx, task in enumerate(self.tasks.keys())}

    @order.setter
    def order(self, value):
        if all(isinstance(i, int) for i in value):
            value = [self.order[i] for i in value]
        self.tasks = {name:self.tasks[name] for name in value}

    def _set_pos_in_tasks(self):
        for position, task in self.order.items():
            setattr(self[task], 'pos', position)
            setattr(self[task], 'of', len(self))

    def __getitem__(self, id):
        return self.tasks[id]

    def __setitem__(self, id, value):
        if isinstance(value, Task):
            if id != value.name:
                warnings.warn(
                    f"The task name '{value.name}' "
                    f"does not match the id '{id}'. "
                    f"Task name is set to '{id}'."
                )
                value.name = id
        else:
            if isinstance(value, tuple):
                kind, *args, kwargs = value
                if isinstance(kwargs, dict):
                    value = task_factory(kind, id, *args, **kwargs)
                else:
                    value = task_factory(kind, id, *args, kwargs)
            else:
                value = task_factory(value, id)
        self.tasks[id] = value
        self._set_pos_in_tasks()

    def __len__(self):
        return len(self._tasks)

    def __iter__(self):
        yield from self.tasks.values()

    def __eq__(self, other):
        if isinstance(other, Tasks):
            return (
                self.tasks == other.tasks and
                self.order == other.order
            )
        return NotImplemented

    def __bool__(self):
        if self.tasks:
            return True
        else:
            return False

    def __str__(self):
        string = ''
        for task in self:
            string += f"{'task':<16}{task.pos}\n"
            string += str(task) + '\n'
        return string

    def __repr__(self):
        return str(self)

    @classmethod
    def from_df(cls, df, instructions=None):
        return cls(cls.extract_tasks_from_df(df, instructions=instructions))

    @staticmethod
    def extract_tasks_from_df(df, instructions=None):
        """
        Extract tasks from dataframe by inferring task kind from dtypes.
        Instructions may be passed as a separate list.

        Limitations:
        - The str and regex tasks have the same dtype (object).
        - When introducing NA the dtype may have been promoted.
            This happens to boolean tasks that are nullable.
            The incorrect inference will be made that the task is str.
            See: https://pandas.pydata.org/pandas-docs/stable/user_guide/gotchas.html#na-type-promotions
        """

        args = []
        instructions = pd.Series(instructions, index=df.columns)
        tasks = pd.concat([df.dtypes, instructions], axis=1)
        tasks.columns = ['dtype', 'instruction']
        for task in tasks.itertuples():
            kwargs = {}
            name = task.Index
            for item in REGISTRY.values():
                if item.dtype == task.dtype.name:
                    kind = item.kind
                    if kind == 'category':
                        kwargs['categories'] = task.dtype.categories
                    break
            kwargs['instruction'] = task.instruction
            args.append((kind, name, kwargs))
        return [
            task_factory(kind, name, **kwargs)
            for kind, name, kwargs in args
        ]


def convert_dtypes(df):
    aliases = {
        alias:task.dtype
        for task in REGISTRY.values()
        for alias in task.alias if alias
    }
    conversions = {}
    for key in aliases:
        conversions.update(
            {col:aliases[key] for col in df.select_dtypes(key).columns}
        )
    return df.astype(conversions)
