"""mp-starter base controller."""

from cement.ext.ext_argparse import ArgparseController, expose

class StarterBaseController(ArgparseController):
    class Meta:
        label = 'base'
        description = 'mp-starter is a lib to optimize my workflow when starting a project. Creating the project and ' \
                      'its skeleton. '
        default_func = 'resume'

    # @expose(hide=True)
    def resume(self):
        print(self.Meta.description)