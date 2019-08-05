# standard library
import re

class Select():
    def __init__(self, name, phrase, data, info=None, n=0):
        self.name = name
        self.phrase = phrase
        self.regex = rf"\b{phrase}\b"
        self.data = data[0]
        self.column = data[1]
        self.info = info
        self.n = n

    @property
    def results(self):
        results = self.data.loc[
            self.data[self.column].str.contains(self.regex, regex=True)
            ].reset_index()
        if results.empty:
            results = self.data.loc[
                self.data[self.column].str.contains(self.phrase)
                ].reset_index()
        return results

    @property
    def n_results(self):
        return len(self.results)

    @property
    def n_samples(self):
        if self.n_results < self.n:
            return self.n_results
        return self.n

    @property
    def phrase_info(self):
        if self.info:
            qry = f"{self.info[1]} == @self.phrase"
            phrase_info = self.info[0].query(qry)
            if not phrase_info.empty:
                return phrase_info
        return None

    def __call__(self):
        if self.n_results:
            return self._yield_results()
        else:
            print(f"Phrase '{self.phrase}' not found")
            return None

    def _yield_results(self):
        if self.n:
            for sample, (idx, row) in enumerate(
                self.results.sample(self.n_samples).iterrows()
                ):
                html = self.get_html(sample + 1, idx, row)
                yield row, html
        else:
            for idx, row in self.results.iterrows():
                html = self.get_html(None, idx, row)
                yield row, html
