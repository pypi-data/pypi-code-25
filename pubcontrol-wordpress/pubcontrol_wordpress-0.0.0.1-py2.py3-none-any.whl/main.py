from abc import ABC, abstractmethod

from pubcontrol.register import *
from pubcontrol.plugin import hookimpl

from pubcontrol_wordpress.views import DefaultPostView, DefaultCommentView
from pubcontrol_wordpress.reference import PublicationReference
from pubcontrol_wordpress.wordpress import Wordpress

import logging


class FilterABC(ABC):

    def __init__(self, register):
        self.register = register

    @abstractmethod
    def get_list(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def __iter__(self):
        pass


class ScopusFilter(FilterABC):

    def __init__(self, register):
        super(ScopusFilter, self).__init__(register)
        self.list = []

    def _process(self):
        natural_publications = self.register.query(Publication).join(Origin).filter(
            and_(
                Origin.name == 'scopus',
                Origin.type == 'PUBLICATION'
            )
        ).all()

        collaboration_publications = self.register.query(Publication).join(Origin).filter(
            and_(
                Origin.name == 'scopus',
                Origin.type == 'COLLABORATION'
            )
        ).all()
        self.list += natural_publications
        self.list += collaboration_publications

    def get_list(self):
        return self.list

    def __iter__(self):
        self._process()
        return iter(self.list)

    def __len__(self):
        return len(self.list)


class ControllerABC(ABC):

    @abstractmethod
    def run(self):
        pass


class Controller:

    def __init__(self,
                 register,
                 filter_class=ScopusFilter,
                 reference_class=PublicationReference,
                 wordpress_class=Wordpress
                 ):
        self.logger = logging.getLogger('wordpress')
        self.reference = reference_class()
        self.filter = filter_class(register)
        self.register = register
        self.wordpress = wordpress_class()

        self.logger.info('[Wordpress] Controller init finalized')

    def run(self):
        publications = list(self.filter)
        self.logger.info('[process] fetched a list of {} publications from register'.format(len(publications)))

        for publication in publications:
            self.logger.info('[process] Starting publication {}'.format(publication.publicationID))
            if not self.reference.contains_publication(publication.publicationID):
                post_id = self.wordpress.post_publication(publication)
                self.reference.add_post(publication, post_id)
                self.logger.info('[process] publication {} posted {}'.format(publication.publicationID, post_id))
            else:
                post_reference = self.reference.get_post(publication.publicationID)
                post_id = post_reference.postID
                self.logger.info('[process] publication {} exits {}'.format(publication.publicationID, post_id))

            for comment in publication.citedby:

                if not self.reference.contains_comment(publication.publicationID, comment.publicationID):
                    comment_id = self.wordpress.comment_citation(post_id, comment)
                    self.reference.add_comment(publication, comment, comment_id)
                    self.logger.info('[process] publication {} comment {} to post {}'.format(
                        comment.publicationID,
                        comment_id,
                        post_id
                    ))


class Plugin:

    def __init__(self,
                 controller_class=Controller):
        self.controller_class = controller_class

    @hookimpl
    def process(self, register):
        controller = self.controller_class(register)
        controller.run()

    @hookimpl
    def register_models(self):
        import pubcontrol_wordpress.reference as ref
        return ref.__name__
