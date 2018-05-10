"""Publicly exposed API."""
from io import StringIO
import yaml
from ymlref.proxies import MappingProxy
from ymlref.ref_loaders import ReferenceLoader


def load(stream, ref_loader=None, raw_loader=yaml.load):
    """Load YAML docfrom a given stream.

    :param stream: file-like object to read a document from.
    :type stream: file-like
    :param ref_loader: ReferenceLoader to further lazily resolve and load
     references present in the document. If None, the default one using yaml.load,
     open and urlopen functions is created.
    :type ref_loader: :py:class:`ReferenceLoader`
    :param raw_loader: a callable to use to load the raw document before making a proxy out of it.
     by default uses :py:func:`yaml.load` function fro `pyaml` package.
    :type raw_loader: callable.
    :rtype: :py:class:`ymlref.proxies.MappingProxy`
    """
    ref_loader = ref_loader if ref_loader is not None else ReferenceLoader()
    return MappingProxy(raw_loader(stream), ref_loader=ref_loader)

def loads(document_str, ref_loader=None, raw_loader=yaml.load):
    """Load YAML doc from a given string.

    This is just a wrapper around `load` function, which passes it `document_str` in `StringIO`.
    """
    return load(StringIO(document_str), ref_loader, raw_loader)
