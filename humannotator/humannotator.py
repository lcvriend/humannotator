# standard library
from collections import namedtuple

# local
from humannotator.utils import Base
from humannotator.data import Data
from humannotator.interface import Interface, Stop
from humannotator.annotations import Annotations, Annotation


class Annotator(Base):
    def __init__(self, data, annotations, name='HUMANNOTATOR'):
        self.name = name
        self.data = data
        self.annotations = annotations
        self._check_input_('data', self.data, Data)
        self._check_input_('annotations', self.annotations, Annotations)

    def __call__(self, ids):
        interface = Interface(self)
        for id in ids:
            if id in self.annotations.annotations.keys():
                continue
            user = interface(id)
            if isinstance(user, Stop):
                break
            if isinstance(user, Annotation):
                self.annotations[id] = user
        return None


if __name__ == '__main__':
    import sys
    import pandas as pd
    from humannotator.data import Data_DataFrame, Data
    from humannotator.annotations import Task_MultipleChoice, Annotations
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
