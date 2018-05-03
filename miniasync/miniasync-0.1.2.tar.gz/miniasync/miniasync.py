import asyncio

from contextlib import contextmanager


class MiniAsync:
    """ MiniAsync objects are used to run a set of co-routines within a loop.

    MiniAsync objects should not be created directly, but obtained using
    the miniasync.loop context manager.

    Args:
        asyncio_loop: The asyncio loop object to use to run the co-routines
    """
    def __init__(self, asyncio_loop):
        self._loop = asyncio_loop

    def run(self, *coroutines, return_exceptions=None):
        """ Runs a list of coroutines asynchronously

        Args:
            *coroutines: A list of coroutine objects to run
            return_exceptions: A list of exceptions that should be returned rather than raised

        Returns:
            A list containing the values returned by each of the coroutines, in the same order
            as the coroutines were provided.

            If any of the coroutines raised an exception listed in return_exceptions, then
            the returned value for that coroutine will be replaced by the raised exception
        """
        futures = [asyncio.ensure_future(coro) for coro in coroutines]
        combined = asyncio.gather(*futures)
        try:
            self._loop.run_until_complete(combined)
        except Exception as e:
            if return_exceptions is None or not isinstance(e, return_exceptions):
                _cancel_futures(futures, self._loop)
                raise e
            else:
                split = SplitFutures(futures)
                pending_results = self.run(*split.pending(), return_exceptions=return_exceptions)
                return split.merge(pending_results)

        return combined.result()


@contextmanager
def loop():
    """ This context manager creates a local event loop

    The loop is set as the current event loop in the execution
    context. It is closed upon exiting the context manager,
    and the previous loop is restored as the current event loop.

    The context manager yields a MiniAsync object that can be used
    to run coroutines

    Yields:
        MiniAsync object
    """
    prev_loop = asyncio.get_event_loop()
    mini_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(mini_loop)

    yield MiniAsync(mini_loop)

    mini_loop.close()
    asyncio.set_event_loop(prev_loop)


def run(*coroutines, return_exceptions=None):
    """ Runs a list of coroutines asynchronously

    This is a shorthand for:

        with miniasync.loop() as loop:
            loop.run(coroutines, return_exceptions)

    Args:
        *coroutines: A list of coroutine objects to run
        return_exceptions: A list of exceptions that should be returned rather than raised

    Returns:
        A list containing the values returned by each of the coroutines, in the same order
        as the coroutines were provided.

        If any of the coroutines raised an exception listed in return_exceptions, then
        the returned value for that coroutine will be replaced by the raised exception
    """
    with loop() as the_loop:
        return the_loop.run(*coroutines, return_exceptions=return_exceptions)


def _cancel_futures(futures, the_loop=None):
    """ Given a list of Futures, cancel the ones that are not done/cancelled,
        and run the loop to allow cancellation to happen
    """
    if the_loop is None:
        the_loop = asyncio.get_event_loop()

    cancelled = []
    for fut in futures:
        if not fut.cancelled() and not fut.done():
            fut.cancel()
            cancelled.append(fut)

    if len(cancelled) > 0:
        combined = asyncio.gather(*cancelled, return_exceptions=True)
        the_loop.run_until_complete(combined)


class SplitFutures:
    """ Class used to split a list of futures into those that are done
    and those that are still pending. Once we have the results of the
    pending one, this can be used to merge the results back with the
    results of the done ones, such that result order matches the order
    of the futures

    Args:
        futures: list of Futures to split
    """
    def __init__(self, futures):
        self._pending = []
        self._pending_index = []
        self._merge = [None] * len(futures)

        for i, fut in enumerate(futures):
            if fut.done():
                if fut.exception() is not None:
                    self._merge[i] = fut.exception()
                else:
                    self._merge[i] = fut.result()
            else:
                self._pending.append(fut)
                self._pending_index.append(i)

    def pending(self):
        """ Returns the list of pending futures """
        return self._pending

    def merge(self, pending_results):
        """ Merge the results of the pending futures with the
        results of the done futures, and return the merged array

        Args:
            pending_results: List of results
        """
        for i, result in enumerate(pending_results):
            self._merge[self._pending_index[i]] = result
        return self._merge
