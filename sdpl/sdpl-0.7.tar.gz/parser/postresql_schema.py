__author__ = 'Bohdan Mushkevych'

from schema.sdpl_schema import Schema, Field, MIN_VERSION_NUMBER, VARCHAR_DEFAULT_LENGTH, FieldType

PGSQL_MAPPING = {
    FieldType.INTEGER.name: 'INTEGER',
    FieldType.LONG.name: 'BIGINT',
    FieldType.FLOAT.name: 'DOUBLE PRECISION',
    FieldType.CHARARRAY.name: 'VARCHAR',
    FieldType.BYTEARRAY.name: 'BYTEA',
    FieldType.BOOLEAN.name: 'BOOLEAN',
    FieldType.DATETIME.name: 'TIMESTAMP',
}


def parse_field(field: Field):
    pgsql_type = PGSQL_MAPPING[field.field_type]
    if field.field_type == 'CHARARRAY':
        length = field.max_length if field.max_length else VARCHAR_DEFAULT_LENGTH
        pgsql_type += '({0})'.format(length)

    out = '{0}\t{1}'.format(field.name, pgsql_type)
    if not field.is_nullable:
        out += '\t{0}'.format('NOT NULL')
    if field.is_unique:
        out += '\t{0}'.format('UNIQUE')
    if field.is_primary_key:
        out += '\t{0}'.format('PRIMARY KEY')
    if field.default:
        out += '\t{0}\t{1}'.format('DEFAULT', field.default)

    return out


def parse_schema(schema: Schema, max_version=MIN_VERSION_NUMBER):
    filtered_fields = [f for f in schema.fields if f.version <= max_version]
    out = ',\n    '.join([parse_field(field) for field in filtered_fields])
    out = '\n    ' + out + '\n'
    return out


def compose_ddl(table_name: str, schema: Schema, max_version: int):
    out = 'CREATE TABLE IF NOT EXISTS {0} ('.format(table_name)
    out += parse_schema(schema, max_version)
    out += ');\n'
    return out
