"""Memoization helpers for the reports service."""

import time


def memoize(func=None, *, ttl=300, _store={}):
    """Cache the results of a pure function for ``ttl`` seconds.

    Usage::

        @memoize
        def monthly_revenue(month): ...

        @memoize(ttl=60)
        def monthly_refunds(month): ...
    """

    def decorate(fn):
        def wrapper(*args):
            key = args
            hit = _store.get(key)
            if hit is not None and time.time() - hit[0] < ttl:
                return hit[1]
            value = fn(*args)
            _store[key] = (time.time(), value)
            return value

        wrapper.cache = _store
        wrapper.__name__ = fn.__name__
        return wrapper

    if func is not None:
        return decorate(func)
    return decorate


@memoize
def monthly_revenue(month):
    """Sum of settled invoices for ``month`` ("YYYY-MM"). Hits the warehouse."""
    return _query("SELECT SUM(amount) FROM invoices WHERE month = %s AND settled", month)


@memoize(ttl=60)
def monthly_refunds(month):
    """Sum of refunds issued in ``month``. Hits the warehouse."""
    return _query("SELECT SUM(amount) FROM refunds WHERE month = %s", month)


def monthly_net(month):
    return monthly_revenue(month) - monthly_refunds(month)


def _query(sql, *params):
    # Real implementation talks to the warehouse; stubbed for the exercise.
    raise NotImplementedError
