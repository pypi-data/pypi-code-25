import operator
import re
from functools import reduce

import yaml


class YamoleParser():
    """Generic parser that reads YAML files and resolves any JSON references
    it may contain.

    Note:
        The JSON references must be reachable within the local machine, so
        using URLs to external resources (like "example.com/foo.json#/bar")
        won't work.

    Args:
        path: The path where the source YAML file can be found.
        max_depth: The maximum nesting level allowed before aborting
            execution. This limit is set to avoid infinite recursion when
            resolving circular references.
    """
    REF_REGEX = re.compile(r'^([^#]*)(#.*)?$')

    def __init__(self, path, max_depth=1000):
        with open(path, 'r') as file:
            self.data = yaml.load(file)
            self.max_depth = max_depth

            self.data = self.expand(self.data)

    def expand(self, obj, depth=0):
        """Recursively expand an object, considering any potential JSON
        references it may contain.

        See https://tools.ietf.org/html/draft-pbryan-zyp-json-ref-03 for a
        brief description on what a JSON reference is.

        Args:
            obj: The object to expand, which may contain JSON references.
            depth: The current object nesting level.
        """
        if depth > self.max_depth:
            raise RuntimeError('The object has a depth higher than the '
                               'current limit ({}). Maybe the document has '
                               'circular references?'
                               .format(self.max_depth))

        if isinstance(obj, dict):
            for key, value in list(obj.items()):
                if key == '$ref':
                    # Parse the reference's format, which should look
                    # something like:
                    #     some/dir/example.json#/foo/bar
                    uri, route = self.REF_REGEX.match(obj['$ref']).groups()
                    route = route.lstrip('#').strip('/')

                    if uri:
                        # Fetch the local file if an URI was specified
                        with open(uri, 'r') as file:
                            ref_src = yaml.load(file)
                    else:
                        # TODO: This isn't 100% right. The reference's source
                        # can be some other file (e.g. a local reference
                        # inside an external file)
                        ref_src = self.data

                    # Index the ref_src dict with the path
                    ref = reduce(operator.getitem, route.split('/'), ref_src)

                    # Replace the $ref key with the reference's contents
                    del obj['$ref']
                    obj.update(self.expand(ref, depth + 1))

                # This key isn't a reference, but it may contain one somewhere
                self.expand(value, depth + 1)
        elif isinstance(obj, list):
            # If this is a list, expand each item one by one
            obj = [self.expand(item, depth + 1) for item in obj]

        # Return the expanded object to end the recursion
        return obj

    def dumps(self, no_alias=True, full_expansion=True):
        """Dump the parsed object as a YAML-compliant string, using a
        customized PyYAML dumper.

        Args:
            no_alias: Don't use any alias in the result.
            full_expansion: Fully expand objects into YAML format (the default
                PyYAML dumper shows some nested objects as dicts).

        Returns:
            A string with the parsed YAML object.
        """

        dumper = yaml.dumper.SafeDumper

        if no_alias:
            dumper.ignore_aliases = lambda self, data: True

        return yaml.dump(self.data, default_flow_style=not full_expansion,
                         Dumper=dumper)
