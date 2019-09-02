# standard library
import pickle

# third party
import pandas as pd

# local
from humannotator.utils import Base
from humannotator.data.data import Data, load_data
from humannotator.interface import Interface, Exit
from humannotator.core.annotations import Annotations


class Annotator(Base):
    def __init__(self, data, tasks, *args, name='HUMANNOTATOR', **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

        if isinstance(tasks, pd.DataFrame):
            self.annotations = Annotations.from_df(tasks)
        else:
            self.annotations = Annotations(tasks)

        if not isinstance(data, Data):
            self.data = load_data(data, **kwargs)
        else:
            self.data = data

    def __call__(self, ids=None):
        if not ids:
            ids = self.data.ids
        self.ids = [
            id for id in ids
            if id not in self.annotations.data.index
        ]
        interface = Interface(self, *self.args, **self.kwargs)
        for i, id in enumerate(self.ids):
            self.i = i
            user = interface(id)
            if isinstance(user, Exit):
                break
            self.annotations[id] = user
        return None

    @property
    def annotated(self):
        return self.annotations.data

        d = self.data.data.copy()
        a = self.annotated.copy()
        d.columns = pd.MultiIndex.from_product([['DATA'], d.columns])
        a.columns = pd.MultiIndex.from_product([['ANNOTATIONS'], a.columns])
        return d.merge(a, left_index=True, right_index=True)

    def save(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)


if __name__ == '__main__':
    import sys
    import pandas as pd
    from humannotator import Annotator, task_factory, load_data
    sys.path.insert(0, '../')

    # load data
    df = pd.read_csv('examples/news.csv', index_col=0)
    data = load_data(df, item_cols=['title', 'date'], id_col='news_id')

    # define tasks
    choices={
        '0': 'not adverse media',
        '1': 'adverse media',
        '3': 'exclude from dataset',
    }
    instruct = "Is the topic political?"
    task1 = task_factory(choices, 'Adverse media')
    task2 = task_factory(
        'bool',
        'Political',
        instruction=instruct,
        nullable=True
    )

    # run annotator
    annotator = Annotator(data, [task1, task2])
    annotator(data.ids)
    print(annotator.annotated)
