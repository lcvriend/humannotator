"""
This module is the main access point to the humannotator. The Annotator class
connects the data, annotations and tasks to the user interface and display.
"""


# standard library
import pickle

# third party
import pandas as pd

# local
from humannotator.utils import Base
from humannotator.interface import Interface
from humannotator.core.annotations import Annotations
from humannotator.core.data import Data, load_data


class Annotator(Base):
    """
    Annotator
    =========
    - Stores the data to be annotated
    - Stores the annotation data
    - Provides an annotation interface

    Call to start annotating the data.
    - Pass a list of ids to annotate only a subset of the data.
    - Pass a user to change the user.
    - Set redo to True, to reannotate previously annotated items..`

    Attributes
    ----------
    name : str
        Name of the annotator.
    data : data
        Data to be annotated.
    user : str
        Name of user.
    tasks : Tasks
        - Annotation tasks
    annotations : Annotations
        Object containing:
        - Annotation tasks
        - Annotation data
    annotated : DataFrame
        Annotation data.
    unannotated : list
        Indeces to the unannotated records.
    merged : DataFrame
        Table merging data and annotations.
    """

    def __init__(
        self,
        data=None,
        tasks=None,
        user=None,
        name='HUMANNOTATOR',
        save_data=False,
        **kwargs
    ):
        """Create an annotator.

        arguments
        ---------
        tasks : Task, list of Task objects, Tasks, Annotations or DataFrame
            Annotation task(s).
            If passed a DataFrame, then the tasks will be inferred from it.
            Annotation data in the dataframe will also be initialized.
        data : data, list-/dict-like, Series or DataFrame, default None
            Data to be annotated.
            If `data` is not already a data object,
            then it will be passed through `load_data`.
            The annotator can be instantiated without data,
            but will only work after data is loaded.
        user : str, default None
            Name of the user.
        name : str, default 'HUMANNOTATOR'
            Name of the annotator.
        save_data : boolean, default False
            Set flag to True if you want to store the data with the annotator.
            This will ensure that the pickled object, will contain the data.

        other parameters
        ----------------
        DISPLAY
        text_display : boolean, default None
            If True will display the annotator in plain text instead of html.
        escape_html : boolean, default False
            If true will escape html content within items.

        DATA
        item_cols : str or list of str, default None
            Name(s) of dataframe column(s) to display when annotating.
            By default: display all columns.
        id_col : str, default None
            Name of dataframe column to use as index.
            By default: use the dataframe's index.

        HIGHLIGHTER
        phrases : str, list of str, default None
            Phrases to highlight in the display.
            The phrases can be regexes.
            It also to pass in a dict where:
            - the keys are the phrases
            - the values are the css styling
        escape : boolean, default False
            Set escape to True in order to escape the phrases.
        flags : int, default 0 (no flags)
            Flags to pass through to the re module, e.g. re.IGNORECASE.

        TRUNCATER
        truncate : boolean, default True
            Set to False to not truncate items.
        trunc_limit : int,
            The number of words beyond which an item will be truncated.

        returns
        -------
        annotator
        """

        self.kwargs = kwargs
        self.user = user
        self.name = name
        self.annotations = tasks
        self.data = data
        self.save_data = save_data

    def __call__(self, ids=None, user=None, redo=False, **kwargs):
        """Run the annotator.

        Arguments
        ---------
        ids : list of ids, default None
            A list of ids to annotate.
            If none are passed than all ids are used.
        user : str, default None
            Name of the user to register the annotations under.
            By default the user (if any) will be used that was passed
            when instantiating the annotator.
        redo : boolean, default False
            Set to True to not skip previously annotated items.
        """

        if user:
            self.user = user
        if self.data is None:
            return None
        kwargs.update(self.kwargs)
        if isinstance(ids, (str, int)):
            ids = [ids]
        if ids is None:
            ids = self._data.ids

        # skip annotated ids, unless redo is True
        if not redo:
            ids = [
                id for id in ids
                if id not in self.annotations.data.index
            ]

        interface = Interface(self, **kwargs)
        interface(ids)

    def __getstate__(self):
        state = self.__dict__.copy()
        if not self.save_data:
            del state['_data']
        return state

    def __setstate__(self, state):
        if '_data' not in state:
            state['_data'] = None
        self.__dict__.update(state)

    @property
    def data(self):
        "Data to be annotated."
        if self._data is None:
            print(
                "NO DATA LOADED\n"
                "==============\n"
                "Load the data first by assigning it "
                "to the `data` property of the annotator."
            )
            return None
        return self._data.data

    @data.setter
    def data(self, data):
        if data is None:
            self._data = None
        elif not isinstance(data, Data):
            self._data = load_data(data, **self.kwargs)
        else:
            self._data = data

    @property
    def annotations(self):
        "Container for the task definitions and annotation data."
        return self._annotations

    @annotations.setter
    def annotations(self, tasks):
        if isinstance(tasks, Annotations):
            self._annotations = tasks
        elif isinstance(tasks, pd.DataFrame):
            self._annotations = Annotations.from_df(tasks)
        else:
            self._annotations = Annotations(tasks)

    @property
    def tasks(self):
        return self.annotations.tasks

    @tasks.setter
    def tasks(self, tasks):
        self.annotations.tasks = tasks

    @property
    def annotated(self):
        "Dataframe with the stored annotations."
        return self.annotations.data

    @property
    def unannotated(self):
        "The indeces to the records that have not been annotated."
        return [
            id for id in self.data.index
            if id not in self.annotations.data.index
        ]

    def merged(self):
        "Return dataframe combining data and annotations."
        if self.data is None:
            return None
        d = self.data.copy()
        a = self.annotated.copy()
        d.columns = pd.MultiIndex.from_product([['DATA'], d.columns])
        a.columns = pd.MultiIndex.from_product([['ANNOTATIONS'], a.columns])
        return d.merge(a, how='left', left_index=True, right_index=True)

    def save(self, filename):
        "Save the annotator with the pickle protocol. "
        "If save_data is True, then data will be stored with the annotator."
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename):
        "Load an annotator from a pickle file. "
        "If save_data is False, then data needs to be loaded in separately."
        with open(filename, 'rb') as f:
            return pickle.load(f)


if __name__ == '__main__':
    import pandas as pd
    from humannotator import Annotator, task_factory, load_data

    # load data
    url = 'https://raw.githubusercontent.com/lcvriend/humannotator/master/examples/news.csv'
    df = pd.read_csv(url, index_col=0)
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
