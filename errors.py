__all__ = ['RuntimeError', 'InvalidStateError', 'EventloopError']


class RuntimeError(Exception):
    pass


class InvalidStateError(Exception):
    pass


class EventloopError(Exception):
    pass