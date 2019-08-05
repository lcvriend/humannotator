class Question(object):
    instruction = """

    """

    def __init__(self):
        self._value = None

    def __call__(self, x):
        self.value = x

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class Question_MultipleChoice(Datum):
    def __init__(self, choices):
        super().__self__()
        self.choices = choices

    @value.setter
    def value(self, value):
        if not value in choices:
            value = None
        self._value = value
