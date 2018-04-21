from pubcontrol.database import *

# Changed 17.04.2018
# Needed to create an Interface for the reference adapter
from abc import ABC, abstractmethod
import datetime

class PostReference(BASE):

    __tablename__ = 'post_reference'

    postID = Column(BigInt, primary_key=True)
    publicationID = Column(BigInt)
    published = Column(DateTime)
    updated = Column(DateTime)

    comments = relationship(
        'CommentReference',
        back_populates='post'
    )


class CommentReference(BASE):

    __tablename__ = 'comment_reference'

    commentID = Column(BigInt, primary_key=True)
    publicationID = Column(BigInt)
    postID = Column(BigInt, ForeignKey('post_reference.postID'))
    published = Column(DateTime)

    post = relationship(
        'PostReference',
        back_populates='comments'
    )


class ReferenceAdapterABC(ABC):

    @abstractmethod
    def adapt_post(self, obj):
        pass

    @abstractmethod
    def adapt_comment(self, obj):
        pass


class ReferenceABC(ABC):

    @abstractmethod
    def contains_post(self, publication_id):
        pass

    @abstractmethod
    def add_post(self, publication, post_id):
        pass

    @abstractmethod
    def contains_comment(self, post_publication_id, comment_publication_id):
        pass

    @abstractmethod
    def add_comment(self, post_publication, comment_publication, comment_id):
        pass


class PublicationReference(ReferenceABC):

    def __init__(self, database_class=MySQLDatabase):
        self.database = database_class()

    def select_publication(self, publication_id):
        return self.database.session.query(PostReference).filter(PostReference.publicationID == publication_id).first()

    def contains_publication(self, publication_id):
        return self.select_publication(publication_id) is not None

    def insert_post_reference(self, reference_dict):
        post_reference = PostReference(
            postID=reference_dict['post'],
            publicationID=reference_dict['publication'],
            published=reference_dict['published'],
            updated=reference_dict['published']
        )

        for comment_reference_dict in reference_dict['comments']:
            comment_reference = CommentReference(
                commentID=comment_reference_dict['comment'],
                postID=comment_reference_dict['post'],
                publicationID=comment_reference_dict['publication'],
                published=comment_reference_dict['published']
            )
            post_reference.comments.append(comment_reference)

        self.database.session.add(post_reference)
        self.database.session.commit()

    def contains_post(self, publication_id):
        return self.get_post(publication_id) is not None

    def add_post(self, publication, post_id):
        post_reference = PostReference(
            postID=post_id,
            publicationID=publication.publicationID,
            published=datetime.datetime.now(),
            updated=datetime.datetime.now()
        )
        self.database.session.add(post_reference)
        self.database.session.commit()

    def get_post(self, publication_id):
        return self.database.session.query(PostReference). \
            filter(PostReference.publicationID == publication_id).first()

    def contains_comment(self, post_publication_id, comment_publication_id):
        return self.database.session.query(PostReference).\
            filter(PostReference.publicationID == post_publication_id).join(CommentReference).\
            filter(CommentReference.publicationID == comment_publication_id).first() is not None

    def add_comment(self, post_publication, comment_publication, comment_id):
        if self.contains_publication(post_publication.publicationID):
            post_reference = self.database.session.query(PostReference).\
                filter(PostReference.publicationID == post_publication.publicationID).first()

            comment_reference = CommentReference(
                commentID=comment_id,
                publicationID=comment_publication.publicationID,
                postID=post_reference.postID,
                published=datetime.datetime.now()
            )

            post_reference.comments.append(comment_reference)
            post_reference.updated = datetime.datetime.now()

            self.database.session.add(post_reference)
            self.database.session.commit()


if __name__ == '__main__':
    print(__name__)