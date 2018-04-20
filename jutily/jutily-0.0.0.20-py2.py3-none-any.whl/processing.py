import threading
import queue
import inspect
import time


def poolable(pool_id=''):

    def mark(func):
        setattr(func, '__poolID__', pool_id)
        return func

    return mark


class ObjectWorkerThread(threading.Thread):

    def __init__(self, poolable_class, function_dict, pool_id, result_queue):
        super().__init__()

        self.poolable_object = poolable_class()
        self.result_queue = result_queue
        self.function_dict = function_dict

        self.active = False
        self.work = None
        self.result = None
        self.id = pool_id

        self.running = False

    def assign_work(self, work_parameter):
        self.active = True
        self.work = work_parameter

    def run(self):
        self.running = True
        while self.running:
            if self.work is not None:
                try:
                    self.result = self.function_dict[self.id](self.poolable_object, self.work)
                    self.result_queue.put(self.result)
                finally:
                    self.work = None
                    self.active = False
            else:
                time.sleep(0.01)


class ObjectWorkerPool:

    def __init__(self, poolable_class, pool_id='', thread_count=10):
        self.poolable_class = poolable_class
        self.id = pool_id

        self.function_dict = {}
        for name, func in inspect.getmembers(poolable_class):
            if callable(func) and hasattr(func, '__poolID__'):
                self.function_dict[func.__poolID__] = func

        self.result_queue = queue.Queue(100)
        self.workers = []
        for i in range(thread_count):
            worker = ObjectWorkerThread(
                self.poolable_class,
                self.function_dict,
                self.id,
                self.result_queue
            )
            self.workers.append(worker)
            worker.start()
        self.workload = []

    def assign_workload(self, workload_list):
        self.workload = workload_list

    def fetch(self):
        while not(len(self.workload) == 0 and self.result_queue.empty() and len(idle_workers) == len(self.workers)):
            # Getting the idle workers and assigning them new work
            idle_workers = list(filter(lambda x: not x.active, self.workers))

            for worker in idle_workers:
                if len(self.workload) != 0:
                    worker.assign_work(self.workload.pop())
                    idle_workers.remove(worker)

            if not self.result_queue.empty():
                yield self.result_queue.get()

            time.sleep(0.01)

    def close(self):
        for worker in self.workers:
            worker.running = False


class DictQuery:
    """
    This is a class, that is supposed to help with the processing of multi layered dictionary structures.
    This is a base class for a state object, that processes one such dictionary at a time, the dictionary being set or
    changed by the 'set' method. The class provides the query dict method, with which a nested value of the dict can
    be acquired by using a standard path query like 'key1/key2/key3'.
    It will be attempted to access the nested structure with this path, but in case there is an exception due to a none
    existing path or something else an exception will be caught and the method 'query_exception' will be executed,
    the query will then return whatever this method returns.
    There is the possibility to specify a default value for every query in case it fails and this is also passed to
    the exception method, wo it could be returned from there, for example

    :ivar dict: The currently processed dict of the object. All the queries will be applied to this dict until it is
        changed
    """
    def __init__(self):
        self.dict = None

    def process(self):
        raise NotImplementedError()

    def set(self, query_dict):
        """
        Sets/changes the currently processed dict of the object

        :param query_dict: The new dict to be processed
        :return: void
        """
        self.dict = query_dict

    def set_query_dict(self, query_dict):
        self.dict = query_dict

    def query_exception(self, query, query_dict, default):
        """
        This method is being called, when a query to the dict fails.

        :param query: The query string for which the exception occurred
        :param query_dict: The whole dict with which the exception occurred
        :param default: The default value given to the query method
        :return: The return will be the return of the query method in case of failure
        """
        raise NotImplementedError()

    def query(self, dict_query, default=None):
        return self.query_dict(dict_query, default)

    def query_dict(self, dict_query, default):
        """
        Attempts to extract the value to the given query "path" from the nested dictionary structure, but in case it
        fails the method 'query_exception' will be executed.

        :param dict_query: The path-like query string defining the order of keys to apply to the nested dict
        :param default: A possible default value in case the query fails
        :return: The value form the dict
        """
        try:
            keys = dict_query.split('/')
            current_dict = self.dict

            for key in keys:
                # Trying to turn the key into an int in case to acces a nested list
                try:
                    current_dict = current_dict[int(key)]
                except (ValueError, TypeError):
                    current_dict = current_dict[key]

            return current_dict
        except (KeyError, ValueError, TypeError) as excpetion:
            return self.query_exception(dict_query, self.dict, default)


if __name__ == '__main__':
    class A:

        def __init__(self):
            pass

        @poolable('ass')
        def add(self, tup):
            return tup[0] + tup[1]

        @poolable('nope')
        def sub(self, tup):
            return tup[0] - tup[1]

    pool = ObjectWorkerPool(A, 'nope', thread_count=3)
    pool.assign_workload([(1,3), (4,5), (34, 60)])
    for i in pool.fetch():
        print(i)
    pool.close()