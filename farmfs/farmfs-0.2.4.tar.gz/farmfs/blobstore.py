from fs import Path
from fs import _checksum #XXX bad to use internal
from fs import ensure_link_fd, ensure_readonly
from func_prototypes import typed, returned
from os.path import sep

@returned(basestring)
@typed(basestring, int, int)
def _checksum_to_path(checksum, num_segs=3, seg_len=3):
  segs = [ checksum[i:i+seg_len] for i in range(0, min(len(checksum), seg_len * num_segs), seg_len)]
  segs.append(checksum[num_segs*seg_len:])
  return sep.join(segs)

def _path_to_checksum(address):
  return address.replace(sep, "")

def _validate_checksum(digest, fd):
  csum = _checksum(fd)
  return csum == digest

class BlobStoreFileSystem:
  def __init__(self, root):
    assert isinstance(root, Path)
    self.root = root;

  #TODO make this real
  def has(self, digest):
    pass

  # Note: This is for filesystem based blobstores only.
  def _get_path(self, digest):
    address = _checksum_to_path(digest)
    path = self.root.join(address)
    return path

  #TODO make this real
  def put(self, fd):
    digest = _checksum(fd)
    blob_path = self._get_path(digest)
    if blob_path.exists():
      print "Found a copy of file already in userdata, skipping copy"
    else:
      print "adding %s to blobs" % blob_path
      #TODO this wont work across fs boundaries. Needs copy based fallback.
      ensure_link_fd(blob_path, fd)
      ensure_readonly(blob_path)
    return blob_path

  # TODO make this real
  # XXX We didn't need this for Volume._export_file because
  # of deep linking.
  def get(self, digest, mode):
      path = self._get_path(digest)
      return path.open(mode)

  #TODO make this real
  def delete(self, digest):
    pass

  #TODO make this real
  def list(self):
    for (path, type_) in self.root.entries():
      if type_ == "file":
        rpath = path.relative_to(self.root)
        digest = _path_to_checksum(rpath)
        yield digest

  def validate(self, digest):
    fd = self.get(digest)
    return _validate_checksum(digest, fd)

