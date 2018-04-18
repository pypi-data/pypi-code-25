# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: sawtooth_sdk/protobuf/client_transaction.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from sawtooth_sdk.protobuf import transaction_pb2 as sawtooth__sdk_dot_protobuf_dot_transaction__pb2
from sawtooth_sdk.protobuf import client_list_control_pb2 as sawtooth__sdk_dot_protobuf_dot_client__list__control__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='sawtooth_sdk/protobuf/client_transaction.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n.sawtooth_sdk/protobuf/client_transaction.proto\x1a\'sawtooth_sdk/protobuf/transaction.proto\x1a/sawtooth_sdk/protobuf/client_list_control.proto\"\x95\x01\n\x1c\x43lientTransactionListRequest\x12\x0f\n\x07head_id\x18\x01 \x01(\t\x12\x17\n\x0ftransaction_ids\x18\x02 \x03(\t\x12%\n\x06paging\x18\x03 \x01(\x0b\x32\x15.ClientPagingControls\x12$\n\x07sorting\x18\x04 \x03(\x0b\x32\x13.ClientSortControls\"\xce\x02\n\x1d\x43lientTransactionListResponse\x12\x35\n\x06status\x18\x01 \x01(\x0e\x32%.ClientTransactionListResponse.Status\x12\"\n\x0ctransactions\x18\x02 \x03(\x0b\x32\x0c.Transaction\x12\x0f\n\x07head_id\x18\x03 \x01(\t\x12%\n\x06paging\x18\x04 \x01(\x0b\x32\x15.ClientPagingResponse\"\x99\x01\n\x06Status\x12\x10\n\x0cSTATUS_UNSET\x10\x00\x12\x06\n\x02OK\x10\x01\x12\x12\n\x0eINTERNAL_ERROR\x10\x02\x12\r\n\tNOT_READY\x10\x03\x12\x0b\n\x07NO_ROOT\x10\x04\x12\x0f\n\x0bNO_RESOURCE\x10\x05\x12\x12\n\x0eINVALID_PAGING\x10\x06\x12\x10\n\x0cINVALID_SORT\x10\x07\x12\x0e\n\nINVALID_ID\x10\x08\"5\n\x1b\x43lientTransactionGetRequest\x12\x16\n\x0etransaction_id\x18\x01 \x01(\t\"\xd0\x01\n\x1c\x43lientTransactionGetResponse\x12\x34\n\x06status\x18\x01 \x01(\x0e\x32$.ClientTransactionGetResponse.Status\x12!\n\x0btransaction\x18\x02 \x01(\x0b\x32\x0c.Transaction\"W\n\x06Status\x12\x10\n\x0cSTATUS_UNSET\x10\x00\x12\x06\n\x02OK\x10\x01\x12\x12\n\x0eINTERNAL_ERROR\x10\x02\x12\x0f\n\x0bNO_RESOURCE\x10\x05\x12\x0e\n\nINVALID_ID\x10\x08\x42\x31\n\x15sawtooth.sdk.protobufP\x01Z\x16\x63lient_transaction_pb2b\x06proto3')
  ,
  dependencies=[sawtooth__sdk_dot_protobuf_dot_transaction__pb2.DESCRIPTOR,sawtooth__sdk_dot_protobuf_dot_client__list__control__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_CLIENTTRANSACTIONLISTRESPONSE_STATUS = _descriptor.EnumDescriptor(
  name='Status',
  full_name='ClientTransactionListResponse.Status',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='STATUS_UNSET', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='OK', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INTERNAL_ERROR', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NOT_READY', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NO_ROOT', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NO_RESOURCE', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INVALID_PAGING', index=6, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INVALID_SORT', index=7, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INVALID_ID', index=8, number=8,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=474,
  serialized_end=627,
)
_sym_db.RegisterEnumDescriptor(_CLIENTTRANSACTIONLISTRESPONSE_STATUS)

_CLIENTTRANSACTIONGETRESPONSE_STATUS = _descriptor.EnumDescriptor(
  name='Status',
  full_name='ClientTransactionGetResponse.Status',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='STATUS_UNSET', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='OK', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INTERNAL_ERROR', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NO_RESOURCE', index=3, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INVALID_ID', index=4, number=8,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=806,
  serialized_end=893,
)
_sym_db.RegisterEnumDescriptor(_CLIENTTRANSACTIONGETRESPONSE_STATUS)


_CLIENTTRANSACTIONLISTREQUEST = _descriptor.Descriptor(
  name='ClientTransactionListRequest',
  full_name='ClientTransactionListRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='head_id', full_name='ClientTransactionListRequest.head_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='transaction_ids', full_name='ClientTransactionListRequest.transaction_ids', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='paging', full_name='ClientTransactionListRequest.paging', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sorting', full_name='ClientTransactionListRequest.sorting', index=3,
      number=4, type=11, cpp_type=10, label=3,
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
  serialized_start=141,
  serialized_end=290,
)


_CLIENTTRANSACTIONLISTRESPONSE = _descriptor.Descriptor(
  name='ClientTransactionListResponse',
  full_name='ClientTransactionListResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='ClientTransactionListResponse.status', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='transactions', full_name='ClientTransactionListResponse.transactions', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='head_id', full_name='ClientTransactionListResponse.head_id', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='paging', full_name='ClientTransactionListResponse.paging', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _CLIENTTRANSACTIONLISTRESPONSE_STATUS,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=293,
  serialized_end=627,
)


_CLIENTTRANSACTIONGETREQUEST = _descriptor.Descriptor(
  name='ClientTransactionGetRequest',
  full_name='ClientTransactionGetRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='transaction_id', full_name='ClientTransactionGetRequest.transaction_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=629,
  serialized_end=682,
)


_CLIENTTRANSACTIONGETRESPONSE = _descriptor.Descriptor(
  name='ClientTransactionGetResponse',
  full_name='ClientTransactionGetResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='ClientTransactionGetResponse.status', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='transaction', full_name='ClientTransactionGetResponse.transaction', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _CLIENTTRANSACTIONGETRESPONSE_STATUS,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=685,
  serialized_end=893,
)

_CLIENTTRANSACTIONLISTREQUEST.fields_by_name['paging'].message_type = sawtooth__sdk_dot_protobuf_dot_client__list__control__pb2._CLIENTPAGINGCONTROLS
_CLIENTTRANSACTIONLISTREQUEST.fields_by_name['sorting'].message_type = sawtooth__sdk_dot_protobuf_dot_client__list__control__pb2._CLIENTSORTCONTROLS
_CLIENTTRANSACTIONLISTRESPONSE.fields_by_name['status'].enum_type = _CLIENTTRANSACTIONLISTRESPONSE_STATUS
_CLIENTTRANSACTIONLISTRESPONSE.fields_by_name['transactions'].message_type = sawtooth__sdk_dot_protobuf_dot_transaction__pb2._TRANSACTION
_CLIENTTRANSACTIONLISTRESPONSE.fields_by_name['paging'].message_type = sawtooth__sdk_dot_protobuf_dot_client__list__control__pb2._CLIENTPAGINGRESPONSE
_CLIENTTRANSACTIONLISTRESPONSE_STATUS.containing_type = _CLIENTTRANSACTIONLISTRESPONSE
_CLIENTTRANSACTIONGETRESPONSE.fields_by_name['status'].enum_type = _CLIENTTRANSACTIONGETRESPONSE_STATUS
_CLIENTTRANSACTIONGETRESPONSE.fields_by_name['transaction'].message_type = sawtooth__sdk_dot_protobuf_dot_transaction__pb2._TRANSACTION
_CLIENTTRANSACTIONGETRESPONSE_STATUS.containing_type = _CLIENTTRANSACTIONGETRESPONSE
DESCRIPTOR.message_types_by_name['ClientTransactionListRequest'] = _CLIENTTRANSACTIONLISTREQUEST
DESCRIPTOR.message_types_by_name['ClientTransactionListResponse'] = _CLIENTTRANSACTIONLISTRESPONSE
DESCRIPTOR.message_types_by_name['ClientTransactionGetRequest'] = _CLIENTTRANSACTIONGETREQUEST
DESCRIPTOR.message_types_by_name['ClientTransactionGetResponse'] = _CLIENTTRANSACTIONGETRESPONSE

ClientTransactionListRequest = _reflection.GeneratedProtocolMessageType('ClientTransactionListRequest', (_message.Message,), dict(
  DESCRIPTOR = _CLIENTTRANSACTIONLISTREQUEST,
  __module__ = 'sawtooth_sdk.protobuf.client_transaction_pb2'
  # @@protoc_insertion_point(class_scope:ClientTransactionListRequest)
  ))
_sym_db.RegisterMessage(ClientTransactionListRequest)

ClientTransactionListResponse = _reflection.GeneratedProtocolMessageType('ClientTransactionListResponse', (_message.Message,), dict(
  DESCRIPTOR = _CLIENTTRANSACTIONLISTRESPONSE,
  __module__ = 'sawtooth_sdk.protobuf.client_transaction_pb2'
  # @@protoc_insertion_point(class_scope:ClientTransactionListResponse)
  ))
_sym_db.RegisterMessage(ClientTransactionListResponse)

ClientTransactionGetRequest = _reflection.GeneratedProtocolMessageType('ClientTransactionGetRequest', (_message.Message,), dict(
  DESCRIPTOR = _CLIENTTRANSACTIONGETREQUEST,
  __module__ = 'sawtooth_sdk.protobuf.client_transaction_pb2'
  # @@protoc_insertion_point(class_scope:ClientTransactionGetRequest)
  ))
_sym_db.RegisterMessage(ClientTransactionGetRequest)

ClientTransactionGetResponse = _reflection.GeneratedProtocolMessageType('ClientTransactionGetResponse', (_message.Message,), dict(
  DESCRIPTOR = _CLIENTTRANSACTIONGETRESPONSE,
  __module__ = 'sawtooth_sdk.protobuf.client_transaction_pb2'
  # @@protoc_insertion_point(class_scope:ClientTransactionGetResponse)
  ))
_sym_db.RegisterMessage(ClientTransactionGetResponse)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\025sawtooth.sdk.protobufP\001Z\026client_transaction_pb2'))
# @@protoc_insertion_point(module_scope)
