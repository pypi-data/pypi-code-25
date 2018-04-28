from __future__ import absolute_import
import atexit
from Queue import Empty
from multiprocessing import Process, Queue
from rllab2.sampler.utils import rollout
import numpy as np

__all__ = [
    u'init_worker',
    u'init_plot',
    u'update_plot'
]

process = None
queue = None


def _worker_start():
    env = None
    policy = None
    max_length = None
    try:
        while True:
            msgs = {}
            # Only fetch the last message of each type
            while True:
                try:
                    msg = Queue.get_nowait()
                    msgs[msg[0]] = msg[1:]
                except Empty:
                    break
            if u'stop' in msgs:
                break
            elif u'update' in msgs:
                env, policy = msgs[u'update']
                # env.start_viewer()
            elif u'demo' in msgs:
                param_values, max_length = msgs[u'demo']
                policy.set_param_values(param_values)
                rollout(env, policy, max_path_length=max_length, animated=True, speedup=5)
            else:
                if max_length:
                    rollout(env, policy, max_path_length=max_length, animated=True, speedup=5)
    except KeyboardInterrupt:
        pass


def _shutdown_worker():
    if process:
        Queue.put([u'stop'])
        Queue.close()
        process.join()


def init_worker():
    global process, Queue
    queue = Queue()
    process = Process(target=_worker_start)
    process.start()
    atexit.register(_shutdown_worker)


def init_plot(env, policy):
    Queue.put([u'update', env, policy])


def update_plot(policy, max_length=np.inf):
    Queue.put([u'demo', policy.get_param_values(), max_length])
