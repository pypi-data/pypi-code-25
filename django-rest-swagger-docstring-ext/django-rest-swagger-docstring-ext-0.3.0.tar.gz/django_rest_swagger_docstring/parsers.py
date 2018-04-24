import re
import yaml
from django.contrib.admindocs.utils import trim_docstring
from rest_framework.utils import formatting


class YAMLDocstringParser(object):
    """
    Docstring should be formatted in yaml language
    1. Control over parameters
    ============================================================================
    Define parameters and its properties in docstrings:
        parameters:
            - name: some_param
              description: Foobar long description goes here
              required: true
              type: integer
              paramType: form
              minimum: 10
              maximum: 100
            - name: other_foo
              paramType: query
            - name: avatar
              type: file

    SAMPLE DOCSTRING:
    ============================================================================
    ---
    # API Docs
    # Note: YAML always starts with `---`

    parameters:
        - name: name
          description: Foobar long description goes here
          required: true
          type: string
          paramType: form
        - name: other_foo
          paramType: query
        - name: other_bar
          paramType: query
        - name: avatar
          type: file
    """
    PARAM_TYPES = ['header',
                   'path',
                   'form',
                   'body',
                   'query', ]

    PRIMITIVES = ['integer',
                  'number',
                  'string',
                  'boolean', ]

    SPLITTER = "---"

    def __init__(self, docstring):
        self.object = self.create_yaml_object(docstring)
        if self.object is None:
            self.object = {}


    @classmethod
    def split_docstring(cls, docstring):
        docstring = trim_docstring(docstring)

        splitter_re = "^|\n{}".format(re.escape(cls.SPLITTER))
        ptn = re.compile(splitter_re)
        splitted = ptn.split(docstring, maxsplit=1)  # `rsplit` would be more useful though.

        if len(splitted) != 2:
            return None, None
        return splitted

    def create_yaml_object(self, docstring):
        """Create YAML object from docstring"""
        base, yaml_string = self.split_docstring(docstring)
        if not yaml_string:
            return None
        yaml_string = formatting.dedent(yaml_string)
        try:
            # Note that it's not `safe_load`. But docstrings shouldn't really
            # have unsafe values, right?..
            return yaml.load(yaml_string)
        except yaml.YAMLError:  # TODO: log?..
            return None

    def get_parameters(self):
        """
        Get parameters from parsed docs
        """
        params = []
        fields = self.object.get('parameters', [])
        for field in fields:
            param_type = field.get('paramType', 'form')
            if param_type not in self.PARAM_TYPES:
                param_type = 'form'
            data_type = field.get('type', 'string')
            if param_type in ('path', 'query', 'header'):
                if data_type not in YAMLDocstringParser.PRIMITIVES:
                    data_type = 'string'
            if data_type == 'file':
                param_type = 'body'

            f = {
                'param_type': param_type,
                'name': field.get('name', ''),
                'description': field.get('description', ''),
                'required': field.get('required', False),
                'data_type': data_type,
                'default_value': field.get('defaultValue', None),
                'allow_multiple': field.get('allowMultiple', False),
                'have_hoices': field.get('choices', None) is not None,
                'choices': field.get('choices', []),
                'minimum': field.get('minimum', None),
                'maximum': field.get('maximum', None),
            }
            params.append(f)
        return params
