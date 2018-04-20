from abc import ABC, abstractmethod

from pubcontrol_wordpress.config import Config

import jinja2

# Added 19.04.2018
# Needed logging for seeing the origin type during view creation
import logging


class WordpressViewABC(ABC):

    def __init__(self, publication):
        self.publication = publication
        self.config = Config()
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.config.TEMPLATE_PATH))
        )


class PostViewABC(WordpressViewABC):

    @property
    @abstractmethod
    def title(self):
        pass

    @property
    @abstractmethod
    def date(self):
        pass

    @property
    @abstractmethod
    def slug(self):
        pass

    @property
    @abstractmethod
    def content(self):
        pass

    @property
    @abstractmethod
    def excerpt(self):
        pass

    @property
    @abstractmethod
    def tags(self):
        pass

    @property
    @abstractmethod
    def categories(self):
        pass


class CommentViewABC(WordpressViewABC):

    @property
    @abstractmethod
    def date(self):
        pass

    @property
    @abstractmethod
    def content(self):
        pass


class DefaultPostView(PostViewABC):

    def __init__(self, publication, template_name='post.j2', author_limit=10):
        super(DefaultPostView, self).__init__(publication)
        self.template = self.env.get_template(template_name)
        self.author_limit = author_limit
        self.logger = logging.getLogger(Config().NAME)

    @property
    def title(self):
        return self.publication.title.encode('utf-8')

    @property
    def date(self):
        return self.publication.published

    @property
    def slug(self):
        return str(self.publication.publicationID)

    @property
    def content(self):
        return self.template.render(
            authors=self._authors(),
            journal=self.publication.journal.name,
            volume=self.publication.journal.volume,
            year=self.publication.published.year,
            doi=self.publication.doi,
            description=self.publication.description,
            links=self.env.get_template('button.j2').render(doi=self.publication.doi)
        )

    @property
    def excerpt(self):
        return u''

    @property
    def tags(self):
        return list(map(
            lambda t: t.content,
            self.publication.tags
        ))

    @property
    def categories(self):
        """
        CHANGELOG

        Changed 19.04.2018
        Added the functionality, that based on the type of publication an corresponding
        :return:
        """
        categories = list(map(
            lambda c: c.content,
            self.publication.categories
        ))
        self.logger.info('[view] {} origin type: {}'.format(self.publication.publicationID, self.publication.origin.type))
        if self.publication.origin.type == 'PUBLICATION':
            categories.append('Publication')
        if self.publication.collaboration.name != 'none':
            categories.append('Collaboration')
        return categories

    def _authors(self):
        author_list = []
        for author in self.publication.authors:
            try:
                index_name = '{}. {}'.format(
                    author.first_name[0].upper(),
                    author.last_name
                )
                author_list.append(index_name)
            # In case there is a index error, that means the first name of the author does not even contain a single
            # character in which case it is useless to even add this string to the list of authors
            except IndexError:
                continue
        if len(author_list) >= self.author_limit:
            author_list = author_list[:self.author_limit]
        return ', '.join(author_list)


class DefaultCommentView(CommentViewABC):

    def __init__(self, publication, template_name='comment.j2'):
        super(DefaultCommentView, self).__init__(publication)
        self.template = self.env.get_template(template_name)

    @property
    def content(self):
        return self.template.render(
            title=self.publication.title,
            journal=self.publication.journal.name,
            volume=self.publication.journal.volume,
            year=self.publication.published.year,
            index_name=self._author_name()
        )

    @property
    def date(self):
        return self.publication.published

    def _author_name(self):
        """
        CHANGELOG
        
        Changed 19.04.2018:
        The publication is a Publication model from regoster, which has no attribute creator thus, assumes that the 
        creator is the first author of the publication and uses that name
        :return: 
        """
        try:
            creator = self.publication.authors[0]
            return '{}. {}'.format(creator.first_name[0], creator.last_name)
        except IndexError:
            return ''
