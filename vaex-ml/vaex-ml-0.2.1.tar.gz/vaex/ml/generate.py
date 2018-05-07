import sys
import os
import re

import traitlets

from . import state
from . import transformations
from . import generate

#registry = {}
registry = []
def register(cls):
    registry.append(cls)
    #registry[(cls.__module__, cls.__name__)] = cls
    return cls

def camel_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def generate_vaex_ml():
    from jinja2 import Template
    template_method = Template("""

import {{ module }}
import traitlets

def {{ method_name }}(self, {{ signature }}):
    obj = {{ module }}.{{ class_name }}({{ args }})
    obj.fit(self{{ extra_fit }})
    return obj

import vaex.dataset
vaex.dataset.Dataset.ml._add({{ method_name }}={{ method_name }})

def __init__(self, {{ full_signature }}):
    super({{ module }}.{{ class_name }}, self).__init__({{ full_args }})

{{ module }}.{{ class_name }}.__init__ = __init__
del __init__
    """)
    filename = os.path.join(os.path.dirname(__file__), "generated.py")
    with open(filename, "w") as f:
        for cls in generate.registry:
            traits = {key:value for key, value in cls.class_traits().items() if 'output' not in value.metadata}
            traits_nodefault = {key:value for key, value in traits.items()
                                if value.default_value is traitlets.Undefined}
            traits_default = {key:value for key, value in traits.items()
                                if key not in traits_nodefault}
            signature_list = ["{name}".format(name=name, value=value.default_value)
                for name, value in traits_nodefault.items()]
            signature_list.extend(["{name}={value!r}".format(name=name, value=value.default_value)
                for name, value in traits_default.items()])
            signature = ", ".join(signature_list)
            args = ", ".join(["{name}={name}".format(name=name, value=value)
                for name, value in traits.items()])

            signature_list = ["{name}={value!r}".format(name=name, value=value.default_value)
                for name, value in traits.items()]
            full_signature = ", ".join(signature_list)
            full_args = args

            method_name = camel_to_underscore(cls.__name__)
            module = cls.__module__
            class_name = cls.__name__

            kwargs = dict(locals())
            code = template_method.render(**kwargs)
            print(code, file=f)

def main(argv=sys.argv):
    generate_vaex_ml()
if __name__ == '__main__':
    main()