from flask import Flask, Blueprint, request


class CronDecorator(object):

    def __init__(self, app, blueprint=None):
        if not isinstance(app, Flask):
            raise ValueError('CronDecorator must be initialized with a Flask app')
        if blueprint and not isinstance(blueprint, Blueprint):
            raise ValueError('CronDecorator blueprint param must be Flask Blueprint')

        self.app = app
        self.blueprint = blueprint

    def task(self, rule, **options):
        """
        This method wraps Flask app.route decorator to validate a Cron task route is called by Google Cloud via
        the X-Appengine-Cron header. Call this method like you would app.route. Your rule will be prefixed by /cron
        """
        # stupid python https://www.python.org/dev/peps/pep-3104/
        decorator_args = (rule, options)

        def decorator(f):
            rule, options = decorator_args

            if self.blueprint:
                rule = self.blueprint.url_prefix + rule

            rule = '/cron' + rule

            if self.blueprint:
                endpoint = '{0}.{1}'.format(self.blueprint.name, f.func_name)
            else:
                endpoint = f.func_name

            def wrap_f(*args, **kwargs):
                if request and request.headers.get('X-Appengine-Cron'):
                    return f(*args, **kwargs)
                else:
                    return '', 403

            options.pop('endpoint', None)
            # We should only need to support GET requests
            options.pop('methods', None)
            self.app.route(rule, endpoint=endpoint, methods=['GET'], **options)(wrap_f)

            return wrap_f
        return decorator
