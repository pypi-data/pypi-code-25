# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: MessageProtocols.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='MessageProtocols.proto',
  package='com.hashmapinc.tempus.edge.proto',
  syntax='proto3',
  serialized_pb=_b('\n\x16MessageProtocols.proto\x12 com.hashmapinc.tempus.edge.proto*7\n\x10MessageProtocols\x12\r\n\tUNDEFINED\x10\x00\x12\n\n\x06\x43ONFIG\x10\x01\x12\x08\n\x04\x44\x41TA\x10\x02\x42\"Z com/hashmapinc/tempus/edge/protob\x06proto3')
)

_MESSAGEPROTOCOLS = _descriptor.EnumDescriptor(
  name='MessageProtocols',
  full_name='com.hashmapinc.tempus.edge.proto.MessageProtocols',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNDEFINED', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CONFIG', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DATA', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=60,
  serialized_end=115,
)
_sym_db.RegisterEnumDescriptor(_MESSAGEPROTOCOLS)

MessageProtocols = enum_type_wrapper.EnumTypeWrapper(_MESSAGEPROTOCOLS)
UNDEFINED = 0
CONFIG = 1
DATA = 2


DESCRIPTOR.enum_types_by_name['MessageProtocols'] = _MESSAGEPROTOCOLS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('Z com/hashmapinc/tempus/edge/proto'))
# @@protoc_insertion_point(module_scope)
