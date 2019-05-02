from asyio.futures import Future, set_result_unless_cancelled
from asyio.errors import RuntimeError


__all__ = ['Task', 'sleep', 'ensure_task']


def ensure_task(coro_or_future, loop=None):
    if isinstance(coro_or_future, Future):
        return coro_or_future
    else:
        task = Task(coro_or_future, loop)
    return task


def sleep(delay, result=None, loop=None):
    if delay == 0:
        yield
        return result
    future = Future(loop=loop)
    h = future._loop.call_later(delay,
                                set_result_unless_cancelled,
                                future, result)
    print('sleep fut ', future)
    yield from future


def wait(futs, loop=None):
    from asyio.eventloops import get_event_loop
    if loop is None:
        loop = get_event_loop()
    for future in futs:
        task = ensure_task(future, loop)



class Task(Future):

    def __init__(self, coro, loop=None):
        super().__init__(loop=loop)
        self._coro = coro
        self._loop.call_soon(self._step)

    def _step(self, exc=None):

        try:
            if exc is None:
                result = self._coro.send(None)
            else:
                print('exc ', exc)
                result = self._coro.throw(exc)
        except StopIteration as exc:
            self.set_result(exc.value)
        else:
            if isinstance(result, Future):
                if result._loop is not self._loop:
                    self._loop.call_soon(
                        self._step, RuntimeError('future 与 task 不在同一个事件循环'))
                elif result._blocking:
                    self._blocking = False
                    result.add_done_callback(self._wakeup, result)
                else:
                    self._loop.call_soon(
                        self._step, RuntimeError('你是不是用了 yield 才导致这个error?')
                    )
            elif result is None:
                self._loop.call_soon(self._step)
            else:
                self._loop.call_soon(self._step, RuntimeError('你产生了一个不合规范的值'))

    def _wakeup(self, future):
        try:
            print('future tuple ', future)
            future.result()
        except Exception as exc:
            self._step(exc)
        else:
            self._step()


