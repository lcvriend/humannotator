class Base(object):
    @staticmethod
    def _check_input_(name, x, cls):
        if not isinstance(x, cls):
            raise TypeError(
                f"`{name}` must be of type {cls.__name__}."
                )
