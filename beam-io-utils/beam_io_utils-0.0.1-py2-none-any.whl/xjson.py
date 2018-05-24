import json

from apache_beam import PTransform
from apache_beam.coders.coders import StrUtf8Coder
from apache_beam.io import filesystem, filebasedsource, filebasedsink, Write

# TODO: Implement.
# class JSONFileSource(filebasedsource.FileBasedSource):

#   def __init__(
#     self #...
#     ):

#   super(self.__class__, self).__init__(
#     self #...
#     ):


# SEE: `https://docs.python.org/2/library/json.html`
class JSONFileSink(filebasedsink.FileBasedSink):

  def __init__(self,
               file_path_prefix,
               file_name_suffix=".json",
               num_shards=1,
               shard_name_template=None,
               coder=StrUtf8Coder(),
               compression_type=filesystem.CompressionTypes.AUTO,
               indent=None,
               separators=None,
               sort_keys=True,
               lines=False):

    super(self.__class__, self).__init__(
        file_path_prefix=file_path_prefix,
        file_name_suffix=file_name_suffix,
        num_shards=num_shards,
        shard_name_template=shard_name_template,
        coder=coder,
        compression_type=compression_type)

    self.cache = dict()
    self.indent = indent,
    self.separators = separators,
    self.sort_keys = sort_keys,
    self.lines = lines

    if self.lines == True:
      self.indent = 0
      self.separators = (',', ':')
      self.sort_keys = True

  def open(self, temp_path):
    file_handle = super(self.__class__, self).open(temp_path)
    file_handle.write("[")

    if self.lines == True:
      file_handle.write("\n")

    return file_handle

  def write_record(self, file_handle, element):
    if self.cache.get(file_handle, None) is not None:
      value = json.dumps(self.cache[file_handle])
      file_handle.write(self.coder.encode(value))

      file_handle.write(",")

      if self.lines == True:
        file_handle.write("\n")

    self.cache[file_handle] = element

  def close(self, file_handle):
    if file_handle is not None:
      value = json.dumps(self.cache[file_handle])
      file_handle.write(self.coder.encode(value))

      if self.lines == True:
        file_handle.write("\n")

      file_handle.write("]")

    file_handle.close()


# The higher level PTransform.
class WriteToJSON(PTransform):

  def __init__(self,
               file_path_prefix,
               file_name_suffix=".json",
               num_shards=1,
               shard_name_template=None,
               coder=StrUtf8Coder(),
               compression_type=filesystem.CompressionTypes.AUTO,
               indent=None,
               separators=None,
               sort_keys=True,
               lines=False):

    self.sink = JSONFileSink(
        file_path_prefix,
        file_name_suffix=".json",
        num_shards=1,
        shard_name_template=None,
        coder=StrUtf8Coder(),
        compression_type=filesystem.CompressionTypes.AUTO,
        indent=indent,
        separators=separators,
        sort_keys=sort_keys,
        lines=lines)

  def expand(self, collection):
    return collection | Write(self.sink)
