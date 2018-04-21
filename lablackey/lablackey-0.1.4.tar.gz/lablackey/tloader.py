import io
from os.path import dirname, join, abspath
from django.apps import apps
from django.template import TemplateDoesNotExist, Origin
from django.template.loaders.app_directories import Loader as BaseLoader

class Loader(BaseLoader):
    is_usable = True
    def get_template_sources(self, template_name, template_dirs=None):
        template_parts = template_name.split(":", 1)
        if len(template_parts) != 2:
            return #raise TemplateDoesNotExist("Unable to find template %s"%template_name)

        app_name, template_name = template_parts
        app_dir = apps.get_app_config(app_name).path
        template_dir = abspath(join(app_dir, 'templates'))

        yield Origin(
            name=join(template_dir, template_name),
            template_name=template_name,
            loader=self,
        )

    #! DEPRACATED Django==1.9 no longer uses this
    def get_template_path(self, app_template_name, template_dirs=None):
        template_parts = app_template_name.split(":", 1)

        if len(template_parts) != 2:
            raise TemplateDoesNotExist("Unable to find template %s"%app_template_name)

        app_name, template_name = template_parts
        app_dir = apps.get_app_config(app_name).path
        template_dir = abspath(join(app_dir, 'templates'))

        return join(template_dir, template_name)

    #! DEPRACATED Django==1.9 no longer uses this
    def load_template_source(self, template_name, template_dirs=None):
        filepath = self.get_template_path(template_name, template_dirs)
        try:
            with io.open(filepath, encoding=self.engine.file_charset) as fp:
                return fp.read(), filepath
        except IOError:
            pass
        raise TemplateDoesNotExist(template_name)
