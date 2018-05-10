"""Classes used for resolving pointers and externals references."""
from enum import Enum
import re
from urllib.request import urlopen
from jsonpointer import resolve_pointer
import yaml


class ReferenceType(Enum):
    """Type of references

    This Enum is here to provide distinction between varoius type of values
    corresponding to $ref key in deserialized objects:
    - INTERNAL: a reference inside a document (i.e. using usual JSON pointer
      or OpenAPI notation, e.g. #/components/pet)
    - REMOTE: a reference to anything that has protocol specified, e.g.:
      https://remote-host.org/myfile.yml, file:///usr/share/schema.yml
    - LOCAL: anything not falling into above schemas is considered a path to local
      file, e.g.: ./copmonents.yml, definitions.yml
    """
    INTERNAL = 'internal'
    LOCAL = 'local'
    REMOTE = 'remote'


class ReferenceLoader:
    """Class for loading various type references."""

    SCHEMA_REGEXP = '[A-Za-z]+://'

    def __init__(self, load_yaml=yaml.load, open_local=open, open_remote=urlopen):
        self.load_yaml = load_yaml
        self.open_local = open_local
        self.open_remote = open_remote

    @classmethod
    def classify_ref(cls, reference):
        """Classify reference

        :param reference: a reference string to classify.
        :type reference: str
        :returns: value indicating the type of input reference.
        :rtype: ReferenceType

        .. note:
           The perfromed check is pretty basic. In particular all references not
           classified as REMOTE or INTERNAL are automatically classified as
           LOCAL.

        .. seealso:
           :py:class:`ReferenceType`
        """
        if reference.startswith('#') or reference.startswith('/'):
            return ReferenceType.INTERNAL
        if re.match(cls.SCHEMA_REGEXP, reference):
            return ReferenceType.REMOTE
        return ReferenceType.LOCAL

    def load_ref(self, root_doc, reference):
        """Load given reference using given document as root.

        :param root_doc: root document. This is a document (probablyl mapping)
         against which INTERNAL references will be resolved and loaded.
        :type root_doc: Mapping (most probably: MappingProxy)
        :param reference: a reference string
        :type reference: str
        :returns: loaded content of the reference.
        :rtype: The precise type depends on the reference type, root document,
         and `load_yaml` used. The rules are as follows:
         - for external (REMOTE, LOCAL) references the returned value depends on
           what `load_yaml` returns for the content obtained from external resource
         - for INTERNAL references the type depends on the object obtained from
           root document. For MappingProxy this will usually be either another
           MappingProxy or some non-document type (leaf of the document).
        """
        ref_type = self.classify_ref(reference)
        if ref_type == ReferenceType.INTERNAL:
            start = 0 if reference[0] != '#' else 1
            return resolve_pointer(root_doc, reference[start:])
        elif ref_type == ReferenceType.LOCAL:
            with self.open_local(reference) as local:
                return self.load_yaml(local.read())
        else:
            with self.open_remote(reference) as remote:
                return self.load_yaml(remote.read())
