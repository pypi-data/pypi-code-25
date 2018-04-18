__author__ = 'Bohdan Mushkevych'

from io import TextIOWrapper
from typing import Union

from grammar.sdplParser import sdplParser
from parser.abstract_lexicon import AbstractLexicon
from parser.data_store import DataStore
from parser.projection import RelationProjection, FieldProjection, ComputableField
from schema.sdpl_schema import Schema, Field, MIN_VERSION_NUMBER, DataType, Compression, ArrayField, MapField


class PigLexicon(AbstractLexicon):
    def __init__(self, output_stream: TextIOWrapper) -> None:
        super(PigLexicon, self).__init__(output_stream)

    def _jdbc_datasink(self, data_sink: DataStore):
        field_names = [f.name for f in data_sink.relation.schema.fields]
        values = ['?' for _ in range(len(field_names))]

        out = "REGISTER /var/lib/sdpl/postgresql-42.0.0.jar;\n"
        out += "REGISTER /var/lib/sdpl/piggybank-0.16.0.jar;\n"
        out += "STORE {0} INTO 'hdfs:///unused-ignore' ".format(data_sink.relation.name)
        out += "USING org.apache.pig.piggybank.storage.DBStorage(\n"
        out += "    'org.postgresql.Driver',\n"
        out += "    'jdbc:postgresql://{0}:{1}/{2}',\n".format(data_sink.data_repository.host,
                                                               data_sink.data_repository.port,
                                                               data_sink.data_repository.db)
        out += "    '{0}', '{1}',\n".format(data_sink.data_repository.user, data_sink.data_repository.password)
        out += "    'INSERT INTO {0} ({1}) VALUES ({2})'\n".format(data_sink.table_name,
                                                                   ','.join(field_names), ','.join(values))
        out += ');'
        return out

    def _file_datasink(self, data_sink: DataStore):
        if data_sink.data_repository.data_type == DataType.CSV.name:
            store_function = "PigStorage(',')"
        elif data_sink.data_repository.data_type == DataType.TSV.name:
            store_function = "PigStorage()"
        elif data_sink.data_repository.data_type == DataType.BIN.name:
            store_function = "BinStorage()"
        elif data_sink.data_repository.data_type == DataType.JSON.name:
            store_function = "JsonStorage()"
        elif data_sink.data_repository.data_type == DataType.ORC.name:
            is_snappy = data_sink.data_repository.compression == Compression.SNAPPY.name
            store_function = "OrcStorage('-c SNAPPY')" if is_snappy else "OrcStorage()"
        else:
            store_function = "PigStorage()"

        if not data_sink.data_repository.host:
            # local file system
            fqfp = '/{0}/{1}'.format(data_sink.data_repository.db.strip('/'),
                                     data_sink.table_name)
        else:
            # distributed file system
            fqfp = '{0}:{1}/{2}/{3}'.format(data_sink.data_repository.host.strip('/'),
                                            data_sink.data_repository.port,
                                            data_sink.data_repository.db.strip('/'),
                                            data_sink.table_name)

        store_string = "STORE {0} INTO '{1}' USING {2} ;".format(data_sink.relation.name, fqfp, store_function)
        return store_string

    def _jdbc_datasource(self, data_source: DataStore):
        raise NotImplementedError('pig_schema._jdbc_datasource is not supported')

    def _file_datasource(self, data_source: DataStore):
        if data_source.data_repository.data_type == DataType.CSV.name:
            load_function = "PigStorage(',')"
        elif data_source.data_repository.data_type == DataType.TSV.name:
            load_function = "PigStorage()"
        elif data_source.data_repository.data_type == DataType.BIN.name:
            load_function = "BinStorage()"
        elif data_source.data_repository.data_type == DataType.JSON.name:
            load_function = "JsonLoader()"
        elif data_source.data_repository.data_type == DataType.ORC.name:
            is_snappy = data_source.data_repository.compression == Compression.SNAPPY.name
            load_function = "OrcStorage('-c SNAPPY')" if is_snappy else "OrcStorage()"
        else:
            load_function = "PigStorage()"

        if not data_source.data_repository.host:
            # local file system
            fqfp = '/{0}/{1}'.format(data_source.data_repository.db.strip('/'),
                                     data_source.table_name)
        else:
            # distributed file system
            fqfp = '{0}:{1}/{2}/{3}'.format(data_source.data_repository.host.strip('/'),
                                            data_source.data_repository.port,
                                            data_source.data_repository.db.strip('/'),
                                            data_source.table_name)

        load_string = "LOAD '{0}' USING {1} AS ({2})".\
            format(fqfp, load_function, self.parse_schema(data_source.relation.schema))
        return load_string

    @classmethod
    def comment_delimiter(cls):
        return '--'

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
            field_type = "TUPLE()"
        elif isinstance(field, MapField):
            field_type = "MAP[{0}]".format(field.value_type)
        else:
            field_type = field.field_type

        out = '{0}:{1}'.format(field.name, field_type)
        return out

    def parse_field_projection(self, field: Union[FieldProjection, ComputableField]):
        if isinstance(field, ComputableField):
            return '{0} AS {1}'.format(field.expression, field.field_name)
        elif isinstance(field, FieldProjection):
            return '{0}.{1} AS {2}'.format(field.schema_name, field.field_name, field.as_field_name)
        else:
            raise TypeError('Unsupported type for field projection: {0}'.format(type(field)))

    def parse_schema(self, schema: Schema, max_version=MIN_VERSION_NUMBER):
        filtered_fields = [f for f in schema.fields if f.version <= max_version]
        out = ',\n    '.join([self.parse_field(field) for field in filtered_fields])
        out = '\n    ' + out + '\n'
        return out

    def parse_operand(self, ctx: sdplParser.OperandContext):
        # SDPL operand semantics are the same as in Pig
        return ctx.getText()

    def parse_filter_terminal_node(self, element: str) -> tuple:
        # SDPL terminal node are: "AND" "OR" and are the same as in Pig
        return element, None

    def emit_udf_registration(self, udf_fqfp: str, udf_alias:str):
        out = 'REGISTER {0}'.format(udf_fqfp)
        out += ' AS {0};'.format(udf_alias) if udf_alias else ';'
        self._out(out)

    def emit_releation_decl(self, relation_name: str, data_source: DataStore):
        self._out("{0} = {1};".format(relation_name, self.parse_datasource(data_source)))

    def emit_schema_projection(self, left_relation_name: str, right_relation_name: str, output_fields: list):
        """ method iterates over the projection and emits FOREACH ... GENERATE code
            NOTICE: computable fields are placed at the tail of the GENERATE block """
        self._out('{0} = FOREACH {1} GENERATE'.format(left_relation_name, right_relation_name))
        output = ',\n    '.join([self.parse_field_projection(f) for f in output_fields])
        self._out('    ' + output)
        self._out(';')

    def emit_join(self, relation_name: str, column_names: list, projection: RelationProjection) -> None:
        """
        :param relation_name: name of joined relation
        :param column_names: list in format [(relation_name, column_name), ..., (relation_name, column_name)]
        :param projection: 
        :return: None 
        """

        # step 0: reformat list [(relation_name, column_name), ..., (relation_name, column_name)] into
        # dict {relation_name: [column_name, ..., column_name]}
        join_elements = self.column_list_to_dict(column_names)

        # step 1: Generate JOIN name as JOIN_SA_SB_..._SZ
        join_name = 'JOIN'
        join_body = ''
        for element_name, join_columns in join_elements.items():
            join_name += '_' + element_name.upper()

            if not join_body:
                # this is the first cycle of the loop
                join_body = 'JOIN {0} BY '.format(element_name)
            else:
                join_body += ', {0} BY '.format(element_name)

            # format output so it contains relation name: a -> A.a
            join_columns = ['{0}.{1}'.format(element_name, column_name) for column_name in join_columns]
            join_body += '(' + ','.join(join_columns) + ')'

        self._out('{0} = {1} ;'.format(join_name, join_body))

        # step 2: expand schema with FOREACH ... GENERATE
        output_fields = projection.fields + projection.computable_fields
        self.emit_schema_projection(relation_name, join_name, output_fields)

    def emit_filterby(self, relation_name: str, source_relation_name: str, filter_exp: str) -> None:
        self._out('{0} = FILTER {1} BY {2} ;'.format(relation_name, source_relation_name, filter_exp))

    def emit_orderby(self, relation_name: str, source_relation_name: str, column_names: list) -> None:
        # ID = ORDER ID BY relationColumn (, relationColumn)* ;
        by_clause = ['{0}.{1}'.format(*entry) for entry in column_names]
        out = ', '.join(by_clause)
        self._out('{0} = ORDER {1} BY {2} ;'.format(relation_name, source_relation_name, out))

    def emit_groupby(self, relation_name: str, source_relation_name: str, column_names: list):
        # ID = ORDER ID BY relationColumn (, relationColumn)* ;
        by_clause = ['{0}.{1}'.format(*entry) for entry in column_names]
        out = ', '.join(by_clause)
        self._out('{0} = GROUP {1} BY {2} ;'.format(relation_name, source_relation_name, out))
