# local
import warnings

# third party
import pandas as pd

# local
from humannotator.utils import Base
from humannotator.core.tasks import registry, task_factory, Task


class Annotations(Base):
    def __init__(self, tasks=None, dependencies=None):
        self.tasks = Tasks(tasks)
        self.data = self._build_data_structure()

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
            if task not in self.tasks_from_df(self._data):
                df = self._build_data_structure()
                df = df.append(self._data, sort=False)
                self._data = df
                break

    @classmethod
    def from_df(cls, df, **kwargs):
        supported_dtypes = [item.dtype for item in registry.values()]
        df = convert_dtypes(df).select_dtypes(include=supported_dtypes)
        if 'timestamp' not in df.columns:
            df['timestamp'] = pd.Series(index=df.index, dtype='datetime64[ns]')
        if 'user' not in df.columns:
            df['user'] = None
        tasks = cls.tasks_from_df(
            df.drop(['timestamp', 'user'], axis=1, errors='ignore'), **kwargs
        )
        annotations = cls(tasks)
        annotations.data = df
        return annotations

    @staticmethod
    def tasks_from_df(df, instructions=None):
        args = []
        instructions = pd.Series(instructions, index=df.columns)
        tasks = pd.concat([df.dtypes, instructions], axis=1)
        tasks.columns = ['dtype', 'instruction']
        for task in tasks.itertuples():
            kwargs = {}
            name = task.Index
            for item in registry.values():
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


class Tasks(Base):
    def __init__(self, tasks=None):
        self.tasks = tasks

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

    @property
    def tasks(self):
        return self._tasks

    @tasks.setter
    def tasks(self, tasks):
        if tasks is None:
            self._tasks = {}
        else:
            if not isinstance(tasks, list):
                tasks = [tasks]
            self._tasks = {task.name:task for task in tasks}
            self._set_pos_in_tasks()

    @property
    def order(self):
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


def convert_dtypes(df):
    aliases = {
        alias:task.dtype
        for task in registry.values()
        for alias in task.alias if alias
    }
    conversions = {}
    for key in aliases:
        conversions.update(
            {col:aliases[key] for col in df.select_dtypes(key).columns}
        )
    return df.astype(conversions)
