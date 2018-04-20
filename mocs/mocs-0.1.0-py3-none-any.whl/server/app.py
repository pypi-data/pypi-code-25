# coding: utf-8

import os
import uuid
import yaml
import json
import typing
from tornado import web, ioloop
from coupling.jsonpath import search
from .resource import RuleListResource, RuleDetailResource
from ..common import RULE_API_REST_BASE_PATH

import logging
logger = logging.getLogger(__name__)


def get_rule_detail_pattern():
    pattern = RULE_API_REST_BASE_PATH.strip()
    if not pattern.endswith('/'):
        pattern += '/'
    return r"{}(.+)".format(pattern)


class Config(object):
    def __init__(self, filename: str=None, writeback: bool=True):
        self.filename = filename
        self.writeback = writeback

        if self.filename is not None:
            root, ext = os.path.splitext(self.filename)
            with open(self.filename) as f:
                if ext == '.json':
                    self.data = json.load(f)
                elif ext in ('.yml', '.yaml'):
                    self.data = yaml.load(f)
                else:
                    raise ValueError("Unsupported ext '{}' of file '{}'".format(ext, self.filename))
        else:
            self.data = {
                "rules": []
            }

        for rule in self.data["rules"]:
            if "id" not in rule:
                rule["id"] = str(uuid.uuid1())
        self._dump()

    def get_rules(self) -> list:
        return self.data["rules"]

    def append_rule(self, rule: dict) -> None:
        self.data["rules"].append(rule)
        self._dump()

    def get_rule(self, id: str) -> typing.Optional[dict]:
        return search('$..rules[?id={}]'.format(id), self.data, default=None, smart_unique=True)

    def search_rules(self, path: str) -> typing.List[dict]:
        rules = search(path, self.data, [], smart_unique=False)
        logger.debug("Found rules by %s: %s", path, rules)
        return rules

    def delete_rule(self, id: str) -> None:
        rules = []
        found = None
        for rule in self.data["rules"]:
            if rule["id"] == id:
                found = rule
            else:
                rules.append(rule)
        self.data["rules"] = rules

        if found:
            self._dump()
        return found

    def update_rule(self, id: str, rule: dict, merge: bool=False) -> None:
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
        if self.writeback and self.filename is not None:
            with open(self.filename, "w") as f:
                yaml.dump(self.data, f)


class Application(web.Application):
    def __init__(self, config: str=None, *args, **kwargs):
        self.config = Config(config)
        handlers = [
            (RULE_API_REST_BASE_PATH, RuleListResource),
            (get_rule_detail_pattern(), RuleDetailResource),
        ]
        web.Application.__init__(self, handlers, *args, **kwargs)


def run_app(port: int, host: str="", config: str=None):
    app = Application(config)
    app.listen(port, host)
    ioloop.IOLoop.current().start()
