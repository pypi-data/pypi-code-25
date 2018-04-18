__author__ = 'Bohdan Mushkevych'

from io import TextIOWrapper
from typing import Union

from grammar.sdplParser import sdplParser
from parser.abstract_lexicon import AbstractLexicon
from parser.data_store import DataStore
from parser.projection import RelationProjection, FieldProjection, ComputableField
from schema.sdpl_schema import Schema, Field, MIN_VERSION_NUMBER, DataType, FieldType, ArrayField, MapField

SPARK_MAPPING = {
    FieldType.INTEGER.name: 'IntegerType',
    FieldType.LONG.name: 'LongType',
    FieldType.FLOAT.name: 'FloatType',
    FieldType.CHARARRAY.name: 'StringType',
    FieldType.BYTEARRAY.name: 'BinaryType',
    FieldType.BOOLEAN.name: 'BooleanType',
    FieldType.DATETIME.name: 'TimestampType',
}


class SparkLexicon(AbstractLexicon):
    def __init__(self, output_stream: TextIOWrapper) -> None:
        super(SparkLexicon, self).__init__(output_stream)

    def _jdbc_datasink(self, data_sink: DataStore):
        jdbc_uri = 'jdbc:postgresql://{0}:{1}/{2}'.format(data_sink.data_repository.host,
                                                          data_sink.data_repository.port,
                                                          data_sink.data_repository.db)

        jdbc_properties = "{{ 'user': '{0}', 'password': '{1}' }}".format(data_sink.data_repository.user,
                                                                          data_sink.data_repository.password)
        store_string = "sqlContext.write.jdbc({0}, {1}, properties={2})". \
            format(jdbc_uri, data_sink.table_name, jdbc_properties)

        return store_string

    def _file_datasink(self, data_sink: DataStore):
        if not data_sink.data_repository.host:
            # local file system
            fqfp = "'/{0}/{1}'".format(data_sink.data_repository.db.strip('/'),
                                       data_sink.table_name)
        else:
            # distributed file system
            fqfp = "'{0}:{1}/{2}/{3}'".format(data_sink.data_repository.host.strip('/'),
                                              data_sink.data_repository.port,
                                              data_sink.data_repository.db.strip('/'),
                                              data_sink.table_name)

        if data_sink.data_repository.data_type == DataType.CSV.name:
            store_string = "sqlContext.write.csv({0}, compression='{1}', sep=',')". \
                format(fqfp, data_sink.data_repository.compression)
        elif data_sink.data_repository.data_type == DataType.TSV.name:
            store_string = "sqlContext.write.csv({0}, compression='{1}', sep='\\t')". \
                format(fqfp, data_sink.data_repository.compression)
        elif data_sink.data_repository.data_type == DataType.BIN.name:
            store_string = "TBD"
        elif data_sink.data_repository.data_type == DataType.JSON.name:
            store_string = "sqlContext.write.json({0}, compression='{1}')". \
                format(fqfp, data_sink.data_repository.compression)
        elif data_sink.data_repository.data_type == DataType.ORC.name:
            store_string = "sqlContext.write.orc({0}, compression='{1}')". \
                format(fqfp, data_sink.data_repository.compression)
        else:
            store_string = "sqlContext.write.text({0}, compression='{1}')". \
                format(fqfp, data_sink.data_repository.compression)

        return store_string

    def _jdbc_datasource(self, data_source: DataStore):
        jdbc_uri = 'jdbc:postgresql://{0}:{1}/{2}'.format(data_source.data_repository.host,
                                                          data_source.data_repository.port,
                                                          data_source.data_repository.db)

        jdbc_properties = "{ 'user': '{0}', 'password': '{1}' }".format(data_source.data_repository.user,
                                                                        data_source.data_repository.password)
        load_string = "sqlContext.read.jdbc({0}, {1}, properties={2})". \
            format(jdbc_uri, data_source.table_name, jdbc_properties)

        return load_string

    def _file_datasource(self, data_source: DataStore):
        if not data_source.data_repository.host:
            # local file system
            fqfp = "'/{0}/{1}'".format(data_source.data_repository.db.strip('/'),
                                       data_source.table_name)
        else:
            # distributed file system
            fqfp = "'{0}:{1}/{2}/{3}'".format(data_source.data_repository.host.strip('/'),
                                              data_source.data_repository.port,
                                              data_source.data_repository.db.strip('/'),
                                              data_source.table_name)

        if data_source.data_repository.data_type == DataType.CSV.name:
            load_string = "sqlContext.read.csv({0}, schema={1}, sep=',')". \
                format(fqfp, self.parse_schema(data_source.relation.schema))
        elif data_source.data_repository.data_type == DataType.TSV.name:
            load_string = "sqlContext.read.csv({0}, schema={1}, sep='\\t')". \
                format(fqfp, self.parse_schema(data_source.relation.schema))
        elif data_source.data_repository.data_type == DataType.BIN.name:
            load_string = "TBD"
        elif data_source.data_repository.data_type == DataType.JSON.name:
            load_string = "sqlContext.read.json({0}, schema={1})". \
                format(fqfp, self.parse_schema(data_source.relation.schema))
        elif data_source.data_repository.data_type == DataType.ORC.name:
            load_string = "sqlContext.read.orc({0})".format(fqfp)
        else:
            load_string = "sqlContext.read.text({0})".format(fqfp)

        return load_string

    @classmethod
    def comment_delimiter(cls):
        return '#'

    def parse_datasource(self, data_source: DataStore):
        if data_source.data_repository.is_file_type:
            return self._file_datasource(data_source)
        else:
            return self._jdbc_datasource(data_source)

    def parse_datasink(self, data_sink: DataStore):
        if data_sink.data_repository.is_file_type:
            return self._file_datasink(data_sink)
        else:
            return self._jdbc_datasink(data_sink)

    def parse_field(self, field: Field):
        if isinstance(field, ArrayField):
            value_type = SPARK_MAPPING[field.value_type]
            field_type = "ArrayType({0}, containsNull=True)".format(value_type)
        elif isinstance(field, MapField):
            key_type = SPARK_MAPPING[field.key_type]
            value_type = SPARK_MAPPING[field.value_type]
            field_type = "MapType({0}, {1}, valueContainsNull=True)".format(key_type, value_type)
        else:
            field_type = SPARK_MAPPING[field.field_type]

        out = "StructField('{0}', {1}, {2})".format(field.name, field_type, bool(field.is_nullable))
        return out

    def parse_field_projection(self, field: Union[FieldProjection, ComputableField]):
        if isinstance(field, ComputableField):
            return '{0} AS {1}'.format(field.expression, field.field_name)
        elif isinstance(field, FieldProjection):
            return "col('{0}').alias('{1}')".format(field.field_name, field.as_field_name)
        else:
            raise TypeError('Unsupported type for field projection: {0}'.format(type(field)))

    def parse_schema(self, schema: Schema, max_version=MIN_VERSION_NUMBER):
        filtered_fields = [f for f in schema.fields if f.version <= max_version]
        out = ',\n    '.join([self.parse_field(field) for field in filtered_fields])
        out = 'StructType([\n    {0} ])\n    '.format(out)
        return out

    def parse_operand(self, ctx: sdplParser.OperandContext):
        # give special treatment to the `sdplParser.RelationColumnContext` instances by wrapping them into 'col'
        if len(ctx.children) == 1 and isinstance(ctx.children[0], sdplParser.RelationColumnContext):
            return 'col({0})'.format(ctx.getText())
        else:
            return ctx.getText()

    def parse_filter_terminal_node(self, element: str) -> tuple:
        if element == 'LIKE':
            return '.like(', ')'
        elif element == 'AND':
            return '&', None
        elif element == 'OR':
            return '|', None
        else:
            return element, None

    def emit_udf_registration(self, udf_fqfp: str, udf_alias: str):
        if not udf_alias:
            raise UserWarning('Full REGISTER ... AS ... clause is required for Spark generation while registering {0}'.
                              format(udf_fqfp))

        self._out("sqlContext.udf.register({1}, '{0}')".format(udf_alias, udf_fqfp))

    def emit_releation_decl(self, relation_name: str, data_source: DataStore):
        self._out("{0} = {1}".format(relation_name, self.parse_datasource(data_source)))

    def emit_schema_projection(self, left_relation_name: str, right_relation_name: str, output_fields: list):
        """ method iterates over the projection and emits FOREACH ... GENERATE code
            NOTICE: computable fields are placed at the tail of the GENERATE block """
        self._out('{0} = {1}.select('.format(left_relation_name, right_relation_name))
        output = ',\n    '.join([self.parse_field_projection(f) for f in output_fields])
        self._out('    ' + output)
        self._out(')')

    def emit_join(self, relation_name: str, column_names: list, projection: RelationProjection) -> None:
        """
        :param relation_name: name of joined relation
        :param column_names: list in format [(relation_name, column_name), ..., (relation_name, column_name)]
        :param projection: 
        :return: None 
        """

        def join_criteria(a_relation, a_join_columns, b_relation, b_join_columns):
            logic_tokens = ['({0}.{1} == {2}.{3})'.format(a_relation, a_column, b_relation, b_column)
                            for a_column, b_column in zip(a_join_columns, b_join_columns)]
            return ' & '.join(logic_tokens)

        # step 0: reformat list [(relation_name, column_name), ..., (relation_name, column_name)] into
        # dict {relation_name: [column_name, ..., column_name]}
        join_elements = self.column_list_to_dict(column_names)

        # step 1: Generate JOIN body
        a_join_relation = None
        a_join_columns = None
        join_body = ''
        for element_name, join_columns in join_elements.items():
            if not join_body:
                join_body = '{0}'.format(element_name)
                a_join_relation = element_name
                a_join_columns = join_columns
                continue

            criteria = join_criteria(a_join_relation, a_join_columns, element_name, join_columns)
            a_join_relation = element_name
            a_join_columns = join_columns
            join_body += ".join({0}, {1}, 'left_outer')".format(element_name, criteria)

        # step 2: Generate JOIN name as JOIN_SA_SB_..._SZ and emit join statement
        join_name = 'JOIN_' + '_'.join([element_name.upper() for element_name in join_elements])
        self._out('{0} = {1}'.format(join_name, join_body))

        # step 3: expand schema with FOREACH ... GENERATE
        output_fields = projection.fields + projection.computable_fields
        self.emit_schema_projection(relation_name, join_name, output_fields)

    def emit_filterby(self, relation_name: str, source_relation_name: str, filter_exp: str) -> None:
        self._out('{0} = {1}.filter({2})'.format(relation_name, source_relation_name, filter_exp))

    def emit_orderby(self, relation_name: str, source_relation_name: str, column_names: list) -> None:
        # ID = ID.orderBy(relationColumn (, relationColumn)*) ;
        by_clause = ['{0}.{1}'.format(*entry) for entry in column_names]
        out = ', '.join(by_clause)
        self._out('{0} = {1}.orderBy({2})'.format(relation_name, source_relation_name, out))

    def emit_groupby(self, relation_name: str, source_relation_name: str, column_names: list):
        # ID = ID.groupBy(relationColumn (, relationColumn)*) ;
        by_clause = ['{0}.{1}'.format(*entry) for entry in column_names]
        out = ', '.join(by_clause)
        self._out('{0} = {1}.groupBy({2})'.format(relation_name, source_relation_name, out))
