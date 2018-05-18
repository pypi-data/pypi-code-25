from cement.core.controller import expose
from cement.ext.ext_argparse import ArgparseController, expose


class Django(ArgparseController):
    class Meta:
        label = 'controller'
        description = 'descricao'
        stacked_on = 'base'
        stacked_type = 'nested'
        help = 'Porra'

    @expose(hide=True)
    def default(self):
        print("Inside StarterBaseController.default(). Controller 1")

        # If using an output handler such as 'mustache', you could also
        # render a data dictionary using a template.  For example:
        #
        #   data = dict(foo='bar')
        #   self.app.render(data, 'default.mustache')
        #
        #
        # The 'default.mustache' file would be loaded from
        # ``mp_starter.cli.templates``, or ``/var/lib/mp_starter/templates/``.
        #
