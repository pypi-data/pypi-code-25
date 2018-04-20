from abc import ABC, abstractmethod

from pubcontrol_wordpress.config import Config

from pubcontrol_wordpress.views import *

from wordpress_xmlrpc import Client, WordPressPost, WordPressComment
from wordpress_xmlrpc.methods.posts import NewPost, DeletePost, GetPost, EditPost
from wordpress_xmlrpc.methods.comments import NewComment


class WordpressABC(ABC):

    def __init__(self, post_view_class, comment_view_class):
        self.post_view_class = post_view_class
        self.comment_view_class = comment_view_class

        self.config = Config()

    @abstractmethod
    def post_publication(self, publication):
        pass

    @abstractmethod
    def comment_citation(self, post_id, publication):
        pass


class Wordpress(WordpressABC):

    def __init__(self,
                 post_view_class=DefaultPostView,
                 comment_view_class=DefaultCommentView):
        super(Wordpress, self).__init__(post_view_class, comment_view_class)
        
        self.config = Config()

        self.url = self.config['WEBSITE']['url']
        self.username = self.config['WEBSITE']['username']
        self.password = self.config['WEBSITE']['password']

        # The client for the wordpress xmlrpc communication
        self.client = Client(
            self.url,
            self.username,
            self.password
        )

    def post_publication(self, publication):
        view = self.post_view_class(publication)

        post = WordPressPost()
        post.title = view.title
        post.excerpt = view.excerpt
        post.slug = view.slug
        post.content = view.content
        post.date = view.date
        post.terms_names = {
            'category': view.categories,
            'post_tag': view.tags
        }
        post.post_status = 'publish'
        post.comment_status = 'closed'

        post_id = self.client.call(NewPost(post))

        return post_id

    def comment_citation(self, post_id, publication):
        self.enable_comments(post_id)

        view = self.comment_view_class(publication)

        comment = WordPressComment()
        comment.content = view.content
        comment.date_created = view.date

        comment_id = self.client.call(NewComment(post_id, comment))
        self.disable_comments(post_id)
        return comment_id

    def enable_comments(self, post_id):
        post = self.client.call(GetPost(post_id))
        post.comment_status = 'open'
        self.client.call(EditPost(post_id, post))

    def disable_comments(self, post_id):
        post = self.client.call(GetPost(post_id))
        post.comment_status = 'closed'
        self.client.call(EditPost(post_id, post))


        

