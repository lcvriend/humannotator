# standard library
from collections.abc import Iterable

# third party
import pandas as pd

# local
from humannotator.utils import Base


class Data(Base):
    data_type = Iterable

    def __init__(self, data):
        self.data = data
        self._check_input_('data', self.data, self.data_type)
        self.ids = None
        self.elements = data

    def __call__(self, id):
        return elements[id]


class Data_List(Data):
    data_type = list

    def __init__(self, data):
        super().__init__(data)
        self.ids = list(range(0, len(data)))
        self.elements = data


class Data_Dict(Data):
    data_type = dict

    def __init__(self, data):
        super().__init__(data)
        self.ids = data.keys()
        self.elements = data.values()


class Data_DataFrame(Data):
    data_type = pd.DataFrame

    def __init__(self, data, element_col, id_col=None):
        super().__init__(data)
        if id_col:
            self.data = self.data.set_index(id_col)
        self.element_col = element_col
        self.ids = self.data.index
        self.elements = self.data[self.element_col]

    def __call__(self, id):
        return self.data.at[id, self.element_col]


if __name__ == '__main__':
    pass
