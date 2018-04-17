from flask import Flask
from werkzeug.utils import find_modules, import_string
from charpy import CHARPY_SQL


class App(object):

    def __init__(self, config=None, debug=False):
        """ Initiate the flask app """
        self.app = Flask(__name__)
        self.app.debug = debug

        self.app.config.update(dict(
            DATABASE=CHARPY_SQL,
            DEBUG=True,
            SECRET_KEY='development key',
            USERNAME='admin',
            PASSWORD='default'
        ))
        self.app.config.update(config or {})
        self.app.config.from_envvar('FLASKR_SETTINGS', silent=True)

        self.register_blueprints()

    def register_blueprints(self):
        """Automagically register all blueprint named bp in packages

        Check the argument 'bp' in all the modules in the folder inserted in findmodules
        then register all blueprints in the app
        """
        for name in find_modules('charpy.flask.blueprints', recursive=True):
            mod = import_string(name)

            if hasattr(mod, 'bp'):
                self.app.register_blueprint(mod.bp)
        return None


if __name__ == "__main__":  # pragma: no cover
    chartapp = App(debug=True)
    # print(app.blueprints)

    chartapp.app.run()
