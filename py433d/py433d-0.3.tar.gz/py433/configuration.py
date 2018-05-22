import json
import logging
import os

import importlib
watchdog = importlib.find_loader('watchdog')
if watchdog:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

from . import defaults


class configuration:

    @classmethod
    def load(cls, filename=defaults.config):
        conf = dict()
        try:
            with open(filename) as f:
                conf = json.load(f)
            loaded = True
        except Exception as e:
            print(e)
        logging.info("Loaded config from file '" + filename + "':" + str(conf))

        new_instance = cls()

        new_instance.filename = filename

        new_instance.tx_pin = conf.get("radio").get("tx_pin", 17)
        new_instance.tx_protocol = conf.get("radio").get("tx_protocol", 1)
        new_instance.tx_pulse = conf.get("radio").get("tx_pulse", 180)

        new_instance.rx_pin = conf.get("radio").get("rx_pin", 27)

        new_instance.port = conf.get("tcp_server").get("port", defaults.port)

        new_instance.log_filename = conf.get("log").get("filename", "433d.log")
        level = conf.get("log").get("level", "INFO").upper()
        if level == "CRITICAL":
            new_instance.log_level = logging.CRITICAL
        elif level == "FATAL":
            new_instance.log_level = logging.FATAL
        elif level == "ERROR":
            new_instance.log_level = logging.ERROR
        elif level == "WARNING":
            new_instance.log_level = logging.WARNING
        elif level == "WARN":
            new_instance.log_level = logging.WARN
        elif level == "INFO":
            new_instance.log_level = logging.INFO
        elif level == "DEBUG":
            new_instance.log_level = logging.DEBUG

        new_instance.messages = conf.get("messages", dict())

        new_instance.mqtt_host = conf.get("mqtt").get("host", None)
        new_instance.mqtt_port = conf.get("mqtt").get("port", None)
        new_instance.mqtt_username = conf.get("mqtt").get("username", None)
        new_instance.mqtt_password = conf.get("mqtt").get("password", None)

        new_instance.codes = conf.get("codes", dict())

        return new_instance

    def watch(self, callback=None):
        if watchdog:

            filename = self.filename
            class Handler(FileSystemEventHandler):
                @staticmethod
                def on_any_event(event):
                    if event.src_path == filename:
                        try:
                            callback()
                        except:
                            pass

            self.observer = Observer()
            self.observer.schedule(Handler(), os.path.dirname(os.path.realpath(self.filename)))
            self.observer.start()

    def stop(self):
        if watchdog:
            self.observer.stop()