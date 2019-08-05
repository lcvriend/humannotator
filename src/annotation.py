# standard library
from collections import namedtuple
from datetime import datetime


class Annotator(object):
    Annotation = namedtuple(
        'Annotation', ['element', 'annotation', 'timestamp']
        )

    def __init__(self, annotations=list()):
        self.annotations = annotations

    @property
    def annotated(self):
        return [annotation.element for annotation in self.annotations]

    def __call__(self, elements):
        """
        Annotate a list of elements.
        The annotator skips elements already in self.annotated.

        Parameters
        ==========
        elements : iterable
            Iterable of elements to be annotated.

        Returns
        =======
        None
        """

        for element in elements:
            if element in self.annotated:
                continue
            user = self._interface(element)
            if user == '.':
                break
        return None

    def to_dataframe(self):
        return pd.DataFrame(self.annotations)

    @classmethod
    def from_dataframe(cls, df):
        annotations = [
            annotation for annotation in df.itertuples(
                index=False, name='Annotation')
                ]
        return Annotator(annotations)


class PhraseAnnotator(Annotator):
    name = 'Phrase Annotator'
    Annotation = namedtuple(
        'Annotation', ['phrase', 'id', 'annotation', 'timestamp']
        )

    def __init__(self, data, info=None, n=5):
        super().__init__()
        self.data = data
        self.info = info
        self.n = n


    def _interface(self, phrase):
        search = Search(
            self.name, phrase, self.data, info=self.info, n=self.n
            )

        test = search()
        if not test:
            self.annotations.append(
                self.Annotation(phrase, None, 'n/f', datetime.now())
                )
            clear_output()
            return None

        for row, html in search():

        return None
