import os

from django.http import FileResponse


class FileAttachmentResponse(FileResponse):
    def __init__(self, *args, **kwargs):
        super(FileAttachmentResponse, self).__init__(*args, **kwargs)
        fp = self.file_to_stream
        if hasattr(fp, 'name'):
            self.set_name(fp.name)
        length = kwargs.get('content_length')
        if length is None:
            # A little faster but won't work for filelike objects
            # os.fstat(f.fileno()).st_size
            pos = fp.tell()
            fp.seek(0, 2)
            length = fp.tell()
            fp.seek(pos)
        self['Content-Length'] = length

    # def set_length(self, length):

    def set_name(self, name):
        # self.setdefault(
            # 'Content-Disposition',
            # 'attachment; filename=%s' % os.path.basename(fp.name))
        fname = os.path.basename(name)
        self['Content-Disposition'] = 'attachment; filename=%s' % fname
