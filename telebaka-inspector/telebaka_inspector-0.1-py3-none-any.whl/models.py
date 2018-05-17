from django.db import models
from uuid import uuid4


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_id = models.CharField(max_length=64)
    message_json = models.TextField()

    def __str__(self):
        return f'#{self.id}'
