# coding: utf-8

import json
import uuid
import pprint
import functools
import typing
from jsonschema import validate, ValidationError
from tornado import web, escape, gen, routing
from coupling.jsonpath import search

from ..common import RULE_JSON_SCHEMA

import logging
logger = logging.getLogger(__name__)


class BaseResource(web.RequestHandler):
    def json(self) -> typing.Optional[dict]:
        content_type = self.request.headers.get("Content-Type", "")
        content_length = self.request.headers.get("Content-Length", -1)
        if 'application/json' in content_type and 0 < int(content_length):
            return escape.json_decode(self.request.body)
        return None

    def write(self, chunk):
        if self._finished:
            raise RuntimeError("Cannot write() after finish()")
        if isinstance(chunk, dict) or isinstance(chunk, list):
            chunk = json.dumps(chunk).replace("</", "<\\/")
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        chunk = escape.utf8(chunk)
        self._write_buffer.append(chunk)

    def data_received(self, chunk):
        pass


def _adjust_pattern(pattern: str) -> str:
    if not pattern.endswith('$'):
        pattern += '$'
    return pattern


class MockRuleResource(BaseResource):
    @gen.coroutine
    def _handle(self, method: str):
        path = self.request.path
        jpath = '$..rules[?request.path="{}"&request.method="{}"]'.format(path, method)

        found = None
        for rule in self.application.config.search_rules(jpath):
            queries = rule.get("queries", {})
            headers = rule.get("headers", {})
            body = rule.get("body", b'')
            logger.debug("Rule queries: %s", queries)
            logger.debug("Request queries: %s", self.request.query_arguments)
            if queries == self.request.query_arguments:
                logger.debug("Rule headers: %s", headers)
                logger.debug("Request headers: %s", self.request.headers)
                header_match = True
                for header_name, header_value in headers.items():
                    if not (header_name in self.request.headers and self.request.headers[header_name] == header_value):
                        header_match = False

                if header_match:
                    logger.debug("Rule body: %s", body)
                    logger.debug("Request body: %s", self.request.body)
                    if body == self.request.body:
                        found = rule
                        break

        if found:
            body = search("$.response.body", found, default=b'')
            status = search("$.response.status", found, default=200)
            headers = search("$.response.headers", found, default={"Content-Type": "application/json"})
            delay = search("$.response.delay", found, default=0)
            yield gen.sleep(delay)
            for k, v in headers.items():
                self.set_header(k, v)
            self.set_status(status)
            self.write(body)
        else:
            self.set_status(404)

    get = functools.partialmethod(_handle, "get")
    post = functools.partialmethod(_handle, "post")
    put = functools.partialmethod(_handle, "put")
    delete = functools.partialmethod(_handle, "delete")
    patch = functools.partialmethod(_handle, "patch")


class RuleListResource(BaseResource):
    def get(self):
        rules = self.application.config.get_rules()
        self.finish(rules)

    def post(self):
        rule = self.json()
        logger.debug("Creating new rule: \n%s", pprint.pformat(rule))
        try:
            validate(rule, RULE_JSON_SCHEMA)
        except ValidationError as err:
            self.set_status(400)
            self.finish({"message": str(err)})
        else:
            if "id" not in rule:
                rule["id"] = str(uuid.uuid1())
            self.application.config.append_rule(rule)
            vhost = ".*"
            pattern = search("$.request.path", rule, default="")
            found = self._find_handler(vhost, pattern)
            if not found:
                self.application.add_handlers(vhost, [
                    (pattern, MockRuleResource)
                ])
            self.finish({"id": rule["id"]})

    def _find_handler(self, vhost, pattern):
        # the HostMatches and PathMatches will auto add $ if the pattern not ends with $.
        # if we don't adjust the original pattern, it will cause we can't find the pattern
        vhost = _adjust_pattern(vhost)
        pattern = _adjust_pattern(pattern)
        for router_rule in self.application.default_router.rules:
            if isinstance(router_rule.matcher, routing.HostMatches) and router_rule.matcher.host_pattern.pattern == vhost:
                logger.debug("found host match '%s': %s", vhost, router_rule.matcher)

                for target_rule in router_rule.target.rules:
                    matcher = target_rule.matcher
                    if isinstance(matcher, routing.PathMatches) and matcher.regex.pattern == pattern:
                        logger.debug("found path match '%s': %s", pattern, matcher)
                        return target_rule.target


class RuleDetailResource(BaseResource):
    def get(self, ident):
        rule = self.application.config.get_rule(ident)
        if rule:
            self.set_status(200)
            self.finish(rule)
        else:
            self.set_status(404)

    def put(self, ident):
        merge = self.get_query_argument("merge", default=False)
        rule = self.json()
        done = self.application.config.update_rule(ident, rule, merge)
        if done:
            self.set_status(200)
        else:
            self.set_status(404)

    def delete(self, ident):
        rule = self.application.config.delete_rule(ident)
        if rule:
            self.set_status(200)
        else:
            self.set_status(404)
