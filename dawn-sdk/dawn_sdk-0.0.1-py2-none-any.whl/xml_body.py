# -*- coding: utf8 -*-

# xml body for request or response.

import xml.etree.ElementTree as ElementTree

from .result import InitMultipartUpload
from .portable import unicode_string

def _find_tag(parent, path):
    child = parent.find(path)
    if child is None:
        raise RuntimeError("parse xml: " + path + " could not be found under " + parent.tag)

    if child.text is None:
        return ''

    return to_string(child.text)

class Parser(object):
  def __init__(self, resp):
    self.resp = resp
    self.body = resp.read()
    self.root = ElementTree.fromstring(self.body)
  
  def init_multipart_upload(self):
    result = InitMultipartUpload(self.resp)
    result.upload_id = _find_tag(self.root, 'UploadId')

    return result

def _add_text_child(parent, tag, text):
  ElementTree.SubElement(parent, tag).text = unicode_string(text)

def _xml_to_string(root):
  return ElementTree.tostring(root, encoding='utf-8')

class PartInfo(object):
  """表示分片信息的文件。

  该文件既用于 :func:`list_parts <dawn.Bucket.list_parts>` 的输出，也用于 :func:`complete_multipart_upload
  <dawn.Bucket.complete_multipart_upload>` 的输入。

  :param int part_number: 分片号
  :param str etag: 分片的ETag
  """
  def __init__(self, part_number, etag):
    self.part_number = part_number
    self.etag = etag

class Maker(object):
  def __init__(self):
    pass

  def complete_upload_request(parts):
    root = ElementTree.Element('CompleteMultipartUpload')
    for p in parts:
      node = ElementTree.SubElement(root, 'Part')
      _add_text_child(node, 'PartNumber', str(p.part_number))
      _add_text_child(node, 'ETag', '"{0}"'.format(p.etag))
    
    return _xml_to_string(root)
      
