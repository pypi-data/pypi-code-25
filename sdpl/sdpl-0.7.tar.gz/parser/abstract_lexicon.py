__author__ = 'Bohdan Mushkevych'

from io import TextIOWrapper
from collections import OrderedDict

from grammar.sdplParser import sdplParser
from parser.data_store import DataStore
from parser.projection import RelationProjection, FieldProjection
from schema.sdpl_schema import Field, Schema, MIN_VERSION_NUMBER


class AbstractLexicon(object):
    def __init__(self, output_stream: TextIOWrapper) -> None:
        self.output_stream = output_stream

    def _out(self, text):
        self.output_stream.write(text)
        self.output_stream.write('\n')

    def column_list_to_dict(self, column_names:list):
        # reformat list [(relation_name, column_name), ..., (relation_name, column_name)] into
        # dict {relation_name: [column_name, ..., column_name]}
        join_elements = OrderedDict()
        for entry in column_names:
            element_name, entry_column = entry
            if element_name not in join_elements:
                join_elements[element_name] = list()

            join_elements[element_name].append(entry_column)
        return join_elements

    @classmethod
    def comment_delimiter(cls):
        pass

    def parse_datasource(self, data_source: DataStore):
        pass

    def parse_datasink(self, data_sink: DataStore):
        pass

    def parse_field(self, field: Field):
        pass

    def parse_field_projection(self, field: FieldProjection):
        pass

    def parse_schema(self, schema: Schema, max_version=MIN_VERSION_NUMBER):
        pass

    def parse_operand(self, ctx: sdplParser.OperandContext):
        pass

    def parse_filter_terminal_node(self, element: str) -> tuple:
        """
        :param element: 
        :return: (parsed_element, closing_statement) 
        """
        pass

    def emit_udf_registration(self, udf_fqfp: str, udf_alias:str):
        pass

    def emit_releation_decl(self, relation_name: str, data_source: DataStore):
        pass

    def emit_schema_projection(self, left_relation_name: str, right_relation_name: str, output_fields: list):
        pass

    def emit_join(self, relation_name: str, column_names: list, projection: RelationProjection) -> None:
        pass

    def emit_filterby(self, relation_name: str, source_relation_name: str, filter_exp: str) -> None:
        pass

    def emit_orderby(self, relation_name: str, source_relation_name: str, column_names: list) -> None:
        pass

    def emit_groupby(self, relation_name: str, source_relation_name: str, column_names: list) -> None:
        pass
