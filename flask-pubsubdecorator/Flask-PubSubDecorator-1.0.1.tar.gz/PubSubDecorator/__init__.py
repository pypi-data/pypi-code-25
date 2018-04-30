from clint.textui import colored
from flask import Flask, Blueprint, request, make_response, wrappers
from google.cloud import pubsub_v1
import google.auth
from google.auth.transport.requests import AuthorizedSession
from requests.exceptions import HTTPError
import logging
import json
import base64
import os
import click
import sys
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

_publisher = pubsub_v1.PublisherClient()
_subscriber = pubsub_v1.SubscriberClient()
_logger = logging.getLogger('flask-pubsub-decorator')
_publish_cli_commands = ['debug', 'shell_plus', 'run', 'run_production']
_subscribe_cli_commands = ['debug', 'run', 'run_production']


class PubSubDecorator(object):

    def __init__(
        self, app, blueprint=None, publish_cli_commands=_publish_cli_commands,
        subscribe_cli_commands=_subscribe_cli_commands, api_key=None
    ):
        if not isinstance(app, Flask):
            raise ValueError('PubSubDecorator must be initialized with a Flask app')
        if blueprint and not isinstance(blueprint, Blueprint):
            raise ValueError('PubSubDecorator blueprint param must be Flask Blueprint')

        scopes = [
            'https://www.googleapis.com/auth/pubsub'
        ]

        self.app = app
        self.api_key = (
            api_key or app.config.get('PUBSUB_DECORATOR_API_KEY') or os.environ.get('PUBSUB_DECORATOR_API_KEY')
        )
        self.blueprint = blueprint
        self.pub_client = _publisher
        self.sub_client = _subscriber
        self.creds, self.project_id = google.auth.default(scopes)
        self.env = os.environ.get(app.config.get('APP_ENV_VAR'))

        try:
            click_ctx = click.get_current_context()
            if click_ctx:
                click_ctx.resilient_parsing = True
                cli_command = (app.cli.parse_args(click_ctx, sys.argv) or [''])[0]
                self.publishable = cli_command in publish_cli_commands
                self.subscriptable = cli_command in subscribe_cli_commands
        except RuntimeError:
            self.publishable = True
            self.subscriptable = True

        if not self.creds:
            raise ValueError('Failed to establish google.auth.credentials.Credentials')

    def _get_authed_session(self):
        return AuthorizedSession(self.creds)

    def _make_request(self, method, url, data=None, headers=None, **kwargs):
        authed_session = self._get_authed_session()
        method = method.upper()

        if 'params' in kwargs:
            _logger.info(u'{method} Request: {url}?{query}'.format(
                method=method, url=url, query=urlencode(kwargs['params']))
            )
        else:
            _logger.info(u'{method} Request: {url}'.format(method=method, url=url))
        if 'json' in kwargs:
            _logger.info('PAYLOAD: {json}'.format(**kwargs))
        if headers:
            _logger.info('HEADERS: {0}'.format(headers))

        r = authed_session.request(method, url, data, headers, **kwargs)

        _logger.info(
            u'{method} Response: {status} {text}'.format(
                method=method, status=r.status_code, text=r.text
            )
        )

        return r

    def publisher(self, topic):
        if not self.publishable:
            def decorator(f):
                return f
            return decorator
        if not topic:
            raise ValueError('You must specify a topic when using publisher decorator')

        topic = self.pub_client.topic_path(self.project_id, topic)

        print colored.yellow('Establishing PubSub topic {0}'.format(topic))

        try:
            r = self._make_request('GET', 'https://pubsub.googleapis.com/v1/' + topic)
            r.raise_for_status()
        except HTTPError:
            _logger.info(colored.yellow('Decorating Topic: {0}'.format(topic)))
            r = self._make_request('PUT', 'https://pubsub.googleapis.com/v1/' + topic)
            r.raise_for_status()

        def decorator(f):
            def wrap_f(*args, **kwargs):
                return f(self.pub_client, topic, *args, **kwargs)
            return wrap_f
        return decorator

    def subscriber(self, subscription, topic, route, methods):
        if not self.subscriptable:
            def decorator(f):
                return f
            return decorator
        if not subscription:
            raise ValueError('You must specify a subscription when using subscriber decorator')
        if not topic:
            raise ValueError('You must specify a topic when using subscriber decorator')
        if not route:
            raise ValueError('You must specify a route when using subscriber decorator')
        if not methods:
            methods = ['POST']

        # stupid python https://www.python.org/dev/peps/pep-3104/
        decorator_args = (subscription, topic, route, methods)

        def decorator(f):
            subscription, topic, route, methods = decorator_args
            self.publisher(topic)
            subscription = self.sub_client.subscription_path(self.project_id, subscription)
            topic = self.sub_client.topic_path(self.project_id, topic)

            if self.blueprint:
                route = self.blueprint.url_prefix + route

            route = '/_ah/push-handlers' + route

            if self.env == 'dev':
                print colored.green('Establishing PubSub pull subscription {0}'.format(subscription))
                push_config = {}
            elif self.api_key:
                print colored.green('Establishing PubSub push subscription {0}'.format(subscription))
                push_config = {
                    'pushEndpoint': 'https://{0}.appspot.com{1}/{2}'.format(self.project_id, route, self.api_key)
                }
                route += '/<api_key>'
            else:
                print colored.green('Establishing PubSub push subscription {0}'.format(subscription))
                push_config = {
                    'pushEndpoint': 'https://{0}.appspot.com{1}'.format(self.project_id, route)
                }

            try:
                r = self._make_request('POST', 'https://pubsub.googleapis.com/v1/{0}:modifyPushConfig'.format(
                    subscription
                ), json={
                    'pushConfig': push_config
                })
                r.raise_for_status()
            except HTTPError:
                _logger.info(colored.yellow('Decorating Subscription: {0}'.format(subscription)))
                r = self._make_request('PUT', 'https://pubsub.googleapis.com/v1/' + subscription, json={
                    'ackDeadlineSeconds': 600,
                    'pushConfig': push_config,
                    'topic': topic
                })
                r.raise_for_status()

            push_endpoint = push_config.get('pushEndpoint')

            if self.blueprint:
                endpoint = '{0}.{1}'.format(self.blueprint.name, f.func_name)
            else:
                endpoint = f.func_name

            def dev_f(message, *args, **kwargs):
                kwargs.update({
                    '__publisher__': self.pub_client,
                    '__topic__': topic,
                    '__subscriber__': self.sub_client,
                    '__subscription__': subscription,
                    '__push_endpoint__': push_endpoint
                })

                try:
                    r = f(json.loads(message.data), *args, **kwargs)
                    # if func returns result, it should be a flask route response.
                    # ack message if successful response, or no response with no exception
                    if r:
                        if not isinstance(r, wrappers.Response):
                            with self.app.app_context():
                                r = make_response(r)
                        if r.status_code < 400:
                            message.ack()
                    else:
                        message.ack()
                except Exception:
                    _logger.exception('Failed to process dev subscription "{0}" Message: {1}'.format(
                        subscription, message.data
                    ))

            def wrap_f(*args, **kwargs):
                message = {}

                if request:
                    try:
                        envelope = json.loads(request.data.decode('utf-8'))
                        message = json.loads(base64.b64decode(envelope['message']['data']).decode())
                        _logger.info('{0} Envelope: {1}'.format(subscription, envelope))
                    except Exception:
                        _logger.exception(
                            'Failed to parse subscription "{0}" Envelope: {1}'.format(subscription, request.data)
                        )

                    if self.api_key and kwargs.get('api_key') != self.api_key:
                        _logger.error('Invalid Request against PubSub Subscription "{0}" with data: {1}'.format(
                            subscription, request.data
                        ))
                        return '', 403

                kwargs.update({
                    '__publisher__': self.pub_client,
                    '__topic__': topic,
                    '__subscriber__': self.sub_client,
                    '__subscription__': subscription,
                    '__push_endpoint__': push_endpoint
                })

                return f(message, *args, **kwargs)

            self.app.route(route, endpoint=endpoint, methods=methods)(wrap_f)
            if self.env == 'dev':
                self.sub_client.subscribe(subscription, callback=dev_f)
            return wrap_f
        return decorator
