# third party
import pandas as pd

# local
from humannotator.utils import Base
from humannotator.core.tasks import registry, task_factory


class Annotations(Base):
    def __init__(self, tasks):
        if not isinstance(tasks, list):
            tasks = [tasks]
        for idx, task in enumerate(tasks):
            setattr(task, 'pos', idx)
            setattr(task, 'of', len(tasks))
        self.tasks = tasks
        dtypes = {task.name:task.dtype for task in tasks}
        dtypes.update({'timestamp': 'datetime64[ns]'})
        self.data = pd.concat(
            [pd.DataFrame(columns=dtypes.keys()),
            pd.DataFrame(columns=['timestamp'])],
            sort=False,
        ).astype(dtypes)

    @property
    def ntasks(self):
        return len(self.tasks)

    @property
    def instructions(self):
        return [task.instruction for task in self.tasks]

    def __setitem__(self, id, values):
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

    @classmethod
    def from_df(cls, df, **kwargs):
        supported_dtypes = [item.dtype for item in registry.values()]
        df = convert_dtypes(df).select_dtypes(include=supported_dtypes)
        if 'timestamp' not in df.columns:
            df['timestamp'] = pd.Series(index=df.index, dtype='datetime64[ns]')
        tasks = cls.tasks_from_df(
            df.drop('timestamp', axis=1, errors='ignore'), **kwargs
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
