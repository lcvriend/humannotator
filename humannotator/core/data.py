"""
This module contains the Data class. Currently only dataframes or data that
can be converted into a dataframe are accepted. In the future support for other
data types may be added.
"""


# standard library
from collections.abc import Sequence, Mapping

# third party
import pandas as pd

# local
from humannotator.utils import Base


registry = {}
def register(cls):
    registry[cls.kind] = cls
    return cls


class Data(Base):
    def __init__(self, data, **kwargs):
        try:
            self.data = data.copy()
        except AttributeError:
            self.data = data

    def __len__(self):
        return len(self.ids)

    def __getitem__(self, id):
        return self.data[id]

    def record(self, id):
        return [('item', self[id])]


@register
class Data_List(Data):
    kind = Sequence

    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)
        self.ids = list(range(0, len(data)))


@register
class Data_Dict(Data):
    kind = Mapping

    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)
        self.ids = data.keys()


@register
class Data_Series(Data):
    kind = pd.Series

    def __init__(self, data, **kwargs):
        super().__init__(data, **kwargs)
        self.ids = self.data.index


@register
class Data_DataFrame(Data):
    kind = pd.DataFrame

    def __init__(self, data, item_cols=None, id_col=None, **kwargs):
        super().__init__(data, **kwargs)
        if id_col:
            self.data = self.data.set_index(id_col)
        if item_cols is None:
            item_cols = self.data.columns
        elif not isinstance(item_cols, list):
            item_cols = [item_cols]
        self.item_cols = item_cols
        self.ids = self.data.index

    def __getitem__(self, id):
        return self.data.loc[id, self.item_cols]

    def record(self, id):
        return self[id].items()


def load_data(data, **kwargs):
    """Prepare data for the Annotator.

    Arguments
    ---------
    data : list-/dict-like, Series or DataFrame
    item_cols : str or list of str, default None
        Name(s) of dataframe column(s) to display when annotating.
        By default: display all columns.
    id_col : str, default None
        Name of dataframe column to use as index.
        By default: use the dataframe's index.

    Returns
    -------
    data:
        Data object that is used for annotating.
        The data itself will be converted to a dataframe.
    """

    if isinstance(data, list):
        data = pd.DataFrame(data).add_prefix('item_')
    elif isinstance(data, dict):
        data = pd.DataFrame(data.values(), data.index()).add_prefix('item_')
    elif isinstance(data, pd.Series):
        data = pd.DataFrame(data)

    for cls in registry.values():
        if isinstance(data, cls.kind):
            return cls(data, **kwargs)
    else:
        raise ValueError(
            f"Data type '{type(data).__name__}' is not supported. "
            "Data needs to be of one of the following types: "
            f"{[cls.kind.__name__ for cls in registry.values()]}."
        )
