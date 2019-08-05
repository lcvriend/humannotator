# standard library
from collections.abc import Iterable

# third party
import pandas as pd

class Data(object):
    data_type = Iterable

    def __init__(self, data):
        self.data = data
        self._check_input_()
        self.ids = None
        self.elements = None

    def _check_input_(self):
        if not isinstance(self.data, self.data_type):
            raise TypeError(
                f"Data must be of type {self.data_type}."
                )


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

    def __init__(self, data, elements, id='index'):
        super().__init__(data)
        self.ids = data.index if id == 'index' else data[id]
        self.elements = data[elements]


if __name__ == '__main__':
    pass
