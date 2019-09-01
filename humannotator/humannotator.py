# standard library
from collections import namedtuple

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

    def __call__(self, ids):
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




if __name__ == '__main__':
    import sys
    import pandas as pd
    from humannotator import Annotator, task_factory, load_data
    sys.path.insert(0, '../')

    df = pd.read_csv('examples/news.csv', index_col=0)
    data = load_data(df, items_cols=['title', 'date'], id_col='news_id')

    instruction = "Choose one of the following options:"
    choices={
        '0': 'not adverse media',
        '1': 'adverse media',
        '3': 'exclude from dataset'
    }
    task1 = task_factory(
        'category',
        'Choice',
        instruction=instruction,
        categories=choices)
    task2 = task_factory('bool', 'Relevant', instruction="State if the article is relevant")

    annotations = Annotations([task1, task2])
    annotator = Annotator(data, annotations)

    annotator(data.ids)
    print(annotator.annotatiosn.data)
