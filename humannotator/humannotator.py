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
    """Annotator:
    - Stores the data to be annotated
    - Stores the annotation data
    - Provides an annotation interface
    Call to start annotating the data.
    Pass a list of ids to the call to annotate only a subset of the data.

    Attributes
    ----------
    name : str
        Name of the annotator.
    data : data
        Data to be annotated.
    annotations : annotations
        Object containing:
        - Annotation tasks
        - Annotation data
    """

    def __init__(self, data, tasks, *args, name='HUMANNOTATOR', **kwargs):
        """Create an annotator.

        arguments
        ---------
        data : data, list-/dict-like, Series or DataFrame
            Data to be annotated.
            If `data` is not already a data object,
            then it will be passed through `load_data`.
        tasks : task, list of task or DataFrame
            Annotation task(s).
            If passed a DataFrame, then the tasks will be inferred from it.
            Annotation data in the dataframe will also be initialized.
        name : str, default='HUMANNOTATOR'
            Name of the annotator.

        other parameters
        ----------------
        text_display : bool, default None
            If True will display the annotator in plain text instead of html.
        item_cols : str or list of str, default None
            Name(s) of dataframe column(s) to display when annotating.
            By default: display all columns.
        id_col : str, default None
            Name of dataframe column to use as index.
            By default: use the dataframe's index.

        returns
        -------
        annotator
        """

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
        if ids is None:
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
        "Dataframe with the stored annotations."
        return self.annotations.data

    def merged(self):
        "Return dataframe combining data and annotations."
        d = self.data.data.copy()
        a = self.annotated.copy()
        d.columns = pd.MultiIndex.from_product([['DATA'], d.columns])
        a.columns = pd.MultiIndex.from_product([['ANNOTATIONS'], a.columns])
        return d.merge(a, left_index=True, right_index=True)

    def save(self, filename):
        "Save the annotator with the pickle protocol."
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename):
        "Load an annotator from a pickle file."
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
