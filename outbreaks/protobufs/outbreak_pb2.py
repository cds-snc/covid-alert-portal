# flake8: noqa
# fmt: off
# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: outbreak.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='outbreak.proto',
  package='',
  syntax='proto2',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0eoutbreak.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"\x94\x01\n\rOutbreakEvent\x12\x13\n\x0blocation_id\x18\x01 \x01(\t\x12.\n\nstart_time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12,\n\x08\x65nd_time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x10\n\x08severity\x18\x04 \x01(\r\"\xb9\x01\n\x15OutbreakEventResponse\x12/\n\x05\x65rror\x18\x01 \x01(\x0e\x32 .OutbreakEventResponse.ErrorCode\"o\n\tErrorCode\x12\x08\n\x04NONE\x10\x00\x12\x0b\n\x07UNKNOWN\x10\x01\x12\x0e\n\nINVALID_ID\x10\x02\x12\x15\n\x11MISSING_TIMESTAMP\x10\x03\x12\x12\n\x0ePERIOD_INVALID\x10\x04\x12\x10\n\x0cSERVER_ERROR\x10\x05'
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,])



_OUTBREAKEVENTRESPONSE_ERRORCODE = _descriptor.EnumDescriptor(
  name='ErrorCode',
  full_name='OutbreakEventResponse.ErrorCode',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NONE', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='INVALID_ID', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='MISSING_TIMESTAMP', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='PERIOD_INVALID', index=4, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SERVER_ERROR', index=5, number=5,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=277,
  serialized_end=388,
)
_sym_db.RegisterEnumDescriptor(_OUTBREAKEVENTRESPONSE_ERRORCODE)


_OUTBREAKEVENT = _descriptor.Descriptor(
  name='OutbreakEvent',
  full_name='OutbreakEvent',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='location_id', full_name='OutbreakEvent.location_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='start_time', full_name='OutbreakEvent.start_time', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='end_time', full_name='OutbreakEvent.end_time', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='severity', full_name='OutbreakEvent.severity', index=3,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=52,
  serialized_end=200,
)


_OUTBREAKEVENTRESPONSE = _descriptor.Descriptor(
  name='OutbreakEventResponse',
  full_name='OutbreakEventResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='error', full_name='OutbreakEventResponse.error', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _OUTBREAKEVENTRESPONSE_ERRORCODE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=203,
  serialized_end=388,
)

_OUTBREAKEVENT.fields_by_name['start_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_OUTBREAKEVENT.fields_by_name['end_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_OUTBREAKEVENTRESPONSE.fields_by_name['error'].enum_type = _OUTBREAKEVENTRESPONSE_ERRORCODE
_OUTBREAKEVENTRESPONSE_ERRORCODE.containing_type = _OUTBREAKEVENTRESPONSE
DESCRIPTOR.message_types_by_name['OutbreakEvent'] = _OUTBREAKEVENT
DESCRIPTOR.message_types_by_name['OutbreakEventResponse'] = _OUTBREAKEVENTRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

OutbreakEvent = _reflection.GeneratedProtocolMessageType('OutbreakEvent', (_message.Message,), {
  'DESCRIPTOR' : _OUTBREAKEVENT,
  '__module__' : 'outbreak_pb2'
  # @@protoc_insertion_point(class_scope:OutbreakEvent)
  })
_sym_db.RegisterMessage(OutbreakEvent)

OutbreakEventResponse = _reflection.GeneratedProtocolMessageType('OutbreakEventResponse', (_message.Message,), {
  'DESCRIPTOR' : _OUTBREAKEVENTRESPONSE,
  '__module__' : 'outbreak_pb2'
  # @@protoc_insertion_point(class_scope:OutbreakEventResponse)
  })
_sym_db.RegisterMessage(OutbreakEventResponse)


# @@protoc_insertion_point(module_scope)
