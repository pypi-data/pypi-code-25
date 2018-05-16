from bl_product_amaz.database import DataBase
from bson.objectid import ObjectId

class US_btgs(DataBase):
    def __init__(self):
        super(US_btgs, self).__init__()
        self.us_btgs = self.db.us_btgs

    def get_btg_dataset(self, offset=0, limit=100):
        query = {}
        btgs = []

        try:
            r = self.us_btgs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        for btg in list(r):
            del btg['_id']
            btgs.append(btg)

        return btgs

    def get_btg_by_node_id(self, node_id, offset=0, limit=10):
        query = {}
        query['node_id'] = node_id
        btgs = []

        try:
            r = self.us_btgs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        for btg in list(r):
            del btg['_id']
            btgs.append(btg)

        return btgs

    def get_btg_by_classification(self, classification, offset=0, limit=10):
        query = {}
        query['classification'] = classification
        btgs = []

        try:
            r = self.us_btgs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        for btg in list(r):
            del btg['_id']
            btgs.append(btg)

        return btgs

    def get_btg_by_classification_field(self, classification_field, offset=0, limit=10):
        query = {}
        query['classification_field'] = classification_field
        btgs = []

        try:
            r = self.us_btgs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        for btg in list(r):
            del btg['_id']
            btgs.append(btg)

        return btgs

    def get_btg_by_valid_value(self, valid_value, offset=0, limit=10):
        query = {}
        query['valid_value'] = valid_value
        btgs = []

        try:
            r = self.us_btgs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        for btg in list(r):
            del btg['_id']
            btgs.append(btg)

        return btgs

    def get_valid_value_by_node_id(self, node_id):
        query={}
        query['node_id'] = node_id

        try:
            r = self.us_btgs.find(query)
        except Exception as e:
            print(e)


        for btg in list(r):
            valid_value = btg['valid_value']
            break

        return valid_value

    def get_attrs_by_node_id(self, node_id, offset=0, limit=10):
        query = {}
        query['node_id'] = node_id
        attrs_list = []


        try:
            r = self.us_btgs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        for btg in list(r):
            for attr in btg['attrs']:
                attrs_query = {}
                attrs_query['attr_code'] = attr
                try:
                    r1 = self.db.amz_attrs.find(attrs_query)
                    for amz_attr in list(r1):
                        attr_dic = {attr : amz_attr['value']}
                        attrs_list.append(attr_dic)
                except Exception as e:
                    print(e)

        return attrs_list


