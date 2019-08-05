from humannotator.results import Answer, Invalid


class Interface(object):
    def __init__(self, answer):
        self.answer = answer
        self._check_input_()

    def _check_input_(self):
        if not isinstance(self.answer, Answer):
            raise TypeError(
                f"`answer` must be of type {Answer}."
                )

    def __call__(self):
        while True:
            print(f"\n{self.answer.question.instruction}\n{Stop.instruction}\n")
            user = input()
            if user == Stop.character:
                break

            user = self.answer.question(user)
            if not isinstance(user, Invalid):
                print(f"Annotation is success! Value is {user}")
                break


class Stop(object):
    character = '.'
    instruction = f"[{character}] - exit"
