from staff_info.models import model_list

from staff_info.settings import connector

class Manager:
    """
    Proxy class, that make sql request to DB
    """


    def __init__(self, model):
        self.connector = connector
        self.model = model

    def _create_objects(self, **kwargs):
        def _create_parameters(model, **kwargs):
            """
            Create sql parameters, placeholders for model. String is forming from model
            parameters.
            Values are extracted from kwargs parameters.
            """
            fields = model.fields
            pk, flag = model.primary_key[0], model.primary_key[1]
            obj = model(**kwargs) #
            column_list = ','.join(fields)
            values = []
            if flag['auto_increment']:
                kwargs[pk] = 'Null'
            [values.append(obj[field]) for field in fields]
            assert len(model.fields) == len(values)
            placeholders = ['%s' for _ in values]
            placeholders_str = ', '.join(placeholders)
            sql = "INSERT INTO {} ({}) VALUES ({});".format(model.table_name, column_list,
                                                            placeholders_str)
            return sql, values

        sql, parameters = _create_parameters(self.model, **kwargs) # sql for creating primary object
        self.connector.execute_sql(sql, *parameters)
        last_row = self.connector.last_row_id
        related_models = self.model.get_related_models(*model_list)
        sql_list = []
        for model in related_models:
            sql_row, values_list = _create_parameters(model, **kwargs)
            values_list[0] = last_row
            sql_list.append((sql_row, values_list))
            # try:
        self.connector.execute_sql_in_transaction(*sql_list)
            # except:
            #     print('Something wrong')
        self.connector.close()

    def create_object(self, **kwargs):
        self._create_objects(**kwargs)

    def create_related_object(self, obj, related_model, **kwargs):
        # Add foreign key to dict parameters
        fk = obj.primary_key[0]
        kwargs[fk] = obj[fk]
        related_obj = related_model(**kwargs)
        self._create_objects(related_model, **related_obj.__dict__)

    def select_object(self, model, **conditions):
        pass

    def get_all(self):
        sql = "SELECT * FROM {};".format(self.model.table_name)
        result = connector.execute_sql(sql, change=False)
        # print(result)
        for item in result:
            e_dict = {}
            for k, v in zip(self.model.fields, item):
                e_dict[k] = v
            self.model(**e_dict)
        return self.model.objects

    def select_related_object(self, model, related_model, **conditions):
        pass

    def get_related_last(self, obj, related_model):
        pk = obj.primary_key[0]
        related_table = related_model.table_name
        select_row = 'SELECT * FROM {}'.format(related_model.table_name)
        where_condition = ' WHERE {}={} and id in '.format(pk, obj[pk])
        inner_select = '(SELECT MAX(id) FROM {} GROUP BY {})'.format(related_table, pk)
        sql = select_row + where_condition + inner_select
        result = connector.execute_sql(sql, change=False)
        return result

