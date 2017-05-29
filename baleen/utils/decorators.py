# baleen.utils.decorators
# Decorators and function utilities for Baleen.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Wed Mar 02 19:03:43 2016 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: decorators.py [538b33d] benjamin@bengfort.com $

"""
Decorators and function utilities for Baleen.
"""

##########################################################################
## Imports
##########################################################################

import signal
from functools import wraps
from baleen.utils.timez import Timer
from baleen.exceptions import BaleenError, BaleenTimeout


##########################################################################
## Memoization
##########################################################################

def memoized(fget):
    """
    Return a property attribute for new-style classes that only calls its
    getter on the first access. The result is stored and on subsequent
    accesses is returned, preventing the need to call the getter any more.
    https://github.com/estebistec/python-memoized-property
    """
    attr_name = '_{0}'.format(fget.__name__)

    @wraps(fget)
    def fget_memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fget(self))
        return getattr(self, attr_name)

    return property(fget_memoized)


##########################################################################
## Timer functions
##########################################################################

def timeit(func):
    """
    Returns the number of seconds that a function took along with the result
    """

    @wraps(func)
    def timer_wrapper(*args, **kwargs):
        """
        Inner function that uses the Timer context object
        """
        with Timer() as timer:
            result = func(*args, **kwargs)

        return result, timer

    return timer_wrapper


def timeout(seconds):
    """
    Raises a TimeoutError if a function does not terminate within
    specified seconds.
    """

    def _timeout_error(signal, frame):
        raise TimeoutError("Operation did not finish within \
        {} seconds".format(seconds))

    def timeout_decorator(func):

        @wraps(func)
        def timeout_wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _timeout_error)
            signal.alarm(seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)

        return timeout_wrapper

    return timeout_decorator


##########################################################################
## Exception Handling
##########################################################################

def reraise(klass=BaleenError, message=None, trap=Exception, ignore=()):
    """
    Catches exceptions (those specified by trap) and then reraises the
    exception type specified by class. Also embeds the original exception as
    a property of the new exception: `error.original`. Finally you can
    specify another message to raise, otherwise the error string is used.
    """

    def reraise_decorator(func):

        @wraps(func)
        def reraise_wrapper(*args, **kwargs):
            """
            Capture Wrapper
            """
            try:
                return func(*args, **kwargs)
            except trap as e:
                if isinstance(e, ignore):
                    raise
                error = klass(message or str(e))
                error.original = e
                raise error

        return reraise_wrapper

    return reraise_decorator
