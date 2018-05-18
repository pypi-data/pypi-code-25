"""mp-starter main application entry point."""

from cement.core.foundation import CementApp
from cement.utils.misc import init_defaults
from cement.core.exc import FrameworkError, CaughtSignal

from mp_starter.cli.controllers.django import Django
from mp_starter.core import exc

# Application default.  Should update config/mp_starter.conf to reflect any
# changes, or additions here.
defaults = init_defaults('mp_starter')

# All internal/external plugin configurations are loaded from here
defaults['mp_starter']['plugin_config_dir'] = '/etc/mp_starter/plugins.d'

# External plugins (generally, do not ship with application code)
defaults['mp_starter']['plugin_dir'] = '/var/lib/mp_starter/plugins'

# External templates (generally, do not ship with application code)
defaults['mp_starter']['template_dir'] = '/var/lib/mp_starter/templates'


class StarterApp(CementApp):
    class Meta:
        label = 'mp_starter'
        config_defaults = defaults

        # All built-in application bootstrapping (always run)
        bootstrap = 'mp_starter.cli.bootstrap'

        # Internal plugins (ship with application code)
        plugin_bootstrap = 'mp_starter.cli.plugins'

        # Internal templates (ship with application code)
        template_module = 'mp_starter.cli.templates'

        # call sys.exit() when app.close() is called
        exit_on_close = True

        handlers = [Django, ]


class StarterTestApp(StarterApp):
    """A test app that is better suited for testing."""
    class Meta:
        # default argv to empty (don't use sys.argv)
        argv = []

        # don't look for config files (could break tests)
        config_files = []

        # don't call sys.exit() when app.close() is called in tests
        exit_on_close = False


# Define the applicaiton object outside of main, as some libraries might wish
# to import it as a global (rather than passing it into another class/func)
app = StarterApp()

def main():
    with app:
        try:
            app.run()
        
        except exc.StarterError as e:
            # Catch our application errors and exit 1 (error)
            print('StarterError > %s' % e)
            app.exit_code = 1
            
        except FrameworkError as e:
            # Catch framework errors and exit 1 (error)
            print('FrameworkError > %s' % e)
            app.exit_code = 1
            
        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('CaughtSignal > %s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
