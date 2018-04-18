__author__ = 'Bohdan Mushkevych'

from threading import Lock
from subprocess import PIPE

import psutil
from psutil import TimeoutExpired

from launch import get_python, PROJECT_ROOT, PROCESS_STARTER
from synergy.conf import settings
from synergy.db.dao.box_configuration_dao import BoxConfigurationDao, QUERY_PROCESSES_FOR_BOX_ID
from synergy.supervisor.supervisor_constants import TRIGGER_INTERVAL
from synergy.supervisor.supervisor_configurator import get_box_id
from synergy.system.utils import remove_pid_file
from synergy.system.decorator import thread_safe
from synergy.system.repeat_timer import RepeatTimer
from synergy.system.synergy_process import SynergyProcess


class Supervisor(SynergyProcess):
    def __init__(self, process_name):
        super(Supervisor, self).__init__(process_name)
        self.thread_handlers = dict()
        self.lock = Lock()
        self.box_id = get_box_id(self.logger)
        self.bc_dao = BoxConfigurationDao(self.logger)
        self.logger.info('Started {0} with configuration for BOX_ID={1}'.format(self.process_name, self.box_id))

    def __del__(self):
        self.logger.info('Shutting down Supervisor...')
        for handler in self.thread_handlers:
            handler.cancel()
        self.thread_handlers.clear()
        super(Supervisor, self).__del__()

    # **************** Supervisor Methods ************************
    def _kill_process(self, box_config):
        """ method is called to kill a running process """
        try:
            self.logger.info('kill: {0} {{'.format(box_config.process_name))
            self.logger.info('target process pid={0}'.format(box_config.pid))
            if box_config.pid and psutil.pid_exists(box_config.pid):
                p = psutil.Process(box_config.pid)
                p.kill()
                p.wait()
                box_config.pid = None
                self.bc_dao.update(box_config)
                remove_pid_file(box_config.process_name)
        except Exception:
            self.logger.error('Exception on killing: {0}'.format(box_config.process_name), exc_info=True)
        finally:
            self.logger.info('}')

    def _start_process(self, box_config):
        if not self.bc_dao.ds.is_alive():
            # ping DB to make sure it is alive.
            # otherwise, processes will be spawned uncontrollably
            raise UserWarning('DB Down Exception: unable to reach db {0}'.format(self.bc_dao.ds))

        try:
            self.logger.info('start: {0} {{'.format(box_config.process_name))
            p = psutil.Popen([get_python(), PROJECT_ROOT + '/' + PROCESS_STARTER, box_config.process_name],
                             close_fds=True,
                             cwd=settings.settings['process_cwd'],
                             stdin=PIPE,
                             stdout=PIPE,
                             stderr=PIPE)
            box_config.pid = p.pid
            self.logger.info('Started {0} with pid = {1}'.format(box_config.process_name, p.pid))
        except Exception:
            box_config.set_process_pid(box_config.process_name, None)
            self.logger.error('Exception on starting: {0}'.format(box_config.process_name), exc_info=True)
        finally:
            self.bc_dao.update(box_config)
            self.logger.info('}')

    def _poll_process(self, box_config):
        """ between killing a process and its actual termination lies poorly documented requirement -
            <purging process' io pipes and reading exit status>.
            this can be done either by os.wait() or process.wait() """
        try:
            p = psutil.Process(box_config.pid)

            return_code = p.wait(timeout=0.01)
            if return_code is None:
                # process is already terminated
                self.logger.info('Process {0} is terminated'.format(box_config.process_name))
                return
            else:
                # process is terminated; possibly by OS
                box_config.pid = None
                self.bc_dao.update(box_config)
                self.logger.info('Process {0} got terminated. Cleaning up'.format(box_config.process_name))
        except TimeoutExpired:
            # process is alive and OK
            pass
        except Exception:
            self.logger.error('Exception on polling: {0}'.format(box_config.process_name), exc_info=True)

    def start(self, *_):
        """ reading box configurations and starting timers to start/monitor/kill processes """
        try:
            box_configurations = self.bc_dao.run_query(QUERY_PROCESSES_FOR_BOX_ID(self.box_id))

            for box_config in box_configurations:
                handler = RepeatTimer(TRIGGER_INTERVAL, self.manage_process, args=[box_config.process_name])
                self.thread_handlers[box_config.process_name] = handler
                handler.start()
                self.logger.info('Started Supervisor Thread for {0}, triggering every {1} seconds'
                                 .format(box_config.process_name, TRIGGER_INTERVAL))
        except LookupError as e:
            self.logger.error('Supervisor failed to start because of: {0}'.format(e))

    @thread_safe
    def manage_process(self, *args):
        """ reads box configuration and start/kill processes. performs process monitoring """
        process_name = args[0]
        try:
            box_config = self.bc_dao.get_one([self.box_id, process_name])
            if not box_config.is_on:
                if box_config.pid is not None:
                    self._kill_process(box_config)
                return

            if not box_config.pid or not psutil.pid_exists(box_config.pid):
                self._start_process(box_config)
            elif box_config.pid and psutil.pid_exists(box_config.pid):
                self._poll_process(box_config)
        except Exception as e:
            self.logger.error('Exception: {0}'.format(e), exc_info=True)


if __name__ == '__main__':
    from synergy.supervisor.supervisor_constants import PROCESS_SUPERVISOR

    source = Supervisor(PROCESS_SUPERVISOR)
    source.start()
