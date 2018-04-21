from django.db import models
import os
import hashlib
import mimetypes


class HoardFile(models.Model):
    path = models.CharField(max_length=256, unique=True, editable=False)
    mtime = models.FloatField(editable=False)
    md5 = models.CharField(max_length=64, editable=False)
    content_type = models.CharField(max_length=32)

    def update(self):
        content_type = mimetypes.guess_type(self.path)[0]
        if not content_type:
            content_type = 'application/octet-stream'
        self.content_type = content_type

        # Update the mtime and md5 fields
        current_mtime = os.path.getmtime(self.path)
        if self.mtime is None or self.mtime < current_mtime:
            current_md5 = hashlib.md5()
            with open(self.path, 'rb') as f:
                data = True
                while data:
                    data = f.read(0x10000)
                    current_md5.update(data)
            self.md5 = current_md5.hexdigest()
            self.mtime = current_mtime
