from bl_product_amaz.database import DataBase

class AMZ_attrs(DataBase):
    def __init__(self):
        super(AMZ_attrs, self).__init__()
        self.amz_attrs = self.db.amz_attrs


    def get_attr_dataset(self, offset=0, limit=100):
        query = {}
        attrs = []

        try:
            r = self.amz_attrs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        for attr in list(r):
            del attr['_id']
            attrs.append(attr)

        return attrs

    def get_attr_by_attr_code(self, attr_code):
        query = {}
        query['attr_code'] = attr_code
        attrs = []

        try:
            r = self.amz_attrs.find(query)
        except Exception as e:
            print(e)

        for attr in list(r):
            del attr['_id']
            attrs.append(attr)

        return attrs


    def get_sub_attr_by_attr_code(self, attr_code, offset=0, limit=10):
        query = {}
        query['attr_code'] = attr_code
        sub_attr_list = []

        try:
            r = self.amz_attrs.find(query)
            for attr in list(r):
                sub_attrs = attr['sub_attrs']
                for sub_attr_code in sub_attrs:
                    sub_attr_query = {}
                    sub_attr_query['sub_attr_code'] = sub_attr_code

                    try:
                        r1 = self.db.amz_sub_attrs.find(sub_attr_query)
                        for sub_attr in list(r1):

                            sub_attr_dic = {'sub_attr_code' : sub_attr_code,
                                            'value' : sub_attr['value'],
                                            'text':sub_attr['text']}
                            sub_attr_list.append(sub_attr_dic)
                    except Exception as e:
                        print(e)

        except Exception as e:
            print(e)

        return sub_attr_list


