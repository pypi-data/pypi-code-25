import os

from sphinx.util import logging
import yaml
from docutils.parsers.rst import Directive
from docutils import nodes
from sphinx.errors import ExtensionError


logger = logging.getLogger(__name__)


class LookupYAMLError(ExtensionError):

    category = 'LookupYAML error'


class LookupYAMLDirective(Directive):

    required_arguments = 1
    has_content = True

    def run(self):
        self.env = self.state.document.settings.env
        self.config = self.env.config
        self.record_dependencies = \
                self.state.document.settings.record_dependencies
        location = os.path.normpath(
                os.path.join(self.env.srcdir,
                             self.config.lookup_yaml_root
                             + '/' + self.arguments[0]))
        if os.path.isfile(location):
            logger.debug('[lookup_yaml] getting variable "%s" from file %s' % (
                ' / '.join(self.content), location))
            yml_raw = self.get_value(location)
        else:
            raise LookupYAMLError('%s:%s: location "%s" is not a file' % (
                self.env.doc2path(self.env.docname, None),
                self.content_offset - 1,
                location))
        self.record_dependencies.add(location)
        return [nodes.literal_block(yml_raw, yml_raw)]

    def get_value(self, location):
        with open(location, 'r', encoding='utf-8') as yml_src:
            value = yaml.load(yml_src.read())
        try:
            for i in self.content:
                if isinstance(value, list):
                    i = int(i)
                value = value[i]
        except (KeyError, IndexError):
            raise LookupYAMLError('Value "%s" not found' % (
                ' / '.join(self.content)))
        except ValueError:
            raise LookupYAMLError(
                    'Can\'t convert index in "%s" to integer, '
                    'when accessing YAML list' % (
                        ' / '.join(self.content)))
        # prevent pyyaml from adding terminating three dots for simple types
        if not isinstance(value, list) and not isinstance(value, dict):
            return value
        return yaml.dump(value)


def setup(app):
    app.add_directive('lookup-yaml', LookupYAMLDirective)
    app.add_config_value('lookup_yaml_root', '..', 'env')
