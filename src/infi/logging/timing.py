from infi.pyutils.decorators import wraps
from infi.pyutils.contexts import contextmanager
from logbook import Logger
from time import time

_logger = Logger(__name__)
_time = time


def set_time_func(f):
    """
    Allow user to set the time function used for time measurements. By default the time function is Python's standard
    library time.time(), but the user can choose a different one, for example by using infi.monotonic_time.
    :param f: a function that has no arguments and returns a float representing seconds
    """
    global _time
    _time = f


def set_logger(l):
    """
    Allow user to set the logger used to log the time measurements. By default the logger is a local logger created.
    :param l: logbook.Logger object
    """
    global _logger
    _logger = l


@contextmanager
def log_timing_context(title, logger=None, log_level="DEBUG"):
    """
    Log the execution time of the context. It generates two log messages: before yielding and after.
    :param title: str to add to the log messages.
    :param logger: logger to use, or None if using the default logger.
    :param log_level: str log level to use [TRACE|DEBUG|INFO|...]
    """
    global _logger, _time
    if logger is None:
        logger = _logger
    log = getattr(logger, log_level.lower())
    t0 = _time()
    log("started timing {} at {:.4f}".format(title, t0))
    try:
        yield
    finally:
        t1 = _time()
        log("ended timing {} at {:.4f}. time taken: {:.4f} seconds".format(title, t1, t1 - t0))


def log_timing(func=None, logger=None, log_level="DEBUG"):
    """
    Decorator to log the decorated function execution time. See `log_timing_context` for more details.

    It can be used in several methods:
    ```
    @log_timing
    def foo():
        pass

    @log_timing(logger=my_logger)
    def foo():
        pass

    @log_timing(logger=my_logger, log_level='DEBUG')
    def foo():
        pass
    ```

    :param func: function to decorate
    :param logger: logger to use, or None if using the default logger.
    :param log_level: str log level to use [TRACE|DEBUG|INFO|...]
    """
    def decorate(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            with log_timing_context("function {!r}".format(f.func_name), logger=logger, log_level=log_level):
                return f(*args, **kwargs)
        return wrapped
    if func is None:
        return decorate
    else:
        return decorate(func)