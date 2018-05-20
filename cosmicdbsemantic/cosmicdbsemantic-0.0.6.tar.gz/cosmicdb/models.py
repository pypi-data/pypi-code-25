from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe

from bs4 import BeautifulSoup

from sitetree.models import TreeItemBase, TreeBase


class User(AbstractUser):

    def unread_notification_no(self):
        return self.usersystemnotification_set.filter(read=False).count()

    def unread_notifications(self):
        return self.usersystemnotification_set.filter(read=False).order_by('-created_at')[:3]

    def read_notifications(self):
        return self.usersystemnotification_set.filter(read=True).order_by('-created_at')[:3]

    def read_notification_no(self):
        return self.usersystemnotification_set.filter(read=True).count()


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'%s' % (self.username)


class UserSystemNotification(models.Model):
    user = models.ForeignKey('User', on_delete=models.PROTECT)
    notification = models.TextField()
    def short_notification(self):
        notification_no_html = BeautifulSoup(self.notification, "html.parser").get_text()
        return notification_no_html[:30]+'..'
    read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return u'%s - %s' % (self.user, self.short_notification())


class CosmicDBTree(TreeBase):
    pass


class CosmicDBTreeItem(TreeItemBase):
    is_right = models.BooleanField(default=False)
    is_button = models.BooleanField(default=False)
