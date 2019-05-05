from asyio.asyio.errors import InvalidStateError
from asyio.asyio.handles import Handle
from asyio.asyio.eventloops import get_event_loop


__all__ = ['Future', 'set_result_unless_cancelled']


def set_result_unless_cancelled(fut, result):
    print('real fut', fut)
    fut.set_result(result)


class Future:

    _FINISHED = 'finished'
    _PENDING = 'pending'
    _CANCELLED = 'CANCELLED'

    def __init__(self, loop=None):
        if loop is None:
            self._loop = get_event_loop()
        else:
            self._loop = loop
        self._callbacks = []
        self.status = self._PENDING
        self._blocking = False
        self._result = None

    def _schedule_callbacks(self):
        for callbacks in self._callbacks:
            self._loop.add_ready(callbacks)
        self._callbacks = []

    def set_result(self, result):
        self.status = self._FINISHED
        self._result = result
        self._schedule_callbacks()

    def add_done_callback(self, callback, *args):
        if self.done():
            self._loop.call_soon(callback, *args)
        else:
            handle = Handle(callback, self._loop, *args)
            self._callbacks.append(handle)

    def cancel(self):
        if self.status != self._PENDING:
            return
        self.status = self._CANCELLED
        self._schedule_callbacks()
        return

    def cancelled(self):
        return self.status == self._CANCELLED

    def done(self):
        return self.status != self._PENDING

    def result(self):
        if self.status != self._FINISHED:
            raise InvalidStateError('future is not ready')
        return self._result

    def __iter__(self):
        if not self.done():
            self._blocking = True
        yield self
        assert self.done(), 'future not done'
        return self.result()
