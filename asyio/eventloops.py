import collections
import heapq
import time
from .handles import Handle, TimeHandle, DelayHandle

_event_loop = None

__all__ = ['get_event_loop', 'Eventloop']


def get_event_loop():
    global _event_loop
    if _event_loop is None:
        _event_loop = Eventloop()
    return _event_loop


def _complete_eventloop(fut):
    fut._loop.stop()


class Eventloop:

    def __init__(self):
        self._ready = collections.deque()
        self._scheduled = []
        self._current_handle = None
        self._stopping = False

    def stop(self):
        self._stopping = True

    def call_soon(self, callback, *args):
        handle = Handle(callback, self, *args)
        self._ready.append(handle)

    def add_ready(self, handle):
        if isinstance(handle, Handle):
            self._ready.append(handle)

    def add_delay(self, handle):
        if isinstance(handle, DelayHandle):
            self.call_later(handle._delay, handle._callback, *handle._args)

    def call_later(self, delay, callback, *args):
        if not delay or delay < 0:
            self.call_soon(callback, *args)
        else:
            when = time.time() + delay
            time_handle = TimeHandle(when, callback, self, *args)
            self._scheduled.append(time_handle)
            heapq.heapify(self._scheduled)

    def run_once(self):
        if (not self._ready) and self._scheduled:
            while self._scheduled[0]._when <= time.time():
                time_handle = heapq.heappop(self._scheduled)
                self._ready.append(time_handle)
                if not self._scheduled:
                    break
        ntodo = len(self._ready)
        for i in range(ntodo):
            handle = self._ready.popleft()
            # print('handle ', handle._callback, handle._args)
            handle._run()

    def run_forever(self):
        while True:
            self.run_once()
            if self._stopping:
                break

    def run_until_complete(self, fut):
        from .tasks import ensure_task
        future = ensure_task(fut, self)
        future.add_done_callback(_complete_eventloop, future)
        self.run_forever()

    def run_not_complete(self, fut):
        from .tasks import ensure_task
        future = ensure_task(fut, self)
        self.run_forever()
