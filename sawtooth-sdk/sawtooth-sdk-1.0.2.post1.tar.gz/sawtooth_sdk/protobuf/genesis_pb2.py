# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: sawtooth_sdk/protobuf/genesis.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from sawtooth_sdk.protobuf import batch_pb2 as sawtooth__sdk_dot_protobuf_dot_batch__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='sawtooth_sdk/protobuf/genesis.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n#sawtooth_sdk/protobuf/genesis.proto\x1a!sawtooth_sdk/protobuf/batch.proto\"&\n\x0bGenesisData\x12\x17\n\x07\x62\x61tches\x18\x01 \x03(\x0b\x32\x06.BatchB&\n\x15sawtooth.sdk.protobufP\x01Z\x0bgenesis_pb2b\x06proto3')
  ,
  dependencies=[sawtooth__sdk_dot_protobuf_dot_batch__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_GENESISDATA = _descriptor.Descriptor(
  name='GenesisData',
  full_name='GenesisData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='batches', full_name='GenesisData.batches', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=74,
  serialized_end=112,
)

_GENESISDATA.fields_by_name['batches'].message_type = sawtooth__sdk_dot_protobuf_dot_batch__pb2._BATCH
DESCRIPTOR.message_types_by_name['GenesisData'] = _GENESISDATA

GenesisData = _reflection.GeneratedProtocolMessageType('GenesisData', (_message.Message,), dict(
  DESCRIPTOR = _GENESISDATA,
  __module__ = 'sawtooth_sdk.protobuf.genesis_pb2'
  # @@protoc_insertion_point(class_scope:GenesisData)
  ))
_sym_db.RegisterMessage(GenesisData)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\025sawtooth.sdk.protobufP\001Z\013genesis_pb2'))
# @@protoc_insertion_point(module_scope)
