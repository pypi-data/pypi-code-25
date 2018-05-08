from bl_product_amaz.database import DataBase

class AMZ_sub_attrs(DataBase):
    def __init__(self):
        super(AMZ_sub_attrs,self).__init__()
        self.amz_sub_attrs = self.db.amz_sub_attrs

    def get_sub_attr_dataset(self, offset=0,limit=0):
        query = {}
        sub_attrs = []

        try:
            r = self.amz_sub_attrs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        for sub_attr in list(r):
            del sub_attr['_id']
            sub_attrs.append(sub_attr)

        return sub_attrs


    def get_sub_attr_by_sub_attr_code(self, sub_attr_code):
        query = {}
        query['sub_attr_code'] = sub_attr_code
        sub_attrs = []

        try:
            r = self.amz_sub_attrs.find(query)
        except Exception as e:
            print(e)

        for sub_attr in list(r):
            del sub_attr['_id']
            sub_attrs.append(sub_attr)

        return sub_attrs

    def add_count_by_sub_attr_code(self, sub_attr_code):
        query = {}
        query['sub_attr_code'] = sub_attr_code

        try:
            r = self.amz_sub_attrs.update( query, {'$inc': {'count': 1}}, upsert=False, multi=False)
        except Exception as e:
            print(e)


