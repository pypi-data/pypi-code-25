__author__ = 'Bohdan Mushkevych'

from google.protobuf import message, descriptor

from schema import sdpl_schema

# `google.protobuf.descriptor.FieldDescriptor`
PROTOBUF_MAPPING = {
    descriptor.FieldDescriptor.TYPE_DOUBLE: sdpl_schema.FieldType.FLOAT,
    descriptor.FieldDescriptor.TYPE_FLOAT: sdpl_schema.FieldType.FLOAT,
    descriptor.FieldDescriptor.TYPE_INT64: sdpl_schema.FieldType.LONG,
    descriptor.FieldDescriptor.TYPE_UINT64: sdpl_schema.FieldType.LONG,
    descriptor.FieldDescriptor.TYPE_INT32: sdpl_schema.FieldType.INTEGER,
    descriptor.FieldDescriptor.TYPE_FIXED64: sdpl_schema.FieldType.LONG,
    descriptor.FieldDescriptor.TYPE_FIXED32: sdpl_schema.FieldType.INTEGER,
    descriptor.FieldDescriptor.TYPE_BOOL: sdpl_schema.FieldType.BOOLEAN,
    descriptor.FieldDescriptor.TYPE_STRING: sdpl_schema.FieldType.CHARARRAY,
    descriptor.FieldDescriptor.TYPE_GROUP: sdpl_schema.FieldType.UNSUPPORTED,
    descriptor.FieldDescriptor.TYPE_BYTES: sdpl_schema.FieldType.BYTEARRAY,
    descriptor.FieldDescriptor.TYPE_UINT32: sdpl_schema.FieldType.INTEGER,
    descriptor.FieldDescriptor.TYPE_ENUM: sdpl_schema.FieldType.CHARARRAY,
    descriptor.FieldDescriptor.TYPE_SFIXED32: sdpl_schema.FieldType.INTEGER,
    descriptor.FieldDescriptor.TYPE_SFIXED64: sdpl_schema.FieldType.LONG,
    descriptor.FieldDescriptor.TYPE_SINT32: sdpl_schema.FieldType.INTEGER,
    descriptor.FieldDescriptor.TYPE_SINT64: sdpl_schema.FieldType.LONG,
    None: None
}


class ProtobufSchema(object):
    def __init__(self, proto_schema: message.Message) -> None:
        self.proto_schema = proto_schema

    def _is_map_entry(self, field: descriptor.FieldDescriptor):
        return (field.type == descriptor.FieldDescriptor.TYPE_MESSAGE and
                field.message_type.has_options and
                field.message_type.GetOptions().map_entry)

    def _is_array_entry(self, field: descriptor.FieldDescriptor):
        return field.label == descriptor.FieldDescriptor.LABEL_REPEATED

    def _parse_array_element(self, schema_element: descriptor.FieldDescriptor):
        sdpl_value_type = PROTOBUF_MAPPING[schema_element.type]
        default_value = None if not schema_element.has_default_value else schema_element.default_value
        return sdpl_schema.ArrayField(name=schema_element.name, value_type=sdpl_value_type,
                                      default=default_value, is_nullable=False)

    def _parse_map_element(self, schema_element: descriptor.FieldDescriptor):
        proto_key_type = schema_element.message_type.fields_by_name['key'].type
        proto_value_type = schema_element.message_type.fields_by_name['value'].type

        sdpl_key_type = PROTOBUF_MAPPING[proto_key_type]
        sdpl_value_type = PROTOBUF_MAPPING[proto_value_type]

        default_value = None if not schema_element.has_default_value else schema_element.default_value
        return sdpl_schema.MapField(name=schema_element.name, key_type=sdpl_key_type, value_type=sdpl_value_type,
                                    default=default_value, is_nullable=False)

    def _parse_primitive(self, schema_element: descriptor.FieldDescriptor):
        sdpl_field_type = PROTOBUF_MAPPING[schema_element.type]
        default_value = None if not schema_element.has_default_value else schema_element.default_value
        return sdpl_schema.Field(name=schema_element.name, field_type=sdpl_field_type,
                                 default=default_value, is_nullable=False)

    def _parse_message(self, msg: message.Message):
        s = sdpl_schema.Schema()
        for element in msg.DESCRIPTOR.fields:
            if self._is_map_entry(element):
                s.fields.append(self._parse_map_element(element))
            elif self._is_array_entry(element):
                s.fields.append(self._parse_array_element(element))
            elif element.type == element.TYPE_MESSAGE:
                s.fields.append(self._parse_message(element))
            else:
                s.fields.append(self._parse_primitive(element))
        return s

    def to_sdpl_schema(self):
        return self._parse_message(self.proto_schema)
