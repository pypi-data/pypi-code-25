import subprocess

from oshino_statsd.agent import StatsdAgent

from oshino_jmx import jmx_trans_command


class JmxAgent(StatsdAgent):
    def on_start(self):
        super(JmxAgent, self).on_start()
        self.jmx = subprocess.run(jmx_trans_command())

    def on_close(self):
        super(JmxAgent, self).on_close()
        self.jmx.kill()
