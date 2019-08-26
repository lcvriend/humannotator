# standard library
from collections.abc import Iterable, Collection, Mapping

# third party
import pandas as pd

# local
from humannotator.utils import Base


class Data(Base):
    data_type = Iterable

    def __init__(self, data):
        try:
            self.data = data.copy()
        except AttributeError:
            self.data = data
        self._check_input('data', self.data, self.data_type)
        self.ids = None
        self.items = data

    def __len__(self):
        return len(self.ids)


class Data_List(Data):
    data_type = Collection

    def __init__(self, data):
        super().__init__(data)
        self.ids = list(range(0, len(data)))
        self.items = data


class Data_Dict(Data):
    data_type = Mapping

    def __init__(self, data):
        super().__init__(data)
        self.ids = data.keys()
        self.items = data.values()


class Data_DataFrame(Data):
    data_type = pd.DataFrame

    def __init__(self, data, items_col, id_col=None):
        super().__init__(data)
        if id_col:
            self.data = self.data.set_index(id_col)
        self.items_col = items_col
        self.ids = self.data.index
        self.items = self.data[self.items_col]

    def __getitem__(self, id):
        return self.data.at[id, self.items_col]


if __name__ == '__main__':
    pass
