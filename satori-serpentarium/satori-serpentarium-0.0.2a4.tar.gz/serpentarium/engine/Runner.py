import logging
import sys

from satori.rtm.connection import enable_wsaccel

from serpentarium.engine.ExecutionContext import ExecutionContext
from serpentarium.logging.LoggingUtil import LoggingUtil
from serpentarium.monitoring.CompoundMonitor import CompoundMonitor
from serpentarium.monitoring.DatadogMonitor import DatadogMonitor
from serpentarium.monitoring.RtmMonitor import RtmMonitor
from serpentarium.rtm.RtmClientUtil import RtmClientUtil
from serpentarium.util.helpers import parse_config


class Runner:

    def __init__(self, config_path: str):

        self.config_path = config_path

    def run(self):
        graph = None
        try:
            # setup basic logging
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            logging.getLogger("satori.rtm").setLevel(logging.WARN)
            logging.getLogger("miniws4py").setLevel(logging.WARN)
            logging.getLogger("datadog.api").setLevel(logging.WARN)

            # Enable UTF-8 validation optimization
            enable_wsaccel()

            config = parse_config(self.config_path)

            tags = config['tags']

            if 'logging' in config:
                # setup advanced logging
                logging_config = config['logging']

                if 'rtm' in logging_config:
                    logging_rtm_client = RtmClientUtil.get_client(logging_config['rtm'])

                    LoggingUtil.setup_logging(settings=logging_config, client=logging_rtm_client, tags=tags)
                    log: logging.Logger = LoggingUtil.get_rtm_logger("default")

                    log.info("RTM logging is set up.")

            monitor_list = []
            monitoring_period = -1
            if 'monitoring' in config:
                # set up monitoring
                monitoring_config = config['monitoring']

                monitoring_period = monitoring_config["period"]
                if 'rtm' in monitoring_config:
                    monitor_list.append(RtmMonitor(settings=monitoring_config, tags=tags))

                if 'datadog' in monitoring_config:
                    monitor_list.append(DatadogMonitor(settings=monitoring_config, tags=tags))

            compound_monitor = CompoundMonitor(monitor_list)

            # setup execution
            graph = ExecutionContext(mods=config['mods'], monitor=compound_monitor,
                                     monitor_polling=monitoring_period)
            graph.start()

        except RuntimeError:
            if graph is not None:
                graph.shutdown()
            RtmClientUtil.dispose()
            sys.exit(-1)
        except KeyboardInterrupt:
            pass
        finally:
            if graph is not None:
                graph.shutdown()
            RtmClientUtil.dispose()
