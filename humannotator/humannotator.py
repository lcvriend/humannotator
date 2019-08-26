# standard library
from collections import namedtuple

# local
from humannotator.utils import Base
from humannotator.data.data import Data
from humannotator.interface import Interface, Stop
from humannotator.core.annotations import Annotations, Annotation


class Annotator(Base):
    def __init__(self, data, annotations, *args, name='HUMANNOTATOR', **kwargs):
        self.name = name
        self.data = data
        self.annotations = annotations
        self._check_input('data', self.data, Data)
        self._check_input('annotations', self.annotations, Annotations)
        self.args = args
        self.kwargs = kwargs

    def __call__(self, ids):
        self.ids = [
            id for id in ids
            if id not in self.annotations.annotations.keys()
        ]
        interface = Interface(self, *self.args, **self.kwargs)
        for i, id in enumerate(self.ids):
            self.i = i
            user = interface(id)
            if isinstance(user, Stop):
                break
            if isinstance(user, Annotation):
                self.annotations[id] = user
        return None


if __name__ == '__main__':
    import sys
    import pandas as pd
    from humannotator.data.data import Data_DataFrame, Data
    from humannotator.core.annotations import Task_MultipleChoice, Annotations
    sys.path.insert(0, '../')

    df = pd.read_csv('examples/news.csv', index_col=0)
    data = Data_DataFrame(df, items_col='title', id_col='news_id')

    instruction = "Choose one of the following options:"
    choices={
        '0': 'not adverse media',
        '1': 'adverse media',
        '3': 'exclude from dataset'
        }

    task = Task_MultipleChoice(instruction=instruction, choices=choices)
    annotations = Annotations(task)
    annotator = Annotator(data, annotations)

    annotator(data.ids)

    print(annotator.annotations())
