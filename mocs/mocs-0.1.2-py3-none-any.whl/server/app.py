# coding: utf-8

import os
import uuid
import yaml
import json
import typing
import multiprocessing
from tornado import web, ioloop
from coupling.jsonpath import search
from .resource import RuleListResource, RuleDetailResource, get_rule_called_default
from ..common import RULE_API_REST_BASE_PATH

import logging
logger = logging.getLogger(__name__)


class Config(object):
    def __init__(self, filename: str=None, writeback: bool=True):
        self.filename = filename
        self.writeback = writeback
        self.data = {"rules": []}

        if filename:
            raw_data = self._load(self.filename)
            for rule in raw_data["rules"]:
                self.append_rule(rule)
        self._dump()

    @staticmethod
    def _load(filename):
        root, ext = os.path.splitext(filename)
        with open(filename) as f:
            if ext == '.json':
                data = json.load(f)
            elif ext in ('.yml', '.yaml'):
                data = yaml.load(f)
            else:
                raise ValueError("Unsupported ext '{}' of file '{}'".format(ext, filename))
        return data

    def get_rules(self) -> list:
        return self.data["rules"]

    def append_rule(self, rule: dict) -> None:
        if "id" not in rule:
            rule["id"] = str(uuid.uuid1())

        if "called" not in rule:
            rule["called"] = get_rule_called_default()
        logger.debug("Append rule: %s", rule)
        self.data["rules"].append(rule)
        self._dump()

    def get_rule(self, id: str) -> typing.Optional[dict]:
        return search('$..rules[?id="{}"]'.format(id), self.data, default=None, smart_unique=True)

    def search_rules(self, path: str) -> typing.List[dict]:
        rules = search(path, self.data, [], smart_unique=False)
        logger.debug("Found rules with jsonpath '%s': %s", path, rules)
        return rules

    def delete_rule(self, id: str) -> typing.Optional[dict]:
        logger.debug("Delete rule by id: %s", id)
        rules = []
        found = None
        for rule in self.data["rules"]:
            if rule["id"] == id:
                found = rule
                logger.debug("Found rule and delete: %s", rule)
            else:
                rules.append(rule)
        self.data["rules"] = rules

        if found:
            self._dump()
        return found

    def update_rule(self, id: str, rule: dict, merge: bool=False) -> typing.Optional[dict]:
        logger.debug("Update rule by id: %s, merge: %s, rule: \n%s,", id, merge, rule)
        found = None
        for r in self.data["rules"]:
            if r["id"] == id:
                if not merge:
                    r.clear()
                r.update(rule)
                found = r

        if found:
            self._dump()
        return found

    def _dump(self):
        if self.filename is not None and self.writeback:
            logger.debug("Dump config into %s", self.filename)
            with open(self.filename, "w") as f:
                yaml.dump(self.data, f)


class Application(web.Application):
    def __init__(self, config: str=None, *args, **kwargs):
        self.config = Config(config)
        handlers = [
            (RULE_API_REST_BASE_PATH, RuleListResource),
            (self._get_rule_detail_pattern(), RuleDetailResource),
        ]
        web.Application.__init__(self, handlers, *args, **kwargs)

    @staticmethod
    def _get_rule_detail_pattern():
        pattern = RULE_API_REST_BASE_PATH.strip()
        if not pattern.endswith('/'):
            pattern += '/'
        return r"{}(.+)".format(pattern)


def run_app(port: int, host: str="", config: str=None):
    app = Application(config)
    app.listen(port, host)
    ioloop.IOLoop.current().start()


class AppProcess(multiprocessing.Process):
    def __init__(self, port: int, host: str="", config: str=None):
        super().__init__()
        self.host = host
        self.port = port
        self.config = config
        self.should_stop = multiprocessing.Event()

    def run(self):
        ioloop.PeriodicCallback(self.try_exit, 100).start()
        run_app(self.port, self.host, self.config)

    def try_exit(self):
        if self.should_stop.is_set():
            logger.debug("%s receive stop signal, exiting...", self)
            ioloop.IOLoop.current().stop()

    def stop(self):
        if self.is_alive():
            self.should_stop.set()
            self.join()
