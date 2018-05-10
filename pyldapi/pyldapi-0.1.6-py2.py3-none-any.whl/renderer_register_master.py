import os.path
from abc import ABCMeta
from flask import render_template, Response
import jinja2
from rdflib import Graph, URIRef, RDF, RDFS, XSD, Namespace, Literal
from .pyldapi import PYLDAPI
from .renderer import Renderer


class RegisterMasterRenderer(Renderer):
    __metaclass__ = ABCMeta

    def __init__(self, register_tree, template, page=None, per_page=None):
        Renderer.__init__(self)

        self.register_uri = 'http://localhost:5000/'
        self.uri = 'http://purl.org/linked-data/registry#Register'
        self.description = 'This API\'s mater Register of Registers'
        self.register_page = []
        self.register_total_count = None
        self.page = page if page is not None else 1
        self.per_page = per_page if per_page is not None else 10
        self.template = template
        self.g = None

        self.register_tree = register_tree
        self.paging_params()

    def render(self, view, mimetype):
        """This method must be implemented by all classes that inherit from Renderer

        :param view: a model view available for this class instance
        :param mimetype: a mimetype string, e.g. text/html
        :return: a Flask Response object
        """
        # alternates view is handled by the pyldapi
        if mimetype == 'text/html':
            return render_template(self.template, register_tree=self.register_tree)
        else:
            self._make_reg_graph(view)
            rdflib_format = PYLDAPI.get_rdf_parser_for_mimetype(mimetype)
            return Response(
                self.g.serialize(format=rdflib_format),
                status=200,
                mimetype=mimetype,
                headers=self.headers
            )
            
    @staticmethod
    def views_formats(description=None):
        """
        return this register's supported views and mimetypes for each view
        """
        return {
            'default': 'reg',
            'alternates': {
                'mimetypes': [
                    'text/html', 'text/turtle', 'application/rdf+xml', 'application/rdf+json', 'application/json'],
                'default_mimetype': 'text/html',
                'namespace': 'http://www.w3.org/ns/ldp#Alternates',
                'description': 'The view listing all other views of this class of object'
            },
            'reg': {
                'mimetypes': ['text/html', 'text/turtle', 'application/rdf+xml', 'application/rdf+json'],
                'default_mimetype': 'text/html',
                'namespace': 'http://purl.org/linked-data/registry#',
                'description':
                    'The Registry Ontology. Core ontology for linked data registry services. Based on ISO19135 but '
                    'heavily modified to suit Linked Data representations and applications',
                'containedItemClass': 'http://purl.org/linked-data/registry#Register'
            },
            'description':
                'This is the Master Register containing all the registers within this Linked Data API.'
        }

    def paging_params(self):
        self.page = int(self.page) if self.page is not None else 1

        links = list()
        links.append('<http://www.w3.org/ns/ldp#Resource>; rel="type"')
        # signalling that this is, in fact, a resource described in pages
        links.append('<http://www.w3.org/ns/ldp#Page>; rel="type"')
        links.append('<{}?per_page={}>; rel="first"'.format(self.register_uri, self.per_page))

        # if this isn't the first page, add a link to "prev"
        if self.page != 1:
            links.append('<{}?per_page={}&page={}>; rel="prev"'.format(
                self.register_uri,
                self.per_page,
                (self.page - 1)
            ))

        # if this isn't the first page, add a link to "prev"
        if self.page != 1:
            self.prev_page = self.page - 1
            links.append('<{}?per_page={}&page={}>; rel="prev"'.format(
                self.register_uri,
                self.per_page,
                self.prev_page
            ))
        else:
            self.prev_page = None

        # add a link to "next" and "last"
        try:
            self.last_page = int(round(self.register_total_count / self.per_page, 0)) + 1  # same as math.ceil()

            # if we've gotten the last page value successfully, we can choke if someone enters a larger value
            if self.page > self.last_page:
                return Response(
                    'You must enter either no value for page or an integer <= {} which is the last page number.'
                    .format(self.last_page),
                    status=400,
                    mimetype='text/plain'
                )

            # add a link to "next"
            if self.page != self.last_page:
                self.next_page = self.page + 1
                links.append('<{}?per_page={}&page={}>; rel="next"'
                             .format(self.register_uri, self.per_page, (self.page + 1)))
            else:
                self.next_page = None

            # add a link to "last"
            links.append('<{}?per_page={}&page={}>; rel="last"'
                         .format(self.register_uri, self.per_page, self.last_page))
        except:
            # if there's some error in getting the no of samples, add the "next" link but not the "last" link
            self.next_page = self.page + 1
            links.append('<{}?per_page={}&page={}>; rel="next"'
                         .format(self.register_uri, self.per_page, (self.page + 1)))
            self.last_page = None

        self.headers = {
            'Link': ', '.join(links)
        }

    def render_html(self, tpl_path, context):
        path, filename = os.path.split(tpl_path)
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(path or './')
        ).get_template(filename).render(context)

    def render_rdf(self, view, format):
        g = Graph()

        if view == 'reg':  # reg is default
            REG = Namespace('http://purl.org/linked-data/registry#')
            g.bind('reg', REG)

            LDP = Namespace('http://www.w3.org/ns/ldp#')
            g.bind('ldp', LDP)

            XHV = Namespace('https://www.w3.org/1999/xhtml/vocab#')
            g.bind('xhv', XHV)

            register_uri = URIRef(self.register_uri)
            g.add((register_uri, RDF.type, REG.Register))
            g.add((register_uri, RDFS.label, Literal('Register', datatype=XSD.string)))

            page_uri_str = self.register_uri
            if self.per_page is not None:
                page_uri_str += '?per_page=' + str(self.per_page)
            else:
                page_uri_str += '?per_page=100'
            page_uri_str_no_page_no = page_uri_str + '&page='
            if self.page is not None:
                page_uri_str += '&page=' + str(self.page)
            else:
                page_uri_str += '&page=1'
            page_uri = URIRef(page_uri_str)

            # pagination
            # this page
            g.add((page_uri, RDF.type, LDP.Page))
            g.add((page_uri, LDP.pageOf, register_uri))

            # links to other pages
            g.add((page_uri, XHV.first, URIRef(page_uri_str_no_page_no + '1')))
            g.add((page_uri, XHV.last, URIRef(page_uri_str_no_page_no + str(self.last_page))))

            if self.page != 1:
                g.add((page_uri, XHV.prev, URIRef(page_uri_str_no_page_no + str(self.page - 1))))

            if self.page != self.last_page:
                g.add((page_uri, XHV.next, URIRef(page_uri_str_no_page_no + str(self.page + 1))))

            # add all the items
            for item in self.register_page:
                if isinstance(item, tuple):  # if it's a tuple, add in the label
                    item_uri = URIRef(item[0])
                    g.add((item_uri, RDF.type, URIRef(self.uri)))
                    g.add((item_uri, RDFS.label, Literal(item[1], datatype=XSD.string)))
                    g.add((item_uri, REG.register, page_uri))
                else:  # just URIs
                    item_uri = URIRef(item)
                    g.add((item_uri, RDF.type, URIRef(self.uri)))
                    g.add((item_uri, REG.register, page_uri))

            # serialize the RDF in whichever format was selected by the user, after converting from mimtype
            return g.serialize(format=PYLDAPI.get_rdf_parser_for_mimetype(format))