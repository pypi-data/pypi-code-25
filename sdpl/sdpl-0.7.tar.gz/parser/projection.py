__author__ = 'Bohdan Mushkevych'

import copy
from collections import Counter
from typing import Union

from parser.relation import Relation
from schema.sdpl_schema import Schema, Field, FieldType


def build_schema(*fields):
    schema = Schema()
    for field in fields:
        assert isinstance(field, Field)
        schema.fields.append(field)
    return schema


class FieldProjection(object):
    def __init__(self, schema_name:str, field_name:str, field:Field, as_field_name:str=None):
        self.schema_name = schema_name
        self.field_name = field_name
        self.as_field_name = as_field_name if as_field_name else field_name
        self.field = copy.deepcopy(field)

        # NOTICE: the schema.sdpl_schema.Field->name is changed here to `as_field_name`
        self.field.name = self.as_field_name

    def __str__(self):
        return '{0}.{1} AS {2}'.format(self.schema_name, self.field_name, self.as_field_name)

    @property
    def schema_field(self):
        return '{0}.{1}'.format(self.schema_name, self.field_name)


class ComputableField(object):
    def __init__(self, field_name:str, field_type:Union[FieldType, str], expression:str):
        self.field_name = field_name
        field_type = FieldType[field_type] if isinstance(field_type, str) else field_type
        self.field = Field(field_name, field_type)
        self.expression = expression

    def __str__(self):
        return '{0} AS {1}'.format(self.expression, self.field_name)


class RelationProjection(object):
    def __init__(self, relations):
        self.relations = relations

        # format list<FieldProjection>
        self.fields = list()

        # format list<FieldProjection>
        self.fields_remove = list()

        # format list<ComputableField>
        self.computable_fields = list()

    def add_all(self, schema_name):
        schema = self.relations[schema_name].schema
        for f in schema.fields:
            self.add(schema_name, f.name)

    def remove_all(self, schema_name):
        schema = self.relations[schema_name].schema
        for f in schema.fields:
            self.remove(schema_name, f.name)

    def add(self, schema_name, field_name, as_field_name=None):
        schema = self.relations[schema_name].schema
        field_proj = FieldProjection(schema_name, field_name, schema[field_name], as_field_name)
        self.fields.append(field_proj)

    def remove(self, schema_name, field_name):
        schema = self.relations[schema_name].schema
        field_proj = FieldProjection(schema_name, field_name, schema[field_name])
        self.fields_remove.append(field_proj)

    def new_field(self, comp_field:ComputableField):
        """ adds a computable field """
        self.computable_fields.append(comp_field)

    def finalize_relation(self, relation_name):
        """ NOTICE: produced relation holds Fields with NAME replaced by AS_FIELD_NAME

            NOTICE: search criteria are different for *remove*, *compute* and *duplicate search*
                    hence - resolve to manual indexing, rather than overriding FieldProjection.__eq__
        """

        def _check_for_duplicates(field_list):
            duplicates = [item for item, count in Counter(field_list).items() if count > 1]
            if duplicates:
                raise ValueError('field {0} is duplicated in the temporary schema'.format(sorted(duplicates)))

        # Step 1: Remove all the requested fields from `fields` collection
        pop_indexes = set()
        schema_field_names = [f.schema_field for f in self.fields]
        for field_proj in self.fields_remove:
            assert isinstance(field_proj, FieldProjection)
            try:
                index = schema_field_names.index(field_proj.schema_field)
                pop_indexes.add(index)
            except ValueError:
                print('WARNING: Referencing non-existent field *{0}* for relation *{1}*'
                      .format(field_proj.schema_field, relation_name))

        # remove items from the tail of the list, so that the smaller indexes are still relevant
        pop_indexes = sorted(pop_indexes, reverse=True)
        for index in pop_indexes:
            self.fields.pop(index)

        # Step 2: Validate that the collection of computed fields contains no duplicates
        comp_field_names = [f.field_name for f in self.computable_fields]
        _check_for_duplicates(comp_field_names)

        # Step 3: Remove fields that are replaced by the `computable fields`
        pop_indexes = set()
        as_field_names = [f.as_field_name for f in self.fields]
        for comp_field in self.computable_fields:
            assert isinstance(comp_field, ComputableField)
            try:
                index = as_field_names.index(comp_field.field_name)
                pop_indexes.add(index)
                print('WARNING: Shadowing existing field *{0}* with computable field in *{1}*'
                      .format(comp_field.field_name, relation_name))
            except ValueError:
                pass

        # remove items from the tail of the list, so that the smaller indexes are still relevant
        pop_indexes = sorted(pop_indexes, reverse=True)
        for index in pop_indexes:
            self.fields.pop(index)

        # Step 4: Validate that the collection of fields contains no duplicates
        as_field_names = [f.as_field_name for f in self.fields]
        _check_for_duplicates(as_field_names)

        # Step 5: build the schema and return it to the caller wrapped in Relation
        union_fields = [f.field for f in self.fields] + [f.field for f in self.computable_fields]
        schema = build_schema(*union_fields)
        relation = Relation(relation_name, None)
        relation._schema = schema
        return relation
