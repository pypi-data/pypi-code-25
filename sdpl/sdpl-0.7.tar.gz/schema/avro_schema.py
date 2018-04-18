__author__ = 'Bohdan Mushkevych'

import avro.schema

from schema import sdpl_schema

# `https://avro.apache.org/docs/1.8.1/spec.html#schema_primitive`
AVRO_MAPPING = {
    'int': sdpl_schema.FieldType.INTEGER,
    'long': sdpl_schema.FieldType.LONG,
    'float': sdpl_schema.FieldType.FLOAT,
    'double': sdpl_schema.FieldType.FLOAT,
    'string': sdpl_schema.FieldType.CHARARRAY,
    'null': sdpl_schema.FieldType.BYTEARRAY,
    'bytes': sdpl_schema.FieldType.BYTEARRAY,
    'boolean': sdpl_schema.FieldType.BOOLEAN,
    'UNDEFINED': sdpl_schema.FieldType.DATETIME,
    'array': sdpl_schema.FieldType.ARRAY,
    'map': sdpl_schema.FieldType.MAP,
    None: None
}


class AvroSchema(object):
    def __init__(self, avro_schema: avro.schema.Schema) -> None:
        self.avro_schema = avro_schema

    def to_sdpl_schema(self):
        def _to_sdpl_field(avro_field):
            field_class = sdpl_schema.Field
            avro_key_type = None    # for type Map
            avro_value_type = None  # for types Array and Map

            if isinstance(avro_field.type, avro.schema.PrimitiveSchema):
                # "type": "string"
                avro_field_type = avro_field.type.type
                is_nullable = False
            elif isinstance(avro_field.type, avro.schema.UnionSchema):
                # "type": ["string", "null"]
                types = set(t.type for t in avro_field.type.schemas)
                if len(types) > 2 or 'null' not in types:
                    raise ValueError('SDPL does not supports AVRO field {0} with types {1}'.
                                     format(avro_field.name, avro_field.type))

                types.remove('null')
                avro_field_type = types.pop()
                is_nullable = True
            elif isinstance(avro_field.type, avro.schema.ArraySchema):
                # {"type": "array", "items": "string"}
                avro_field_type = avro_field.type.type
                avro_value_type = avro_field.type.items.type
                is_nullable = False
                field_class = sdpl_schema.ArrayField
            elif isinstance(avro_field.type, avro.schema.MapSchema):
                # {"type": "map", "values": "long"}
                # per Avro spec, map keys are assumed to be strings
                avro_field_type = avro_field.type.type
                avro_value_type = avro_field.type.values.type
                avro_key_type = 'string'
                is_nullable = False
                field_class = sdpl_schema.MapField
            else:
                raise ValueError(
                    'SDPL does not supports AVRO field {0} with types {1}'.format(avro_field.name, avro_field.type)
                )

            sdpl_field_type = AVRO_MAPPING[avro_field_type]
            sdpl_key_type = AVRO_MAPPING[avro_key_type]
            sdpl_value_type = AVRO_MAPPING[avro_value_type]
            default_value = None if not avro_field.has_default else avro_field.default
            return field_class(name=avro_field.name, field_type=sdpl_field_type,
                               default=default_value, is_nullable=is_nullable,
                               key_type=sdpl_key_type, value_type=sdpl_value_type)

        s = sdpl_schema.Schema()
        for f in self.avro_schema.fields:
            assert isinstance(f, avro.schema.Field)
            s.fields.append(_to_sdpl_field(f))
        return s
