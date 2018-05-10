from .SphinxDocumentHandler import SphinxDocumentHandler


def setup(app):
    SphinxDocumentHandler.setup_sphinx_extension(app)
