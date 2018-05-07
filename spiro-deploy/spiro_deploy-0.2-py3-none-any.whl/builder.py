import tarfile
import io
import os


def is_vcs(fname):
    """
    Checks if this path looks like it's a VCS metadata directory
    """
    # TODO
    return False

def mktarinfo(data, **args):
    """
    Convenience function to synthesize a TarInfo
    """
    ti = tarfile.TarInfo()
    ti.size = len(data)
    ti.type = tarfile.REGTYPE
    for name, value in args.items():
        setattr(ti, name, value)
    return ti, io.BytesIO(data)


class TarballBuilder:
    """
    Builds up a deployment bundle.
    >>> with TarballBuilder() as builder:
    ...     ...

    >>> builder.buffer
    """
    def __enter__(self):
        """
        Initialize the buffer and tar metadata
        """
        self.buffer = io.BytesIO()
        self._tf = tarfile.TarFile(fileobj=self.buffer, mode='w')
        self._tf.__enter__()
        return self

    def __exit__(self, *args):
        """
        Close out the tar data and resets the buffer for external user
        """
        rv = self._tf.__exit__(*args)
        self.buffer.seek(0)
        return rv
    
    def add_saltdir(self, dirname):
        """
        Add a salt data directory (_salt)
        """
        for fname in os.listdir(dirname):
            self._tf.add(os.path.join(dirname, fname), fname, exclude=is_vcs)

    def add_artifact(self, path, name):
        """
        Add a build artifact (into _artifacts)
        """
        self._tf.add(path, os.path.join('_artifacts', name))

    def add_virtual(self, path, data):
        """
        Add a synthesized file
        """
        self._tf.addfile(
            *mktarinfo(data, name=path)
        )

    def add_gitcommit(self, path=None):
        """
        Tag with the git commit data
        """
        # TODO
        self.add_virtual('.gitcommit', b'TODO')

