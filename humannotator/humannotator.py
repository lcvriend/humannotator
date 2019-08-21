# standard library
from collections import namedtuple

# local
from humannotator.utils import Base
from humannotator.data import Data
from humannotator.interface import Interface, Stop
from humannotator.annotations import Annotations, Annotation


class Annotator(Base):
    def __init__(self, data, annotations):
        self.data = data
        self.annotations = annotations
        self._check_input_('data', self.data, Data)
        self._check_input_('annotations', self.annotations, Annotations)

    def __call__(self, ids):
        interface = Interface(self.data, self.annotations)
        for id in ids:
            if id in self.annotations.annotations.keys():
                continue
            user = interface(id)
            if isinstance(user, Stop):
                break
            if isinstance(user, Annotation):
                self.annotations[id] = user
        return None

    def to_dataframe(self):
        return pd.DataFrame(self.annotations)
