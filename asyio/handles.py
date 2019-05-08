__all__ = ['Handle', 'DelayHandle', 'TimeHandle']


class Handle:

    def __init__(self, callback, loop, *args):
        self._callback = callback
        self._loop = loop
        self._args = args

    def _run(self):
        self._callback(*self._args)


class DelayHandle(Handle):

    def __init__(self, delay, callback, loop, *args):
        super().__init__(callback, loop, *args)
        self._delay = delay


class TimeHandle(Handle):

    def __init__(self, when, callback, loop, *args):
        super().__init__(callback, loop, *args)
        self._when = when

    def __hash__(self):
        return hash(self._when)

    def __lt__(self, other):
        return self._when < other._when

    def __le__(self, other):
        if self._when < other._when:
            return True
        return self.__eq__(other)

    def __eq__(self, other):
        return self._when == self._when

    def __gt__(self, other):
        return self._when > other._when

    def __ge__(self, other):
        if self._when > other._when:
            return True
        return self.__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

