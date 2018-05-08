import time
from .qing_errors import BootError
from .qingdom import WorkerState


class QingWorker():
    queues = {'in': [], 'out': []}
    worker_stats = {'id': None, 'init_at': None, 'finished_at': None}

    def __init__(self, in_queues, out_queues):
        self.state = WorkerState(self.worker_stats)
        done_boothing = self.boot(in_queues, out_queues)
        while not done_boothing:
            time.sleep(3)
        else:
            self.wait()

    def boot(self, in_queues, out_queues):
        self.state.update('booting')
        for q in in_queues:
            q_connection = q.attempt_connection()
            if q_connection:
                self.queues['in'][q] = q_connection
            else:
                raise BootError(self, "In Queue not connected {}".format(q))

        for q in out_queues:
            q_connection = q.attempt_connection()
            if q_connection:
                self.queues['out'][q] = q_connection
            else:
                raise BootError(self, "Out Queue not connected {}".format(q))

    def wait(self):
        self.state.update('waiting')
        # while self.queues['in']['campaigns_queue'].empty:
        #   sleep
        # else:
        #   read()
        pass

    def read(self):
        self.state.update('running', 'reading')
        pass

    def process(self):
        self.state.update('running', 'processing')
        pass

    def write(self):
        self.state.update('running', 'writing')
        pass
