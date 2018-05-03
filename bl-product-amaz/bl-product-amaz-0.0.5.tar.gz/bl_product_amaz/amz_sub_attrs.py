from bl_product_amaz.database import DataBase

class AMZ_sub_attrs(DataBase):
    def __init__(self):
        super(AMZ_sub_attrs,self).__init__()

    def get_sub_attr_dataset(self, offset=0,limit=0):
        query = {}

        try:
            r = self.db.amz_sub_attrs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        return list(r)

    def get_sub_attr_by_sub_attr_code(self, sub_attr_code):
        query = {}
        query['sub_attr_code'] = sub_attr_code

        try:
            r = self.db.amz_sub_attrs.find(query)
        except Exception as e:
            print(e)

        return list(r)

    def add_count_by_sub_attr_code(self, sub_attr_code):
        query = {}
        query['sub_attr_code'] = sub_attr_code

        try:
            r = self.db.amz_sub_attrs.update( query, {'$inc': {'count': 1}}, upsert=False, multi=False)
        except Exception as e:
            print(e)


